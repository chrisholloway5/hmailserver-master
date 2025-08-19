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

# Check Visual Studio
try {
    if ($Generator -like "*Visual Studio*") {
        $vsWhere = "${env:ProgramFiles(x86)}\Microsoft Visual Studio\Installer\vswhere.exe"
        if (Test-Path $vsWhere) {
            $vsInstances = & $vsWhere -latest -products * -requires Microsoft.VisualStudio.Component.VC.Tools.x86.x64 -format json | ConvertFrom-Json
            if ($vsInstances.Count -gt 0) {
                Write-Host "✓ Visual Studio found: $($vsInstances[0].displayName)" -ForegroundColor Green
            } else {
                throw "Visual Studio with C++ tools not found"
            }
        } else {
            throw "Visual Studio Installer not found"
        }
    }
} catch {
    Write-Host "✗ Visual Studio with C++ tools not found." -ForegroundColor Red
    Write-Host "  Please install Visual Studio 2019 or later with C++ development tools." -ForegroundColor Red
    exit 1
}

# Check dependencies
Write-Host ""
Write-Host "Checking dependencies..." -ForegroundColor Yellow

# Check for vcpkg or find libraries manually
$vcpkgDir = ""
if ($env:VCPKG_ROOT) {
    $vcpkgDir = $env:VCPKG_ROOT
    Write-Host "✓ vcpkg found at: $vcpkgDir" -ForegroundColor Green
} else {
    Write-Host "⚠ vcpkg not found. Will attempt to find libraries manually." -ForegroundColor Yellow
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

if ($vcpkgDir) {
    $toolchainFile = Join-Path $vcpkgDir "scripts\buildsystems\vcpkg.cmake"
    if (Test-Path $toolchainFile) {
        $cmakeArgs += "-DCMAKE_TOOLCHAIN_FILE=$toolchainFile"
        Write-Host "✓ Using vcpkg toolchain" -ForegroundColor Green
    }
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

# Run tests if enabled
if ($BuildTests) {
    Write-Host ""
    Write-Host "Running tests..." -ForegroundColor Yellow
    
    Push-Location $BuildDir
    try {
        & ctest --output-on-failure --parallel 4 -C $BuildType
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ All tests passed" -ForegroundColor Green
        } else {
            Write-Host "⚠ Some tests failed" -ForegroundColor Yellow
        }
    } finally {
        Pop-Location
    }
}

# Install
Write-Host ""
Write-Host "Installing..." -ForegroundColor Yellow

& cmake --install $BuildDir --config $BuildType

if ($LASTEXITCODE -eq 0) {
    Write-Host "✓ Installation completed" -ForegroundColor Green
    Write-Host "Installation directory: $InstallDir" -ForegroundColor Gray
} else {
    Write-Host "⚠ Installation failed" -ForegroundColor Yellow
}

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

# Check if executable was created
$exePath = Join-Path $BuildDir "$BuildType\hMailServerNext.exe"
if (Test-Path $exePath) {
    Write-Host "✓ Executable created: $exePath" -ForegroundColor Green
    
    # Show version information
    try {
        $versionInfo = Get-ItemProperty $exePath | Select-Object VersionInfo
        if ($versionInfo) {
            Write-Host "Version: $($versionInfo.VersionInfo.FileVersion)" -ForegroundColor Gray
        }
    } catch {
        # Ignore version info errors
    }
} else {
    Write-Host "⚠ Executable not found at expected location" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Build completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Configure hMailServer: Edit $InstallDir\etc\hmailserver\hMailServerNext.conf"
Write-Host "2. Setup database: Run database setup scripts"
Write-Host "3. Configure SSL certificates"
Write-Host "4. Start the service: $InstallDir\bin\hMailServerNext.exe"
Write-Host ""

exit 0