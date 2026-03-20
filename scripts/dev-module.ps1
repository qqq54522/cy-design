param(
    [Parameter(Mandatory=$true)]
    [string]$ModuleKey
)

$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$configPath = Join-Path $root "config\modules.json"
$config = Get-Content $configPath -Raw -Encoding UTF8 | ConvertFrom-Json

$mod = $config.modules | Where-Object { $_.key -eq $ModuleKey }

if (-not $mod) {
    $available = ($config.modules | ForEach-Object { $_.key }) -join ", "
    Write-Host "Module '$ModuleKey' not found. Available: $available" -ForegroundColor Red
    exit 1
}

function Get-ActivateScript {
    param([string[]]$Candidates)
    foreach ($c in $Candidates) {
        if (Test-Path $c) { return $c }
    }
    return $null
}

$rootVenv = Join-Path $root "venv\Scripts\activate.bat"

Write-Host "`n========================================"
Write-Host "   Starting module: $($mod.name)"
Write-Host "========================================`n"

$backendCwd = Join-Path $root $mod.backend.cwd
$frontendCwd = Join-Path $root $mod.frontend.cwd

$activate = Get-ActivateScript -Candidates @(
    (Join-Path $backendCwd "venv\Scripts\activate.bat"),
    (Join-Path $backendCwd ".venv\Scripts\activate.bat"),
    $rootVenv
)

if ($activate) {
    $cmd = "cd /d ""$backendCwd"" && call ""$activate"" && python -m uvicorn $($mod.backend.uvicornModule) --host 0.0.0.0 --port $($mod.backend.port) --reload"
} else {
    $cmd = "cd /d ""$backendCwd"" && python -m uvicorn $($mod.backend.uvicornModule) --host 0.0.0.0 --port $($mod.backend.port) --reload"
}
Start-Process cmd -ArgumentList "/k $cmd" -WindowStyle Normal
Write-Host "Started $($mod.name) backend on port $($mod.backend.port)"

$cmd = "cd /d ""$frontendCwd"" && npm run dev"
Start-Process cmd -ArgumentList "/k $cmd" -WindowStyle Normal
Write-Host "Started $($mod.name) frontend on port $($mod.frontend.port)"

Write-Host "`nFrontend: $($mod.frontend.origin)$($mod.defaultPath)"
Write-Host "Backend:  $($mod.backend.origin)$($mod.backend.healthPath)`n"
