#!/bin/bash
# update_imports.sh - Actualiza imports y referencias para nueva estructura

set -e

echo "🔧 Actualizando imports y referencias..."

# Función para actualizar imports en archivos Python
update_python_imports() {
    local file="$1"
    echo "Actualizando imports Python en: $file"
    
    # Backup del archivo original
    cp "$file" "$file.backup"
    
    # Actualizar imports comunes
    sed -i 's|from mcp_orchestration_server|from services.orchestration.mcp_orchestration_server|g' "$file"
    sed -i 's|from sam_memory_analyzer|from services.memory-analyzer.sam_memory_analyzer|g' "$file"
    sed -i 's|from complete_webhook_agent_end_task_system|from services.webhook-system.complete_webhook_agent_end_task_system|g' "$file"
    sed -i 's|from voice_system|from services.voice-system|g' "$file"
    sed -i 's|from a2a_system|from services.a2a-system|g' "$file"
    sed -i 's|import multimodel|from agents.specialized import multimodel|g' "$file"
    sed -i 's|import swarm_|from agents.swarm import swarm_|g' "$file"
}

# Función para actualizar imports en archivos JavaScript
update_js_imports() {
    local file="$1"
    echo "Actualizando imports JavaScript en: $file"
    
    # Backup del archivo original
    cp "$file" "$file.backup"
    
    # Actualizar rutas relativas
    sed -i 's|../backend/|../apps/backend/|g' "$file"
    sed -i 's|../frontend/|../apps/frontend/|g' "$file"
    sed -i 's|./src/adapters/|../apps/backend/src/adapters/|g' "$file"
    sed -i 's|./src/services/|../apps/backend/src/services/|g' "$file"
}

# Función para actualizar configuraciones Docker
update_docker_configs() {
    local file="$1"
    echo "Actualizando configuración Docker: $file"
    
    # Backup del archivo original
    cp "$file" "$file.backup"
    
    # Actualizar rutas de contexto
    sed -i 's|context: ./frontend|context: ./apps/frontend|g' "$file"
    sed -i 's|context: ./backend|context: ./apps/backend|g' "$file"
    sed -i 's|context: ./mcp-observatory|context: ./apps/mcp-observatory|g' "$file"
    sed -i 's|context: ./voice_system|context: ./services/voice-system|g' "$file"
    
    # Actualizar volúmenes
    sed -i 's|./config:|./config/environments:|g' "$file"
    sed -i 's|./nginx:|./infrastructure/nginx:|g' "$file"
    sed -i 's|./ssl:|./infrastructure/ssl:|g' "$file"
    sed -i 's|./logs:|./logs/production:|g' "$file"
}

echo "🔍 Buscando archivos Python para actualizar..."
find . -name "*.py" -not -path "./data/*" -not -path "./*backup*" | while read -r file; do
    if [ -f "$file" ]; then
        update_python_imports "$file"
    fi
done

echo "🔍 Buscando archivos JavaScript para actualizar..."
find . -name "*.js" -o -name "*.jsx" -not -path "./node_modules/*" -not -path "./data/*" -not -path "./*backup*" | while read -r file; do
    if [ -f "$file" ]; then
        update_js_imports "$file"
    fi
done

echo "🔍 Buscando archivos Docker Compose para actualizar..."
find . -name "docker-compose*.yml" -not -path "./data/*" -not -path "./*backup*" | while read -r file; do
    if [ -f "$file" ]; then
        update_docker_configs "$file"
    fi
done

