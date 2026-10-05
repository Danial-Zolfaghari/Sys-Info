param(
    [string]$DestRoot = (Join-Path $PSScriptRoot "..\gui\src-tauri\WebView2Runtime")
)

$ErrorActionPreference = "Stop"
$marker = Join-Path $DestRoot ".ready"

if (Test-Path $marker) {
    Write-Host "WebView2 runtime already prepared."
    exit 0
}

$msedge = Get-ChildItem -Path $DestRoot -Recurse -Filter "msedgewebview2.exe" -ErrorAction SilentlyContinue | Select-Object -First 1
if ($msedge) {
    Set-Content -Path $marker -Value $msedge.FullName
    Write-Host "WebView2 runtime found at $($msedge.FullName)"
    exit 0
}

Write-Host "Preparing WebView2 Fixed Runtime for standalone portable builds..."
New-Item -ItemType Directory -Force -Path $DestRoot | Out-Null

$version = "131.0.2903.112"
$nugetUrl = "https://www.nuget.org/api/v2/package/WebView2.Runtime.X64/$version"
$packagePath = Join-Path $DestRoot "webview2.nupkg"
$extractPath = Join-Path $DestRoot "_extract"

Write-Host "Downloading WebView2.Runtime.X64 $version ..."
try {
    Invoke-WebRequest -Uri $nugetUrl -OutFile $packagePath -UseBasicParsing -TimeoutSec 600
} catch {
    Write-Warning "Could not download WebView2 runtime: $_"
    Write-Warning "Installer will still embed WebView2 offline setup via Tauri."
    Write-Warning "Portable exe requires WebView2 (preinstalled on Windows 11)."
    exit 0
}

Copy-Item $packagePath (Join-Path $DestRoot "webview2.zip") -Force
Expand-Archive (Join-Path $DestRoot "webview2.zip") $extractPath -Force

$runtimeExe = Get-ChildItem -Path $extractPath -Recurse -Filter "msedgewebview2.exe" | Select-Object -First 1
if (-not $runtimeExe) {
    Write-Warning "WebView2 runtime files not found in NuGet package."
    exit 0
}

$runtimeRoot = $runtimeExe.Directory.FullName
Get-ChildItem -Path $runtimeRoot | Copy-Item -Destination $DestRoot -Recurse -Force
Set-Content -Path $marker -Value $runtimeRoot
Write-Host "WebView2 runtime ready at $DestRoot"
