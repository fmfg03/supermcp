#!/bin/bash

# 🎪 SuperMCP 2.0 Development Launcher
# Comprehensive AI orchestration platform with swarm intelligence

set -e

echo "🎪 SuperMCP 2.0 - Development Environment"
echo "=========================================="
echo "🏗️ Clean Architecture Multi-Agent AI System"
echo "📦 Components:"
echo "   🏛️ Core Infrastructure"
echo "   🤖 Swarm Intelligence (18+ agents)" 
echo "   🔗 MCP Protocol Integration"
echo "   🧠 Multi-Model AI Router"
echo "   🔒 Enterprise Security"
echo "   📊 Real-time Monitoring"
echo "=========================================="

# Configuration
export ENVIRONMENT="development"
export PYTHONPATH="${PWD}:${PYTHONPATH}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check prerequisites
check_prerequisites() {
    log_info "Checking prerequisites..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        log_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_warning "Node.js not found - some features may be limited"
    fi
    
    # Check Redis
    if ! command -v redis-cli &> /dev/null; then
        log_warning "Redis not found - starting without caching"
    fi
    
    log_success "Prerequisites check completed"
}

# Setup environment
setup_environment() {
    log_info "Setting up environment..."
    
    # Create logs directory
    mkdir -p logs
    
    # Create data directories
    mkdir -p data/{backups,migrations,seeds}
    
    # Copy environment template if .env doesn't exist
    if [ ! -f .env ]; then
        if [ -f project/.env.example ]; then
            cp project/.env.example .env
            log_info "Created .env from template - please configure your API keys"
        fi
    fi
    
    log_success "Environment setup completed"
}

# Kill existing processes
cleanup_processes() {
    log_info "Cleaning up existing processes..."
    
    # Kill processes by name patterns
    pkill -f "intelligence_system.py" 2>/dev/null || true
    pkill -f "dashboard.py" 2>/dev/null || true
    pkill -f "swarm_gateway.py" 2>/dev/null || true
    pkill -f "router.py" 2>/dev/null || true
    pkill -f "terminal_agent.py" 2>/dev/null || true
    pkill -f "connection_manager.py" 2>/dev/null || true
    
    sleep 2
    log_success "Process cleanup completed"
}

# Start core services
start_core_services() {
    log_info "Starting core infrastructure services..."
    
    # 1. Start Swarm Intelligence Core
    log_info "1️⃣ Starting Swarm Intelligence System (Port 8400)..."
    python3 -m agents.swarm.intelligence_system > logs/swarm_core.log 2>&1 &
    SWARM_PID=$!
    echo $SWARM_PID > logs/swarm.pid
    log_success "Swarm Intelligence started (PID: $SWARM_PID)"
    sleep 3
    
    # 2. Start Multi-Model AI Router
    log_info "2️⃣ Starting Multi-Model AI Router (Port 8300)..."
    python3 -m ai.models.router > logs/ai_router.log 2>&1 &
    ROUTER_PID=$!
    echo $ROUTER_PID > logs/router.pid
    log_success "AI Router started (PID: $ROUTER_PID)"
    sleep 3
    
    # 3. Start MCP Connection Manager
    log_info "3️⃣ Starting MCP Connection Manager (Ports 8600-8605)..."
    python3 -m mcp.client.connection_manager > logs/mcp_manager.log 2>&1 &
    MCP_PID=$!
    echo $MCP_PID > logs/mcp.pid
    log_success "MCP Manager started (PID: $MCP_PID)"
    sleep 3
    
    # 4. Start Core Application Orchestrator
    log_info "4️⃣ Starting Core Orchestrator (Port 8000)..."
    python3 -m core.application.orchestrator > logs/orchestrator.log 2>&1 &
    ORCHESTRATOR_PID=$!
    echo $ORCHESTRATOR_PID > logs/orchestrator.pid
    log_success "Orchestrator started (PID: $ORCHESTRATOR_PID)"
    sleep 3
}

# Start specialized services
start_specialized_services() {
    log_info "Starting specialized agent services..."
    
    # 5. Start Terminal Agent
    log_info "5️⃣ Starting Terminal Agent (Port 8500)..."
    python3 -m agents.specialized.terminal_agent > logs/terminal_agent.log 2>&1 &
    TERMINAL_PID=$!
    echo $TERMINAL_PID > logs/terminal.pid
    log_success "Terminal Agent started (PID: $TERMINAL_PID)"
    sleep 3
    
    # 6. Start SAM Agent
    log_info "6️⃣ Starting SAM Agent..."
    python3 -m agents.specialized.sam_agent > logs/sam_agent.log 2>&1 &
    SAM_PID=$!
    echo $SAM_PID > logs/sam.pid
    log_success "SAM Agent started (PID: $SAM_PID)"
    sleep 3
    
    # 7. Start GoogleAI Agent
    log_info "7️⃣ Starting GoogleAI Agent..."
    python3 -m agents.specialized.googleai_agent > logs/googleai_agent.log 2>&1 &
    GOOGLEAI_PID=$!
    echo $GOOGLEAI_PID > logs/googleai.pid
    log_success "GoogleAI Agent started (PID: $GOOGLEAI_PID)"
    sleep 3
}

