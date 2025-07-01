#!/bin/bash

# SuperMCP Operational Deployment Script
# This script deploys the complete SuperMCP system with broker and dashboard

set -e

echo "🚀 SuperMCP Operational Deployment Starting..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env.production"

echo -e "${BLUE}📍 Project root: $PROJECT_ROOT${NC}"

# Function to print colored output
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

# Check if we're in the right directory
if [ ! -f "$PROJECT_ROOT/docker-compose.production.yml" ]; then
    print_error "docker-compose.production.yml not found in $PROJECT_ROOT"
    exit 1
fi

# Check if .env.production exists
if [ ! -f "$ENV_FILE" ]; then
    print_error ".env.production not found. Please create it first."
    exit 1
fi

# Check Docker and Docker Compose
print_step "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

print_success "Docker and Docker Compose are available"

# Create necessary directories
print_step "Creating necessary directories..."
mkdir -p "$PROJECT_ROOT/logs"
mkdir -p "$PROJECT_ROOT/uploads"
mkdir -p "$PROJECT_ROOT/ssl"
mkdir -p "$PROJECT_ROOT/database/backups"
mkdir -p "$PROJECT_ROOT/memory_data"
mkdir -p "$PROJECT_ROOT/config"

print_success "Directories created"

# Install broker dependencies
print_step "Installing broker dependencies..."
cd "$PROJECT_ROOT/broker"
if [ -f "package.json" ]; then
    npm install --production
    print_success "Broker dependencies installed"
else
    print_warning "No package.json found in broker directory"
fi

cd "$PROJECT_ROOT"

# Apply database schema
print_step "Preparing database schema..."
if [ -f "$PROJECT_ROOT/database/supabase-broker-schema.sql" ]; then
    print_success "Database schema ready for Supabase deployment"
    print_warning "Please run the schema manually in your Supabase SQL editor"
else
    print_warning "Database schema not found"
fi

# Stop existing containers
print_step "Stopping existing containers..."
docker-compose -f docker-compose.production.yml down --remove-orphans || true
print_success "Existing containers stopped"

# Pull latest images
print_step "Pulling latest base images..."
docker-compose -f docker-compose.production.yml pull

# Build custom images
print_step "Building custom images..."
docker-compose -f docker-compose.production.yml build --no-cache

print_success "Images built successfully"

# Start the system
print_step "Starting SuperMCP system..."
docker-compose -f docker-compose.production.yml up -d

print_success "SuperMCP system started"

# Wait for services to be ready
print_step "Waiting for services to be ready..."
sleep 30

# Health checks
print_step "Performing health checks..."

# Check broker
if curl -f http://localhost:8080/health &> /dev/null; then
    print_success "Broker is healthy"
else
    print_error "Broker health check failed"
fi

# Check dashboard
if curl -f http://localhost:8081/health &> /dev/null; then
    print_success "Dashboard is healthy"
else
    print_error "Dashboard health check failed"
fi

# Check database
if docker-compose -f docker-compose.production.yml exec -T postgres pg_isready -U mcp_user &> /dev/null; then
    print_success "Database is healthy"
else
    print_error "Database health check failed"
fi

# Check Redis
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping &> /dev/null; then
    print_success "Redis is healthy"
else
    print_error "Redis health check failed"
fi

# Display system status
print_step "System Status:"
docker-compose -f docker-compose.production.yml ps

# Display access information
echo ""
echo -e "${GREEN}🎉 SuperMCP Operational Deployment Complete!${NC}"
echo ""
echo -e "${BLUE}📊 Access Points:${NC}"
echo -e "  • Operator Dashboard: http://localhost:8081"
echo -e "  • Broker API: http://localhost:8080"
echo -e "  • Main Backend: http://localhost:3000"
echo -e "  • Grafana: http://localhost:3001"
echo -e "  • Prometheus: http://localhost:9091"
echo ""
echo -e "${BLUE}🔗 WebSocket Connection:${NC}"
echo -e "  • Broker WebSocket: ws://localhost:8080"
echo ""
echo -e "${BLUE}📋 Next Steps:${NC}"
echo -e "  1. Configure your Supabase credentials in .env.production"
echo -e "  2. Run the database schema in your Supabase SQL editor"
echo -e "  3. Update API keys for external services"
echo -e "  4. Configure SSL certificates for production domain"
echo -e "  5. Set up monitoring alerts"
echo ""
echo -e "${BLUE}🔧 Management Commands:${NC}"
echo -e "  • View logs: docker-compose -f docker-compose.production.yml logs -f"
echo -e "  • Restart system: docker-compose -f docker-compose.production.yml restart"
echo -e "  • Stop system: docker-compose -f docker-compose.production.yml down"
echo -e "  • Update system: $0"
echo ""

# Optional: Show recent logs
read -p "Show recent logs? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_step "Recent logs:"
    docker-compose -f docker-compose.production.yml logs --tail=50
fi

print_success "Deployment script completed successfully!"