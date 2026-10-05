@echo off
setlocal EnableDelayedExpansion
title SysInfo Builder

set "ROOT=%~dp0"
cd /d "%ROOT%"

echo.
echo  ==================================================
echo           SysInfo - Build and Launch Script
echo  ==================================================
echo.

if /I "%~1"=="dev" goto dev
if /I "%~1"=="build" goto build
if /I "%~1"=="run" goto run_only

:menu
echo  [1] Build everything (installer + portable) - default
echo  [2] Dev mode (hot reload)
echo  [3] Run existing build
echo.
set "CHOICE="
set /p CHOICE="Select option [1]: "
if "%CHOICE%"=="" set CHOICE=1
if "%CHOICE%"=="2" goto dev
if "%CHOICE%"=="3" goto run_only
goto build

:dev
call :check_deps
if errorlevel 1 exit /b 1
call :ensure_icons
echo.
echo  Starting development server...
cd /d "%ROOT%gui"
if not exist node_modules call npm install
call npm run tauri dev
exit /b %errorlevel%

:run_only
set "PORTABLE=%ROOT%output\portable\SysInfo.exe"
if exist "%PORTABLE%" (
    start "" "%PORTABLE%"
    exit /b 0
)
echo  Portable build not found. Run build first.
exit /b 1

:build
call :check_deps
if errorlevel 1 exit /b 1
call :ensure_icons
call :prepare_build
call :build_gui
if errorlevel 1 exit /b 1
call :package_output
if errorlevel 1 exit /b 1
echo.
echo  ==================================================
echo   Build complete!
echo   Installer : %ROOT%output\installer\
echo   Portable  : %ROOT%output\portable\
echo  ==================================================
echo.
set /p LAUNCH="Launch portable version now? [Y/n]: "
if /I "!LAUNCH!"=="n" exit /b 0
start "" "%ROOT%output\portable\SysInfo.exe"
exit /b 0

:check_deps
echo  Checking build dependencies...
where node >nul 2>&1 || (echo  ERROR: Node.js not found & exit /b 1)
where npm >nul 2>&1 || (echo  ERROR: npm not found & exit /b 1)
where cargo >nul 2>&1 || (echo  ERROR: Rust/Cargo not found. Install from https://rustup.rs & exit /b 1)
echo  Build tools OK.
exit /b 0

:ensure_icons
echo.
echo  Checking application icons...
if exist "%ROOT%gui\src-tauri\icons\icon.ico" (
    copy /Y "%ROOT%gui\src-tauri\icons\icon.png" "%ROOT%gui\public\icon.png" >nul 2>&1
    exit /b 0
)
where python >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Icons missing. Install Python or add icons to gui\src-tauri\icons\
    exit /b 1
)
python -m pip install -q pillow 2>nul
python "%ROOT%scripts\generate_icons.py"
if errorlevel 1 exit /b 1
copy /Y "%ROOT%gui\src-tauri\icons\icon.png" "%ROOT%gui\public\icon.png" >nul
exit /b 0

:prepare_build
echo.
echo  Preparing bundled runtime and assets...
powershell -NoProfile -ExecutionPolicy Bypass -File "%ROOT%scripts\prepare_build.ps1"
if errorlevel 1 exit /b 1
exit /b 0

:build_gui
echo.
echo  Building standalone application (first build may take several minutes)...
cd /d "%ROOT%gui"
if not exist node_modules call npm install
call npm run tauri build
if errorlevel 1 (
    echo  ERROR: Tauri build failed
    exit /b 1
)
exit /b 0

:package_output
echo.
echo  Packaging output files...
taskkill /IM SysInfo.exe /F >nul 2>&1
taskkill /IM sysinfo-app.exe /F >nul 2>&1
timeout /t 1 /nobreak >nul

set "OUT=%ROOT%output"
set "TAURI_OUT=%ROOT%gui\src-tauri\target\release"
set "BUNDLE=%TAURI_OUT%\bundle\nsis"

if not exist "%OUT%\installer" mkdir "%OUT%\installer"
if not exist "%OUT%\portable" mkdir "%OUT%\portable"

if exist "%OUT%\portable\WebView2Runtime" rmdir /s /q "%OUT%\portable\WebView2Runtime" 2>nul
del /q "%OUT%\portable\MicrosoftEdgeWebview2Setup*.exe" 2>nul

if not exist "%TAURI_OUT%\sysinfo-app.exe" (
    echo  ERROR: Release build not found. Run build first.
    exit /b 1
)

for %%F in ("%BUNDLE%\SysInfo_*-setup.exe") do copy /Y "%%F" "%OUT%\installer\" >nul
for %%F in ("%BUNDLE%\sysinfo_*-setup.exe") do copy /Y "%%F" "%OUT%\installer\" >nul

copy /Y "%TAURI_OUT%\sysinfo-app.exe" "%OUT%\portable\SysInfo.exe" >nul
if errorlevel 1 (
    echo  ERROR: Could not copy portable executable. Close SysInfo and retry.
    exit /b 1
)

(
echo SysInfo - Portable Edition
echo.
echo Run SysInfo.exe - no Node.js or Rust required.
echo.
echo Requires Microsoft WebView2 Runtime ^(preinstalled on Windows 11^).
echo If the app does not start, install WebView2 from Microsoft.
) > "%OUT%\portable\README.txt"

(
echo SysInfo v1.0.0
echo.
echo INSTALLER: output/installer/  ^(small setup, ~10 MB^)
echo PORTABLE:  output/portable/SysInfo.exe  ^(~9 MB^)
echo.
echo Dev mode:   start.bat dev
echo Rebuild:    start.bat build
) > "%OUT%\README.txt"

exit /b 0
