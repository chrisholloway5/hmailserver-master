# 🚀 hMailServer Production Deployment Guide

## 📋 **Quick Start Production Deployment**

This guide will deploy the complete hMailServer Next-Generation system with all phases integrated.

---

## 🏗️ **System Architecture Overview**

```
Internet → Nginx → API Gateway → {
    ├── C++ Core Engine (Phase 1)
    ├── Python AI Services (Phase 2)
    ├── Autonomous Operations (Phase 3)
    └── Next.js Web Interface (Phase 4)
}
```

### **Technology Stack**
- **C++26** - Core email processing engine
- **Python 3.13** - AI/ML services with PyTorch 2.5
- **.NET 9** - API Gateway and service orchestration
- **React 19 + Next.js 15** - Modern web interface
- **PostgreSQL 17** - Primary database
- **Redis 7** - Caching and session storage
- **Nginx** - Reverse proxy and load balancer

---

## ⚡ **One-Command Deployment**

### **Prerequisites**
- Docker 24.0+ with Compose V2
- 8GB+ RAM available
- 50GB+ storage space
- Linux/macOS/Windows with WSL2

### **Quick Deploy**
```bash
# Clone and navigate to production directory
cd implementation/Production_Integration

# Copy environment template
cp .env.example .env

# Edit environment variables (REQUIRED)
nano .env

# Deploy complete system
docker compose -f docker-compose.production.yml up -d

# Check deployment status
docker compose -f docker-compose.production.yml ps

# View logs
docker compose -f docker-compose.production.yml logs -f
```

---

## 🔧 **Environment Configuration**

Create `.env` file with your settings:

```bash
# Database Configuration
DB_PASSWORD=your_secure_db_password_here
POSTGRES_DB=hmailserver

# Redis Configuration
REDIS_PASSWORD=your_secure_redis_password_here

# Security Keys
JWT_SECRET=your-super-secret-jwt-key-minimum-256-bits
NEXTAUTH_SECRET=your-next-auth-secret-change-in-production

# Domain Configuration
DOMAIN=yourdomain.com
NEXTAUTH_URL=https://yourdomain.com

# CORS Configuration
CORS_ORIGINS=https://yourdomain.com,https://mail.yourdomain.com

# Monitoring
GRAFANA_PASSWORD=your_grafana_admin_password

# Email Configuration
SMTP_HOST=yourdomain.com
SMTP_PORT=587
SMTP_USER=noreply@yourdomain.com
SMTP_PASS=your_smtp_password

# AI Configuration (Optional)
OPENAI_API_KEY=your_openai_api_key_for_enhanced_ai
HUGGINGFACE_TOKEN=your_huggingface_token_for_models

# SSL Configuration
SSL_CERT_PATH=/etc/ssl/certs/yourdomain.com.crt
SSL_KEY_PATH=/etc/ssl/private/yourdomain.com.key
```

---

## 🌐 **Service Endpoints**

After deployment, services are available at:

| Service | URL | Purpose |
|---------|-----|---------|
| **Web Interface** | http://localhost:3000 | Main user interface |
| **API Gateway** | http://localhost:8080 | REST API endpoints |
| **Core Engine** | grpc://localhost:50051 | C++ email engine |
| **AI Services** | http://localhost:50052 | Python AI/ML services |
| **Autonomous Ops** | http://localhost:50053 | Self-managing operations |
| **Prometheus** | http://localhost:9090 | Metrics collection |
| **Grafana** | http://localhost:3001 | Performance dashboards |

---

## 📊 **Health Checks & Monitoring**

### **System Health Check**
```bash
# Check all services health
curl http://localhost:8080/health | jq

# Individual service health
curl http://localhost:50052/health  # AI Services
curl http://localhost:50053/health  # Autonomous
curl http://localhost:3000/api/health  # Web Interface
```

### **Performance Monitoring**

