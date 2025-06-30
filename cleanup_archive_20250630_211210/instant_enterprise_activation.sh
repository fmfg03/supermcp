#!/bin/bash
# instant_enterprise_activation.sh
# Activa inmediatamente todas las capacidades enterprise de SuperMCP25

echo "🚀 ACTIVANDO SUPERMCP25 ENTERPRISE STACK"
echo "========================================"
echo ""

cd /root/supermcp

# 1. VERIFICAR ARCHIVOS ENTERPRISE DISPONIBLES
echo "📁 Verificando archivos enterprise disponibles..."

enterprise_files=(
    "mcp_logs_dashboard_system.py"
    "mcp_task_validation_offline_system.py" 
    "mcp_active_webhook_monitoring.py"
    "sam_persistent_context_management.py"
    "sam_enterprise_authentication_security.py"
    "sam_memory_analyzer.py"
    "mcp_orchestration_server.py"
    "sam_agent_role_management.py"
    "sam_advanced_error_handling.py"
)

available_files=()
missing_files=()

for file in "${enterprise_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - DISPONIBLE"
        available_files+=("$file")
    else
        echo "❌ $file - FALTANTE"
        missing_files+=("$file")
    fi
done

echo ""
echo "📊 RESUMEN:"
echo "✅ Archivos disponibles: ${#available_files[@]}"
echo "❌ Archivos faltantes: ${#missing_files[@]}"
echo ""

# 2. CREAR DIRECTORIO DE LOGS
echo "📂 Creando estructura de directorios..."
mkdir -p logs/{dashboard,validation,monitoring,enterprise}
mkdir -p data/enterprise
mkdir -p config/enterprise

# 3. CONFIGURAR ENVIRONMENT ENTERPRISE
echo "⚙️ Configurando entorno enterprise..."

if [ ! -f ".env" ]; then
    echo "📝 Creando archivo .env..."
    cat > .env << 'ENVEOF'
# MCP Enterprise Configuration
NODE_ENV=production
PORT=3000

# Supabase Configuration
SUPABASE_URL=your_supabase_url_here
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# Enterprise Features
ENTERPRISE_MODE=true
DASHBOARD_PORT=8126
VALIDATION_PORT=8127
MONITORING_PORT=8125
ORCHESTRATION_PORT=8128

# Security
JWT_SECRET=mcp_enterprise_super_secret_jwt_key_2025
API_KEY_EXPIRY=30d
ENCRYPTION_KEY=mcp_aes_256_encryption_key_enterprise

# Monitoring
WEBHOOK_RETRY_COUNT=5
WEBHOOK_BACKUP_EMAIL=francisco@example.com
LOG_RETENTION_DAYS=30

# Context Management
CONTEXT_BACKEND=sqlite
CONTEXT_TTL=3600
CONTEXT_COMPRESSION=true
ENVEOF
    echo "✅ Archivo .env creado"
else
    echo "✅ Archivo .env ya existe"
    
    # Agregar configuraciones enterprise si no existen
    if ! grep -q "ENTERPRISE_MODE" .env; then
        echo "" >> .env
        echo "# Enterprise Features Added" >> .env
        echo "ENTERPRISE_MODE=true" >> .env
        echo "DASHBOARD_PORT=8126" >> .env
        echo "VALIDATION_PORT=8127" >> .env
        echo "MONITORING_PORT=8125" >> .env
        echo "ORCHESTRATION_PORT=8128" >> .env
        echo "✅ Configuraciones enterprise agregadas al .env"
    fi
fi

# 4. CREAR SCRIPT DE STARTUP ENTERPRISE
echo "🔧 Creando script de startup enterprise..."

cat > start_enterprise_stack.sh << 'STARTEOF'
#!/bin/bash
echo "🚀 STARTING SUPERMCP ENTERPRISE STACK"
echo "===================================="

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment loaded"
else
    echo "❌ .env file not found"
    exit 1
fi

# Create logs directories
mkdir -p logs/{dashboard,validation,monitoring,enterprise}

# Function to start enterprise service
start_enterprise_service() {
    local name=$1
    local script=$2
    local port=$3
    local log_dir=$4
    
    if [ -f "$script" ]; then
        echo "Starting $name on port $port..."
        python3 "$script" > "logs/$log_dir/${name,,}.log" 2>&1 &
        local pid=$!
        echo $pid > "logs/${name,,}.pid"
        echo "✅ $name started (PID: $pid)"
        sleep 3
    else
        echo "⚠️ $script not found, skipping $name"
    fi
}

echo ""
echo "🎯 Starting Enterprise Services..."
echo "================================"

