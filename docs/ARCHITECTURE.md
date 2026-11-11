# Architecture

```mermaid
flowchart LR
  U[User: leaf photo + optional weather] --> FE[React + Vite dashboard]
  FE -->|REST/JSON| API[FastAPI]
  API --> PRED[prediction_service<br/>MobileNetV2 .keras]
  API --> CAM[gradcam_service]
  API --> WX[weather_service<br/>Open-Meteo]
  API --> RISK[risk_engine<br/>documented rules]
  API --> REC[recommendation_service<br/>knowledge base]
  API --> SAT[satellite_service<br/>Earth Engine Sentinel-2, optional]
  API --> REP[report_service PDF]
  API --> DB[(SQLite / PostgreSQL)]
  PRED -. never receives weather .- RISK
```

The image model and the environmental engine are independent. The decision-support layer only *places their outputs side by side* and builds recommendations from (predicted class, confidence, rule-based risk).

```mermaid
sequenceDiagram
  participant B as Browser
  participant A as FastAPI
  participant M as MobileNetV2
  participant R as risk_engine
  B->>A: POST /api/predict (image, optional weather)
  A->>A: validate + re-encode image
  A->>M: 224x224 float 0-255
  M-->>A: softmax scores
  A->>R: assess(weather) if provided
  A->>A: build recommendation, save scan
  A-->>B: prediction + risk + recommendation
  B->>A: GET /api/explain/{id}
  A->>M: Grad-CAM (pre-softmax logit)
  A-->>B: overlay + region summary
```

## Training pipeline
PlantVillage -> `prepare_data.py` (validate, dedupe by MD5, stratified 70/15/15, seed 42) -> `train.py` (baseline CNN or MobileNetV2: frozen backbone, optional fine-tune of last 30 layers with BatchNorm frozen, early stopping) -> `evaluate.py` (test split, optional PlantDoc field images).

## Data sources and their role
| Source | Role | Linked to the CNN? |
|---|---|---|
| PlantVillage | Labelled leaf images, trains/evaluates classifier | Yes |
| PlantDoc (optional) | Field images for generalisation test | Evaluation only |
| Open-Meteo | Current/forecast/historical weather for context | No |
| Sentinel-2 via Earth Engine | Field-level NDVI/NDMI indicators | No |
