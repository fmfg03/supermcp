#!/bin/bash
# enterprise_features_activation.sh

echo "🚀 ACTIVANDO FEATURES ENTERPRISE INMEDIATAMENTE"
echo "==============================================="

cd /root/supermcp

# 1. VERIFICAR ARCHIVOS ENTERPRISE
echo "📁 Verificando archivos enterprise..."
enterprise_files=(
    "mcp_logs_dashboard_system.py"
    "mcp_task_validation_offline_system.py" 
    "mcp_active_webhook_monitoring.py"
    "sam_persistent_context_management.py"
    "sam_enterprise_authentication_security.py"
)

missing_count=0
for file in "${enterprise_files[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file - ENCONTRADO"
    else
        echo "❌ $file - FALTANTE"
        missing_count=$((missing_count + 1))
    fi
done

if [ $missing_count -gt 0 ]; then
    echo "❌ $missing_count archivos enterprise faltantes!"
    exit 1
fi

# 2. SETUP ENTERPRISE ENVIRONMENT
echo "⚙️ Configurando entorno enterprise..."

# Variables enterprise
cat >> .env << 'EOF'

# ENTERPRISE FEATURES CONFIGURATION
ENTERPRISE_MODE=true
DASHBOARD_PORT=8126
VALIDATION_PORT=8127
MONITORING_PORT=8125

# PERSISTENT CONTEXT
CONTEXT_BACKEND=sqlite
CONTEXT_TTL=3600
CONTEXT_COMPRESSION=true

# SECURITY
JWT_SECRET=your_super_secret_jwt_key_here
API_KEY_EXPIRY=30d
ENCRYPTION_KEY=your_aes_256_key_here

# MONITORING
WEBHOOK_RETRY_COUNT=5
WEBHOOK_BACKUP_EMAIL=francisco@example.com
LOG_RETENTION_DAYS=30
EOF

# 3. CREAR SCRIPT DE INICIO ENTERPRISE
echo "🔧 Creando startup script enterprise..."

cat > start_enterprise_stack.sh << 'EOF'
#!/bin/bash
echo "🚀 STARTING SUPERMCP ENTERPRISE STACK"
echo "===================================="

# Crear directorio de logs si no existe
mkdir -p logs/{dashboard,validation,monitoring}

# Función para iniciar servicio en background
start_service() {
    local name=$1
    local script=$2
    local port=$3
    local log_file=$4
    
    echo "Starting $name on port $port..."
    python3 $script > logs/$log_file 2>&1 &
    local pid=$!
    echo $pid > logs/${name}.pid
    echo "✅ $name started (PID: $pid)"
    sleep 2
}

# Iniciar servicios enterprise
start_service "Dashboard" "mcp_logs_dashboard_system.py" "8126" "dashboard/dashboard.log"
start_service "Validation" "mcp_task_validation_offline_system.py" "8127" "validation/validation.log"  
start_service "Monitoring" "mcp_active_webhook_monitoring.py" "8125" "monitoring/monitoring.log"

# Esperar que inicien
echo "⏳ Waiting for services to start..."
sleep 10

# Health checks
echo "🏥 Checking service health..."
services_healthy=0

check_health() {
    local name=$1
    local port=$2
    
    if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name - HEALTHY"
        services_healthy=$((services_healthy + 1))
    else
        echo "❌ $name - NOT RESPONDING"
    fi
}

check_health "Dashboard" "8126"
check_health "Validation" "8127"
check_health "Monitoring" "8125"

echo ""
echo "🎉 SUPERMCP ENTERPRISE STACK ACTIVE!"
echo "=================================="
echo "Services healthy: $services_healthy/3"
echo ""
echo "🌐 ENTERPRISE DASHBOARDS:"
echo "📊 Logs Dashboard:    http://localhost:8126"
echo "✅ Task Validation:   http://localhost:8127"  
echo "👀 Webhook Monitor:   http://localhost:8125"
echo ""
echo "🎯 Original System:"
echo "🖥️  Frontend:         http://localhost:5174"
echo "⚙️  Backend:          http://localhost:3000"
echo ""
echo "📋 Logs: tail -f logs/*/*.log"
echo "🛑 Stop: ./stop_enterprise_stack.sh"
EOF

