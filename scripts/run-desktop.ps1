$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path "$PSScriptRoot\..").Path
Push-Location $projectRoot
try { & "$projectRoot\venv\Scripts\python.exe" -m desktop.main }
finally { Pop-Location }
