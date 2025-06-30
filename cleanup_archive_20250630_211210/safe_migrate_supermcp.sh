#!/bin/bash
# safe_migrate_supermcp.sh - Migración segura paso a paso
# Ejecutar desde /root/supermcp

set -e  # Exit on any error

echo "🏗️ SuperMCP Safe Migration Script"
echo "================================="
echo "Working directory: $(pwd)"
echo "Date: $(date)"

# 1. Crear backup interno
echo "📦 Step 1: Creating internal backup..."
mkdir -p migration_backup
cp -r . migration_backup/original_$(date +%Y%m%d_%H%M%S) 2>/dev/null || echo "⚠️  Some files couldn't be backed up (in use)"

# 2. Crear estructura nueva gradualmente
echo "📁 Step 2: Creating new directory structure..."

# Apps (aplicaciones principales)
mkdir -p apps/{frontend,backend,mcp-observatory,mcp-devtool}

# Services (microservicios)
mkdir -p services/{orchestration,memory-analyzer,webhook-system,voice-system,a2a-system,notification-system}

# Agents (agentes)
mkdir -p agents/{core,specialized,swarm}

# Infrastructure (infraestructura)
mkdir -p infrastructure/{docker,k8s,nginx,ssl}

# Config (configuraciones)
mkdir -p config/{environments,schemas,security}

# Scripts (scripts organizados)
mkdir -p scripts/{setup,deployment,monitoring,backup}

# Docs (documentación)
mkdir -p docs/{api,guides,architecture,deployment}

# Tests (testing)
mkdir -p tests/{unit,integration,e2e,performance}

# Data (datos)
mkdir -p data/{migrations,seeds,backups,temp,uploads,cache}

# Logs (logs organizados)
mkdir -p logs/{production,development,archived}

# Tools (herramientas)
mkdir -p tools/{cli,generators,monitoring}

echo "✅ New directory structure created!"

# 3. Migración gradual de archivos críticos
echo "📦 Step 3: Migrating critical files..."

# Frontend apps
if [ -d "frontend" ]; then
    echo "Moving frontend..."
    cp -r frontend/* apps/frontend/ 2>/dev/null || echo "⚠️  Frontend copy issues"
fi

if [ -d "mcp-frontend" ]; then
    echo "Moving mcp-frontend..."
    cp -r mcp-frontend/* apps/frontend/ 2>/dev/null || echo "⚠️  MCP-Frontend copy issues"
fi

# Backend
if [ -d "backend" ]; then
    echo "Moving backend..."
    cp -r backend/* apps/backend/ 2>/dev/null || echo "⚠️  Backend copy issues"
fi

# Observatory
if [ -d "mcp-observatory" ]; then
    echo "Moving mcp-observatory..."
    cp -r mcp-observatory/* apps/mcp-observatory/ 2>/dev/null || echo "⚠️  Observatory copy issues"
fi

if [ -d "mcp-observatory-enterprise" ]; then
    echo "Moving mcp-observatory-enterprise..."
    cp -r mcp-observatory-enterprise/* apps/mcp-observatory/ 2>/dev/null || echo "⚠️  Observatory Enterprise copy issues"
fi

# DevTool
if [ -d "mcp-devtool-client" ]; then
    echo "Moving mcp-devtool-client..."
    cp -r mcp-devtool-client/* apps/mcp-devtool/ 2>/dev/null || echo "⚠️  DevTool copy issues"
fi

# 4. Migrar servicios core
echo "🔧 Step 4: Migrating core services..."

# Orchestration service
[ -f "mcp_orchestration_server.py" ] && cp mcp_orchestration_server.py services/orchestration/
[ -f "python_orchestration_server.py" ] && cp python_orchestration_server.py services/orchestration/

# Memory analyzer
[ -f "sam_memory_analyzer.py" ] && cp sam_memory_analyzer.py services/memory-analyzer/

# Webhook system
[ -f "complete_webhook_agent_end_task_system.py" ] && cp complete_webhook_agent_end_task_system.py services/webhook-system/
[ -f "manus_webhook_receiver.py" ] && cp manus_webhook_receiver.py services/webhook-system/

# Voice system
if [ -d "voice_system" ]; then
    cp -r voice_system/* services/voice-system/ 2>/dev/null || echo "⚠️  Voice system copy issues"
fi

# A2A system
if [ -d "a2a_system" ]; then
    cp -r a2a_system/* services/a2a-system/ 2>/dev/null || echo "⚠️  A2A system copy issues"
fi

# Notification system
[ -f "sam_manus_notification_protocol.py" ] && cp sam_manus_notification_protocol.py services/notification-system/

# 5. Migrar agentes
echo "🤖 Step 5: Migrating agents..."

# Core agents
for file in *agent*.py; do
    [ -f "$file" ] && cp "$file" agents/core/
done

# Specialized agents
for file in multimodel*.py; do
    [ -f "$file" ] && cp "$file" agents/specialized/
done

# Swarm agents
for file in swarm*.py; do
    [ -f "$file" ] && cp "$file" agents/swarm/
done

# 6. Migrar infraestructura
echo "🏗️ Step 6: Migrating infrastructure..."

# Docker
if [ -d "docker" ]; then
    cp -r docker/* infrastructure/docker/ 2>/dev/null || echo "⚠️  Docker copy issues"
fi

# Docker compose files
for file in docker-compose*.yml; do
    [ -f "$file" ] && cp "$file" infrastructure/docker/
done

for file in Dockerfile*; do
    [ -f "$file" ] && cp "$file" infrastructure/docker/
done

# Nginx
if [ -d "nginx" ]; then
    cp -r nginx/* infrastructure/nginx/ 2>/dev/null || echo "⚠️  Nginx copy issues"
fi

# SSL
if [ -d "ssl" ]; then
    cp -r ssl/* infrastructure/ssl/ 2>/dev/null || echo "⚠️  SSL copy issues"
fi

# 7. Migrar configuraciones
echo "⚙️ Step 7: Migrating configurations..."

# Config files
if [ -d "config" ]; then
    cp -r config/* config/environments/ 2>/dev/null || echo "⚠️  Config copy issues"
fi

# JSON schemas
for file in *.json; do
    if [ -f "$file" ] && [[ "$file" != "package"* ]]; then
        cp "$file" config/schemas/
    fi
done

# Package files (keep in root for now)
[ -f "package.json" ] && cp package.json config/schemas/
[ -f "package-lock.json" ] && cp package-lock.json config/schemas/

# Schema and validation files
[ -f "mcp_payload_schemas.py" ] && cp mcp_payload_schemas.py config/schemas/
[ -f "api_validation_middleware.py" ] && cp api_validation_middleware.py config/security/

# 8. Migrar scripts
echo "📜 Step 8: Migrating scripts..."

# Setup scripts
for file in setup*.sh install*.sh; do
    [ -f "$file" ] && cp "$file" scripts/setup/
done

# Deployment scripts
for file in deploy*.sh start*.sh stop*.sh; do
    [ -f "$file" ] && cp "$file" scripts/deployment/
done

# Monitoring scripts
for file in monitor*.sh diagnose*.sh; do
    [ -f "$file" ] && cp "$file" scripts/monitoring/
done

# Backup scripts
for file in backup*.sh; do
    [ -f "$file" ] && cp "$file" scripts/backup/
done

# Other scripts
for file in *.sh; do
    if [ -f "$file" ] && ! ls scripts/*/ | grep -q "$(basename "$file")" 2>/dev/null; then
        cp "$file" scripts/setup/
    fi
