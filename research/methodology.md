# Methodology (fill numbers only from `models/metrics/`)

**Problem.** Image-only leaf disease classifiers ignore context and rarely explain themselves; lab-trained models often fail on field photos.
**Proposed framework.** (1) MobileNetV2 transfer learning on PlantVillage; (2) Grad-CAM explanations; (3) a separate, rule-based environmental risk engine fed by Open-Meteo; (4) knowledge-based recommendations traceable to inputs; (5) optional Sentinel-2 NDVI/NDMI field indicators.
**Not claimed.** A jointly trained multimodal model - PlantVillage has no aligned weather/satellite records. Fusion here is at the decision-support level only.

## Data
PlantVillage (Kaggle `emmarex/plantdisease`), 15 classes. Preprocessing: integrity check, MD5 de-duplication (and label-conflict removal), 224x224 RGB, stratified 70/15/15 split with seed 42. Augmentation (train only): flips, rotation 0.1, zoom 0.1, contrast 0.1. Limitation: no leaf IDs, so near-duplicates may cross splits.
## Models
Baseline: 4 conv blocks (32-64-128-128) + BN + pooling + GAP + dropout 0.3. MobileNetV2: ImageNet weights, frozen backbone, GAP, dropout 0.2, dense softmax; optional fine-tuning of last 30 layers at lr 1e-5. Adam, sparse categorical cross-entropy, early stopping on val accuracy (patience 3).
## Explainability
Grad-CAM on the last MobileNetV2 feature map using the pre-softmax logit of the predicted class; 7x7 map upsampled; region summary from pixels >= 0.5.
## Environmental rules
See `backend/app/services/risk_engine.py` (`rules-v1`). Thresholds are generic and unvalidated; justify or cite sources before publishing, or run a sensitivity analysis.
## Experiments to run
E1 baseline vs MobileNetV2 (test split). E2 effect of fine-tuning. E3 external field images (PlantDoc, mapped classes only) - report the lab-to-field drop. E4 CPU latency per image. E5 qualitative Grad-CAM analysis (correct vs wrong, leaf vs background attention).
