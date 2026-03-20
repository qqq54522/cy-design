$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)

$configPath = Join-Path $root "config\modules.json"
$config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json
$platform = $config.platform

function Get-ActivateScript {
    param([string[]]$Candidates)
    foreach ($c in $Candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

$platformApi = Join-Path $root "platform_api"
$hubFrontend = Join-Path $root "frontend"
$rootVenv = Join-Path $root "venv\Scripts\activate.bat"

Write-Host "`n========================================"
Write-Host "   Starting Platform Only..."
Write-Host "========================================`n"

$activate = Get-ActivateScript -Candidates @(
    (Join-Path $platformApi ".venv\Scripts\activate.bat"),
    $rootVenv
)

if ($activate) {
    $cmd = "cd /d ""$platformApi"" && call ""$activate"" && python -m uvicorn app.main:app --host 0.0.0.0 --port $($platform.port) --reload"
} else {
    $cmd = "cd /d ""$platformApi"" && python -m uvicorn app.main:app --host 0.0.0.0 --port $($platform.port) --reload"
}
Start-Process cmd -ArgumentList "/k $cmd" -WindowStyle Normal
Write-Host "Started Platform API on port $($platform.port)"

$cmd = "cd /d ""$hubFrontend"" && npm run dev"
Start-Process cmd -ArgumentList "/k $cmd" -WindowStyle Normal
Write-Host "Started Hub frontend"

Start-Sleep -Seconds 3
Start-Process $platform.shellOrigin

Write-Host "`nHub:        $($platform.shellOrigin)"
Write-Host "Platform:   $($platform.origin)/health`n"