# Start API services
start_api_services() {
    log_info "Starting API and interface services..."
    
    # 8. Start WebSocket Gateway
    log_info "8️⃣ Starting WebSocket Gateway (Port 8402)..."
    python3 -m api.websocket.swarm_gateway > logs/websocket_gateway.log 2>&1 &
    GATEWAY_PID=$!
    echo $GATEWAY_PID > logs/gateway.pid
    log_success "WebSocket Gateway started (PID: $GATEWAY_PID)"
    sleep 3
    
    # 9. Start REST API Dashboard
    log_info "9️⃣ Starting Web Dashboard (Port 8401)..."
    python3 -m api.rest.v1.dashboard > logs/dashboard.log 2>&1 &
    DASHBOARD_PID=$!
    echo $DASHBOARD_PID > logs/dashboard.pid
    log_success "Web Dashboard started (PID: $DASHBOARD_PID)"
    sleep 3
}

# Start coordination services
start_coordination_services() {
    log_info "Starting coordination and task distribution..."
    
    # 10. Start Message Broker
    log_info "🔟 Starting Message Broker..."
    python3 -m agents.coordination.message_broker > logs/message_broker.log 2>&1 &
    BROKER_PID=$!
    echo $BROKER_PID > logs/broker.pid
    log_success "Message Broker started (PID: $BROKER_PID)"
    sleep 3
    
    # 11. Start Task Distributor
    log_info "1️⃣1️⃣ Starting Task Distributor..."
    python3 -m agents.coordination.task_distributor > logs/task_distributor.log 2>&1 &
    DISTRIBUTOR_PID=$!
    echo $DISTRIBUTOR_PID > logs/distributor.pid
    log_success "Task Distributor started (PID: $DISTRIBUTOR_PID)"
    sleep 3
}

# Display system status
display_status() {
    echo ""
    log_success "🎪 SuperMCP 2.0 Development Environment is RUNNING!"
    echo "================================================================"
    echo "🌐 System Interfaces:"
    echo "   🏛️ Core Orchestrator:      http://localhost:8000"
    echo "   🤖 Multi-Model AI Router:  http://localhost:8300" 
    echo "   🖥️ Terminal Agent:         http://localhost:8500"
    echo "   🌉 WebSocket Gateway:      http://localhost:8402"
    echo "   📊 Web Dashboard:          http://localhost:8401"
    echo "   🔌 Swarm Core:             ws://localhost:8400"
    echo ""
    echo "🔗 MCP Servers:"
    echo "   📁 FileSystem Server:      Port 8600"
    echo "   🌐 Browser Server:         Port 8601"
    echo "   🧠 Knowledge Server:       Port 8602"
    echo "   🛠️ Developer Server:       Port 8603"
    echo "   📝 Version Control:        Port 8604"
    echo "   🔍 Search Server:          Port 8605"
    echo ""
    echo "📊 System Status:"
    echo "   🤖 Active Agents:          18+ intelligent agents"
    echo "   🧠 AI Models:              OpenAI, Claude, Google, Local"
    echo "   🔗 MCP Integrations:       6 specialized servers"
    echo "   📝 Log Directory:          ./logs/"
    echo "================================================================"
    echo ""
    echo "🎯 Key Features Active:"
    echo "   ✅ Swarm Intelligence with emergent behavior detection"
    echo "   ✅ Multi-model AI routing with cost optimization"
    echo "   ✅ MCP protocol integration (File, Browser, Knowledge, Dev, Git, Search)"
    echo "   ✅ Terminal agent with security classification"
    echo "   ✅ Democratic consensus building"
    echo "   ✅ Real-time monitoring and health checks"
    echo "   ✅ Enterprise-grade security and authentication"
    echo ""
    echo "🔍 Monitoring Commands:"
    echo "   📊 Dashboard:    http://localhost:8401"
    echo "   📝 Core Logs:    tail -f logs/swarm_core.log"
    echo "   🤖 Agent Logs:   tail -f logs/sam_agent.log"
    echo "   🔗 MCP Logs:     tail -f logs/mcp_manager.log"
    echo ""
    echo "🎪 The system demonstrates:"
    echo "   🔄 Collaborative task assignment and execution"
    echo "   🗳️ Democratic consensus building"
    echo "   👑 Emergent leadership patterns"
    echo "   🧠 Collective problem solving"
    echo "   🔀 Intelligent model routing and fallback"
    echo ""
    log_success "SuperMCP 2.0 is ready for development!"
    echo "Press Ctrl+C to stop all services"
}

# Cleanup function for graceful shutdown
cleanup() {
    echo ""
    log_info "🛑 Shutting down SuperMCP 2.0..."
    
    # Read PIDs and kill processes
    for pidfile in logs/*.pid; do
        if [ -f "$pidfile" ]; then
            PID=$(cat "$pidfile")
            if kill -0 "$PID" 2>/dev/null; then
                kill "$PID" 2>/dev/null
                log_info "Stopped process $PID"
            fi
            rm -f "$pidfile"
        fi
    done
    
    # Additional cleanup for any remaining processes
    pkill -f "intelligence_system.py" 2>/dev/null || true
    pkill -f "router.py" 2>/dev/null || true
    pkill -f "connection_manager.py" 2>/dev/null || true
    
    log_success "✅ All SuperMCP services stopped"
    exit 0
}

# Set trap for graceful shutdown
trap cleanup SIGINT SIGTERM

# Main execution
main() {
    check_prerequisites
    setup_environment
    cleanup_processes
    start_core_services
    start_specialized_services
    start_api_services
    start_coordination_services
    display_status
    
    # Keep script running
    while true; do
        sleep 1
    done
}

# Run main function
main