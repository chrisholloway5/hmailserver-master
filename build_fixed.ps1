# hMailServer Next-Generation Build Script
# PowerShell script for building hMailServer with AI and security enhancements

param(
    [string]$BuildType = "Release",
    [switch]$EnableAI = $true,
    [switch]$EnableZeroTrust = $true,
    [switch]$EnableQuantumCrypto = $false,
    [switch]$BuildTests = $true,
    [switch]$CleanBuild = $false,
    [string]$Generator = "Visual Studio 16 2019",
    [string]$Architecture = "x64",
    [string]$InstallPrefix = "",
    [switch]$Help
)

function Show-Help {
    Write-Host "hMailServer Next-Generation Build Script" -ForegroundColor Green
    Write-Host ""
    Write-Host "USAGE:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1 [OPTIONS]"
    Write-Host ""
    Write-Host "OPTIONS:" -ForegroundColor Yellow
    Write-Host "  -BuildType <type>        Build type (Debug, Release, RelWithDebInfo) [default: Release]"
    Write-Host "  -EnableAI                Enable AI and MCP integration [default: true]"
    Write-Host "  -EnableZeroTrust         Enable zero-trust security framework [default: true]"
    Write-Host "  -EnableQuantumCrypto     Enable quantum-safe cryptography [default: false]"
    Write-Host "  -BuildTests              Build unit tests [default: true]"
    Write-Host "  -CleanBuild              Clean previous build files"
    Write-Host "  -Generator <generator>   CMake generator [default: 'Visual Studio 16 2019']"
    Write-Host "  -Architecture <arch>     Target architecture (x64, Win32) [default: x64]"
    Write-Host "  -InstallPrefix <path>    Installation prefix"
    Write-Host "  -Help                    Show this help message"
    Write-Host ""
    Write-Host "EXAMPLES:" -ForegroundColor Yellow
    Write-Host "  .\build.ps1                                    # Standard release build"
    Write-Host "  .\build.ps1 -BuildType Debug -CleanBuild      # Debug build with clean"
    Write-Host "  .\build.ps1 -EnableQuantumCrypto             # Enable quantum crypto"
    Write-Host ""
}

if ($Help) {
    Show-Help
    exit 0
}

# Configuration
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$SourceDir = $ScriptDir
$BuildDir = Join-Path $ScriptDir "build"
$InstallDir = if ($InstallPrefix) { $InstallPrefix } else { Join-Path $ScriptDir "install" }

Write-Host "hMailServer Next-Generation Build Script" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
Write-Host ""

# Check prerequisites
Write-Host "Checking prerequisites..." -ForegroundColor Yellow

# Check CMake
try {
    $cmakeVersion = cmake --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ CMake found: $($cmakeVersion[0])" -ForegroundColor Green
    } else {
        throw "CMake not found"
    }
} catch {
    Write-Host "✗ CMake not found. Please install CMake 3.16 or later." -ForegroundColor Red
    exit 1
}

# Prepare build directory
Write-Host ""
Write-Host "Preparing build directory..." -ForegroundColor Yellow

if ($CleanBuild -and (Test-Path $BuildDir)) {
    Write-Host "Cleaning previous build..." -ForegroundColor Yellow
    Remove-Item -Recurse -Force $BuildDir
}

if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

# Configure CMake arguments
$cmakeArgs = @(
    "-S", $SourceDir,
    "-B", $BuildDir,
    "-G", $Generator,
    "-A", $Architecture,
    "-DCMAKE_BUILD_TYPE=$BuildType",
    "-DCMAKE_INSTALL_PREFIX=$InstallDir"
)

if ($EnableAI) {
    $cmakeArgs += "-DENABLE_AI_FEATURES=ON"
    Write-Host "✓ AI features enabled" -ForegroundColor Green
} else {
    $cmakeArgs += "-DENABLE_AI_FEATURES=OFF"
    Write-Host "- AI features disabled" -ForegroundColor Gray
}

if ($EnableZeroTrust) {
    $cmakeArgs += "-DENABLE_ZERO_TRUST=ON"
    Write-Host "✓ Zero-trust security enabled" -ForegroundColor Green
} else {
    $cmakeArgs += "-DENABLE_ZERO_TRUST=OFF"
    Write-Host "- Zero-trust security disabled" -ForegroundColor Gray
}

if ($EnableQuantumCrypto) {
    $cmakeArgs += "-DENABLE_QUANTUM_CRYPTO=ON"
    Write-Host "✓ Quantum-safe cryptography enabled" -ForegroundColor Green
} else {
    $cmakeArgs += "-DENABLE_QUANTUM_CRYPTO=OFF"
    Write-Host "- Quantum-safe cryptography disabled" -ForegroundColor Gray
}

if ($BuildTests) {
    $cmakeArgs += "-DBUILD_TESTS=ON"
    Write-Host "✓ Unit tests enabled" -ForegroundColor Green
} else {
    $cmakeArgs += "-DBUILD_TESTS=OFF"
    Write-Host "- Unit tests disabled" -ForegroundColor Gray
}

# Configure
Write-Host ""
Write-Host "Configuring build..." -ForegroundColor Yellow
Write-Host "Command: cmake $($cmakeArgs -join ' ')" -ForegroundColor Gray

$configureStart = Get-Date
& cmake @cmakeArgs

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Configuration failed!" -ForegroundColor Red
    exit 1
}

$configureTime = (Get-Date) - $configureStart
Write-Host "✓ Configuration completed in $($configureTime.TotalSeconds.ToString('F1'))s" -ForegroundColor Green

# Build
Write-Host ""
Write-Host "Building..." -ForegroundColor Yellow

$buildStart = Get-Date
& cmake --build $BuildDir --config $BuildType --parallel

if ($LASTEXITCODE -ne 0) {
    Write-Host "✗ Build failed!" -ForegroundColor Red
    exit 1
}

$buildTime = (Get-Date) - $buildStart
Write-Host "✓ Build completed in $($buildTime.TotalMinutes.ToString('F1'))m" -ForegroundColor Green

# Summary
$totalTime = (Get-Date) - $configureStart
Write-Host ""
Write-Host "Build Summary" -ForegroundColor Green
Write-Host "=============" -ForegroundColor Green
Write-Host "Build Type:              $BuildType"
Write-Host "Architecture:            $Architecture"
Write-Host "AI Features:             $EnableAI"
Write-Host "Zero-Trust Security:     $EnableZeroTrust"
Write-Host "Quantum Cryptography:    $EnableQuantumCrypto"
Write-Host "Unit Tests:              $BuildTests"
Write-Host "Total Time:              $($totalTime.TotalMinutes.ToString('F1'))m"
Write-Host "Build Directory:         $BuildDir"
Write-Host "Install Directory:       $InstallDir"
Write-Host ""

Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure hMailServer: Edit configuration files"
Write-Host "2. Setup database: Run database setup scripts"
Write-Host "3. Configure SSL certificates"
Write-Host "4. Start the service"
Write-Host ""

exit 0