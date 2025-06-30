#!/bin/bash

# 🎪 SuperMCP Swarm Intelligence Demo Launcher
# Launches the complete swarm intelligence system with all components

echo "🎪 SuperMCP Swarm Intelligence System"
echo "====================================="
echo "🏗️ Architecture:"
echo "    🎯 Manus ←→ ⚡ SAM ←→ 🧠 Memory"
echo "         ↕         ↕         ↕"
echo "    🤖 GoogleAI ←→ 📱 Notion ←→ 📧 Email"
echo "         ↕         ↕         ↕"
echo "    🌐 Web ←→ 📊 Analytics ←→ 🔍 Search"
echo "====================================="

# Kill any existing processes
echo "🧹 Cleaning up existing processes..."
pkill -f swarm_intelligence_system.py
pkill -f swarm_web_dashboard.py
pkill -f swarm_demo_agents.py
sleep 2

# Create logs directory
mkdir -p logs

echo "🚀 Starting Swarm Intelligence System..."

# 1. Start the core swarm intelligence system
echo "1️⃣ Starting Core Swarm System (Port 8400)..."
python3 swarm_intelligence_system.py > logs/swarm_core.log 2>&1 &
SWARM_PID=$!
echo "   Core swarm started (PID: $SWARM_PID)"
sleep 3

# 2. Start the web dashboard
echo "2️⃣ Starting Web Dashboard (Port 8401)..."
python3 swarm_web_dashboard.py > logs/swarm_dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "   Dashboard started (PID: $DASHBOARD_PID)"
sleep 3

# 3. Start SAM.CHAT Gateway
echo "3️⃣ Starting SAM.CHAT Gateway (Port 8402)..."
python3 sam_chat_swarm_gateway.py > logs/sam_chat_gateway.log 2>&1 &
GATEWAY_PID=$!
echo "   SAM.CHAT Gateway started (PID: $GATEWAY_PID)"
sleep 3

# 4. Start Multi-Model Router
echo "4️⃣ Starting Multi-Model Router (Port 8300)..."
python3 multi_model_system.py > logs/multimodel_router.log 2>&1 &
ROUTER_PID=$!
echo "   Multi-Model Router started (PID: $ROUTER_PID)"
sleep 3

# 5. Start Terminal Agent
echo "5️⃣ Starting Terminal Agent (Port 8500)..."
python3 terminal_agent_system.py > logs/terminal_agent.log 2>&1 &
TERMINAL_PID=$!
echo "   Terminal Agent started (PID: $TERMINAL_PID)"
sleep 3

# 6. Start Multi-Model Swarm Integration  
echo "6️⃣ Starting Multi-Model Swarm Integration..."
python3 multimodel_swarm_integration.py > logs/multimodel_swarm.log 2>&1 &
MULTIMODEL_SWARM_PID=$!
echo "   Multi-Model Swarm Agent started (PID: $MULTIMODEL_SWARM_PID)"
sleep 3

# 7. Start Terminal Swarm Integration
echo "7️⃣ Starting Terminal Swarm Integration..."
python3 terminal_swarm_integration.py > logs/terminal_swarm.log 2>&1 &
TERMINAL_SWARM_PID=$!
echo "   Terminal Swarm Agent started (PID: $TERMINAL_SWARM_PID)"
sleep 3

# 8. Start MCP Server Manager
echo "8️⃣ Starting MCP Server Manager (Ports 8600-8605)..."
python3 mcp_server_manager.py > logs/mcp_servers.log 2>&1 &
MCP_PID=$!
echo "   MCP Server Manager started (PID: $MCP_PID)"
sleep 3

# 9. Start demo agents
echo "9️⃣ Starting Demo Agents..."
python3 swarm_demo_agents.py > logs/swarm_agents.log 2>&1 &
AGENTS_PID=$!
echo "   Demo agents started (PID: $AGENTS_PID)"
sleep 5

echo ""
echo "✅ SuperMCP Unified System is running!"
echo "======================================="
echo "🖥️ Terminal Agent:     http://sam.chat:8500"
echo "🤖 Multi-Model Router: http://sam.chat:8300"
echo "🌉 SAM.CHAT Gateway:   http://sam.chat:8402"
echo "🌐 Web Dashboard:      http://sam.chat:8401"
echo "🔌 Swarm Core:         ws://sam.chat:8400"
echo "🔗 MCP Servers:        Ports 8600-8605"
echo "   • FileSystem:       Port 8600"
echo "   • Browser:          Port 8601"
echo "   • Knowledge:        Port 8602"
echo "   • Developer:        Port 8603"
echo "   • Version Control:  Port 8604"
echo "   • Search:           Port 8605"
echo "📊 Agent Count:        18+ intelligent agents (12 swarm + 6 MCP)"
echo "📝 Logs Directory:     ./logs/"
echo "======================================="
echo ""
echo "🎯 SuperMCP Features Active:"
echo "   • 🎪 Swarm Intelligence with 18+ agents (12 swarm + 6 MCP)"
echo "   • 🤖 Multi-Model AI Router (all major APIs + local models)"
echo "   • 🖥️ Terminal Agent with security classification"
echo "   • 🌉 SAM.CHAT integration with natural language interface"
echo "   • 🔗 MCP Server Integration (File-systems, Browser, Knowledge, Developer, Version Control, Search)"
echo "   • 💰 Automatic cost optimization (prefers free local models)"
echo "   • 🧠 Emergent intelligence detection"
echo "   • 🔄 Auto-fallback across models"
echo "   • 📊 Real-time monitoring dashboard"
echo "   • 🗳️ Democratic consensus building"
echo "   • 🔒 Security-controlled command execution"
echo ""
echo "🔍 Monitor the system:"
echo "   Dashboard: http://sam.chat:8401"
echo "   Core logs: tail -f logs/swarm_core.log"
echo "   Agent logs: tail -f logs/swarm_agents.log"
echo ""
echo "⚡ The swarm is now demonstrating:"
echo "   1. Collaborative Task Assignment"
echo "   2. Consensus Building"
echo "   3. Emergent Leadership"
echo "   4. Collective Problem Solving"
echo ""
echo "🎪 Swarm Intelligence Demo is LIVE!"
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap 'echo ""; echo "🛑 Stopping SuperMCP System..."; kill $SWARM_PID $DASHBOARD_PID $GATEWAY_PID $ROUTER_PID $TERMINAL_PID $MULTIMODEL_SWARM_PID $TERMINAL_SWARM_PID $MCP_PID $AGENTS_PID 2>/dev/null; echo "✅ All services stopped"; exit 0' INT

# Keep script running
wait