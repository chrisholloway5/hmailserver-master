#!/bin/bash

# hMailServer Next-Generation Production Deployment Script
# Automated deployment for the complete integrated system

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$(dirname "$SCRIPT_DIR")")"
DEPLOYMENT_DIR="$SCRIPT_DIR"

# Functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        log_error "Docker is not installed. Please install Docker 24.0+"
        exit 1
    fi
    
    # Check Docker Compose V2
    if ! docker compose version &> /dev/null; then
        log_error "Docker Compose V2 is not available. Please install Docker Compose V2"
        exit 1
    fi
    
    # Check available resources
    AVAILABLE_MEMORY=$(free -g | awk '/^Mem:/{print $7}')
    if [ "$AVAILABLE_MEMORY" -lt 6 ]; then
        log_warning "Less than 6GB RAM available. System may be slow."
    fi
    
    AVAILABLE_DISK=$(df -BG "$PWD" | awk 'NR==2{print $4}' | sed 's/G//')
    if [ "$AVAILABLE_DISK" -lt 30 ]; then
        log_warning "Less than 30GB disk space available. Consider freeing space."
    fi
    
    log_success "Prerequisites check completed"
}

setup_environment() {
    log_info "Setting up environment..."
    
    cd "$DEPLOYMENT_DIR"
    
    # Create environment file if it doesn't exist
    if [ ! -f .env ]; then
        log_info "Creating environment file..."
        cat > .env << 'EOF'
# hMailServer Production Environment Configuration

# Database Configuration
DB_PASSWORD=hmailserver_secure_password_change_me
POSTGRES_DB=hmailserver

# Redis Configuration  
REDIS_PASSWORD=redis_secure_password_change_me

# Security Keys (CHANGE THESE!)
JWT_SECRET=your-super-secret-jwt-key-minimum-256-bits-change-this
NEXTAUTH_SECRET=your-next-auth-secret-change-in-production-environment

# Domain Configuration (UPDATE FOR YOUR DOMAIN)
DOMAIN=localhost
NEXTAUTH_URL=http://localhost:3000

# CORS Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Monitoring
GRAFANA_PASSWORD=admin123

# Email Configuration (UPDATE FOR YOUR SMTP)
SMTP_HOST=localhost
SMTP_PORT=587
SMTP_USER=noreply@localhost
SMTP_PASS=change_me

# AI Configuration (Optional - for enhanced features)
# OPENAI_API_KEY=your_openai_api_key_here
# HUGGINGFACE_TOKEN=your_huggingface_token_here

# SSL Configuration (UPDATE PATHS FOR YOUR CERTIFICATES)
# SSL_CERT_PATH=/etc/ssl/certs/yourdomain.com.crt  
# SSL_KEY_PATH=/etc/ssl/private/yourdomain.com.key
EOF
        
        log_warning "Environment file created. Please edit .env with your configuration!"
        log_warning "IMPORTANT: Change all passwords and secrets before production use!"
        
        # Ask if user wants to continue with defaults
        read -p "Continue with default configuration for testing? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log_info "Please edit .env file and run the script again"
            exit 0
        fi
    fi
    
    # Create necessary directories
    mkdir -p {ssl,logs,backups,monitoring/grafana/dashboards,monitoring/grafana/datasources,nginx/conf.d}
    
    log_success "Environment setup completed"
}

generate_ssl_certificates() {
    log_info "Setting up SSL certificates..."
    
    if [ ! -f ssl/localhost.crt ] || [ ! -f ssl/localhost.key ]; then
        log_info "Generating self-signed SSL certificates for testing..."
        
        openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
            -keyout ssl/localhost.key \
            -out ssl/localhost.crt \
            -subj "/C=US/ST=Test/L=Test/O=hMailServer/CN=localhost" \
            -addext "subjectAltName=DNS:localhost,DNS:*.localhost,IP:127.0.0.1" 2>/dev/null
            
        log_success "Self-signed certificates generated"
        log_warning "Use proper certificates from Let's Encrypt for production!"
    else
        log_success "SSL certificates already exist"
    fi
}

create_nginx_config() {
    log_info "Creating Nginx configuration..."
    
    cat > nginx/nginx.conf << 'EOF'
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Logging format
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for"';
    
    access_log /var/log/nginx/access.log main;
    
    # Performance settings
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 100M;
    
    # Gzip compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=web:10m rate=30r/s;
    
    # Upstream servers
    upstream api_backend {
        server api-gateway:8080;
        keepalive 32;
    }
    
    upstream web_backend {
        server web-interface:3000;
        keepalive 32;
    }
    
    # Main server block
    server {
        listen 80;
        server_name localhost;
        
        # Redirect HTTP to HTTPS (disabled for local testing)
        # return 301 https://$server_name$request_uri;
        
        # API routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://api_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            proxy_read_timeout 300s;
            proxy_connect_timeout 10s;
        }
        
        # Health check
        location /health {
            proxy_pass http://api_backend/health;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
        }
        
        # Web interface
        location / {
            limit_req zone=web burst=50 nodelay;
            proxy_pass http://web_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
        }
        
        # Static files caching
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            proxy_pass http://web_backend;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }
    
    # HTTPS server (for production with real certificates)
    # server {
    #     listen 443 ssl http2;
    #     server_name yourdomain.com;
    #     
    #     ssl_certificate /etc/nginx/ssl/yourdomain.com.crt;
    #     ssl_certificate_key /etc/nginx/ssl/yourdomain.com.key;
    #     
    #     # Include other location blocks here
    # }
}
EOF

    log_success "Nginx configuration created"
}

