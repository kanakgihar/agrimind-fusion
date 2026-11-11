# Copies the 15 PlantVillage class folders into data\raw, skipping a nested duplicate "PlantVillage" folder.
# Usage:  .\scripts\copy_dataset.ps1 -Source "C:\Users\KANAK\Downloads\archive (3)\PlantVillage"
param([Parameter(Mandatory = $true)][string]$Source)
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path $Source)) { throw "Source not found: $Source" }
New-Item -ItemType Directory -Force -Path data\raw | Out-Null
robocopy "$Source" "data\raw" /E /XD "$Source\PlantVillage" /NFL /NDL /NJH /NJS
if ($LASTEXITCODE -ge 8) { throw "robocopy failed with code $LASTEXITCODE" }
$classes = Get-ChildItem data\raw -Directory
Write-Host "Class folders: $($classes.Count) (expected 15 for this dataset)"
$classes | ForEach-Object { [pscustomobject]@{ Class = $_.Name; Images = (Get-ChildItem $_.FullName -File -Include *.jpg,*.jpeg,*.png -Recurse).Count } } | Format-Table -AutoSize
