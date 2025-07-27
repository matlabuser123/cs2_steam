# CS2 Configuration Deployment Script
# Manages deployment of CS2 customizations between repository and game directory

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("deploy", "update-repo")]
    [string]$Action = "deploy",
    
    [Parameter(Mandatory=$false)]
    [string]$RepoPath = "$env:USERPROFILE\Documents\cs2-optimizer",
    
    [Parameter(Mandatory=$false)]
    [string]$CS2Path = "$PSScriptRoot"
)

# File mapping: repo location -> CS2 location
$fileMapping = @{
    "cs2tune" = "cs2tune"
    "msi_drivers" = "msi_drivers"
    "overlay" = "overlay"
    "autoexec.cfg" = "autoexec.cfg"
    "dashboard.py" = "dashboard.py"
    "cs2tune_cli.py" = "cs2tune_cli.py"
    "docker-compose.yml" = "docker-compose.yml"
    "Dockerfile" = "Dockerfile"
    "requirements.txt" = "requirements.txt"
}

function Write-Log {
    param([string]$Message)
    Write-Host "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss'): $Message"
}

function Deploy-ToCS2 {
    Write-Log "Deploying customizations to CS2..."
    
    foreach ($source in $fileMapping.Keys) {
        $sourcePath = Join-Path $RepoPath $source
        $destPath = Join-Path $CS2Path $fileMapping[$source]
        
        if (Test-Path $sourcePath) {
            if (Test-Path $destPath) {
                Write-Log "Backing up $($fileMapping[$source])..."
                Copy-Item -Path $destPath -Destination "$destPath.backup" -Recurse -Force
            }
            
            Write-Log "Deploying $source..."
            if ((Get-Item $sourcePath).PSIsContainer) {
                Copy-Item -Path $sourcePath -Destination $destPath -Recurse -Force
            } else {
                Copy-Item -Path $sourcePath -Destination $destPath -Force
            }
        } else {
            Write-Log "Warning: Source $source not found in repository"
        }
    }
    
    Write-Log "Deployment completed!"
}

function Update-Repository {
    Write-Log "Updating repository with current CS2 configurations..."
    
    foreach ($source in $fileMapping.Keys) {
        $cs2Path = Join-Path $CS2Path $fileMapping[$source]
        $repoPath = Join-Path $RepoPath $source
        
        if (Test-Path $cs2Path) {
            Write-Log "Updating $source in repository..."
            if ((Get-Item $cs2Path).PSIsContainer) {
                Copy-Item -Path $cs2Path -Destination $repoPath -Recurse -Force
            } else {
                Copy-Item -Path $cs2Path -Destination $repoPath -Force
            }
        } else {
            Write-Log "Warning: Source $($fileMapping[$source]) not found in CS2"
        }
    }
    
    Write-Log "Repository update completed!"
}

# Create repository directory if it doesn't exist
if (-not (Test-Path $RepoPath)) {
    Write-Log "Creating repository directory..."
    New-Item -ItemType Directory -Path $RepoPath -Force | Out-Null
}

# Execute requested action
switch ($Action) {
    "deploy" { Deploy-ToCS2 }
    "update-repo" { Update-Repository }
}
