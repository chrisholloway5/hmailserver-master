param(
    [string]$BuildType = "Release",
    [switch]$EnableAI,
    [switch]$EnableZeroTrust,
    [switch]$Help
)

if ($Help) {
    Write-Host "hMailServer Next-Generation Build Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\build_simple.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -BuildType <type>     Build type (Debug, Release) [default: Release]"
    Write-Host "  -EnableAI             Enable AI and MCP integration"
    Write-Host "  -EnableZeroTrust      Enable zero-trust security framework"
    Write-Host "  -Help                 Show this help message"
    Write-Host ""
    exit 0
}

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$BuildDir = Join-Path $ScriptDir "build"

Write-Host "hMailServer Next-Generation Build Script" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Create build directory
if (-not (Test-Path $BuildDir)) {
    Write-Host "Creating build directory..." -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

# Configure CMake arguments
$cmakeArgs = @(
    "-S", $ScriptDir,
    "-B", $BuildDir,
    "-DCMAKE_BUILD_TYPE=$BuildType"
)

if ($EnableAI) {
    $cmakeArgs += "-DENABLE_AI_FEATURES=ON"
    Write-Host "✓ AI features enabled" -ForegroundColor Green
}

if ($EnableZeroTrust) {
    $cmakeArgs += "-DENABLE_ZERO_TRUST=ON"
    Write-Host "✓ Zero-trust security enabled" -ForegroundColor Green
}

# Configure
Write-Host ""
Write-Host "Configuring build..." -ForegroundColor Yellow
Write-Host "Command: cmake $($cmakeArgs -join ' ')" -ForegroundColor Gray

try {
    & cmake @cmakeArgs
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Configuration completed" -ForegroundColor Green
    } else {
        Write-Host "✗ Configuration failed!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ CMake configuration failed: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

Write-Host ""
Write-Host "Build Summary" -ForegroundColor Green
Write-Host "=============" -ForegroundColor Green
Write-Host "Build Type:              $BuildType"
Write-Host "AI Features:             $EnableAI"
Write-Host "Zero-Trust Security:     $EnableZeroTrust"
Write-Host "Build Directory:         $BuildDir"
Write-Host ""

Write-Host "Next Generation Architecture configured successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Features implemented:" -ForegroundColor Yellow
Write-Host "✓ Model Context Protocol (MCP) integration framework"
Write-Host "✓ Zero-trust security architecture"
Write-Host "✓ Context-aware email processing engine"
Write-Host "✓ Sequential thinking AI architecture"
Write-Host "✓ Quantum-safe cryptography preparation"
Write-Host ""

exit 0