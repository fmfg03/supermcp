#!/bin/bash
# stop_integrated_services.sh

echo "🛑 STOPPING SUPERMCP INTEGRATED SYSTEM"
echo "======================================"

cd /root/supermcp

# Función para parar servicio
stop_service() {
    local name=$1
    local pidfile="logs/${name,,}.pid"
    
    if [ -f "$pidfile" ]; then
        local pid=$(cat "$pidfile")
        if kill -0 "$pid" 2>/dev/null; then
            echo "🛑 Stopping $name (PID: $pid)..."
            kill "$pid"
            rm "$pidfile"
            echo "✅ $name stopped"
        else
            echo "⚠️ $name was not running"
            rm -f "$pidfile"
        fi
    else
        echo "⚠️ $name PID file not found"
    fi
}

# Parar todos los servicios
echo "📊 Stopping Enterprise Services..."
stop_service "Dashboard"
stop_service "Validation"
stop_service "Monitoring"

echo "📡 Stopping A2A System..."
stop_service "A2A-Server"
stop_service "GoogleAI-Agent"

echo "🌐 Stopping Bridges..."
stop_service "Unified-Bridge"
stop_service "Enterprise-Bridge"

# Cleanup adicional por si acaso
echo "🧹 Additional cleanup..."
pkill -f "mcp_logs_dashboard_system.py" 2>/dev/null || true
pkill -f "mcp_task_validation_offline_system.py" 2>/dev/null || true
pkill -f "mcp_active_webhook_monitoring.py" 2>/dev/null || true
pkill -f "supermcp_a2a_server.py" 2>/dev/null || true
pkill -f "googleai_agent_a2a.py" 2>/dev/null || true
pkill -f "enterprise_unified_bridge.py" 2>/dev/null || true
pkill -f "mcp_enterprise_bridge.py" 2>/dev/null || true

echo ""
echo "✅ SUPERMCP INTEGRATED SYSTEM STOPPED"
echo "====================================="
echo "All services have been terminated."