**Grafana Dashboards** (http://localhost:3001):
- **System Overview** - Overall system health
- **Email Processing** - Email throughput and latency
- **AI Performance** - ML model performance metrics
- **Resource Usage** - CPU, memory, disk usage
- **Error Tracking** - Error rates and debugging

**Prometheus Metrics** (http://localhost:9090):
- `hmailserver_emails_processed_total`
- `hmailserver_ai_processing_duration_seconds`
- `hmailserver_autonomous_actions_total`
- `hmailserver_errors_total`

---

## 🔐 **Security Configuration**

### **SSL/TLS Setup**
```bash
# Generate self-signed certificates (for testing)
mkdir -p ssl
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/yourdomain.com.key \
  -out ssl/yourdomain.com.crt \
  -subj "/C=US/ST=State/L=City/O=Organization/CN=yourdomain.com"

# For production, use Let's Encrypt:
certbot certonly --standalone -d yourdomain.com
cp /etc/letsencrypt/live/yourdomain.com/*.pem ssl/
```

### **Firewall Configuration**
```bash
# Allow required ports
ufw allow 80    # HTTP
ufw allow 443   # HTTPS
ufw allow 25    # SMTP
ufw allow 587   # Submission
ufw allow 993   # IMAPS
ufw allow 995   # POP3S
ufw allow 3000  # Web Interface (optional, behind proxy)
ufw allow 8080  # API Gateway (optional, behind proxy)
```

---

## 📈 **Scaling Configuration**

### **Horizontal Scaling**
```yaml
# Add to docker-compose.production.yml
services:
  ai-services:
    deploy:
      replicas: 3  # Scale AI services
      
  web-interface:
    deploy:
      replicas: 2  # Scale web interface
```

### **Resource Limits**
```yaml
# Optimize for your hardware
services:
  core-engine:
    deploy:
      resources:
        limits:
          memory: 4G      # Increase for high volume
          cpus: '4.0'
          
  ai-services:
    deploy:
      resources:
        limits:
          memory: 8G      # More memory for AI models
          cpus: '6.0'
```

---

## 🛠️ **Maintenance Commands**

### **Backup & Restore**
```bash
# Backup database
docker exec hmailserver-database pg_dump -U hmailserver hmailserver > backup_$(date +%Y%m%d).sql

# Backup volumes
docker run --rm -v hmailserver_database-data:/data -v $(pwd):/backup alpine tar czf /backup/database_backup.tar.gz /data

# Restore database
cat backup_20241225.sql | docker exec -i hmailserver-database psql -U hmailserver -d hmailserver
```

### **Log Management**
```bash
# View real-time logs
docker compose logs -f web-interface
docker compose logs -f ai-services
docker compose logs -f core-engine

# Rotate logs
docker system prune -f
docker volume prune -f
```

### **Updates & Upgrades**
```bash
# Pull latest images
docker compose pull

# Restart with new images
docker compose up -d

# Clean old images
docker image prune -f
```

---

## 🐛 **Troubleshooting**

### **Common Issues**

**1. Services not starting**
```bash
# Check resource usage
docker stats

# Check service logs
docker compose logs [service-name]

# Restart individual service
docker compose restart [service-name]
```

**2. Database connection issues**
```bash
# Test database connection
docker exec hmailserver-database psql -U hmailserver -d hmailserver -c "SELECT version();"

# Reset database
docker compose down database
docker volume rm hmailserver_database-data
docker compose up -d database
```

**3. AI Services not responding**
```bash
# Check AI service health
curl http://localhost:50052/health

# View AI service logs
docker compose logs ai-services

# Restart AI services (models reload)
docker compose restart ai-services
```

**4. Web interface issues**
```bash
# Check Next.js logs
docker compose logs web-interface

# Rebuild web interface
docker compose build web-interface
docker compose up -d web-interface
```

### **Performance Optimization**

**1. Database Performance**
```sql
-- Connect to database
docker exec -it hmailserver-database psql -U hmailserver -d hmailserver

-- Check slow queries
SELECT query, mean_exec_time, calls 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;

-- Analyze table statistics
ANALYZE;
```

**2. Memory Optimization**
```bash
# Adjust service memory limits
# Edit docker-compose.production.yml

# Monitor memory usage
docker stats --no-stream
```

---

## 📋 **Production Checklist**

### **Pre-Deployment**
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] DNS records configured
- [ ] Firewall rules set
- [ ] Backup strategy planned
- [ ] Monitoring alerts configured

### **Post-Deployment**
- [ ] All services healthy
- [ ] Web interface accessible
- [ ] Email processing working
- [ ] AI services responding
- [ ] Monitoring dashboards active
- [ ] Backup system tested
- [ ] Performance metrics baseline established

### **Security Verification**
- [ ] SSL/TLS certificates valid
- [ ] Strong passwords set
- [ ] JWT secrets configured
- [ ] Database access restricted
- [ ] API endpoints secured
- [ ] Log access controlled

---

## 🚀 **Production Deployment Scripts**

### **Quick Deploy Script**
```bash
#!/bin/bash
# deploy-production.sh

set -e

echo "🚀 Deploying hMailServer Production System..."

# Check prerequisites
command -v docker >/dev/null 2>&1 || { echo "Docker required"; exit 1; }
command -v docker compose >/dev/null 2>&1 || { echo "Docker Compose V2 required"; exit 1; }

# Setup environment
if [ ! -f .env ]; then
    echo "📝 Creating environment file..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration"
    exit 1
fi

# Create directories
mkdir -p {ssl,logs,backups,monitoring/grafana/dashboards,nginx/conf.d}

# Deploy system
echo "🏗️  Starting deployment..."
docker compose -f docker-compose.production.yml pull
docker compose -f docker-compose.production.yml up -d

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 60

# Health check
echo "🔍 Checking system health..."
curl -s http://localhost:8080/health | jq '.healthy' | grep -q true && echo "✅ System healthy" || echo "❌ System unhealthy"

echo "🎉 Deployment complete!"
echo "📱 Web Interface: http://localhost:3000"
echo "📊 Monitoring: http://localhost:3001 (admin/admin123)"
echo "📈 Metrics: http://localhost:9090"
```

### **Health Check Script**
```bash
#!/bin/bash
# health-check.sh

echo "🔍 hMailServer System Health Check"
echo "=================================="

services=("web-interface:3000" "api-gateway:8080" "ai-services:50052" "autonomous:50053")

for service in "${services[@]}"; do
    name=${service%:*}
    port=${service#*:}
    
    if curl -s http://localhost:$port/health >/dev/null; then
        echo "✅ $name - Healthy"
    else
        echo "❌ $name - Unhealthy"
    fi
done

echo ""
echo "📊 Resource Usage:"
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | head -6
```

---

## 📞 **Support & Documentation**

### **Getting Help**
- **Documentation**: `/docs` directory
- **API Reference**: http://localhost:8080/swagger (dev mode)
- **Monitoring**: http://localhost:3001
- **Logs**: `docker compose logs [service]`

### **Key Files**
- `docker-compose.production.yml` - Main deployment file
- `.env` - Environment configuration
- `nginx/nginx.conf` - Nginx configuration
- `monitoring/prometheus.yml` - Metrics configuration

---

**🎉 Your hMailServer Next-Generation system is now ready for production!**

The system integrates:
- ✅ **C++26 Core Engine** - High-performance email processing
- ✅ **Python AI Services** - Intelligent email enhancement
- ✅ **Autonomous Operations** - Self-managing system
- ✅ **React 19 Web Interface** - Modern user experience
- ✅ **Production Monitoring** - Comprehensive observability

**Next Steps**: Configure your domain, set up email accounts, and start processing emails with AI-enhanced capabilities!