done

# 9. Migrar documentación
echo "📚 Step 9: Migrating documentation..."

if [ -d "docs" ]; then
    cp -r docs/* docs/guides/ 2>/dev/null || echo "⚠️  Docs copy issues"
fi

for file in *.md; do
    if [ -f "$file" ] && [ "$file" != "README.md" ]; then
        cp "$file" docs/architecture/
    fi
done

# 10. Migrar tests
echo "🧪 Step 10: Migrating tests..."

if [ -d "tests" ]; then
    cp -r tests/* tests/unit/ 2>/dev/null || echo "⚠️  Tests copy issues"
fi

for file in test*.py *test*.py; do
    [ -f "$file" ] && cp "$file" tests/integration/
done

# 11. Migrar datos y logs
echo "📊 Step 11: Migrating data and logs..."

# Logs
for file in *.log; do
    [ -f "$file" ] && cp "$file" logs/production/
done

if [ -d "logs" ]; then
    cp -r logs/* logs/archived/ 2>/dev/null || echo "⚠️  Logs copy issues"
fi

# Data
[ -d "uploads" ] && cp -r uploads/* data/uploads/ 2>/dev/null
[ -d "temp" ] && cp -r temp/* data/temp/ 2>/dev/null
[ -d "__pycache__" ] && cp -r __pycache__/* data/cache/ 2>/dev/null

# Database files
for file in *.db *.sqlite *.sql; do
    [ -f "$file" ] && cp "$file" data/migrations/
done

# 12. Crear archivos índice en cada directorio
echo "📋 Step 12: Creating index files..."

# Crear README en cada directorio principal
cat > apps/README.md << 'EOF'
# Applications

This directory contains the main applications:
- `frontend/` - React/Vue frontend applications
- `backend/` - Backend APIs and services
- `mcp-observatory/` - Observatory dashboard
- `mcp-devtool/` - Development tools
EOF

cat > services/README.md << 'EOF'
# Services

This directory contains microservices:
- `orchestration/` - MCP orchestration service
- `memory-analyzer/` - SAM memory analysis
- `webhook-system/` - Webhook handling
- `voice-system/` - Voice processing
- `a2a-system/` - Agent-to-Agent communication
- `notification-system/` - Notification handling
EOF

cat > agents/README.md << 'EOF'
# Agents

This directory contains agent implementations:
- `core/` - Core agent functionality
- `specialized/` - Specialized agents
- `swarm/` - Swarm intelligence
EOF

# 13. Verificar migración
echo "✅ Step 13: Verification..."

echo "📊 Migration Summary:"
echo "===================="
echo "Apps:          $(find apps -type f | wc -l) files"
echo "Services:      $(find services -type f | wc -l) files"
echo "Agents:        $(find agents -type f | wc -l) files"
echo "Infrastructure:$(find infrastructure -type f | wc -l) files"
echo "Config:        $(find config -type f | wc -l) files"
echo "Scripts:       $(find scripts -type f | wc -l) files"
echo "Docs:          $(find docs -type f | wc -l) files"
echo "Tests:         $(find tests -type f | wc -l) files"
echo "Data:          $(find data -type f | wc -l) files"
echo "Logs:          $(find logs -type f | wc -l) files"

echo ""
echo "✅ Migration completed successfully!"
echo "🔍 Next steps:"
echo "   1. Review the new structure: ls -la"
echo "   2. Test critical services"
echo "   3. Update import paths where needed"
echo "   4. Commit changes to git"
echo ""
echo "⚠️  Original files remain in place. Remove them after testing."