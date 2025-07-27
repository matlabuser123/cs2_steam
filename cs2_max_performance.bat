@echo off
setlocal enabledelayedexpansion

echo ========================================
echo CS2 MAX PERFORMANCE LAUNCHER
echo ========================================
echo.

REM Set high priority for the script
echo Setting high priority...
wmic process where name="cmd.exe" CALL setpriority "high priority"

REM Switch to Ultimate Performance Power Plan
echo Activating Ultimate Performance power plan...
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61 > nul 2>&1
for /f "tokens=4" %%i in ('powercfg -list ^| findstr /C:"Ultimate Performance"') do (
    set "GUID=%%i"
)
if defined GUID (
    powercfg /setactive !GUID!
    echo Power plan set to Ultimate Performance
) else (
    echo Ultimate Performance plan not found, using High Performance instead
    powercfg -setactive 8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c
)

REM Set NVIDIA settings to maximum performance
echo Configuring NVIDIA settings for maximum performance...
if exist "%PROGRAMFILES%\NVIDIA Corporation\Control Panel Client\nvcplui.exe" (
    REM Setting PowerMizer to maximum performance
    reg add "HKCU\Software\NVIDIA Corporation\Global\NVTweak" /v "PowermizerLevel" /t REG_DWORD /d "1" /f > nul 2>&1
    reg add "HKCU\Software\NVIDIA Corporation\Global\NVTweak" /v "PowermizerEnable" /t REG_DWORD /d "1" /f > nul 2>&1
    echo NVIDIA settings configured
) else (
    echo NVIDIA Control Panel not found
)

REM Disable Windows services that impact gaming
echo Optimizing Windows services...
net stop "SysMain" /y > nul 2>&1
net stop "DiagTrack" /y > nul 2>&1
net stop "XboxNetApiSvc" /y > nul 2>&1
net stop "XblAuthManager" /y > nul 2>&1

REM Close unnecessary background processes
echo Closing unnecessary background applications...
taskkill /F /IM OneDrive.exe > nul 2>&1
taskkill /F /IM Discord.exe > nul 2>&1
taskkill /F /IM Teams.exe > nul 2>&1
taskkill /F /IM Spotify.exe > nul 2>&1
taskkill /F /IM Chrome.exe > nul 2>&1
taskkill /F /IM slack.exe > nul 2>&1
taskkill /F /IM msedge.exe > nul 2>&1

REM Clean memory
echo Cleaning system memory...
echo.>EmptyStandbyList.exe
if exist EmptyStandbyList.exe (
    EmptyStandbyList.exe workingsets
    EmptyStandbyList.exe modifiedpagelist
    EmptyStandbyList.exe priority0standbylist
    EmptyStandbyList.exe standbylist
    echo Memory cleaned
) else (
    echo EmptyStandbyList.exe not found, skipping memory cleaning
)

REM Set CS2 performance profile
echo Setting maximum performance CS2 profile...
cd /d "%~dp0"
copy /y "cs2tune\profiles\max_fps.cfg" "autoexec.cfg" > nul 2>&1
echo CS2 profile set to maximum performance

REM Start CS2 with optimized launch options
echo Starting CS2 with optimized launch options...
start "" steam://rungameid/730 -high -threads 32 -nojoy -novid +fps_max 0 +exec autoexec.cfg

REM Start OBS with optimized settings if needed
REM Uncomment the next line to also start OBS
REM start "" "C:\Program Files\obs-studio\bin\64bit\obs64.exe" --profile "LowLatency" --collection "CS2Stream" --minimize-to-tray

REM Start the monitoring dashboard in the browser
echo Starting performance monitoring dashboard...
timeout /t 15
start "" http://localhost:8501

echo ========================================
echo CS2 MAX PERFORMANCE SETUP COMPLETE!
echo ========================================
echo.
echo Enjoy your optimized gaming experience!
echo.
pause
