# Run from the project root:  .\scripts\setup_windows.ps1
$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)

py -3.12 --version
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 not found. Install it from python.org and re-run." }

if (-not (Test-Path .\.venv\Scripts\python.exe)) { py -3.12 -m venv .venv }
& .\.venv\Scripts\python.exe --version
& .\.venv\Scripts\python.exe -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "pip upgrade failed" }
& .\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt -r backend\requirements.txt
if ($LASTEXITCODE -ne 0) { throw "dependency install failed - read the error above" }

if (-not (Test-Path backend\.env)) { Copy-Item backend\.env.example backend\.env; Write-Host "Created backend\.env" }

& .\.venv\Scripts\python.exe -c "import tensorflow as tf, fastapi, sqlalchemy, cv2; print('TensorFlow', tf.__version__, '| FastAPI', fastapi.__version__)"
if ($LASTEXITCODE -ne 0) { throw "import check failed" }
Write-Host "Setup OK" -ForegroundColor Green
