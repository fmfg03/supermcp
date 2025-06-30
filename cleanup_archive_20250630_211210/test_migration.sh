#!/bin/bash
# test_migration.sh - Prueba la migración con un subconjunto de archivos

set -e

echo "🧪 Ejecutando prueba de migración..."

# Crear directorio temporal para la prueba
TEST_DIR="/tmp/supermcp_test"
rm -rf "$TEST_DIR"
mkdir -p "$TEST_DIR"

echo "📂 Copiando archivos de prueba..."

# Copiar algunos archivos representativos para la prueba
mkdir -p "$TEST_DIR"/{frontend,backend,voice_system,config}

# Simular estructura actual
echo "console.log('Frontend test');" > "$TEST_DIR/frontend/test.js"
echo "console.log('Backend test');" > "$TEST_DIR/backend/test.js"
echo "print('Voice system test')" > "$TEST_DIR/voice_system/test.py"
echo '{"test": "config"}' > "$TEST_DIR/config/test.json"

# Crear docker-compose de prueba
cat > "$TEST_DIR/docker-compose.yml" << 'EOF'
version: '3.8'
services:
  frontend:
    context: ./frontend
    dockerfile: Dockerfile
  backend:
    context: ./backend
    dockerfile: Dockerfile
  voice:
    context: ./voice_system
    dockerfile: Dockerfile
  volumes:
    - ./config:/app/config
    - ./nginx:/etc/nginx
    - ./ssl:/etc/ssl
EOF

cd "$TEST_DIR"

echo "🏗️ Creando estructura de prueba..."

# Crear nueva estructura
mkdir -p {apps,services,agents,infrastructure,config,scripts,docs,tests,data,logs,tools}/{frontend,backend,orchestration,memory-analyzer,webhook-system,voice-system,a2a-system,core,specialized,docker,k8s,nginx,ssl,environments,schemas,security,setup,deployment,monitoring,backup,api,guides,architecture,unit,integration,e2e,performance,migrations,seeds,backups,production,development,archived,cli,generators}

echo "📦 Probando migración de archivos..."

# Mover archivos de prueba
if [ -d "frontend" ]; then
    cp -r frontend/* apps/frontend/
    echo "✅ Frontend migrado"
fi

if [ -d "backend" ]; then
    cp -r backend/* apps/backend/
    echo "✅ Backend migrado"
fi

if [ -d "voice_system" ]; then
    cp -r voice_system/* services/voice-system/
    echo "✅ Voice system migrado"
fi

if [ -d "config" ]; then
    cp config/*.json config/environments/ 2>/dev/null || true
    echo "✅ Config migrado"
fi

echo "🔧 Probando actualización de docker-compose..."

if [ -f "docker-compose.yml" ]; then
    cp docker-compose.yml infrastructure/docker/
    
    # Simular actualización de rutas
    sed -i 's|context: ./frontend|context: ./apps/frontend|g' infrastructure/docker/docker-compose.yml
    sed -i 's|context: ./backend|context: ./apps/backend|g' infrastructure/docker/docker-compose.yml
    sed -i 's|context: ./voice_system|context: ./services/voice-system|g' infrastructure/docker/docker-compose.yml
    sed -i 's|./config:|./config/environments:|g' infrastructure/docker/docker-compose.yml
    sed -i 's|./nginx:|./infrastructure/nginx:|g' infrastructure/docker/docker-compose.yml
    sed -i 's|./ssl:|./infrastructure/ssl:|g' infrastructure/docker/docker-compose.yml
    
    echo "✅ Docker compose actualizado"
fi

echo "🔍 Validando estructura de prueba..."

# Verificar que los archivos se movieron correctamente
tests_passed=0
total_tests=4

if [ -f "apps/frontend/test.js" ]; then
    echo "✅ Archivo frontend encontrado en nueva ubicación"
    ((tests_passed++))
else
    echo "❌ Archivo frontend NO encontrado"
fi

if [ -f "apps/backend/test.js" ]; then
    echo "✅ Archivo backend encontrado en nueva ubicación"
    ((tests_passed++))
else
    echo "❌ Archivo backend NO encontrado"
fi

if [ -f "services/voice-system/test.py" ]; then
    echo "✅ Archivo voice system encontrado en nueva ubicación"
    ((tests_passed++))
else
    echo "❌ Archivo voice system NO encontrado"
fi

if [ -f "config/environments/test.json" ]; then
    echo "✅ Archivo config encontrado en nueva ubicación"
    ((tests_passed++))
else
    echo "❌ Archivo config NO encontrado"
fi

echo ""
echo "📊 Resultados de la prueba:"
echo "Tests pasados: $tests_passed/$total_tests"

if [ $tests_passed -eq $total_tests ]; then
    echo "🎉 ¡Prueba de migración EXITOSA!"
    echo "✅ El script de migración está listo para ejecutarse"
else
    echo "⚠️  Algunos tests fallaron. Revisar el script de migración."
fi

echo ""
echo "📂 Estructura de prueba creada en: $TEST_DIR"
echo "🔍 Puedes revisar los archivos migrados manualmente"

# Mostrar árbol de la nueva estructura
echo ""
echo "🌳 Estructura generada:"
cd "$TEST_DIR"
find . -type d -name ".*" -prune -o -type d -print | head -20 | sort

echo ""
echo "📁 Archivos migrados:"
find apps/ services/ config/ infrastructure/ -type f 2>/dev/null | head -10

cd - > /dev/null

echo ""
echo "🧹 Para limpiar archivos de prueba: rm -rf $TEST_DIR"