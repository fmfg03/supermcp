#!/bin/bash

# SuperMCP Deployment to sam.chat
# This script deploys the complete SuperMCP system to the sam.chat domain

set -e

echo "🚀 Deploying SuperMCP to sam.chat..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Configuration
DOMAIN="sam.chat"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env.production"

print_step() {
    echo -e "${BLUE}▶ $1${NC}"
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we have access to sam.chat deployment
check_deployment_access() {
    print_step "Checking deployment access to sam.chat..."
    
    # Check if we can reach sam.chat
    if ! curl -s --connect-timeout 5 https://sam.chat > /dev/null; then
        print_error "Cannot reach sam.chat. Check network connectivity."
        exit 1
    fi
    
    print_success "sam.chat is accessible"
    
    # Check if we have deployment credentials/access
    if [[ -z "${DEPLOY_HOST:-}" ]]; then
        print_warning "DEPLOY_HOST not set. Using sam.chat as default."
        export DEPLOY_HOST="sam.chat"
    fi
    
    if [[ -z "${DEPLOY_USER:-}" ]]; then
        print_warning "DEPLOY_USER not set. Using root as default."
        export DEPLOY_USER="root"
    fi
    
    if [[ -z "${DEPLOY_KEY:-}" ]]; then
        print_warning "DEPLOY_KEY not set. Will attempt password authentication."
    fi
}

# Update environment for sam.chat
update_environment_for_domain() {
    print_step "Updating environment configuration for sam.chat..."
    
    # Create production environment with sam.chat domain
    cp "$ENV_FILE" "$ENV_FILE.backup"
    
    # Update domain-specific settings
    sed -i "s/DOMAIN=.*/DOMAIN=sam.chat/" "$ENV_FILE"
    sed -i "s/CORS_ORIGIN=.*/CORS_ORIGIN=https:\/\/sam.chat/" "$ENV_FILE"
    sed -i "s/SSL_EMAIL=.*/SSL_EMAIL=admin@sam.chat/" "$ENV_FILE"
    
    # Update URLs for sam.chat
    sed -i "s/REACT_APP_API_URL=.*/REACT_APP_API_URL=https:\/\/sam.chat\/api/" "$ENV_FILE"
    sed -i "s/REACT_APP_WS_URL=.*/REACT_APP_WS_URL=wss:\/\/sam.chat\/ws/" "$ENV_FILE"
    
    print_success "Environment updated for sam.chat domain"
}

# Create deployment package
create_deployment_package() {
    print_step "Creating deployment package..."
    
    # Create temporary deployment directory
    DEPLOY_DIR="/tmp/supermcp-deploy-$(date +%s)"
    mkdir -p "$DEPLOY_DIR"
    
    # Copy essential files
    cp -r "$PROJECT_ROOT"/{broker,operator-dashboard,backend,mcp-frontend,nginx,database,scripts,config} "$DEPLOY_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT"/{docker-compose.production.yml,Dockerfile.*,.env.production} "$DEPLOY_DIR/" 2>/dev/null || true
    cp "$PROJECT_ROOT/package.json" "$DEPLOY_DIR/" 2>/dev/null || true
    
    # Create deployment-specific docker-compose
    cat > "$DEPLOY_DIR/docker-compose.deploy.yml" << 'EOF'
version: '3.8'

services:
  # Nginx Reverse Proxy with SSL for sam.chat
  nginx:
    image: nginx:alpine
    container_name: mcp_nginx
    restart: unless-stopped
    volumes:
      - ./nginx/nginx-sam-chat.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
      - ./operator-dashboard:/usr/share/nginx/html/operator
    ports:
      - "80:80"
      - "443:443"
    networks:
      - mcp_network
    depends_on:
      - mcp_backend
      - mcp_broker
    environment:
      - DOMAIN=sam.chat

  # Central Message Broker
  mcp_broker:
    build:
      context: .
      dockerfile: Dockerfile.broker
    container_name: mcp_broker
    restart: unless-stopped
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - BROKER_PORT=8080
      - CORS_ORIGIN=https://sam.chat
      - NODE_ENV=production
    volumes:
      - ./logs:/app/logs
    networks:
      - mcp_network
    depends_on:
      - redis

  # Backend
  mcp_backend:
    build:
      context: .
      dockerfile: Dockerfile.backend.production
    container_name: mcp_backend
    restart: unless-stopped
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://mcp_user:${POSTGRES_PASSWORD}@postgres:5432/mcp_enterprise
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379
      - JWT_SECRET=${JWT_SECRET}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
    volumes:
      - ./logs:/app/logs
      - ./uploads:/app/uploads
    networks:
      - mcp_network
    depends_on:
      - postgres
      - redis

  # PostgreSQL
  postgres:
    image: postgres:15-alpine
    container_name: mcp_postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: mcp_enterprise
      POSTGRES_USER: mcp_user
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init:/docker-entrypoint-initdb.d
    networks:
      - mcp_network

  # Redis
  redis:
    image: redis:7-alpine
    container_name: mcp_redis
    restart: unless-stopped
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    networks:
      - mcp_network

volumes:
  postgres_data:
  redis_data:

networks:
  mcp_network:
    driver: bridge
EOF

    # Create nginx configuration for sam.chat
    cat > "$DEPLOY_DIR/nginx/nginx-sam-chat.conf" << 'EOF'
events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=broker:10m rate=100r/s;
    
    # Main server block for sam.chat
    server {
        listen 80;
        server_name sam.chat www.sam.chat;
        
        # Redirect HTTP to HTTPS
        return 301 https://$server_name$request_uri;
    }
    
    server {
        listen 443 ssl http2;
        server_name sam.chat www.sam.chat;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/live/sam.chat/fullchain.pem;
        ssl_certificate_key /etc/nginx/ssl/live/sam.chat/privkey.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512;
        ssl_prefer_server_ciphers off;
        
        # Security headers
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
        
        # Operator Dashboard
        location /operator {
            alias /usr/share/nginx/html/operator;
            try_files $uri $uri/ /operator/index.html;
            
            # No cache for HTML
            location ~* \.html$ {
                add_header Cache-Control "no-cache, no-store, must-revalidate";
            }
        }
        
        # API Routes
        location /api/ {
            limit_req zone=api burst=20 nodelay;
            proxy_pass http://mcp_backend:3000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # WebSocket for Broker
        location /ws/ {
            limit_req zone=broker burst=50 nodelay;
            proxy_pass http://mcp_broker:8080/;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_read_timeout 86400;
        }
        
        # Broker API
        location /broker/ {
            limit_req zone=broker burst=30 nodelay;
            proxy_pass http://mcp_broker:8080/api/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Main application (if needed)
        location / {
            proxy_pass http://mcp_backend:3000/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "OK";
            add_header Content-Type text/plain;
        }
    }
}
EOF

    # Create deploy script for the server
    cat > "$DEPLOY_DIR/deploy.sh" << 'EOF'
#!/bin/bash
set -e

echo "🚀 Deploying SuperMCP on sam.chat server..."

# Stop existing containers
docker-compose -f docker-compose.deploy.yml down --remove-orphans 2>/dev/null || true

# Pull and build images
docker-compose -f docker-compose.deploy.yml build --no-cache
docker-compose -f docker-compose.deploy.yml pull

# Start services
docker-compose -f docker-compose.deploy.yml up -d

echo "✅ SuperMCP deployed successfully!"
echo "🌐 Access: https://sam.chat/operator"
EOF

    chmod +x "$DEPLOY_DIR/deploy.sh"
    
    print_success "Deployment package created at $DEPLOY_DIR"
    echo "$DEPLOY_DIR"
}

# Deploy to sam.chat
deploy_to_sam_chat() {
    local deploy_dir="$1"
    
    print_step "Deploying to sam.chat server..."
    
    # Create archive
    cd "$(dirname "$deploy_dir")"
    tar -czf supermcp-deploy.tar.gz "$(basename "$deploy_dir")"
    
    print_step "Uploading deployment package..."
    
    # Method 1: Try SCP if we have SSH access
    if [[ -n "${DEPLOY_KEY:-}" ]]; then
        scp -i "$DEPLOY_KEY" supermcp-deploy.tar.gz "$DEPLOY_USER@$DEPLOY_HOST:/tmp/"
        ssh -i "$DEPLOY_KEY" "$DEPLOY_USER@$DEPLOY_HOST" "
            cd /tmp && 
            tar -xzf supermcp-deploy.tar.gz && 
            cd $(basename "$deploy_dir") && 
            ./deploy.sh
        "
    elif command -v rsync &> /dev/null; then
        # Method 2: Try rsync
        rsync -avz "$deploy_dir/" "$DEPLOY_USER@$DEPLOY_HOST:/opt/supermcp/"
        ssh "$DEPLOY_USER@$DEPLOY_HOST" "cd /opt/supermcp && ./deploy.sh"
    else
        # Method 3: Manual instructions
        print_warning "No direct deployment method available."
        print_step "Manual deployment instructions:"
        echo ""
        echo "1. Copy the deployment package to your sam.chat server:"
        echo "   scp supermcp-deploy.tar.gz user@sam.chat:/tmp/"
        echo ""
        echo "2. Extract and deploy on the server:"
        echo "   ssh user@sam.chat"
        echo "   cd /tmp"
        echo "   tar -xzf supermcp-deploy.tar.gz"
        echo "   cd $(basename "$deploy_dir")"
        echo "   ./deploy.sh"
        echo ""
        echo "3. Configure SSL certificates:"
        echo "   certbot --nginx -d sam.chat"
        echo ""
        return 1
    fi
    
    print_success "Deployment completed!"
}

# Verify deployment
verify_deployment() {
    print_step "Verifying deployment..."
    
    # Wait a bit for services to start
    sleep 10
    
    # Check if sam.chat responds
    if curl -s -k https://sam.chat/health > /dev/null; then
        print_success "sam.chat is responding"
    else
        print_warning "sam.chat health check failed"
    fi
    
    # Check operator dashboard
    if curl -s -k https://sam.chat/operator/ > /dev/null; then
        print_success "Operator dashboard is accessible"
    else
        print_warning "Operator dashboard check failed"
    fi
}

# Main deployment flow
main() {
    print_step "Starting deployment to sam.chat..."
    
    check_deployment_access
    update_environment_for_domain
    
    DEPLOY_DIR=$(create_deployment_package)
    
    if deploy_to_sam_chat "$DEPLOY_DIR"; then
        verify_deployment
        
        echo ""
        print_success "🎉 SuperMCP successfully deployed to sam.chat!"
        echo ""
        echo "🔗 Access Points:"
        echo "  • Main Site: https://sam.chat"
        echo "  • Operator Dashboard: https://sam.chat/operator"
        echo "  • API: https://sam.chat/api"
        echo "  • WebSocket: wss://sam.chat/ws"
        echo ""
        echo "📋 Next Steps:"
        echo "  1. Test the operator dashboard"
        echo "  2. Configure DNS if needed"
        echo "  3. Set up monitoring alerts"
        echo "  4. Configure backups"
        echo ""
    else
        print_error "Deployment failed. Check the manual instructions above."
        exit 1
    fi
    
    # Cleanup
    rm -rf "$DEPLOY_DIR" 2>/dev/null || true
    rm -f /tmp/supermcp-deploy.tar.gz 2>/dev/null || true
}

# Check arguments
case "${1:-deploy}" in
    "deploy")
        main
        ;;
    "verify")
        verify_deployment
        ;;
    "package-only")
        update_environment_for_domain
        DEPLOY_DIR=$(create_deployment_package)
        echo "Deployment package created at: $DEPLOY_DIR"
        ;;
    *)
        echo "Usage: $0 [deploy|verify|package-only]"
        exit 1
        ;;
esac