# Actualizar package.json con nueva estructura
echo "📦 Actualizando package.json principal..."
if [ -f "package.json" ]; then
    cp package.json package.json.backup
    
    # Crear nuevo package.json para el monorepo
    cat > package.json << 'EOF'
{
  "name": "supermcp",
  "version": "2.0.0",
  "description": "Multi-Agent Coordination Platform - Restructured",
  "private": true,
  "workspaces": [
    "apps/*",
    "services/*",
    "tools/*"
  ],
  "scripts": {
    "build": "npm run build --workspaces",
    "test": "npm run test --workspaces",
    "start": "npm run start --workspaces",
    "dev": "npm run dev --workspaces",
    "lint": "npm run lint --workspaces"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
EOF
fi

# Crear archivos package.json para cada workspace si no existen
echo "📦 Creando package.json para workspaces..."

# Apps workspace
for app in apps/*/; do
    if [ -d "$app" ] && [ ! -f "$app/package.json" ]; then
        app_name=$(basename "$app")
        cat > "$app/package.json" << EOF
{
  "name": "@supermcp/$app_name",
  "version": "2.0.0",
  "private": true,
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "start": "node server.js",
    "test": "jest"
  }
}
EOF
    fi
done

# Services workspace
for service in services/*/; do
    if [ -d "$service" ] && [ ! -f "$service/package.json" ]; then
        service_name=$(basename "$service")
        cat > "$service/package.json" << EOF
{
  "name": "@supermcp/$service_name",
  "version": "2.0.0",
  "private": true,
  "scripts": {
    "start": "python main.py",
    "test": "pytest",
    "dev": "python main.py --dev"
  }
}
EOF
    fi
done

echo "🔧 Creando scripts de actualización específicos..."

# Script para actualizar rutas en archivos de configuración
cat > scripts/setup/update_config_paths.sh << 'EOF'
#!/bin/bash
# Actualiza rutas en archivos de configuración

echo "Actualizando rutas en configuraciones..."

# Actualizar archivos de configuración JSON
find config/ -name "*.json" | while read -r file; do
    if [ -f "$file" ]; then
        echo "Actualizando: $file"
        sed -i 's|"./backend/|"../apps/backend/|g' "$file"
        sed -i 's|"./frontend/|"../apps/frontend/|g' "$file"
        sed -i 's|"./voice_system/|"../services/voice-system/|g' "$file"
    fi
done

echo "Configuraciones actualizadas."
EOF

chmod +x scripts/setup/update_config_paths.sh

# Script para validar la nueva estructura
cat > scripts/monitoring/validate_structure.sh << 'EOF'
#!/bin/bash
# Valida que la nueva estructura esté correcta

echo "🔍 Validando nueva estructura SuperMCP..."

errors=0

# Verificar directorios principales
dirs=("apps" "services" "agents" "infrastructure" "config" "scripts" "docs" "tests" "data" "logs" "tools")
for dir in "${dirs[@]}"; do
    if [ ! -d "$dir" ]; then
        echo "❌ Directorio faltante: $dir"
        ((errors++))
    else
        echo "✅ Directorio encontrado: $dir"
    fi
done

# Verificar aplicaciones
apps=("frontend" "backend" "mcp-observatory" "mcp-devtool")
for app in "${apps[@]}"; do
    if [ ! -d "apps/$app" ]; then
        echo "❌ App faltante: apps/$app"
        ((errors++))
    else
        echo "✅ App encontrada: apps/$app"
    fi
done

# Verificar servicios
services=("orchestration" "memory-analyzer" "webhook-system" "voice-system" "a2a-system" "notification-system")
for service in "${services[@]}"; do
    if [ ! -d "services/$service" ]; then
        echo "❌ Servicio faltante: services/$service"
        ((errors++))
    else
        echo "✅ Servicio encontrado: services/$service"
    fi
done

if [ $errors -eq 0 ]; then
    echo "🎉 Validación exitosa! Nueva estructura implementada correctamente."
else
    echo "⚠️  Se encontraron $errors errores en la estructura."
fi

echo "📊 Resumen de archivos migrados:"
echo "Apps: $(find apps/ -type f 2>/dev/null | wc -l) archivos"
echo "Services: $(find services/ -type f 2>/dev/null | wc -l) archivos"
echo "Agents: $(find agents/ -type f 2>/dev/null | wc -l) archivos"
echo "Infrastructure: $(find infrastructure/ -type f 2>/dev/null | wc -l) archivos"
echo "Config: $(find config/ -type f 2>/dev/null | wc -l) archivos"
echo "Scripts: $(find scripts/ -type f 2>/dev/null | wc -l) archivos"
echo "Docs: $(find docs/ -type f 2>/dev/null | wc -l) archivos"
echo "Tests: $(find tests/ -type f 2>/dev/null | wc -l) archivos"
EOF

chmod +x scripts/monitoring/validate_structure.sh

echo "✅ Scripts de actualización creados exitosamente!"
echo ""
echo "📋 Próximos pasos:"
echo "1. Ejecutar validación: ./scripts/monitoring/validate_structure.sh"
echo "2. Actualizar configuraciones: ./scripts/setup/update_config_paths.sh"
echo "3. Verificar imports actualizados en archivos"
echo ""
echo "⚠️  Nota: Se crearon backups (.backup) de todos los archivos modificados"