create_monitoring_config() {
    log_info "Creating monitoring configuration..."
    
    # Prometheus configuration
    cat > monitoring/prometheus.yml << 'EOF'
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"

scrape_configs:
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  - job_name: 'hmailserver-core'
    static_configs:
      - targets: ['core-engine:9090']

  - job_name: 'hmailserver-ai'
    static_configs:
      - targets: ['ai-services:9091']

  - job_name: 'hmailserver-autonomous'
    static_configs:
      - targets: ['autonomous-service:9092']

  - job_name: 'hmailserver-gateway'
    static_configs:
      - targets: ['api-gateway:9093']

  - job_name: 'hmailserver-web'
    static_configs:
      - targets: ['web-interface:9094']
EOF

    # Grafana datasource configuration
    cat > monitoring/grafana/datasources/prometheus.yml << 'EOF'
apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
EOF

    log_success "Monitoring configuration created"
}

deploy_system() {
    log_info "Deploying hMailServer system..."
    
    cd "$DEPLOYMENT_DIR"
    
    # Pull latest images
    log_info "Pulling Docker images..."
    docker compose -f docker-compose.production.yml pull --quiet || {
        log_warning "Some images may need to be built locally"
    }
    
    # Start the system
    log_info "Starting services..."
    docker compose -f docker-compose.production.yml up -d
    
    log_success "System deployment initiated"
}

wait_for_services() {
    log_info "Waiting for services to start..."
    
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        log_info "Health check attempt $attempt/$max_attempts..."
        
        # Check if key services are responding
        local services_healthy=0
        
        # Check API Gateway
        if curl -s http://localhost:8080/health > /dev/null 2>&1; then
            ((services_healthy++))
        fi
        
        # Check Web Interface
        if curl -s http://localhost:3000/api/health > /dev/null 2>&1; then
            ((services_healthy++))
        fi
        
        # Check AI Services  
        if curl -s http://localhost:50052/health > /dev/null 2>&1; then
            ((services_healthy++))
        fi
        
        if [ $services_healthy -ge 2 ]; then
            log_success "Core services are responding"
            break
        fi
        
        if [ $attempt -eq $max_attempts ]; then
            log_warning "Not all services are responding yet, but continuing..."
            break
        fi
        
        sleep 10
        ((attempt++))
    done
}

verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check running containers
    local running_containers=$(docker compose -f docker-compose.production.yml ps --services --filter "status=running" | wc -l)
    local total_containers=$(docker compose -f docker-compose.production.yml config --services | wc -l)
    
    log_info "$running_containers/$total_containers services are running"
    
    # Check key endpoints
    local endpoints=(
        "http://localhost:3000|Web Interface"
        "http://localhost:8080/health|API Gateway"
        "http://localhost:9090|Prometheus"
        "http://localhost:3001|Grafana"
    )
    
    for endpoint in "${endpoints[@]}"; do
        local url="${endpoint%|*}"
        local name="${endpoint#*|}"
        
        if curl -s "$url" > /dev/null 2>&1; then
            log_success "$name is accessible"
        else
            log_warning "$name is not responding"
        fi
    done
}

show_completion_message() {
    echo
    echo "🎉 hMailServer Next-Generation Deployment Complete!"
    echo "=================================================="
    echo
    echo "📱 Web Interface:    http://localhost:3000"
    echo "🔧 API Gateway:      http://localhost:8080"
    echo "📊 Grafana:          http://localhost:3001 (admin/admin123)"
    echo "📈 Prometheus:       http://localhost:9090"
    echo
    echo "🔍 System Status:"
    docker compose -f docker-compose.production.yml ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}"
    echo
    echo "📋 Useful Commands:"
    echo "  View logs:         docker compose logs -f [service]"
    echo "  Check health:      curl http://localhost:8080/health"
    echo "  Stop system:       docker compose down"
    echo "  Update system:     docker compose pull && docker compose up -d"
    echo
    echo "🔐 Security Notes:"
    echo "  - Change all passwords in .env file for production"
    echo "  - Use proper SSL certificates for production"
    echo "  - Configure firewall rules"
    echo "  - Set up regular backups"
    echo
    echo "📚 Documentation: ./DEPLOYMENT_GUIDE.md"
    echo
}

cleanup_on_error() {
    log_error "Deployment failed. Cleaning up..."
    cd "$DEPLOYMENT_DIR"
    docker compose -f docker-compose.production.yml down --remove-orphans 2>/dev/null || true
    exit 1
}

# Main execution
main() {
    trap cleanup_on_error ERR
    
    echo "🚀 hMailServer Next-Generation Production Deployment"
    echo "===================================================="
    echo
    
    check_prerequisites
    setup_environment
    generate_ssl_certificates
    create_nginx_config
    create_monitoring_config
    deploy_system
    wait_for_services
    verify_deployment
    show_completion_message
    
    log_success "Deployment completed successfully!"
}

# Run main function
main "$@"