# Start available enterprise services
start_enterprise_service "Dashboard" "mcp_logs_dashboard_system.py" "8126" "dashboard"
start_enterprise_service "Validation" "mcp_task_validation_offline_system.py" "8127" "validation"  
start_enterprise_service "Monitoring" "mcp_active_webhook_monitoring.py" "8125" "monitoring"
start_enterprise_service "Orchestration" "mcp_orchestration_server.py" "8128" "enterprise"
start_enterprise_service "MemoryAnalyzer" "sam_memory_analyzer.py" "8129" "enterprise"

# Wait for services to start
echo ""
echo "⏳ Waiting for services to initialize..."
sleep 15

# Health checks
echo "🏥 Checking service health..."
services_healthy=0
total_services=0

check_health() {
    local name=$1
    local port=$2
    
    total_services=$((total_services + 1))
    
    if curl -s -f --connect-timeout 5 "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name (port $port) - HEALTHY"
        services_healthy=$((services_healthy + 1))
    elif curl -s -f --connect-timeout 5 "http://localhost:$port/" > /dev/null 2>&1; then
        echo "✅ $name (port $port) - RESPONDING"
        services_healthy=$((services_healthy + 1))
    elif netstat -tuln | grep ":$port " > /dev/null 2>&1; then
        echo "✅ $name (port $port) - LISTENING"
        services_healthy=$((services_healthy + 1))
    else
        echo "❌ $name (port $port) - NOT RESPONDING"
    fi
}

# Check each service
[ -f "logs/dashboard.pid" ] && check_health "Dashboard" "8126"
[ -f "logs/validation.pid" ] && check_health "Validation" "8127"
[ -f "logs/monitoring.pid" ] && check_health "Monitoring" "8125"
[ -f "logs/orchestration.pid" ] && check_health "Orchestration" "8128"
[ -f "logs/memoryanalyzer.pid" ] && check_health "MemoryAnalyzer" "8129"

echo ""
echo "🎉 SUPERMCP ENTERPRISE STACK STATUS"
echo "=================================="
echo "Services healthy: $services_healthy/$total_services"
echo ""
echo "🌐 ENTERPRISE DASHBOARDS:"
if [ -f "logs/dashboard.pid" ]; then
    echo "📊 Logs Dashboard:    http://65.109.54.94:8126"
fi
if [ -f "logs/validation.pid" ]; then
    echo "✅ Task Validation:   http://65.109.54.94:8127"
fi
if [ -f "logs/monitoring.pid" ]; then
    echo "👀 Webhook Monitor:   http://65.109.54.94:8125"
fi
if [ -f "logs/orchestration.pid" ]; then
    echo "🎯 Orchestration:     http://65.109.54.94:8128"
fi
if [ -f "logs/memoryanalyzer.pid" ]; then
    echo "🧠 Memory Analyzer:   http://65.109.54.94:8129"
fi
echo ""
echo "🎯 SISTEMA ORIGINAL:"
echo "🖥️  Frontend:         http://65.109.54.94:5174"
echo "⚙️  Backend:          http://65.109.54.94:3000"
echo ""
echo "📋 Monitor logs: tail -f logs/*/*.log"
echo "🛑 Stop enterprise: ./stop_enterprise_stack.sh"
echo "📊 Status: ./status_enterprise_stack.sh"
STARTEOF

chmod +x start_enterprise_stack.sh

# 5. CREAR SCRIPT DE STOP
echo "🛑 Creando script de stop..."

cat > stop_enterprise_stack.sh << 'STOPEOF'
#!/bin/bash
echo "🛑 STOPPING ENTERPRISE STACK..."

# Kill processes by PID files
for pidfile in logs/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        service_name=$(basename "$pidfile" .pid)
        
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill "$pid"
            sleep 2
            if kill -0 "$pid" 2>/dev/null; then
                echo "Force killing $service_name..."
                kill -9 "$pid" 2>/dev/null
            fi
        else
            echo "$service_name was not running"
        fi
        rm "$pidfile"
    fi
done

echo "✅ Enterprise stack stopped"
STOPEOF

chmod +x stop_enterprise_stack.sh

echo ""
echo "✅ ENTERPRISE ACTIVATION SETUP COMPLETE!"
echo "========================================"
echo ""
echo "🎯 READY TO ACTIVATE:"
echo "1. 🚀 START ENTERPRISE STACK:"
echo "   ./start_enterprise_stack.sh"
echo ""
echo "2. 📊 CHECK STATUS:"
echo "   ./status_enterprise_stack.sh"
echo ""
echo "3. 🛑 STOP WHEN NEEDED:"
echo "   ./stop_enterprise_stack.sh"
echo ""
echo "🎉 ¡SUPERMCP25 ENTERPRISE LISTO!"
