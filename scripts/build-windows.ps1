param([string]$Python = "$PSScriptRoot\..\venv\Scripts\python.exe", [string]$ReleaseDir = 'dist/release-0.10.19', [switch]$Archive)
$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path "$PSScriptRoot\..").Path
Push-Location "$projectRoot\frontend"
try {
    npm ci
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed.' }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed.' }
} finally { Pop-Location }
Push-Location $projectRoot
try {
    & $Python -m pip install -r desktop/requirements.txt
    if ($LASTEXITCODE -ne 0) { throw 'Desktop dependency installation failed.' }
    & $Python -m unittest discover -s tests -p 'test_*.py'
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
    & $Python scripts/download-speech-model.py
    if ($LASTEXITCODE -ne 0) { throw 'Speech model download failed.' }
    & $Python scripts/download-speaker-model.py
    if ($LASTEXITCODE -ne 0) { throw 'Speaker model download failed.' }
    & $Python -m PyInstaller --noconfirm --distpath $ReleaseDir desktop/Bob.spec
    if ($LASTEXITCODE -ne 0) { throw 'Packaging failed.' }
    if ($Archive) { & $Python scripts/package-release.py --release-dir $ReleaseDir }
    else { & $Python scripts/package-release.py --release-dir $ReleaseDir --folder-only }
    if ($LASTEXITCODE -ne 0) { throw 'Release archive failed.' }
    Get-FileHash -LiteralPath (Join-Path $ReleaseDir 'Bob/Bob.exe') -Algorithm SHA256 | Format-List
} finally { Pop-Location }
