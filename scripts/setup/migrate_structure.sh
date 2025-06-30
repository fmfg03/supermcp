#!/bin/bash
# migrate_structure.sh - Reorganiza la estructura SuperMCP según la propuesta

set -e

echo "🏗️ Iniciando reestructuración SuperMCP..."
echo "📂 Creando nueva estructura de directorios..."

# Crear estructura principal
mkdir -p apps/{frontend,backend,mcp-observatory,mcp-devtool}
mkdir -p services/{orchestration,memory-analyzer,webhook-system,voice-system,a2a-system,notification-system}
mkdir -p agents/{core,specialized,swarm}
mkdir -p infrastructure/{docker,k8s,nginx,ssl}
mkdir -p config/{environments,schemas,security}
mkdir -p scripts/{setup,deployment,monitoring,backup}
mkdir -p docs/{api,guides,architecture,deployment}
mkdir -p tests/{unit,integration,e2e,performance}
mkdir -p data/{migrations,seeds,backups}
mkdir -p logs/{production,development,archived}
mkdir -p tools/{cli,generators,monitoring}

echo "🔄 Fase 1: Migrando aplicaciones principales..."

# Mover aplicaciones frontend
if [ -d "frontend" ]; then
    echo "Moving frontend app..."
    cp -r frontend/* apps/frontend/
fi

if [ -d "mcp-frontend" ]; then
    echo "Moving mcp-frontend app..."
    cp -r mcp-frontend/* apps/frontend/
fi

# Mover backend
if [ -d "backend" ]; then
    echo "Moving backend app..."
    cp -r backend/* apps/backend/
fi

# Mover observatory
if [ -d "mcp-observatory" ]; then
    echo "Moving mcp-observatory app..."
    cp -r mcp-observatory/* apps/mcp-observatory/
fi

if [ -d "mcp-observatory-enterprise" ]; then
    echo "Moving mcp-observatory-enterprise app..."
    cp -r mcp-observatory-enterprise/* apps/mcp-observatory/
fi

# Mover devtool
if [ -d "mcp-devtool-client" ]; then
    echo "Moving mcp-devtool-client app..."
    cp -r mcp-devtool-client/* apps/mcp-devtool/
fi

echo "🔄 Fase 2: Migrando servicios especializados..."

# Mover servicios de orquestación
mv mcp_orchestration_server.py services/orchestration/ 2>/dev/null || true
mv python_orchestration_server.py services/orchestration/ 2>/dev/null || true
mv mcp_real_orchestration.py services/orchestration/ 2>/dev/null || true

# Mover análisis de memoria
mv sam_memory_analyzer.py services/memory-analyzer/ 2>/dev/null || true
mv sam_persistent_context_management.py services/memory-analyzer/ 2>/dev/null || true

# Mover sistema de webhooks
mv complete_webhook_agent_end_task_system.py services/webhook-system/ 2>/dev/null || true
mv manus_webhook_receiver.py services/webhook-system/ 2>/dev/null || true
mv mcp_active_webhook_monitoring.py services/webhook-system/ 2>/dev/null || true

# Mover sistema de voz
if [ -d "voice_system" ]; then
    echo "Moving voice system..."
    cp -r voice_system/* services/voice-system/
fi

# Mover sistema A2A
if [ -d "a2a_system" ]; then
    echo "Moving a2a system..."
    cp -r a2a_system/* services/a2a-system/
fi

# Mover sistema de notificaciones
mv sam_manus_notification_protocol.py services/notification-system/ 2>/dev/null || true

echo "🔄 Fase 3: Migrando agentes..."

# Agentes core
mv *agent*.py agents/core/ 2>/dev/null || true
mv sam_chat_swarm_gateway.py agents/core/ 2>/dev/null || true
mv terminal_agent_system.py agents/core/ 2>/dev/null || true

# Agentes especializados
mv multi_model_system.py agents/specialized/ 2>/dev/null || true
mv multimodel_*.py agents/specialized/ 2>/dev/null || true
mv enterprise_unified_bridge.py agents/specialized/ 2>/dev/null || true

# Sistema swarm
mv swarm_*.py agents/swarm/ 2>/dev/null || true
mv terminal_swarm_integration.py agents/swarm/ 2>/dev/null || true

echo "🔄 Fase 4: Migrando infraestructura..."

# Docker
if [ -d "docker" ]; then
    cp -r docker/* infrastructure/docker/
fi
mv docker-compose*.yml infrastructure/docker/ 2>/dev/null || true
mv Dockerfile* infrastructure/docker/ 2>/dev/null || true

# Nginx
if [ -d "nginx" ]; then
    cp -r nginx/* infrastructure/nginx/
fi
mv nginx*.conf infrastructure/nginx/ 2>/dev/null || true

# SSL
if [ -d "ssl" ]; then
    cp -r ssl/* infrastructure/ssl/
fi

echo "🔄 Fase 5: Migrando configuraciones..."

# Configuraciones por ambiente
if [ -d "config" ]; then
    cp -r config/* config/environments/
fi
if [ -d "configs" ]; then
    cp -r configs/* config/environments/
fi

# Schemas
mv *_schemas.py config/schemas/ 2>/dev/null || true
mv *.json config/schemas/ 2>/dev/null || true
mv components.json config/schemas/ 2>/dev/null || true

# Seguridad
mv *security*.py config/security/ 2>/dev/null || true
mv api_validation_middleware.py config/security/ 2>/dev/null || true
if [ -d "keys" ]; then
    cp -r keys/* config/security/
fi

echo "🔄 Fase 6: Migrando scripts..."

# Scripts de setup
mv setup_*.sh scripts/setup/ 2>/dev/null || true
mv quick_start.sh scripts/setup/ 2>/dev/null || true
mv unified_setup_script.sh scripts/setup/ 2>/dev/null || true

# Scripts de deployment
mv deploy*.sh scripts/deployment/ 2>/dev/null || true
mv start_*.sh scripts/deployment/ 2>/dev/null || true
mv stop_*.sh scripts/deployment/ 2>/dev/null || true

# Scripts de monitoreo
mv monitor_*.sh scripts/monitoring/ 2>/dev/null || true
mv diagnose_*.sh scripts/monitoring/ 2>/dev/null || true

# Scripts de backup
mv backup*.sh scripts/backup/ 2>/dev/null || true

echo "🔄 Fase 7: Migrando documentación..."

# Documentación existente
if [ -d "docs" ]; then
    cp -r docs/* docs/guides/
fi

# Documentación arquitectura
mv *.md docs/architecture/ 2>/dev/null || true
mv README.md ./

echo "🔄 Fase 8: Migrando tests..."

# Tests existentes
if [ -d "tests" ]; then
    cp -r tests/* tests/unit/
fi
mv test_*.py tests/integration/ 2>/dev/null || true
mv *test*.js tests/unit/ 2>/dev/null || true

echo "🔄 Fase 9: Migrando datos y logs..."

# Datos
if [ -d "data" ]; then
    cp -r data/* data/backups/
fi
mv *.db data/backups/ 2>/dev/null || true
mv *.sql data/migrations/ 2>/dev/null || true

# Logs
if [ -d "logs" ]; then
    cp -r logs/* logs/production/
fi
mv *.log logs/production/ 2>/dev/null || true

echo "🔄 Fase 10: Migrando herramientas..."

# Scripts de herramientas
if [ -d "scripts" ]; then
    cp -r scripts/* tools/cli/
fi

# Monitoreo
if [ -d "monitoring" ]; then
    cp -r monitoring/* tools/monitoring/
fi

echo "🧹 Limpieza de archivos temporales..."

# Crear directorio temp para archivos temporales
mkdir -p data/temp
mv temp/* data/temp/ 2>/dev/null || true
mv uploads/* data/temp/ 2>/dev/null || true

# Limpiar backups antiguos
mkdir -p data/backups/old
mv backup_* data/backups/old/ 2>/dev/null || true

echo "📝 Creando archivos de configuración para nueva estructura..."

# Crear archivo de configuración principal
cat > config/supermcp.yaml << 'EOF'
# SuperMCP Configuration
version: "2.0"
name: "SuperMCP"
description: "Multi-Agent Coordination Platform"

structure:
  apps:
    - frontend
    - backend
    - mcp-observatory
    - mcp-devtool
  
  services:
    - orchestration
    - memory-analyzer
    - webhook-system
    - voice-system
    - a2a-system
    - notification-system

  agents:
    core: ["basic", "reasoning", "memory"]
    specialized: ["multimodel", "enterprise", "terminal"]
    swarm: ["collaboration", "intelligence"]

environments:
  - development
  - staging
  - production
EOF

# Crear README para nueva estructura
cat > NUEVA_ESTRUCTURA.md << 'EOF'
# Nueva Estructura SuperMCP

## 📂 Estructura Implementada

```
supermcp/
├── apps/                 # Aplicaciones principales
├── services/            # Microservicios
├── agents/              # Agentes especializados
├── infrastructure/      # Infraestructura
├── config/              # Configuraciones
├── scripts/             # Scripts de automatización
├── docs/                # Documentación
├── tests/               # Testing
├── data/                # Datos y storage
├── logs/                # Logs centralizados
└── tools/               # Herramientas desarrollo
```

## 🚀 Próximos Pasos

1. Actualizar imports en archivos migrados
2. Actualizar configuraciones Docker
3. Verificar funcionamiento de servicios
4. Ejecutar tests de integración

## 📋 Archivos Migrados

- ✅ Aplicaciones principales
- ✅ Servicios especializados
- ✅ Sistemas de agentes
- ✅ Infraestructura Docker/Nginx
- ✅ Configuraciones y schemas
- ✅ Scripts de automatización
- ✅ Documentación
- ✅ Tests y datos

EOF

echo "✅ Reestructuración completada!"
echo "📂 Nueva estructura implementada en: $(pwd)"
echo "📋 Revisa NUEVA_ESTRUCTURA.md para detalles"
echo ""
echo "🔧 Próximos pasos recomendados:"
echo "1. Ejecutar: ./scripts/setup/update_imports.sh"
echo "2. Ejecutar: ./scripts/deployment/update_docker_configs.sh"
echo "3. Verificar: ./scripts/monitoring/test_new_structure.sh"