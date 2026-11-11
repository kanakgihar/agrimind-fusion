# Starts the React dev server on http://localhost:5173
Set-Location (Join-Path (Split-Path $PSScriptRoot -Parent) "frontend")
if (-not (Test-Path node_modules)) { npm install; if ($LASTEXITCODE -ne 0) { throw "npm install failed" } }
npm run dev
