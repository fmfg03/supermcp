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
