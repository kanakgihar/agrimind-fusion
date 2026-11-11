# Project Synopsis

**Title:** AgriMind Fusion - Context-Aware AI for Crop Stress Detection and Explainable Agricultural Decision Support
**Programme:** B.Tech CSE (AI & ML), Third Year Major Project
**Team:** (Member 1), (Member 2), (Member 3)  **Guide:** (name)

## 1. Introduction
Crop diseases reduce yield and farmers often lack quick access to experts. Deep learning can classify leaf diseases from photos, but most systems give a label without explanation, ignore the weather conditions that drive disease spread, and are trained on lab-style images that may not reflect field conditions.

## 2. Problem statement
Build an accessible web system that (a) detects crop leaf disease from an image, (b) explains the prediction visually, (c) puts the prediction in environmental context, and (d) gives clearly sourced, general management guidance - while stating honestly what the AI can and cannot do.

## 3. Objectives
1. Train and compare a baseline CNN and a MobileNetV2 transfer-learning model on PlantVillage (15 classes) using CPU-friendly settings.
2. Evaluate with accuracy, precision, recall, F1 and confusion matrices; test generalisation on real field images (PlantDoc, overlapping classes).
3. Provide Grad-CAM explanations.
4. Build a rule-based environmental risk engine from Open-Meteo weather, with a what-if simulator.
5. Provide traceable recommendations, scan history, analytics and PDF reports in a React + FastAPI application.
6. (Optional) Add Sentinel-2 NDVI/NDMI field indicators via Google Earth Engine.

## 4. Scope and honesty statement
The classifier is trained only on PlantVillage images; weather and satellite data are **not** aligned with those images, therefore they are not model inputs. The project does not claim a trained multimodal model. Recommendations are general guidance, not a diagnosis.

## 5. Proposed methodology
Data validation and stratified split -> transfer learning (MobileNetV2) vs baseline CNN -> evaluation (lab test set + field images) -> Grad-CAM -> rule-based context engine (Open-Meteo) -> knowledge-based recommendations -> web deployment. See `research/methodology.md`.

## 6. Technology
Python 3.12, TensorFlow/Keras, OpenCV, scikit-learn, FastAPI, SQLAlchemy (SQLite/PostgreSQL), React + Vite + Recharts, ReportLab, Open-Meteo API, Google Earth Engine (optional), Docker.

## 7. Expected outcomes
A working web application, a reproducible evaluation pipeline, an experimental report with measured baseline-vs-transfer-learning results and the lab-to-field accuracy gap, and documentation suitable for a conference-style paper.

## 8. Work plan (4 days for MVP)
Day 1 environment, data, training. Day 2 evaluation, Grad-CAM, API. Day 3 frontend, context engine, history. Day 4 testing, report, documentation, optional satellite/deployment.

## 9. Team responsibilities
Member 1: data, models, evaluation, Grad-CAM. Member 2: weather, risk rules, knowledge base, satellite, research writing. Member 3: frontend, backend integration, database, reports, deployment.

## 10. Datasets and sources
PlantVillage (Kaggle), PlantDoc, Open-Meteo, Sentinel-2 `COPERNICUS/S2_SR_HARMONIZED`. References in `research/references.md`.
