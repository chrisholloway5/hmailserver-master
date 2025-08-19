# hMailServer Autonomous Edition - Windows Native Installer
# WiX Toolset Configuration for MSI Package Creation

# Product Information
$ProductName = "hMailServer Autonomous Edition"
$ProductVersion = "2.0.0"
$ProductCode = "{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}"
$UpgradeCode = "{B2C3D4E5-F6A7-8901-BCDE-F12345678901}"
$Manufacturer = "hMailServer Autonomous Project"

# Installation Directories
$ProgramFilesFolder = "C:\Program Files\hMailServer Autonomous"
$ProgramDataFolder = "C:\ProgramData\hMailServer Autonomous"
$LogFolder = "C:\Logs\hMailServer Autonomous"

# Components to Install
$Components = @{
    # Core C++23 Email Engine
    "CoreEngine" = @{
        "Path" = "bin\hMailServerCore.exe"
        "Type" = "Executable"
        "Service" = $true
        "Description" = "Core email processing engine built with C++23"
    }
    
    # .NET 8 Web Administration
    "WebAdmin" = @{
        "Path" = "web\*"
        "Type" = "WebApplication"
        "IISRequired" = $true
        "Description" = "Blazor Server web administration interface"
    }
    
    # AI and Machine Learning Components
    "AIComponents" = @{
        "Path" = "ai\*"
        "Type" = "PythonModule"
        "Requirements" = "Python 3.13+"
        "Description" = "Autonomous AI capabilities and machine learning models"
    }
    
    # Database Scripts and Migrations
    "Database" = @{
        "Path" = "database\*"
        "Type" = "DatabaseScript"
        "Engines" = @("SqlServer", "MySQL", "PostgreSQL")
        "Description" = "Database schemas and migration scripts"
    }
    
    # Configuration Files
    "Configuration" = @{
        "Path" = "config\*"
        "Type" = "ConfigurationFile"
        "Protected" = $true
        "Description" = "Default configuration templates and settings"
    }
    
    # Documentation and Help
    "Documentation" = @{
        "Path" = "docs\*"
        "Type" = "Documentation"
        "Optional" = $true
        "Description" = "User guides and technical documentation"
    }
}

# Windows Services Configuration
$Services = @{
    "hMailServerCore" = @{
        "DisplayName" = "hMailServer Autonomous Core"
        "Description" = "Core email processing service with autonomous capabilities"
        "StartType" = "Automatic"
        "Account" = "LocalSystem"
        "Dependencies" = @("MSSQLSERVER", "W3SVC")
    }
    
    "hMailServerAI" = @{
        "DisplayName" = "hMailServer AI Engine"
        "Description" = "Artificial intelligence and machine learning service"
        "StartType" = "Automatic"
        "Account" = "NetworkService"
        "Dependencies" = @("hMailServerCore")
    }
    
    "hMailServerMonitor" = @{
        "DisplayName" = "hMailServer Autonomous Monitor"
        "Description" = "Self-healing and performance monitoring service"
        "StartType" = "Automatic"
        "Account" = "LocalService"
        "Dependencies" = @("hMailServerCore")
    }
}

# Registry Configuration
$RegistryKeys = @{
    "HKLM:\SOFTWARE\hMailServer Autonomous" = @{
        "InstallPath" = $ProgramFilesFolder
        "DataPath" = $ProgramDataFolder
        "Version" = $ProductVersion
        "Edition" = "Autonomous"
    }
    
    "HKLM:\SOFTWARE\hMailServer Autonomous\Engine" = @{
        "MaxConnections" = 10000
        "ThreadPoolSize" = 100
        "MemoryLimit" = 8589934592  # 8GB in bytes
        "EnableC23Features" = 1
    }
    
    "HKLM:\SOFTWARE\hMailServer Autonomous\AI" = @{
        "EnableAutonomousMode" = 1
        "EnableSelfHealing" = 1
        "EnablePredictiveScaling" = 1
        "EnableQuantumOps" = 1
        "EnableThreatIntel" = 1
        "ModelPath" = "$ProgramDataFolder\Models"
    }
}

