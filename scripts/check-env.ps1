$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$errors = @()
$warnings = @()

Write-Host "`n========================================"
Write-Host "   Environment Check"
Write-Host "========================================`n"

$node = Get-Command node -ErrorAction SilentlyContinue
if ($node) {
    $nodeVer = & node --version
    Write-Host "[OK] Node.js $nodeVer" -ForegroundColor Green
} else {
    $errors += "Node.js not found (>= 18.0.0 required)"
}

$pnpm = Get-Command pnpm -ErrorAction SilentlyContinue
if ($pnpm) {
    $pnpmVer = & pnpm --version
    Write-Host "[OK] pnpm $pnpmVer" -ForegroundColor Green
} else {
    $errors += "pnpm not found (>= 8.0.0 required)"
}

$python = Get-Command python -ErrorAction SilentlyContinue
if ($python) {
    $pyVer = & python --version
    Write-Host "[OK] $pyVer" -ForegroundColor Green
} else {
    $errors += "Python not found (>= 3.11 required)"
}

$envFile = Join-Path $root ".env"
if (Test-Path $envFile) {
    Write-Host "[OK] .env file exists" -ForegroundColor Green
} else {
    $warnings += ".env file not found - copy from .env.example"
}

$nodeModules = Join-Path $root "node_modules"
if (Test-Path $nodeModules) {
    Write-Host "[OK] node_modules installed" -ForegroundColor Green
} else {
    $errors += "node_modules not found - run 'pnpm install'"
}

$ports = @(5174, 5175, 5176, 5180, 8001, 8002, 8003, 8100)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    if ($conn) {
        $warnings += "Port $port is already in use"
    }
}

Write-Host ""
if ($errors.Count -gt 0) {
    Write-Host "ERRORS:" -ForegroundColor Red
    foreach ($e in $errors) { Write-Host "  - $e" -ForegroundColor Red }
}
if ($warnings.Count -gt 0) {
    Write-Host "WARNINGS:" -ForegroundColor Yellow
    foreach ($w in $warnings) { Write-Host "  - $w" -ForegroundColor Yellow }
}
if ($errors.Count -eq 0 -and $warnings.Count -eq 0) {
    Write-Host "All checks passed!" -ForegroundColor Green
}
Write-Host ""
