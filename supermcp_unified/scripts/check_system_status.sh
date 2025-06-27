#!/bin/bash
echo "🏥 SUPERMCP UNIFIED SYSTEM STATUS"
echo "================================"

services=(
    "Enterprise Dashboard:8126"
    "Task Validation:8127"
    "Webhook Monitoring:8125"
    "A2A Server:8200"
    "GoogleAI Agent:8213"
    "Unified Bridge:9001"
    "Enterprise Bridge:8128" 
    "Voice System:8300"
    "LangGraph SAM:8400"
    "Unified Dashboard:9000"
)

healthy=0
total=${#services[@]}

for service in "${services[@]}"; do
    IFS=':' read -r name port <<< "$service"
    
    if curl -s -f "http://localhost:$port/health" > /dev/null 2>&1; then
        echo "✅ $name - HEALTHY (port $port)"
        healthy=$((healthy + 1))
    else
        echo "❌ $name - NOT RESPONDING (port $port)"
    fi
done

echo ""
echo "📊 SYSTEM SUMMARY:"
echo "   Services: $healthy/$total healthy"
echo "   Health: $((healthy * 100 / total))%"

if [ $healthy -eq $total ]; then
    echo "   Status: 🟢 EXCELLENT"
elif [ $healthy -gt $((total * 3 / 4)) ]; then
    echo "   Status: 🟡 GOOD"
else
    echo "   Status: 🔴 NEEDS ATTENTION"
fi

echo ""
echo "🌐 Access unified dashboard: http://localhost:9000"
