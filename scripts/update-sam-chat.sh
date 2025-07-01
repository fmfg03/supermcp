#!/bin/bash

# SuperMCP sam.chat Integration Update Script
# This script updates the existing sam.chat deployment with the new broker and operational features

set -e

echo "🔄 Updating SuperMCP on sam.chat with operational features..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Create update package for sam.chat
create_update_package() {
    print_step "Creating update package for sam.chat..."
    
    UPDATE_DIR="/tmp/supermcp-update-$(date +%s)"
    mkdir -p "$UPDATE_DIR"
    
    # Copy new components
    cp -r "$PROJECT_ROOT/broker" "$UPDATE_DIR/"
    cp -r "$PROJECT_ROOT/operator-dashboard" "$UPDATE_DIR/"
    cp "$PROJECT_ROOT/Dockerfile.broker" "$UPDATE_DIR/"
    cp "$PROJECT_ROOT/database/supabase-broker-schema.sql" "$UPDATE_DIR/"
    cp "$PROJECT_ROOT/nginx/dashboard.conf" "$UPDATE_DIR/"
    
    # Create integration docker-compose for sam.chat
    cat > "$UPDATE_DIR/docker-compose.broker-update.yml" << 'EOF'
version: '3.8'

services:
  # Add Central Message Broker to existing deployment
  mcp_broker:
    build:
      context: .
      dockerfile: Dockerfile.broker
    container_name: mcp_broker
    restart: unless-stopped
    environment:
      - REDIS_URL=redis://:${REDIS_PASSWORD:-redis_secure_password_2024}@redis:6379
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - BROKER_PORT=8080
      - CORS_ORIGIN=https://sam.chat
      - NODE_ENV=production
    volumes:
      - ./logs:/app/logs
    ports:
      - "8080:8080"
    networks:
      - default
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 10s
      retries: 5

  # Operator Dashboard as separate nginx service
  mcp_dashboard:
    image: nginx:alpine
    container_name: mcp_dashboard
    restart: unless-stopped
    volumes:
      - ./operator-dashboard:/usr/share/nginx/html
      - ./dashboard.conf:/etc/nginx/conf.d/default.conf
    ports:
      - "8081:80"
    networks:
      - default
    depends_on:
      - mcp_broker
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3

networks:
  default:
    external: true
    name: mcp_network
EOF

    # Create update script for sam.chat server
    cat > "$UPDATE_DIR/update-sam-chat.sh" << 'EOF'
#!/bin/bash
set -e

echo "🔄 Updating SuperMCP on sam.chat server..."

# Backup existing setup
BACKUP_DIR="./backup-$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r docker-compose*.yml "$BACKUP_DIR/" 2>/dev/null || true
cp -r nginx/ "$BACKUP_DIR/" 2>/dev/null || true

# Install broker dependencies
cd broker
npm install --production
cd ..

# Add broker to existing docker-compose
echo "Adding broker services to existing deployment..."

# Start broker services
docker-compose -f docker-compose.broker-update.yml up -d

# Wait for services
echo "Waiting for broker to be healthy..."
sleep 30

# Verify broker health
if curl -f http://localhost:8080/health > /dev/null 2>&1; then
    echo "✅ Broker is healthy"
else
    echo "❌ Broker health check failed"
    exit 1
fi

# Verify dashboard
if curl -f http://localhost:8081/health > /dev/null 2>&1; then
    echo "✅ Dashboard is healthy" 
else
    echo "❌ Dashboard health check failed"
    exit 1
fi

# Update main nginx configuration to proxy to broker and dashboard
echo "Updating nginx configuration..."

# Add broker proxy rules to existing nginx config
cat >> /etc/nginx/sites-available/sam.chat << 'NGINX_EOF'

    # SuperMCP Broker Integration
    location /broker/ {
        proxy_pass http://localhost:8080/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # CORS headers
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
        add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
    }
    
    # SuperMCP WebSocket
    location /ws/ {
        proxy_pass http://localhost:8080/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 86400;
    }
    
    # Operator Dashboard
    location /operator/ {
        proxy_pass http://localhost:8081/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

NGINX_EOF

# Reload nginx
nginx -t && nginx -s reload

echo "✅ SuperMCP operational update completed!"
echo ""
echo "🔗 New Access Points:"
echo "  • Operator Dashboard: https://sam.chat/operator/"
echo "  • Broker API: https://sam.chat/broker/"
echo "  • WebSocket: wss://sam.chat/ws/"
echo ""
echo "📊 Direct Access:"
echo "  • Dashboard: http://localhost:8081"
echo "  • Broker: http://localhost:8080"
echo ""
EOF

    chmod +x "$UPDATE_DIR/update-sam-chat.sh"
    
    # Create nginx route addition for existing setup
    cat > "$UPDATE_DIR/add-nginx-routes.conf" << 'EOF'
# Add these routes to your existing sam.chat nginx configuration

# SuperMCP Broker API
location /broker/ {
    proxy_pass http://localhost:8080/api/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Rate limiting
    limit_req zone=api burst=20 nodelay;
    
    # CORS headers
    add_header Access-Control-Allow-Origin "https://sam.chat";
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
    add_header Access-Control-Allow-Headers "DNT,User-Agent,X-Requested-With,If-Modified-Since,Cache-Control,Content-Type,Range,Authorization";
}

# SuperMCP WebSocket
location /ws/ {
    proxy_pass http://localhost:8080/;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_read_timeout 86400;
    proxy_send_timeout 86400;
    proxy_connect_timeout 60;
}

# Operator Dashboard
location /operator/ {
    proxy_pass http://localhost:8081/;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
        proxy_pass http://localhost:8081;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

    # Create simple installation instructions
    cat > "$UPDATE_DIR/INSTALL_INSTRUCTIONS.md" << 'EOF'
# SuperMCP Operational Update for sam.chat

## Quick Installation

1. **Upload the update package to your sam.chat server:**
   ```bash
   scp -r update-package/ user@sam.chat:/opt/supermcp-update/
   ```

2. **Run the update script on the server:**
   ```bash
   ssh user@sam.chat
   cd /opt/supermcp-update
   ./update-sam-chat.sh
   ```

3. **Verify the installation:**
   - Check broker: `curl http://localhost:8080/health`
   - Check dashboard: `curl http://localhost:8081/health`
   - Test web access: https://sam.chat/operator/

## Manual Integration Steps

If the automatic script doesn't work:

1. **Copy files to server:**
   - `broker/` → `/opt/supermcp/broker/`
   - `operator-dashboard/` → `/opt/supermcp/operator-dashboard/`
   - `Dockerfile.broker` → `/opt/supermcp/`

2. **Build and start broker:**
   ```bash
   cd /opt/supermcp
   docker build -f Dockerfile.broker -t supermcp-broker .
   docker run -d --name mcp_broker -p 8080:8080 --network mcp_network supermcp-broker
   ```

3. **Start dashboard:**
   ```bash
   docker run -d --name mcp_dashboard -p 8081:80 \
     -v /opt/supermcp/operator-dashboard:/usr/share/nginx/html \
     nginx:alpine
   ```

4. **Add nginx routes:**
   Add the contents of `add-nginx-routes.conf` to your main nginx configuration.

5. **Reload nginx:**
   ```bash
   nginx -t && nginx -s reload
   ```

## Access Points After Update

- **Operator Dashboard**: https://sam.chat/operator/
- **Broker API**: https://sam.chat/broker/
- **WebSocket**: wss://sam.chat/ws/
- **Direct Dashboard**: http://sam.chat:8081
- **Direct Broker**: http://sam.chat:8080

## Environment Variables

Add these to your existing `.env` file:

```
BROKER_PORT=8080
SUPABASE_URL=your-supabase-url
SUPABASE_KEY=your-supabase-key
```

## Database Setup

Run the SQL schema in your Supabase dashboard:
`supabase-broker-schema.sql`

## Verification

Test all endpoints:
```bash
curl https://sam.chat/operator/
curl https://sam.chat/broker/nodes
curl -H "Upgrade: websocket" https://sam.chat/ws/
```
EOF

    print_success "Update package created at $UPDATE_DIR"
    echo "$UPDATE_DIR"
}

# Generate deployment instructions
show_deployment_instructions() {
    local update_dir="$1"
    
    echo ""
    print_success "🎯 SuperMCP sam.chat Update Package Ready!"
    echo ""
    echo -e "${BLUE}📦 Package Location:${NC} $update_dir"
    echo ""
    echo -e "${BLUE}🚀 Quick Deployment Commands:${NC}"
    echo ""
    echo "1. Copy to server:"
    echo "   scp -r $update_dir/ user@sam.chat:/opt/supermcp-update/"
    echo ""
    echo "2. Deploy on server:"
    echo "   ssh user@sam.chat"
    echo "   cd /opt/supermcp-update"
    echo "   ./update-sam-chat.sh"
    echo ""
    echo -e "${BLUE}🔗 After deployment, access:${NC}"
    echo "  • Operator Dashboard: https://sam.chat/operator/"
    echo "  • Broker API: https://sam.chat/broker/"
    echo "  • WebSocket: wss://sam.chat/ws/"
    echo ""
    echo -e "${BLUE}📋 Included Files:${NC}"
    ls -la "$update_dir/"
    echo ""
    echo -e "${YELLOW}💡 Tip:${NC} Check INSTALL_INSTRUCTIONS.md for detailed setup steps"
}

# Main function
main() {
    print_step "Creating SuperMCP operational update for sam.chat..."
    
    UPDATE_DIR=$(create_update_package)
    show_deployment_instructions "$UPDATE_DIR"
    
    # Ask if user wants to create a tar package
    echo ""
    read -p "Create tar.gz package for easy transfer? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd "$(dirname "$UPDATE_DIR")"
        tar -czf "supermcp-sam-chat-update.tar.gz" "$(basename "$UPDATE_DIR")"
        print_success "Package created: $(dirname "$UPDATE_DIR")/supermcp-sam-chat-update.tar.gz"
        echo ""
        echo "Transfer command:"
        echo "scp $(dirname "$UPDATE_DIR")/supermcp-sam-chat-update.tar.gz user@sam.chat:/tmp/"
        echo ""
        echo "Extract and run:"
        echo "ssh user@sam.chat 'cd /tmp && tar -xzf supermcp-sam-chat-update.tar.gz && cd $(basename "$UPDATE_DIR") && ./update-sam-chat.sh'"
    fi
}

# Check arguments
case "${1:-update}" in
    "update")
        main
        ;;
    "package-only")
        UPDATE_DIR=$(create_update_package)
        echo "Update package created at: $UPDATE_DIR"
        ;;
    *)
        echo "Usage: $0 [update|package-only]"
        exit 1
        ;;
esac