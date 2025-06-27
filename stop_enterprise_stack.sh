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
