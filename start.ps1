$root = Split-Path -Parent $MyInvocation.MyCommand.Path

# ---------------------------------------------------------------------------
# Read module registry – single source of truth
# ---------------------------------------------------------------------------
$configPath = Join-Path $root "config\modules.json"
$config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$platform = $config.platform

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

function Get-ActivateScript {
    param(
        [string[]]$Candidates
    )

    foreach ($candidate in $Candidates) {
        if (Test-Path $candidate) {
            return $candidate
        }
    }

    return $null
}

function Start-PythonService {
    param(
        [string]$Title,
        [string]$WorkingDirectory,
        [string]$Module,
        [int]$Port,
        [string[]]$ActivateCandidates
    )

    $activate = Get-ActivateScript -Candidates $ActivateCandidates
    if ($activate) {
        $command = "cd /d ""$WorkingDirectory"" && call ""$activate"" && python -m uvicorn $Module --host 0.0.0.0 --port $Port --reload"
    } else {
        $command = "cd /d ""$WorkingDirectory"" && python -m uvicorn $Module --host 0.0.0.0 --port $Port --reload"
    }

    Start-Process cmd -ArgumentList "/k $command" -WindowStyle Normal
    Write-Host "Started $Title on port $Port"
}

function Start-FrontendService {
    param(
        [string]$Title,
        [string]$WorkingDirectory
    )

    $command = "cd /d ""$WorkingDirectory"" && npm run dev"
    Start-Process cmd -ArgumentList "/k $command" -WindowStyle Normal
    Write-Host "Started $Title frontend"
}

# ---------------------------------------------------------------------------
# Common paths
# ---------------------------------------------------------------------------
$platformApi = Join-Path $root "platform_api"
$hubFrontend = Join-Path $root "frontend"
$rootVenv = Join-Path $root "venv\Scripts\activate.bat"

Write-Host ""
Write-Host "========================================"
Write-Host "   Lingqiao Creative Hub Starting..."
Write-Host "========================================"
Write-Host ""

# ---------------------------------------------------------------------------
# Start Platform API
# ---------------------------------------------------------------------------
Start-PythonService -Title "Platform API" -WorkingDirectory $platformApi -Module "app.main:app" -Port $platform.port -ActivateCandidates @(
    (Join-Path $platformApi ".venv\Scripts\activate.bat"),
    $rootVenv
)

# ---------------------------------------------------------------------------
# Start module backends & frontends from registry
# ---------------------------------------------------------------------------
foreach ($mod in $config.modules) {
    $backendCwd = Join-Path $root $mod.backend.cwd
    $frontendCwd = Join-Path $root $mod.frontend.cwd

    Start-PythonService -Title "$($mod.name) backend" -WorkingDirectory $backendCwd -Module $mod.backend.uvicornModule -Port $mod.backend.port -ActivateCandidates @(
        (Join-Path $backendCwd "venv\Scripts\activate.bat"),
        (Join-Path $backendCwd ".venv\Scripts\activate.bat"),
        $rootVenv
    )

    Start-FrontendService -Title $mod.name -WorkingDirectory $frontendCwd
}

# ---------------------------------------------------------------------------
# Start Hub frontend
# ---------------------------------------------------------------------------
Start-FrontendService -Title "Hub" -WorkingDirectory $hubFrontend

Start-Sleep -Seconds 5
Start-Process $platform.shellOrigin

Write-Host ""
Write-Host "Hub:        $($platform.shellOrigin)"
Write-Host "Platform:   $($platform.origin)/health"
foreach ($mod in $config.modules) {
    Write-Host "$($mod.name):".PadRight(12) "$($mod.frontend.origin)$($mod.defaultPath)"
}
Write-Host ""
