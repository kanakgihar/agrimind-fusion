"""Grad-CAM for the MobileNetV2 model built by scripts/train.py (nested base layer 'mobilenetv2_base')."""
import cv2
import numpy as np
from PIL import Image

BASE_LAYER = "mobilenetv2_base"
MAX_SIDE = 512


class GradCamUnsupported(Exception):
    pass


def compute_cam(model, x: np.ndarray, class_idx: int) -> np.ndarray:
    """x: (1,224,224,3) float 0-255. Returns a 7x7 map in [0,1]. Uses the pre-softmax logit of class_idx."""
    import tensorflow as tf
    names = [layer.name for layer in model.layers]
    if BASE_LAYER not in names:
        raise GradCamUnsupported("Grad-CAM needs the MobileNetV2 model (layer 'mobilenetv2_base' not found).")
    i = names.index(BASE_LAYER)
    base, head = model.layers[i], model.layers[i + 1:]
    dense = head[-1]
    kernel, bias = dense.get_weights()
    xin = tf.convert_to_tensor(x / 127.5 - 1.0, dtype=tf.float32)  # MobileNetV2 preprocess_input
    with tf.GradientTape() as tape:
        feats = base(xin, training=False)
        tape.watch(feats)
        h = feats
        for layer in head[:-1]:  # GAP + dropout (inactive at inference)
            h = layer(h)
        logits = tf.matmul(h, tf.constant(kernel)) + tf.constant(bias)
        score = logits[:, class_idx]
    grads = tape.gradient(score, feats)
    weights = tf.reduce_mean(grads, axis=(1, 2))
    cam = tf.nn.relu(tf.reduce_sum(feats * weights[:, None, None, :], axis=-1))[0].numpy()
    m = cam.max()
    return cam / m if m > 0 else cam


def describe_regions(cam_full: np.ndarray) -> dict:
    """Plain-language summary computed from the heatmap (not invented)."""
    mask = cam_full >= 0.5
    cover = float(mask.mean())
    if not mask.any():
        return {"main_region": "no clear region", "coverage_pct": 0.0}
    ys, xs = np.nonzero(mask)
    h, w = cam_full.shape
    cy, cx = ys.mean() / h, xs.mean() / w
    v = "upper" if cy < 0.34 else "lower" if cy > 0.66 else "middle"
    hz = "left" if cx < 0.34 else "right" if cx > 0.66 else "centre"
    region = "central" if (v, hz) == ("middle", "centre") else f"{v} {hz}".replace("middle ", "")
    return {"main_region": region, "coverage_pct": round(100 * cover, 1)}


def generate(model, class_idx: int, x: np.ndarray, image_path, out_overlay, out_heatmap) -> dict:
    cam = compute_cam(model, x, class_idx)
    img = Image.open(image_path).convert("RGB")
    img.thumbnail((MAX_SIDE, MAX_SIDE))
    rgb = np.asarray(img)
    h, w = rgb.shape[:2]
    cam_full = np.clip(cv2.resize(cam, (w, h), interpolation=cv2.INTER_CUBIC), 0, 1)
    heat = cv2.cvtColor(cv2.applyColorMap(np.uint8(255 * cam_full), cv2.COLORMAP_JET), cv2.COLOR_BGR2RGB)
    overlay = np.uint8(0.55 * rgb + 0.45 * heat)
    Image.fromarray(heat).save(out_heatmap, quality=90)
    Image.fromarray(overlay).save(out_overlay, quality=90)
    Image.fromarray(rgb).save(str(out_overlay).replace("_overlay", "_original"), quality=90)
    return describe_regions(cam_full)
