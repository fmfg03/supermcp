#!/bin/bash
echo "📊 SUPERmcp A2A System Monitor"
echo "=============================="

# Function para mostrar métricas
show_metrics() {
    echo "🔍 A2A System Metrics:"
    echo "======================"
    
    # Métricas del servidor A2A
    if curl -s http://localhost:8200/metrics > /dev/null 2>&1; then
        echo "📈 A2A Server Metrics:"
        curl -s http://localhost:8200/metrics | python3 -m json.tool
        echo ""
    else
        echo "❌ A2A Server not responding"
    fi
    
    # Lista de agentes
    echo "🤖 Registered Agents:"
    echo "===================="
    if curl -s http://localhost:8200/agents > /dev/null 2>&1; then
        curl -s http://localhost:8200/agents | python3 -c "
import json, sys
data = json.load(sys.stdin)
agents = data.get('agents', [])
print(f'Total Agents: {len(agents)}')
for agent in agents:
    print(f'  🤖 {agent[\"name\"]} ({agent[\"agent_id\"]})')
    print(f'     Status: {agent[\"status\"]}')
    print(f'     Load: {agent[\"load_score\"]}')
    print(f'     Capabilities: {len(agent[\"capabilities\"])}')
    print()
"
    else
        echo "❌ Cannot retrieve agent information"
    fi
}

# Function para health check
health_check() {
    echo "🏥 A2A Health Check:"
    echo "==================="
    
    services=(
        "A2A-Server:http://localhost:8200/health"
        "Manus-Agent:http://localhost:8210/health"
        "SAM-Agent:http://localhost:8211/health"
        "Memory-Agent:http://localhost:8212/health"
    )
    
    healthy_count=0
    
    for service in "${services[@]}"; do
        name=$(echo $service | cut -d: -f1)
        url=$(echo $service | cut -d: -f2-)
        
        if curl -s -f "$url" > /dev/null 2>&1; then
            echo "✅ $name: Healthy"
            healthy_count=$((healthy_count + 1))
        else
            echo "❌ $name: Unhealthy"
        fi
    done
    
    echo ""
    echo "System Health: $healthy_count/4 services healthy"
    echo ""
}

# Function para mostrar logs
show_logs() {
    echo "📋 Recent A2A Logs:"
    echo "=================="
    
    if [ -d "logs/a2a" ]; then
        echo "🔍 Last 10 lines from each A2A service:"
        for logfile in logs/a2a/*.log; do
            if [ -f "$logfile" ]; then
                echo ""
                echo "--- $(basename $logfile) ---"
                tail -n 5 "$logfile"
            fi
        done
    else
        echo "❌ A2A log directory not found"
    fi
    echo ""
}

# Menu interactivo
while true; do
    echo "📊 A2A Monitor Menu:"
    echo "1) Show Metrics"
    echo "2) Health Check"
    echo "3) Show Logs"
    echo "4) Continuous Monitor (30s refresh)"
    echo "5) Exit"
    echo ""
    read -p "Select option (1-5): " choice
    
    case $choice in
        1)
            show_metrics
            ;;
        2)
            health_check
            ;;
        3)
            show_logs
            ;;
        4)
            echo "🔄 Starting continuous monitor (Ctrl+C to stop)..."
            while true; do
                clear
                echo "📊 SUPERmcp A2A Continuous Monitor - $(date)"
                echo "============================================"
                health_check
                show_metrics
                echo "🔄 Refreshing in 30 seconds... (Ctrl+C to stop)"
                sleep 30
            done
            ;;
        5)
            echo "👋 Exiting A2A Monitor"
            exit 0
            ;;
        *)
            echo "❌ Invalid option"
            ;;
    esac
    
    echo ""
    read -p "Press Enter to continue..."
    clear
done
