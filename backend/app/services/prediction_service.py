"""Loads the trained Keras model once and runs inference. TensorFlow is imported lazily."""
import json
import logging
import threading

import numpy as np
from PIL import Image

from app.config import settings
from app.services.disease_knowledge import display_name

log = logging.getLogger("agrimind.predict")
IMG = 224
NOTE = "confidence is a softmax score, not a calibrated probability"


class ModelNotReady(Exception):
    pass


def crop_of(class_name: str) -> str:
    return class_name.split("_")[0]


def is_healthy(class_name: str) -> bool:
    return class_name.lower().endswith("healthy")


class PredictionService:
    def __init__(self):
        self._model = None
        self._classes = None
        self._lock = threading.Lock()

    @property
    def model_path(self):
        return settings.models_dir / settings.model_file

    @property
    def model_version(self) -> str:
        return self.model_path.stem

    def status(self) -> dict:
        return {"model_file": settings.model_file, "model_file_exists": self.model_path.exists(),
                "class_names_exist": (settings.models_dir / "class_names.json").exists(),
                "model_loaded": self._model is not None}

    def load(self):
        with self._lock:
            if self._model is not None:
                return
            cls_file = settings.models_dir / "class_names.json"
            if not self.model_path.exists() or not cls_file.exists():
                raise ModelNotReady(
                    f"Model not found. Expected {self.model_path} and {cls_file}. "
                    "Train it first: python scripts/prepare_data.py, then python scripts/train.py --model mobilenet")
            from tensorflow import keras  # lazy import
            self._classes = json.loads(cls_file.read_text())
            self._model = keras.models.load_model(self.model_path)
            out = self._model.output_shape[-1]
            if out != len(self._classes):
                self._model = None
                raise ModelNotReady(f"class_names.json has {len(self._classes)} classes but the model outputs {out}.")
            log.info("Model loaded: %s (%d classes)", self.model_path.name, len(self._classes))

    @property
    def model(self):
        self.load()
        return self._model

    @property
    def classes(self):
        self.load()
        return self._classes

    def preprocess(self, image_path) -> np.ndarray:
        import tensorflow as tf
        img = Image.open(image_path).convert("RGB")
        arr = np.asarray(img, dtype=np.float32)
        x = tf.image.resize(arr, (IMG, IMG)).numpy()  # same resize op as training; values stay 0-255
        return x[None, ...]

    def predict(self, image_path) -> dict:
        model = self.model
        x = self.preprocess(image_path)
        probs = model(x, training=False).numpy()[0]
        order = np.argsort(probs)[::-1][:3]
        top3 = [{"class": self._classes[i], "display_name": display_name(self._classes[i]),
                 "confidence": float(probs[i])} for i in order]
        best = top3[0]["class"]
        return {"predicted_class": best, "display_name": display_name(best), "crop": crop_of(best),
                "is_healthy": is_healthy(best), "confidence": top3[0]["confidence"], "top3": top3,
                "class_index": int(order[0]), "model_version": self.model_version, "note": NOTE}


prediction_service = PredictionService()
