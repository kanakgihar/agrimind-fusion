# Deployment notes (nothing here has been deployed yet - verify each step)

## Backend (Render or similar, Docker)
1. Train locally, then make the model available to the container: simplest is to commit `models/class_names.json` and host `mobilenetv2_final.keras` in storage (Release asset / object storage) and download it at build time, or copy it into `models/` before `docker build` (it is gitignored by default).
2. Create a managed PostgreSQL instance; set `DATABASE_URL` from its connection string.
3. Environment variables: `DATABASE_URL`, `CORS_ORIGINS=https://<your-vercel-app>.vercel.app`, `MODEL_FILE`, optional `EE_*`.
4. **Persistent storage**: uploaded images live in `STORAGE_DIR`. Mount a persistent disk there; otherwise images vanish on redeploy. For production use object storage instead (not implemented).
5. Health check path: `/api/health`.
6. TensorFlow needs ~1 GB RAM; free tiers may be too small.

## Frontend (Vercel)
Root directory `frontend`, build `npm run build`, output `dist`, env `VITE_API_URL=https://<backend-url>` (no trailing slash). `vercel.json` rewrites routes to `index.html`.

## Verify after deploying
`/api/health` -> model_ready true; upload a leaf from the deployed frontend; confirm no CORS errors in the browser console.
Known gaps: no authentication (sessions are an unguessable browser ID), uploads are served from unguessable URLs, no Alembic migrations (tables are created at startup).
