#!/bin/bash
echo "🚀 Starting SUPERmcp A2A System"
echo "==============================="

# Function para iniciar servicio con logging
start_a2a_service() {
    local service_name=$1
    local script_name=$2
    local port=$3
    
    echo "Starting A2A $service_name on port $port..."
    python3 "$script_name" > "logs/a2a/${service_name}.log" 2>&1 &
    local pid=$!
    echo $pid > "logs/a2a/${service_name}.pid"
    echo "✅ A2A $service_name started (PID: $pid)"
    sleep 2
}

# Iniciar A2A Server primero
echo "🏗️ Starting A2A Server..."
start_a2a_service "a2a-server" "supermcp_a2a_server.py" 8200

# Esperar que el servidor A2A esté listo
echo "⏳ Waiting for A2A Server to initialize..."
sleep 5

# Iniciar agentes A2A
echo "🤖 Starting A2A Agents..." 
start_a2a_service "a2a-agents" "supermcp_a2a_agents.py" 8210

# Health check A2A
echo "🏥 Performing A2A health checks..."
sleep 5

check_a2a_service() {
    local name=$1
    local url=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo "✅ A2A $name is healthy"
        return 0
    else
        echo "❌ A2A $name is not responding"
        return 1
    fi
}

a2a_services_ok=0

check_a2a_service "Server" "http://localhost:8200/health" && a2a_services_ok=$((a2a_services_ok + 1))
check_a2a_service "Manus Agent" "http://localhost:8210/health" && a2a_services_ok=$((a2a_services_ok + 1))
check_a2a_service "SAM Agent" "http://localhost:8211/health" && a2a_services_ok=$((a2a_services_ok + 1))
check_a2a_service "Memory Agent" "http://localhost:8212/health" && a2a_services_ok=$((a2a_services_ok + 1))

echo ""
echo "🎉 A2A SYSTEM STARTED!"
echo "====================="
echo "A2A Services running: $a2a_services_ok/4"
echo ""
echo "🌐 A2A Access Points:"
echo "A2A Server:     http://65.109.54.94:8200"
echo "Manus Agent:    http://65.109.54.94:8210"
echo "SAM Agent:      http://65.109.54.94:8211"
echo "Memory Agent:   http://65.109.54.94:8212"
echo ""
echo "📊 A2A Logs: tail -f logs/a2a/*.log"
echo "🔍 A2A Metrics: curl http://localhost:8200/metrics"
echo ""

# Mostrar agentes registrados
echo "🤖 Registered A2A Agents:"
curl -s http://localhost:8200/agents | python3 -m json.tool

echo ""
echo "✨ SUPERmcp A2A Integration is now LIVE!"
echo "Ready for multi-agent collaboration! 🚀"
