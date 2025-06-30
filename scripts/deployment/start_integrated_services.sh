#!/bin/bash
# start_integrated_services.sh

echo "🌟 STARTING COMPLETE SUPERMCP INTEGRATED SYSTEM"
echo "==============================================="

cd /root/supermcp

# Crear directorios necesarios
mkdir -p logs/{dashboard,validation,monitoring,a2a,googleai,bridge}
mkdir -p data/a2a

# Función para iniciar servicio
start_service() {
    local name=$1
    local script=$2
    local port=$3
    local log_dir=$4
    
    echo "🚀 Starting $name on port $port..."
    python3 $script > logs/$log_dir/service.log 2>&1 &
    local pid=$!
    echo $pid > logs/${name,,}.pid
    echo "✅ $name started (PID: $pid)"
    sleep 2
}

# 1. INICIAR ENTERPRISE SERVICES
echo "📊 Starting Enterprise Services..."
start_service "Dashboard" "mcp_logs_dashboard_system.py" "8126" "dashboard"
start_service "Validation" "mcp_task_validation_offline_system.py" "8127" "validation"
start_service "Monitoring" "mcp_active_webhook_monitoring.py" "8125" "monitoring"

# 2. INICIAR A2A SYSTEM
echo "📡 Starting A2A System..."
start_service "A2A-Server" "supermcp_a2a_server.py" "8200" "a2a"
start_service "GoogleAI-Agent" "googleai_agent_a2a.py" "8213" "googleai"

# 3. INICIAR UNIFIED BRIDGE
echo "🌐 Starting Unified Bridge..."
start_service "Unified-Bridge" "enterprise_unified_bridge.py" "9000" "bridge"

# 4. INICIAR ENTERPRISE BRIDGE
echo "🌉 Starting Enterprise Bridge..."
start_service "Enterprise-Bridge" "mcp_enterprise_bridge.py" "8128" "bridge"

# Esperar servicios
echo "⏳ Waiting for all services to initialize..."
sleep 15

# Health checks
echo "🏥 Performing health checks..."
services_healthy=0
total_services=7

check_health() {
    local name=$1
    local port=$2
    
    if curl -s -f "http://sam.chat:$port/health" > /dev/null 2>&1; then
        echo "✅ $name - HEALTHY (port $port)"
        services_healthy=$((services_healthy + 1))
    else
        echo "❌ $name - NOT RESPONDING (port $port)"
    fi
}

# Check all services
check_health "Dashboard" "8126"
check_health "Validation" "8127"
check_health "Monitoring" "8125"
check_health "A2A Server" "8200"
check_health "GoogleAI Agent" "8213"
check_health "Unified Bridge" "9000"
check_health "Enterprise Bridge" "8128"

echo ""
echo "🎉 SUPERMCP INTEGRATED SYSTEM ACTIVE!"
echo "===================================="
echo "Services healthy: $services_healthy/$total_services"
echo ""
echo "🌟 UNIFIED ACCESS POINT:"
echo "🌐 Main Gateway:          http://sam.chat:9000"
echo ""
echo "🏢 ENTERPRISE SERVICES:"
echo "📊 Dashboard:             http://sam.chat:8126"
echo "✅ Validation:            http://sam.chat:8127"
echo "👀 Monitoring:            http://sam.chat:8125"
echo "🌉 Enterprise Bridge:      http://sam.chat:8128"
echo ""
echo "🤖 A2A COMMUNICATION:"
echo "📡 A2A Server:            http://sam.chat:8200"
echo "🧠 GoogleAI Agent:        http://sam.chat:8213"
echo ""
echo "🎯 ORIGINAL SYSTEM:"
echo "🖥️ Frontend:              http://sam.chat:5174"
echo "⚙️ Backend:               http://sam.chat:3000"
echo ""
echo "🎛️ MANAGEMENT:"
echo "📋 View logs: tail -f logs/*/service.log"
echo "🛑 Stop all: ./stop_integrated_services.sh"
echo "🧪 Test: python3 test_integrated_system.py"
echo ""
echo "🚀 WORLD'S FIRST MCP + LANGGRAPH + GRAPHITI + A2A ENTERPRISE SYSTEM ACTIVE!"