#!/bin/bash
echo "🚀 STARTING SUPERMCP UNIFIED SYSTEM"
echo "=================================="

cd /root/supermcp

# Create logs directory
mkdir -p supermcp_unified/logs

# Start function
start_service() {
    local name=$1
    local script=$2
    local port=$3
    local log_file=$4
    
    echo "🔄 Starting $name on port $port..."
    python3 $script > supermcp_unified/logs/$log_file 2>&1 &
    local pid=$!
    echo $pid > supermcp_unified/logs/${name,,}.pid
    echo "✅ $name started (PID: $pid)"
    sleep 2
}

# 1. Start enterprise services
echo "🏢 Starting Enterprise Services..."
start_service "Enterprise-Dashboard" "mcp_logs_dashboard_system.py" "8126" "enterprise_dashboard.log"
start_service "Task-Validation" "mcp_task_validation_offline_system.py" "8127" "task_validation.log"
start_service "Webhook-Monitoring" "mcp_active_webhook_monitoring.py" "8125" "webhook_monitoring.log"

# 2. Start A2A system
echo "📡 Starting A2A Communication..."
start_service "A2A-Server" "supermcp_a2a_server.py" "8200" "a2a_server.log"
start_service "GoogleAI-Agent" "googleai_agent_a2a.py" "8213" "googleai_agent.log"

# 3. Start bridge services
echo "🌉 Starting Bridge Services..."
start_service "Unified-Bridge" "enterprise_unified_bridge.py" "9001" "unified_bridge.log"
start_service "Enterprise-Bridge" "mcp_enterprise_bridge.py" "8128" "enterprise_bridge.log"

# 4. Start voice system
echo "🎤 Starting Voice System..."
start_service "Voice-System" "voice_system/voice_api_langwatch.py" "8300" "voice_system.log"

# 5. Start LangGraph SAM
echo "🧠 Starting LangGraph SAM..."
start_service "LangGraph-SAM" "langgraph_system/enhanced_sam_agent.py" "8400" "langgraph_sam.log"

# 6. Start unified dashboard
echo "🌐 Starting Unified Command Center..."
start_service "Unified-Dashboard" "supermcp_unified/web/unified_dashboard.py" "9000" "unified_dashboard.log"

# Wait for services to start
echo "⏳ Waiting for services to initialize..."
sleep 20

# Health checks
echo "🏥 Performing health checks..."
./supermcp_unified/scripts/check_system_status.sh

echo ""
echo "🎉 SUPERMCP UNIFIED SYSTEM ACTIVE!"
echo "================================="
echo ""
echo "🌟 UNIFIED COMMAND CENTER:"
echo "   http://localhost:9000"
echo ""
echo "🎯 MANAGEMENT COMMANDS:"
echo "   ./supermcp_unified/scripts/stop_unified_system.sh"
echo "   ./supermcp_unified/scripts/restart_unified_system.sh"
echo "   ./supermcp_unified/scripts/check_system_status.sh"
