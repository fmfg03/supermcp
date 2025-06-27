#!/bin/bash
echo "🛑 STOPPING SUPERMCP UNIFIED SYSTEM"
echo "=================================="

cd /root/supermcp

# Stop function
stop_service() {
    local name=$1
    local pidfile="supermcp_unified/logs/${name,,}.pid"
    
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

# Stop all services
services=(
    "Enterprise-Dashboard"
    "Task-Validation" 
    "Webhook-Monitoring"
    "A2A-Server"
    "GoogleAI-Agent"
    "Unified-Bridge"
    "Enterprise-Bridge"
    "Voice-System"
    "LangGraph-SAM"
    "Unified-Dashboard"
)

for service in "${services[@]}"; do
    stop_service "$service"
done

# Additional cleanup
echo "🧹 Additional cleanup..."
pkill -f "mcp_logs_dashboard_system.py" 2>/dev/null || true
pkill -f "mcp_task_validation_offline_system.py" 2>/dev/null || true
pkill -f "mcp_active_webhook_monitoring.py" 2>/dev/null || true
pkill -f "supermcp_a2a_server.py" 2>/dev/null || true
pkill -f "googleai_agent_a2a.py" 2>/dev/null || true
pkill -f "enterprise_unified_bridge.py" 2>/dev/null || true
pkill -f "mcp_enterprise_bridge.py" 2>/dev/null || true
pkill -f "voice_api_langwatch.py" 2>/dev/null || true
pkill -f "enhanced_sam_agent.py" 2>/dev/null || true
pkill -f "unified_dashboard.py" 2>/dev/null || true

echo ""
echo "✅ SUPERMCP UNIFIED SYSTEM STOPPED"
echo "================================="