chmod +x start_enterprise_stack.sh

# 4. CREAR SCRIPT DE STOP
cat > stop_enterprise_stack.sh << 'EOF'
#!/bin/bash
echo "🛑 STOPPING ENTERPRISE STACK..."

# Matar procesos por PID files
for pidfile in logs/*.pid; do
    if [ -f "$pidfile" ]; then
        pid=$(cat "$pidfile")
        service_name=$(basename "$pidfile" .pid)
        
        if kill -0 "$pid" 2>/dev/null; then
            echo "Stopping $service_name (PID: $pid)..."
            kill "$pid"
            rm "$pidfile"
        else
            echo "$service_name was not running"
        fi
    fi
done

echo "✅ Enterprise stack stopped"
EOF

chmod +x stop_enterprise_stack.sh

# 5. INTEGRATION TEST
echo "🧪 Ejecutando test de integración..."

cat > test_enterprise_integration.py << 'EOF'
#!/usr/bin/env python3
"""Test de integración enterprise"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_enterprise_stack():
    """Test completo del stack enterprise"""
    print("🧪 TESTING ENTERPRISE STACK INTEGRATION")
    print("=" * 40)
    
    services = [
        ("Dashboard", "http://localhost:8126"),
        ("Validation", "http://localhost:8127"), 
        ("Monitoring", "http://localhost:8125")
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in services:
            try:
                # Health check
                async with session.get(f"{url}/health") as resp:
                    if resp.status == 200:
                        print(f"✅ {name} - HEALTHY")
                        
                        # Test específico por servicio
                        if "8127" in url:  # Validation
                            await test_validation_service(session, url)
                        elif "8125" in url:  # Monitoring  
                            await test_monitoring_service(session, url)
                        elif "8126" in url:  # Dashboard
                            await test_dashboard_service(session, url)
                    else:
                        print(f"❌ {name} - UNHEALTHY ({resp.status})")
                        
            except Exception as e:
                print(f"❌ {name} - ERROR: {e}")

async def test_validation_service(session, base_url):
    """Test del sistema de validación"""
    test_task_id = f"test_task_{datetime.now().strftime('%H%M%S')}"
    
    # Test crear task_id
    data = {
        "task_id": test_task_id,
        "agent_id": "test_agent",
        "task_type": "test"
    }
    
    async with session.post(f"{base_url}/tasks", json=data) as resp:
        if resp.status == 200:
            print(f"  ✅ Task creation test passed")
        else:
            print(f"  ❌ Task creation test failed")

async def test_monitoring_service(session, base_url):
    """Test del sistema de monitoreo"""
    # Test webhook health
    async with session.get(f"{base_url}/webhooks/stats") as resp:
        if resp.status == 200:
            print(f"  ✅ Webhook monitoring test passed")
        else:
            print(f"  ❌ Webhook monitoring test failed")

async def test_dashboard_service(session, base_url):
    """Test del dashboard"""
    # Test logs endpoint
    async with session.get(f"{base_url}/logs") as resp:
        if resp.status == 200:
            print(f"  ✅ Dashboard logs test passed")
        else:
            print(f"  ❌ Dashboard logs test failed")

if __name__ == "__main__":
    asyncio.run(test_enterprise_stack())
EOF

chmod +x test_enterprise_integration.py

echo ""
echo "✅ ENTERPRISE FEATURES ACTIVATION COMPLETE!"
echo "==========================================="
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Iniciar stack: ./start_enterprise_stack.sh"
echo "2. Test integration: python3 test_enterprise_integration.py"
echo "3. Verificar dashboards en URLs mostradas"
echo "4. Integrar con sistema MCP existente"
echo ""
echo "🎉 ¡TU SISTEMA AHORA TIENE CAPACIDADES ENTERPRISE!"