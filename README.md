# AgriMind Fusion

Context-aware crop disease detection with explainable AI and agricultural decision support (B.Tech CSE AI & ML major project).

**What it is.** A MobileNetV2 image classifier (PlantVillage, 15 tomato/potato/pepper classes) with Grad-CAM explanations, wrapped in a FastAPI + React web app that also shows Open-Meteo weather, a rule-based environmental risk engine, a what-if simulator, a traceable recommendation engine, scan history, analytics, PDF reports, a rule-based assistant, and an (optional) Sentinel-2 NDVI/NDMI module.

**What it is not.** It is not a trained multimodal model. PlantVillage images have no matching weather or satellite records, so weather and satellite outputs are kept separate from the image prediction and never change it. The UI labels each panel by source (model output / your inputs / rule-based / general guidance).

## Honest status (what was verified, and where)

| Part | Status |
|---|---|
| Risk engine, knowledge base, recommendations, assistant, PDF report, weather parsing | Unit-tested (17 tests pass: `scripts\run_tests.ps1`) |
| JSX syntax of every frontend file | Checked with esbuild |
| FastAPI app, SQLAlchemy models, routes | Written, compiled, **not yet run** (author's sandbox had no internet) - first run is your test |
| `npm install` / `vite build` | **Not run yet** - do it in step 6 |
| Model training and evaluation scripts | Written, **not run** - you train on your PC; no accuracy numbers exist yet |
| Live Open-Meteo calls | Parsing tested on mock data; **verify live** in step 7 |
| Sentinel-2 / Earth Engine | Written, **untested**, needs your Earth Engine account (`docs/SATELLITE_SETUP.md`). No map layers yet |
| Docker / Render / Vercel | Files provided, **never deployed** - see `docs/DEPLOYMENT.md` |
| Not built | Map drawing, Leaflet layers, satellite index comparison across dates, Alembic migrations, LLM assistant, user accounts |

## Quick start (Windows 11, PowerShell, Python 3.12, CPU only)

Prerequisites: Python 3.12 (`py -3.12 --version`), Node.js LTS (`winget install OpenJS.NodeJS.LTS`, then reopen PowerShell), Git.
Use `py -3.12`, never plain `python`, if you also have Python 3.14/3.15 installed (TensorFlow does not support them).
Unzip to a path **without spaces**, for example `C:\Projects\AgriMind-Fusion`.

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned   # once, if scripts are blocked
cd C:\Projects\AgriMind-Fusion

# 1. Environment (several minutes; TensorFlow is large)
.\scripts\setup_windows.ps1                 # expect "Setup OK"

# 2. Logic tests (no dataset needed)
.\scripts\run_tests.ps1                     # expect "Ran 17 tests ... OK"

# 3. Dataset (Kaggle: emmarex/plantdisease). Download and unzip it yourself, then:
.\scripts\copy_dataset.ps1 -Source "C:\Users\KANAK\Downloads\archive (3)\PlantVillage"   # expect 15 class folders

# 4. Validate + split (writes data\processed\splits.csv and models\class_names.json)
.\.venv\Scripts\python.exe scripts\prepare_data.py --raw-dir data/raw

# 5. Train. First a 2-minute smoke test (its accuracy is meaningless):
.\.venv\Scripts\python.exe scripts\train.py --model mobilenet --epochs 1 --limit-per-class 10
# then the real runs (note seconds/epoch; run baseline on a teammate's PC if you can):
.\.venv\Scripts\python.exe scripts\train.py --model mobilenet --epochs 8 --fine-tune-epochs 3
.\.venv\Scripts\python.exe scripts\train.py --model baseline --epochs 12
.\.venv\Scripts\python.exe scripts\evaluate.py            # writes models\metrics\*

# 6. Run the app (two terminals)
.\scripts\run_backend.ps1      # http://127.0.0.1:8000/docs  -> try GET /api/health
.\scripts\run_frontend.ps1     # http://localhost:5173
```

### Verification checklist (do not skip)
1. `GET http://127.0.0.1:8000/api/health` returns `"status":"ok"` and `"model_ready":true`.
2. In Swagger (`/docs`) call `POST /api/simulator` with the example body - you get a risk category.
3. Crop Doctor: upload a leaf image -> prediction, top 3, Grad-CAM slider, PDF download opens.
4. Scan appears in Scan history; delete asks for confirmation.
5. Weather page: search your town -> current values and 7-day chart load (this is the live Open-Meteo check).
6. `cd frontend; npm run build` completes with no errors.

## Evaluation for the paper
`scripts\evaluate.py` produces accuracy, macro precision/recall/F1, per-class report, confusion matrices, training curves and a baseline-vs-MobileNetV2 comparison in `models\metrics\`. For the field-image generalisation test, download PlantDoc, copy `data/external/plantdoc_label_map.example.json` to `plantdoc_label_map.json`, **check every key against the real folder names**, and run
`python scripts\evaluate.py --external-dir data/external/plantdoc --label-map data/external/plantdoc_label_map.json`.
Split caveat: PlantVillage has no leaf IDs, so near-duplicate photos can land in different splits and inflate test accuracy. State this in the paper.

## API summary
`GET /api/health` · `POST /api/predict` · `GET /api/explain/{id}` · `GET/DELETE /api/scans[/{id}]` · `GET /api/weather[/geocode|/history]` · `POST /api/simulator` · `POST /api/recommendations` · `GET /api/analytics/summary|export` · `GET /api/reports/{id}` · `POST /api/chat` · `GET /api/satellite/status` · `POST /api/satellite/indices`. Details: `docs/API_CONTRACT.md`.

## Team split
Member 1 (ML): `scripts/`, `models/`, `backend/app/services/prediction_service.py`, `gradcam_service.py`. Member 2 (environment/research): `weather_service.py`, `risk_engine.py`, `satellite_service.py`, `disease_knowledge.py`, `research/`, `docs/`. Member 3 (full stack): `frontend/`, `routes/`, DB, reports, deployment.

## Git
```powershell
git init; git add .; git commit -m "feat: initial AgriMind Fusion project"
```
`.gitignore` already excludes `.env`, datasets, `*.keras`, uploads and the database. Never commit Earth Engine keys.

## Troubleshooting
| Symptom | Fix |
|---|---|
| `Activate.ps1 cannot be loaded` | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `No matching distribution found for tensorflow` | You are on Python 3.14/3.15. Recreate the venv with `py -3.12 -m venv .venv` |
| Health shows `model_ready:false` | Train first; check `models\mobilenetv2_final.keras` and `class_names.json` exist |
| Prediction 503 | Same as above; the message names the missing file |
| Grad-CAM 501 | Loaded model is not the MobileNetV2 one; set `MODEL_FILE=mobilenetv2_final.keras` |
| Browser says cannot reach backend | Start `run_backend.ps1`; CORS origin must match `CORS_ORIGINS` in `backend\.env` |
| Weather 502 | No internet or Open-Meteo error; message is shown. History needs end date >= 2 days ago |
