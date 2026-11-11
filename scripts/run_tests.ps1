Set-Location (Split-Path $PSScriptRoot -Parent)
& .\.venv\Scripts\python.exe -m unittest discover -s backend\tests -v
