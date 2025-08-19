# hMailServer Next-Generation Deployment Guide

## Quick Start Deployment

### Prerequisites

1. **Windows Server 2019/2022** or **Windows 10/11** (64-bit)
2. **Visual Studio 2019 Build Tools** or later
3. **CMake 3.16** or later
4. **Git** for source control
5. **PowerShell 5.1** or later

### Hardware Requirements

**Minimum:**
- CPU: 4 cores, 2.5 GHz
- RAM: 8 GB
- Storage: 50 GB SSD
- Network: 1 Gbps

**Recommended:**
- CPU: 8 cores, 3.0 GHz (with AI acceleration)
- RAM: 32 GB
- Storage: 200 GB NVMe SSD
- Network: 10 Gbps
- GPU: NVIDIA RTX 4060 or better (for local AI)

### Step 1: Clone and Build

```powershell
# Clone the repository
git clone https://github.com/hmailserver/hmailserver-master.git
cd hmailserver-master

# Build with AI features enabled
.\build.ps1 -EnableAI -EnableZeroTrust -BuildType Release

# The build will create binaries in the build/Release directory
```

### Step 2: Install Dependencies

**Required Libraries:**
- Boost 1.75.0+
- OpenSSL 1.1.1+
- libcurl (for AI integration)
- nlohmann-json (for configuration)

**For AI Features:**
- Python 3.9+ (for model management)
- ONNX Runtime (for local AI models)
- CUDA Toolkit (optional, for GPU acceleration)

### Step 3: Configuration

1. **Copy configuration file:**
```powershell
cp config/hMailServerNext.conf.in config/hMailServerNext.conf
```

2. **Edit configuration:**
   - Database settings
   - SSL certificates
   - AI model API keys
   - Security parameters

3. **Setup MCP configuration:**
```powershell
cp config/mcp/config.json C:\ProgramData\hMailServer\mcp\
```

### Step 4: Database Setup

```sql
-- Create database
CREATE DATABASE hmailserver_next;

-- Run initialization scripts
mysql -u root -p hmailserver_next < scripts/database/mysql_init.sql
```

### Step 5: Service Installation

```powershell
# Register as Windows service
sc create "hMailServer Next" binPath="C:\Program Files\hMailServer Next\bin\hMailServerNext.exe --service"

# Start the service
sc start "hMailServer Next"
```

## Advanced Configuration

### AI Model Setup

1. **Local Models:**
```bash
# Download pre-trained models
mkdir C:\ProgramData\hMailServer\models
# Place ONNX model files in the models directory
```

2. **Cloud AI Setup:**
```bash
# Set environment variables
$env:OPENAI_API_KEY = "your-openai-key"
$env:ANTHROPIC_API_KEY = "your-anthropic-key"
```

### Security Configuration

1. **SSL Certificates:**
```powershell
# Generate self-signed certificate (development only)
New-SelfSignedCertificate -DnsName "mail.example.com" -CertStoreLocation "cert:\LocalMachine\My"
```

2. **Zero-Trust Setup:**
   - Configure behavioral analytics
   - Set up device fingerprinting
   - Enable continuous verification

### Performance Optimization

1. **Memory Settings:**
```ini
[Performance]
max_memory_usage = "4GB"
enable_memory_compression = true
```

2. **AI Optimization:**
```ini
[AI]
ai_processing_timeout = 10
ai_max_concurrent_requests = 20
local_model_threads = 8
```

## Monitoring and Maintenance

### Health Checks

```powershell
# Check service status
sc query "hMailServer Next"

# Check logs
Get-Content "C:\ProgramData\hMailServer\logs\hmailserver.log" -Tail 50
```

### Performance Monitoring

1. **Built-in Metrics:**
   - Email processing rates
   - AI model performance
   - Security threat detection

2. **External Monitoring:**
   - Prometheus metrics export
   - Windows Performance Counters
   - Custom dashboards

### Maintenance Tasks

1. **Regular Updates:**
```powershell
# Update AI models
Update-AIModels

# Update threat signatures
Update-ThreatSignatures
```

2. **Database Maintenance:**
```sql
-- Optimize database
OPTIMIZE TABLE hmailserver_messages;
ANALYZE TABLE hmailserver_accounts;
```

## Troubleshooting

### Common Issues

1. **AI Features Not Working:**
   - Check API keys in environment variables
   - Verify network connectivity to AI providers
   - Check model file permissions

2. **Performance Issues:**
   - Monitor CPU and memory usage
   - Check database connection pool
   - Review AI processing timeouts

3. **Security Alerts:**
   - Review zero-trust logs
   - Check threat detection settings
   - Validate SSL certificates

### Debug Mode

```powershell
# Run in debug mode
hMailServerNext.exe --debug --verbose

# Enable detailed logging
Set-ItemProperty -Path "HKLM:\SOFTWARE\hMailServer" -Name "LogLevel" -Value "DEBUG"
```

## Support and Documentation

- **Official Documentation:** https://www.hmailserver.com/documentation
- **Community Forum:** https://www.hmailserver.com/forum
- **GitHub Issues:** https://github.com/hmailserver/hmailserver/issues
- **AI Integration Guide:** docs/AI_Integration.md
- **Security Best Practices:** docs/Security_Guide.md

## License and Legal

This software is provided under the GPL v3 license. The AI integration features may require additional licenses for commercial AI providers.

For enterprise support and custom integrations, contact: enterprise@hmailserver.com