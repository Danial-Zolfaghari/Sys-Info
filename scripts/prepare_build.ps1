param([string]$ProjectRoot = (Join-Path $PSScriptRoot ".."))
$ErrorActionPreference = "Stop"
$guiRoot = Join-Path $ProjectRoot "gui"
$tauriRoot = Join-Path $guiRoot "src-tauri"
$iconsDir = Join-Path $tauriRoot "icons"
$publicDir = Join-Path $guiRoot "public"
$resourceDir = Join-Path $tauriRoot "resources"
$collectorScript = Join-Path $ProjectRoot "collector\sys_info_collector.py"
$collectorOut = Join-Path $resourceDir "sys-info-collector.exe"

Write-Host "==> Preparing SysInfo build assets..."
New-Item -ItemType Directory -Force -Path $resourceDir | Out-Null

python -m pip install -r (Join-Path $ProjectRoot "requirements-build.txt")
python (Join-Path $ProjectRoot "scripts\generate_icons.py")
Copy-Item (Join-Path $iconsDir "icon.png") (Join-Path $publicDir "icon.png") -Force

$work = Join-Path $ProjectRoot ".build-collector"
$dist = Join-Path $work "dist"
Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path $work | Out-Null
python -m PyInstaller --noconfirm --clean --onefile --name sys-info-collector --distpath $dist --workpath (Join-Path $work "work") --specpath $work $collectorScript
Copy-Item (Join-Path $dist "sys-info-collector.exe") $collectorOut -Force
Remove-Item $work -Recurse -Force -ErrorAction SilentlyContinue
Write-Host "==> Collector bundled at $collectorOut"
