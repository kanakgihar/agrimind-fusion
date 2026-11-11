"""Evaluate trained models on the held-out TEST split (and optionally on external field images).

From project root:
    python scripts/evaluate.py                       # evaluates every *_final.keras found in models/
    python scripts/evaluate.py --external-dir data/external/plantdoc --label-map data/external/plantdoc_label_map.json

Outputs (models/metrics/):
    comparison.csv / comparison.md, <tag>_per_class.csv, <tag>_confusion_matrix.png/.csv,
    <tag>_curves.png, <tag>_external_*.{csv,png}  (only when --external-dir is given)
Every number comes from running the model; nothing is hard-coded.
"""
import argparse
import json
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             precision_recall_fscore_support)

sys.path.insert(0, str(Path(__file__).parent))
from tensorflow import keras  # noqa: E402
from train import make_ds  # noqa: E402

TAGS = {"baseline_cnn": "Baseline CNN", "mobilenetv2": "MobileNetV2 (transfer learning)"}


def plot_cm(cm, labels, title, path):
    fig, ax = plt.subplots(figsize=(10, 9))
    ax.imshow(cm, cmap="Greens")
    ax.set_xticks(range(len(labels)))
    ax.set_yticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=90, fontsize=7)
    ax.set_yticklabels(labels, fontsize=7)
    thr = cm.max() / 2 if cm.max() else 1
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            if cm[i, j]:
                ax.text(j, i, int(cm[i, j]), ha="center", va="center", fontsize=6,
                        color="white" if cm[i, j] > thr else "black")
    ax.set_xlabel("Predicted")
    ax.set_ylabel("True")
    ax.set_title(title)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


def plot_curves(tag, metrics_dir):
    files = [metrics_dir / f"{tag}_history.csv", metrics_dir / f"{tag}_finetuned_history.csv"]
    hist = [pd.read_csv(f) for f in files if f.exists()]
    if not hist:
        return
    h = pd.concat(hist, ignore_index=True)
    fig, ax = plt.subplots(1, 2, figsize=(11, 4))
    ax[0].plot(h["accuracy"], label="train")
    ax[0].plot(h["val_accuracy"], label="validation")
    ax[0].set_title(f"{tag}: accuracy")
    ax[0].set_xlabel("epoch (fine-tuning epochs appended)")
    ax[0].legend()
    ax[1].plot(h["loss"], label="train")
    ax[1].plot(h["val_loss"], label="validation")
    ax[1].set_title(f"{tag}: loss")
    ax[1].set_xlabel("epoch")
    ax[1].legend()
    fig.tight_layout()
    fig.savefig(metrics_dir / f"{tag}_curves.png", dpi=150)
    plt.close(fig)


def predict_all(model, ds):
    t0 = time.time()
    probs = model.predict(ds, verbose=0)
    return probs, time.time() - t0


def summarize(y_true, y_pred, labels_idx, names):
    p, r, f, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels_idx, average="macro", zero_division=0)
    _, _, fw, _ = precision_recall_fscore_support(y_true, y_pred, labels=labels_idx, average="weighted", zero_division=0)
    return {"accuracy": accuracy_score(y_true, y_pred), "precision_macro": p, "recall_macro": r,
            "f1_macro": f, "f1_weighted": fw}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--splits", default="data/processed/splits.csv")
    ap.add_argument("--models-dir", default="models")
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--external-dir", default="")
    ap.add_argument("--label-map", default="", help="JSON {external_folder_name: our_class_name}")
    a = ap.parse_args()

    models_dir = Path(a.models_dir)
    metrics_dir = models_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    names = json.loads((models_dir / "class_names.json").read_text())
    c2i = {c: i for i, c in enumerate(names)}
    idx = list(range(len(names)))

    test_df = pd.read_csv(a.splits).query("split == 'test'")
    test_ds = make_ds(test_df, Path(a.raw_dir), c2i, False, a.batch_size)
    y_true = test_df["label"].map(c2i).values

    ext_df = None
    if a.external_dir:
        ext_root = Path(a.external_dir)
        lmap = json.loads(Path(a.label_map).read_text()) if a.label_map else {}
        rows = []
        for p in ext_root.rglob("*"):
            if p.is_file() and p.suffix.lower() in {".jpg", ".jpeg", ".png"}:
                mapped = lmap.get(p.parent.name)
                if mapped in c2i:
                    rows.append({"path": p.relative_to(ext_root).as_posix(), "label": mapped})
        ext_df = pd.DataFrame(rows)
        print(f"External images with a mapped label: {len(ext_df)}")
        if ext_df.empty:
            ext_df = None

    results = []
    for tag, pretty in TAGS.items():
        f = models_dir / f"{tag}_final.keras"
        if not f.exists():
            print(f"[skip] {f} not found")
            continue
        print(f"\n=== {pretty} ===")
        model = keras.models.load_model(f)
        probs, secs = predict_all(model, test_ds)
        y_pred = probs.argmax(1)
        s = summarize(y_true, y_pred, idx, names)
        s.update({"model": pretty, "params": int(model.count_params()), "n_test": len(y_true),
                  "cpu_ms_per_image_batched": round(1000 * secs / len(y_true), 2)})
        rep = classification_report(y_true, y_pred, labels=idx, target_names=names, output_dict=True, zero_division=0)
        pd.DataFrame(rep).T.to_csv(metrics_dir / f"{tag}_per_class.csv")
        cm = confusion_matrix(y_true, y_pred, labels=idx)
        pd.DataFrame(cm, index=names, columns=names).to_csv(metrics_dir / f"{tag}_confusion_matrix.csv")
        plot_cm(cm, names, f"{pretty} - test confusion matrix", metrics_dir / f"{tag}_confusion_matrix.png")
        plot_curves(tag, metrics_dir)
        print({k: (round(v, 4) if isinstance(v, float) else v) for k, v in s.items()})

        if ext_df is not None:
            ext_ds = make_ds(ext_df, Path(a.external_dir), c2i, False, a.batch_size)
            ey = ext_df["label"].map(c2i).values
            ep = model.predict(ext_ds, verbose=0).argmax(1)
            present = sorted(set(ey))
            es = summarize(ey, ep, present, names)
            s.update({f"external_{k}": v for k, v in es.items()})
            s["n_external"] = len(ey)
            erep = classification_report(ey, ep, labels=present, target_names=[names[i] for i in present],
                                         output_dict=True, zero_division=0)
            pd.DataFrame(erep).T.to_csv(metrics_dir / f"{tag}_external_per_class.csv")
            ecm = confusion_matrix(ey, ep, labels=present)
            plot_cm(ecm, [names[i] for i in present], f"{pretty} - external field images",
                    metrics_dir / f"{tag}_external_confusion_matrix.png")
            print("external:", {k: round(v, 4) for k, v in es.items()})
        results.append(s)

    if results:
        out = pd.DataFrame(results).set_index("model")
        out.to_csv(metrics_dir / "comparison.csv")
        (metrics_dir / "comparison.md").write_text(out.round(4).to_markdown() if hasattr(out, "to_markdown") else out.round(4).to_string())
        print("\nSaved comparison to", metrics_dir / "comparison.csv")
    else:
        print("No trained models found. Run scripts/train.py first.")


if __name__ == "__main__":
    main()
