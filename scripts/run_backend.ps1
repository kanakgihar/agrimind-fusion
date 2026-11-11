# Starts the API on http://127.0.0.1:8000  (docs at /docs)
Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) "backend")
& ..\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
