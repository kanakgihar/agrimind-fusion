# Sentinel-2 / Google Earth Engine setup (optional module)

Status: code written in `backend/app/services/satellite_service.py`, **untested** until you finish this setup.

1. Create a Google Cloud project and register it for Earth Engine (noncommercial/research use) at https://earthengine.google.com. Note the project ID.
2. `pip install earthengine-api` inside `.venv`.
3. Local development: `earthengine authenticate` (opens a browser), then set `EE_PROJECT=<your-project-id>` in `backend\.env`.
4. Deployment: create a service account, grant it Earth Engine access, store the JSON key as a **secret file** on the host (never in git or the frontend) and set `EE_SERVICE_ACCOUNT`, `EE_PRIVATE_KEY_FILE`, `EE_PROJECT` as environment variables.
5. Verify: open the Satellite page; status should show installed = yes, project configured = yes; run a query for a farm location and a 120-day range. If no cloud-free scene exists you will see a clear "no usable imagery" message.

Method: collection `COPERNICUS/S2_SR_HARMONIZED`, scenes filtered by `CLOUDY_PIXEL_PERCENTAGE`, per-pixel masking with SCL (cloud shadow 3, cloud 8-9, cirrus 10, snow 11), NDVI = (B8-B4)/(B8+B4), NDMI = (B8-B11)/(B8+B11), mean over a circular buffer at 20 m. These are vegetation/moisture indicators, not disease diagnoses.