# Firewall Rules
$FirewallRules = @{
    "hMailServer-SMTP" = @{
        "Port" = 25
        "Protocol" = "TCP"
        "Direction" = "Inbound"
        "Action" = "Allow"
        "Description" = "hMailServer SMTP (incoming mail)"
    }
    
    "hMailServer-SMTPS" = @{
        "Port" = 587
        "Protocol" = "TCP"
        "Direction" = "Inbound"
        "Action" = "Allow"
        "Description" = "hMailServer SMTP over TLS (outgoing mail)"
    }
    
    "hMailServer-IMAPS" = @{
        "Port" = 993
        "Protocol" = "TCP"
        "Direction" = "Inbound"
        "Action" = "Allow"
        "Description" = "hMailServer IMAP over SSL"
    }
    
    "hMailServer-POP3S" = @{
        "Port" = 995
        "Protocol" = "TCP"
        "Direction" = "Inbound"
        "Action" = "Allow"
        "Description" = "hMailServer POP3 over SSL"
    }
    
    "hMailServer-WebAdmin" = @{
        "Port" = 8080
        "Protocol" = "TCP"
        "Direction" = "Inbound"
        "Action" = "Allow"
        "Description" = "hMailServer Web Administration"
    }
    
    "hMailServer-API" = @{
        "Port" = 8443
        "Protocol" = "TCP"
        "Direction" = "Inbound"
        "Action" = "Allow"
        "Description" = "hMailServer REST API (HTTPS)"
    }
}

# Prerequisites Check
$Prerequisites = @{
    "WindowsVersion" = @{
        "Minimum" = "10.0.20348"  # Windows Server 2022
        "Recommended" = "10.0.20348"
        "Description" = "Windows Server 2022 or later required"
    }
    
    "DotNetRuntime" = @{
        "Version" = "8.0"
        "Component" = "Microsoft.AspNetCore.App"
        "Download" = "https://dotnet.microsoft.com/download/dotnet/8.0"
        "Description" = ".NET 8 ASP.NET Core Runtime"
    }
    
    "VCRedist" = @{
        "Version" = "14.38"
        "Architecture" = "x64"
        "Component" = "Microsoft Visual C++ 2022 Redistributable"
        "Description" = "Visual C++ Runtime for C++23 components"
    }
    
    "Python" = @{
        "Version" = "3.13"
        "Optional" = $false
        "Component" = "Python 3.13+ with pip"
        "Description" = "Python runtime for AI components"
    }
    
    "IIS" = @{
        "Features" = @("IIS-WebServerRole", "IIS-AspNetCoreModuleV2")
        "Optional" = $false
        "Description" = "Internet Information Services for web administration"
    }
}

# Installation Features
$Features = @{
    "Complete" = @{
        "Components" = @("CoreEngine", "WebAdmin", "AIComponents", "Database", "Configuration", "Documentation")
        "Default" = $true
        "Description" = "Complete installation with all autonomous features"
    }
    
    "Server" = @{
        "Components" = @("CoreEngine", "AIComponents", "Database", "Configuration")
        "Default" = $false
        "Description" = "Server-only installation without web administration"
    }
    
    "Custom" = @{
        "Components" = @()  # User selectable
        "Default" = $false
        "Description" = "Custom installation with selectable components"
    }
}

# Post-Installation Configuration
$PostInstall = @{
    "CreateDatabase" = $true
    "ConfigureIIS" = $true
    "StartServices" = $true
    "OpenFirewallPorts" = $true
    "CreateDesktopShortcuts" = $true
    "RegisterEventSources" = $true
    "InstallPerfCounters" = $true
    "ConfigureLogging" = $true
}

# Uninstallation Configuration
$Uninstall = @{
    "StopServices" = $true
    "RemoveServices" = $true
    "RemoveFirewallRules" = $true
    "KeepUserData" = $true
    "KeepLogs" = $false
    "RemoveIISConfiguration" = $true
}

Write-Host "hMailServer Autonomous Edition - Native Windows Installer Configuration"
Write-Host "This MSI installer provides enterprise-grade deployment without Docker containers"
Write-Host "Built for Windows Server 2022 with C++23 and .NET 8 technology stack"