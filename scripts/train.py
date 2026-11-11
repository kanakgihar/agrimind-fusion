"""Train baseline CNN or MobileNetV2 on the prepared PlantVillage splits (CPU friendly).

Examples (from project root):
    python scripts/train.py --model mobilenet --epochs 1 --limit-per-class 10   # smoke test
    python scripts/train.py --model mobilenet --epochs 8 --fine-tune-epochs 3
    python scripts/train.py --model baseline --epochs 12
"""
import argparse
import json
import time
from pathlib import Path

import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

IMG = 224
SEED = 42
BASE_LAYER_NAME = "mobilenetv2_base"  # the backend Grad-CAM service relies on this name


def make_ds(df, raw: Path, class_to_idx, training: bool, batch: int):
    paths = [str(raw / p) for p in df["path"]]
    labels = df["label"].map(class_to_idx).astype("int32").values

    def load(path, label):
        img = tf.io.decode_image(tf.io.read_file(path), channels=3, expand_animations=False)
        img.set_shape([None, None, 3])
        img = tf.image.resize(img, (IMG, IMG))
        return tf.cast(img, tf.float32), label  # 0-255; scaling happens inside the model

    ds = tf.data.Dataset.from_tensor_slices((paths, labels))
    if training:
        ds = ds.shuffle(2048, seed=SEED, reshuffle_each_iteration=True)
    ds = ds.map(load, num_parallel_calls=tf.data.AUTOTUNE).batch(batch)
    return ds.prefetch(tf.data.AUTOTUNE)


def augmentation():
    return keras.Sequential([
        layers.RandomFlip("horizontal_and_vertical"),
        layers.RandomRotation(0.1),
        layers.RandomZoom(0.1),
        layers.RandomContrast(0.1),
    ], name="augmentation")


def build_mobilenet(n_classes):
    base = keras.applications.MobileNetV2(
        input_shape=(IMG, IMG, 3), include_top=False, weights="imagenet", name=BASE_LAYER_NAME)
    base.trainable = False
    inp = keras.Input((IMG, IMG, 3))
    x = augmentation()(inp)
    x = keras.applications.mobilenet_v2.preprocess_input(x)  # scales to [-1, 1]
    x = base(x, training=False)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.2)(x)
    out = layers.Dense(n_classes, activation="softmax")(x)
    return keras.Model(inp, out, name="mobilenetv2_agri"), base


def build_baseline(n_classes):
    inp = keras.Input((IMG, IMG, 3))
    x = augmentation()(inp)
    x = layers.Rescaling(1.0 / 255)(x)
    for f in (32, 64, 128, 128):
        x = layers.Conv2D(f, 3, padding="same", activation="relu")(x)
        x = layers.BatchNormalization()(x)
        x = layers.MaxPooling2D()(x)
    x = layers.GlobalAveragePooling2D()(x)
    x = layers.Dropout(0.3)(x)
    out = layers.Dense(n_classes, activation="softmax")(x)
    return keras.Model(inp, out, name="baseline_cnn"), None


def compile_model(model, lr):
    model.compile(optimizer=keras.optimizers.Adam(lr),
                  loss="sparse_categorical_crossentropy", metrics=["accuracy"])


def callbacks(tag, models_dir, metrics_dir, suffix=""):
    return [
        keras.callbacks.EarlyStopping(monitor="val_accuracy", patience=3, restore_best_weights=True),
        keras.callbacks.ModelCheckpoint(str(models_dir / f"{tag}{suffix}.keras"),
                                        monitor="val_accuracy", save_best_only=True),
        keras.callbacks.CSVLogger(str(metrics_dir / f"{tag}{suffix}_history.csv")),
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=["baseline", "mobilenet"], required=True)
    ap.add_argument("--epochs", type=int, default=8)
    ap.add_argument("--fine-tune-epochs", type=int, default=0)
    ap.add_argument("--batch-size", type=int, default=32)
    ap.add_argument("--limit-per-class", type=int, default=0, help="smoke-test: cap images per class/split")
    ap.add_argument("--raw-dir", default="data/raw")
    ap.add_argument("--splits", default="data/processed/splits.csv")
    ap.add_argument("--models-dir", default="models")
    a = ap.parse_args()

    keras.utils.set_random_seed(SEED)
    raw, models_dir = Path(a.raw_dir), Path(a.models_dir)
    metrics_dir = models_dir / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    class_names = json.loads((models_dir / "class_names.json").read_text())
    class_to_idx = {c: i for i, c in enumerate(class_names)}
    df = pd.read_csv(a.splits)
    if a.limit_per_class:
        df = df.groupby(["split", "label"]).head(a.limit_per_class)
    tr, va = df[df.split == "train"], df[df.split == "val"]
    print(f"train={len(tr)} val={len(va)} classes={len(class_names)}")

    train_ds = make_ds(tr, raw, class_to_idx, True, a.batch_size)
    val_ds = make_ds(va, raw, class_to_idx, False, a.batch_size)

    build = build_mobilenet if a.model == "mobilenet" else build_baseline
    model, base = build(len(class_names))
    tag = "mobilenetv2" if a.model == "mobilenet" else "baseline_cnn"
    compile_model(model, 1e-3)
    model.summary()

    t0 = time.time()
    model.fit(train_ds, validation_data=val_ds, epochs=a.epochs,
              callbacks=callbacks(tag, models_dir, metrics_dir))

    if a.model == "mobilenet" and a.fine_tune_epochs > 0:
        base.trainable = True
        for layer in base.layers[:-30]:
            layer.trainable = False
        for layer in base.layers:
            if isinstance(layer, layers.BatchNormalization):
                layer.trainable = False
        compile_model(model, 1e-5)
        model.fit(train_ds, validation_data=val_ds, epochs=a.fine_tune_epochs,
                  callbacks=callbacks(tag, models_dir, metrics_dir, "_finetuned"))

    model.save(models_dir / f"{tag}_final.keras")
    meta = {"model": tag, "args": vars(a), "train_seconds": round(time.time() - t0, 1),
            "tensorflow": tf.__version__, "params": int(model.count_params()),
            "n_train": len(tr), "n_val": len(va)}
    (metrics_dir / f"{tag}_train_meta.json").write_text(json.dumps(meta, indent=2))
    print("Saved:", models_dir / f"{tag}_final.keras")


if __name__ == "__main__":
    main()
