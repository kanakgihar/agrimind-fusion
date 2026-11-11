"""Validate PlantVillage images and create reproducible stratified splits.

Run from the project root:
    python scripts/prepare_data.py --raw-dir data/raw
Outputs:
    data/processed/splits.csv, data/processed/data_report.json
    models/class_names.json, models/preprocessing_config.json
"""
import argparse
import hashlib
import json
from pathlib import Path

import pandas as pd
from PIL import Image
from sklearn.model_selection import train_test_split

IMG_EXT = {".jpg", ".jpeg", ".png"}
IMG_SIZE = 224


def md5_of(path: Path) -> str:
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_valid_image(path: Path) -> bool:
    try:
        with Image.open(path) as im:
            im.verify()
        with Image.open(path) as im:
            im.load()
        return True
    except Exception:
        return False


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--out-dir", default="data/processed")
    ap.add_argument("--models-dir", default="models")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()

    raw, out, models = Path(a.raw_dir), Path(a.out_dir), Path(a.models_dir)
    if not raw.is_dir():
        raise SystemExit(f"Raw dir not found: {raw.resolve()}")
    out.mkdir(parents=True, exist_ok=True)
    models.mkdir(parents=True, exist_ok=True)

    files = sorted(p for p in raw.rglob("*") if p.is_file() and p.suffix.lower() in IMG_EXT)
    if not files:
        raise SystemExit(f"No images found under {raw.resolve()}")
    print(f"Found {len(files)} image files. Validating (this takes a few minutes)...")

    records, corrupt = [], []
    for i, p in enumerate(files, 1):
        if i % 2000 == 0:
            print(f"  checked {i}/{len(files)}")
        if not is_valid_image(p):
            corrupt.append(p.relative_to(raw).as_posix())
            continue
        records.append({"path": p.relative_to(raw).as_posix(), "label": p.parent.name, "md5": md5_of(p)})

    df = pd.DataFrame(records)

    # Same bytes under different class names = label conflict -> drop all copies.
    n_labels = df.groupby("md5")["label"].nunique()
    conflict_hashes = set(n_labels[n_labels > 1].index)
    n_conflict_files = int(df["md5"].isin(conflict_hashes).sum())
    df = df[~df["md5"].isin(conflict_hashes)]

    # Exact duplicates (e.g. nested PlantVillage/PlantVillage copy) -> keep one.
    n_dupes = int(df.duplicated("md5").sum())
    df = df.drop_duplicates("md5", keep="first").reset_index(drop=True)

    counts = df["label"].value_counts()
    if counts.min() < 10:
        raise SystemExit(f"A class has fewer than 10 images:\n{counts.tail()}")

    train_df, tmp = train_test_split(df, test_size=0.30, stratify=df["label"], random_state=a.seed)
    val_df, test_df = train_test_split(tmp, test_size=0.50, stratify=tmp["label"], random_state=a.seed)
    splits = pd.concat([train_df.assign(split="train"), val_df.assign(split="val"),
                        test_df.assign(split="test")], ignore_index=True)
    splits.to_csv(out / "splits.csv", index=False)

    class_names = sorted(df["label"].unique())
    (models / "class_names.json").write_text(json.dumps(class_names, indent=2))
    (models / "preprocessing_config.json").write_text(json.dumps({
        "img_size": IMG_SIZE, "channels": 3, "seed": a.seed,
        "split": {"train": 0.70, "val": 0.15, "test": 0.15},
        "note": "Pixels are fed as float 0-255; model-internal layers do scaling.",
    }, indent=2))

    report = {
        "files_found": len(files), "corrupt_removed": len(corrupt), "corrupt_files": corrupt,
        "label_conflict_files_removed": n_conflict_files, "exact_duplicates_removed": n_dupes,
        "images_kept": len(df), "num_classes": len(class_names),
        "split_sizes": splits["split"].value_counts().to_dict(), "seed": a.seed,
        "limitation": "Near-duplicate images of the same leaf may fall in different splits "
                      "(PlantVillage has no leaf IDs), which can inflate test accuracy.",
    }
    (out / "data_report.json").write_text(json.dumps(report, indent=2))

    print("\n=== DATA REPORT ===")
    print({k: v for k, v in report.items() if k != "corrupt_files"})
    print("\nPer-class counts by split:")
    print(pd.crosstab(splits["label"], splits["split"]).to_string())


if __name__ == "__main__":
    main()
