# Windows Optimization Script for CS2 Gaming
# Automates power settings, NVIDIA optimizations, and Steam configurations

# Enable Ultimate Performance Power Plan
Write-Host "Enabling Ultimate Performance Power Plan..."
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61

# NVIDIA Control Panel Settings
Write-Host "Applying NVIDIA Control Panel optimizations..."
$regPath = "HKLM:\SOFTWARE\NVIDIA Corporation\Global\NvCplApi\Policies"
Set-ItemProperty -Path $regPath -Name "PowerMizerEnable" -Value 1
Set-ItemProperty -Path $regPath -Name "PowerMizerLevel" -Value 0
Set-ItemProperty -Path $regPath -Name "PowerMizerLevelAC" -Value 0

# Steam Configurations
Write-Host "Disabling Steam Overlay and Hardware Acceleration..."
$steamConfigPath = "$env:USERPROFILE\AppData\Local\Steam\config\config.vdf"
(Get-Content $steamConfigPath) -replace '"EnableOverlay"\s*"1"', '"EnableOverlay" "0"' | Set-Content $steamConfigPath
(Get-Content $steamConfigPath) -replace '"HardwareAcceleration"\s*"1"', '"HardwareAcceleration" "0"' | Set-Content $steamConfigPath

Write-Host "Windows optimizations applied successfully!"
