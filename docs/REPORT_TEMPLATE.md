# An Explainable Context-Aware AI Framework for Crop Disease Recognition and Agricultural Decision Support
*Experimental report / paper skeleton. Items marked [RESULT] must be filled with measured values from `models/metrics/`. Delete nothing that is a limitation.*

**Abstract.** [Write last. State: data, models, key measured result, lab-to-field gap, what is rule-based vs learned.]

## 1. Introduction
Motivation, problem statement, contributions (list only what was actually built and tested).

## 2. Related work
[Add 8-12 real papers: PlantVillage CNNs, MobileNet-based plant disease work, PlantDoc/field generalisation, Grad-CAM in agriculture, weather-based disease forecasting. Use `research/references.md` as seed.]

## 3. Data
3.1 PlantVillage: 15 classes, [RESULT: images before/after cleaning, duplicates removed from `data_report.json`], split 70/15/15. 3.2 PlantDoc field subset: class mapping table, number of images [RESULT]. 3.3 Open-Meteo and Sentinel-2: context sources, not training data. 3.4 Limitations: controlled backgrounds; possible near-duplicate leakage.

## 4. Methods
4.1 Preprocessing and augmentation. 4.2 Baseline CNN. 4.3 MobileNetV2 transfer learning (+ fine-tuning). 4.4 Training setup (CPU, batch size, epochs, seconds/epoch [RESULT]). 4.5 Grad-CAM. 4.6 Environmental rule engine (rules-v1, thresholds and their justification/citations). 4.7 Recommendation engine. 4.8 System architecture (insert `docs/ARCHITECTURE.md` diagrams).

## 5. Experiments and results
5.1 Test-set comparison table [RESULT]. 5.2 Per-class precision/recall/F1 [RESULT]. 5.3 Confusion matrices and most confused pairs [RESULT]. 5.4 Training curves [RESULT]. 5.5 External field evaluation and accuracy drop [RESULT]. 5.6 CPU inference time [RESULT]. 5.7 Grad-CAM case studies: correct, incorrect, background-attention failures. 5.8 Rule engine behaviour: scenario table from the simulator (illustrative, labelled as rules, not validation).

## 6. Discussion
What the numbers do and do not show; softmax confidence is not calibrated; why weather is not fused into training; threats to validity.

## 7. Limitations
15 classes and 3 crops only; PlantVillage domain gap; unvalidated rule thresholds; knowledge base not expert-reviewed; no user study; satellite module [tested / untested - state which].

## 8. Conclusion and future work
Aligned multimodal data collection, calibration, field trials with agronomists, more crops, regional language support.

## References
[From `research/references.md`, verified.]
