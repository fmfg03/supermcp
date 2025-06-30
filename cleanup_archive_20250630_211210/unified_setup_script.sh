#!/bin/bash
# unified_setup_script.sh - SuperMCP Unified System Setup

echo "🚀 SUPERMCP UNIFIED SYSTEM SETUP"
echo "================================"

cd /root/supermcp

# Create unified directory structure
echo "📁 Creating unified directory structure..."
mkdir -p supermcp_unified/{scripts,config,logs,web,data}

# 1. CREATE UNIFIED CONFIGURATION
echo "⚙️ Creating unified configuration..."
cat > supermcp_unified/config/unified_config.json << 'EOF'
{
  "unified_system": {
    "name": "SuperMCP Unified Command Center",
    "version": "1.0.0",
    "port": 9000,
    "host": "0.0.0.0"
  },
  "services": {
    "mcp_backend": {
      "port": 3000,
      "status": "external",
      "health_endpoint": "/health"
    },
    "mcp_frontend": {
      "port": 5174,
      "status": "external",
      "health_endpoint": "/"
    },
    "enterprise_dashboard": {
      "port": 8126,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "task_validation": {
      "port": 8127,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "webhook_monitoring": {
      "port": 8125,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "a2a_server": {
      "port": 8200,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "googleai_agent": {
      "port": 8213,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "unified_bridge": {
      "port": 9001,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "enterprise_bridge": {
      "port": 8128,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "voice_system": {
      "port": 8300,
      "status": "managed",
      "health_endpoint": "/health"
    },
    "langgraph_sam": {
      "port": 8400,
      "status": "managed",
      "health_endpoint": "/health"
    }
  },
  "features": {
    "voice_enabled": true,
    "a2a_enabled": true,
    "enterprise_enabled": true,
    "langgraph_enabled": true,
    "graphiti_enabled": true,
    "monitoring_enabled": true
  }
}
EOF

# 2. CREATE UNIFIED DASHBOARD
echo "🌐 Creating unified dashboard..."
cat > supermcp_unified/web/unified_dashboard.py << 'EOF'
#!/usr/bin/env python3
"""
SuperMCP Unified Command Center
Single interface for all SuperMCP services
"""

from flask import Flask, render_template_string, jsonify, request, redirect
from flask_cors import CORS
import requests
import json
import logging
from datetime import datetime
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class UnifiedDashboard:
    def __init__(self):
        self.config = self.load_config()
        self.services = self.config["services"]
        logger.info("Unified Dashboard initialized")
    
    def load_config(self):
        config_path = "../config/unified_config.json"
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.error(f"Config file {config_path} not found")
            return {"services": {}, "features": {}}
    
    def check_service_health(self, service_name, service_config):
        """Check health of individual service"""
        try:
            port = service_config["port"]
            health_endpoint = service_config.get("health_endpoint", "/health")
            url = f"http://localhost:{port}{health_endpoint}"
            
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                return {"status": "healthy", "response_time": response.elapsed.total_seconds()}
            else:
                return {"status": "unhealthy", "error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"status": "offline", "error": str(e)}
    
    def get_system_status(self):
        """Get status of all services"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "services": {},
            "summary": {"total": 0, "healthy": 0, "unhealthy": 0, "offline": 0}
        }
        
        for service_name, service_config in self.services.items():
            service_status = self.check_service_health(service_name, service_config)
            status["services"][service_name] = {
                "port": service_config["port"],
                "status": service_status["status"],
                "managed": service_config.get("status") == "managed",
                "url": f"http://localhost:{service_config['port']}",
                **service_status
            }
            
            status["summary"]["total"] += 1
            if service_status["status"] == "healthy":
                status["summary"]["healthy"] += 1
            elif service_status["status"] == "unhealthy":
                status["summary"]["unhealthy"] += 1
            else:
                status["summary"]["offline"] += 1
        
        return status

# Global dashboard instance
dashboard = UnifiedDashboard()

# HTML Template for unified dashboard
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SuperMCP Unified Command Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Arial', sans-serif; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .header { 
            text-align: center; 
            margin-bottom: 30px; 
            background: rgba(255,255,255,0.1);
            padding: 20px; 
            border-radius: 10px;
        }
        .header h1 { font-size: 2.5em; margin-bottom: 10px; }
        .header p { font-size: 1.2em; opacity: 0.9; }
        .stats-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .stat-card { 
            background: rgba(255,255,255,0.15); 
            padding: 20px; 
            border-radius: 10px; 
            text-align: center;
            backdrop-filter: blur(10px);
        }
        .stat-number { font-size: 2.5em; font-weight: bold; margin-bottom: 10px; }
        .stat-label { font-size: 1.1em; opacity: 0.9; }
        .services-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); 
            gap: 20px; 
            margin-bottom: 30px; 
        }
        .service-card { 
            background: rgba(255,255,255,0.15); 
            padding: 20px; 
            border-radius: 10px;
            backdrop-filter: blur(10px);
        }
        .service-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; }
        .service-name { font-size: 1.3em; font-weight: bold; }
        .status-badge { 
            padding: 5px 15px; 
            border-radius: 20px; 
            font-size: 0.9em; 
            font-weight: bold;
        }
        .status-healthy { background: #4CAF50; }
        .status-unhealthy { background: #FF9800; }
        .status-offline { background: #F44336; }
        .service-info { margin-bottom: 10px; }
        .service-url { 
            background: rgba(0,0,0,0.2); 
            padding: 8px; 
            border-radius: 5px; 
            font-family: monospace;
            font-size: 0.9em;
        }
        .service-url a { color: #64B5F6; text-decoration: none; }
        .service-url a:hover { text-decoration: underline; }
        .refresh-btn { 
            background: #4CAF50; 
            color: white; 
            padding: 10px 20px; 
            border: none; 
            border-radius: 5px; 
            cursor: pointer;
            font-size: 1em;
            margin: 20px auto;
            display: block;
        }
        .refresh-btn:hover { background: #45a049; }
        .footer { 
            text-align: center; 
            margin-top: 30px; 
            padding: 20px; 
            background: rgba(255,255,255,0.1);
            border-radius: 10px;
        }
        .loading { opacity: 0.7; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🚀 SuperMCP Unified Command Center</h1>
            <p>World's First MCP + LangGraph + Graphiti + A2A + Voice Enterprise System</p>
        </div>
        
        <div class="stats-grid" id="stats-grid">
            <!-- Stats will be loaded here -->
        </div>
        
        <div class="services-grid" id="services-grid">
            <!-- Services will be loaded here -->
        </div>
        
        <button class="refresh-btn" onclick="refreshDashboard()">🔄 Refresh System Status</button>
        
        <div class="footer">
            <p>Last updated: <span id="last-updated">Loading...</span></p>
            <p>🎯 SuperMCP - The Ultimate MCP Enterprise Platform</p>
        </div>
    </div>

    <script>
        async function loadSystemStatus() {
            try {
                document.getElementById('services-grid').classList.add('loading');
                
                const response = await fetch('/api/status');
                const data = await response.json();
                
                updateStats(data.summary);
                updateServices(data.services);
                
                document.getElementById('last-updated').textContent = new Date(data.timestamp).toLocaleString();
                document.getElementById('services-grid').classList.remove('loading');
            } catch (error) {
                console.error('Error loading system status:', error);
                document.getElementById('services-grid').innerHTML = '<div class="service-card"><h3>Error loading system status</h3></div>';
                document.getElementById('services-grid').classList.remove('loading');
            }
        }
        
        function updateStats(summary) {
            const statsGrid = document.getElementById('stats-grid');
            const healthPercentage = summary.total > 0 ? Math.round((summary.healthy / summary.total) * 100) : 0;
            
            statsGrid.innerHTML = `
                <div class="stat-card">
                    <div class="stat-number">${summary.total}</div>
                    <div class="stat-label">Total Services</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #4CAF50;">${summary.healthy}</div>
                    <div class="stat-label">Healthy Services</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #FF9800;">${summary.unhealthy}</div>
                    <div class="stat-label">Unhealthy Services</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: #F44336;">${summary.offline}</div>
                    <div class="stat-label">Offline Services</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" style="color: ${healthPercentage >= 80 ? '#4CAF50' : healthPercentage >= 50 ? '#FF9800' : '#F44336'};">${healthPercentage}%</div>
                    <div class="stat-label">System Health</div>
                </div>
            `;
        }
        
        function updateServices(services) {
            const servicesGrid = document.getElementById('services-grid');
            let html = '';
            
            for (const [serviceName, serviceInfo] of Object.entries(services)) {
                const statusClass = `status-${serviceInfo.status}`;
                const displayName = serviceName.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
                
                html += `
                    <div class="service-card">
                        <div class="service-header">
                            <div class="service-name">${displayName}</div>
                            <div class="status-badge ${statusClass}">${serviceInfo.status.toUpperCase()}</div>
                        </div>
                        <div class="service-info">
                            <div>Port: ${serviceInfo.port}</div>
                            <div>Managed: ${serviceInfo.managed ? 'Yes' : 'No'}</div>
                            ${serviceInfo.response_time ? `<div>Response Time: ${(serviceInfo.response_time * 1000).toFixed(2)}ms</div>` : ''}
                            ${serviceInfo.error ? `<div style="color: #FF9800;">Error: ${serviceInfo.error}</div>` : ''}
                        </div>
                        <div class="service-url">
                            <a href="${serviceInfo.url}" target="_blank">${serviceInfo.url}</a>
                        </div>
                    </div>
                `;
            }
            
            servicesGrid.innerHTML = html;
        }
        
        function refreshDashboard() {
            loadSystemStatus();
        }
        
        // Load initial data
        loadSystemStatus();
        
        // Auto-refresh every 30 seconds
        setInterval(loadSystemStatus, 30000);
    </script>
</body>
</html>
"""

@app.route('/')
def unified_dashboard():
    """Main unified dashboard"""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/status')
def api_status():
    """API endpoint for system status"""
    return jsonify(dashboard.get_system_status())

@app.route('/health')
def health_check():
    """Health check for the unified dashboard"""
    return jsonify({
        "status": "healthy",
        "service": "SuperMCP Unified Command Center",
        "timestamp": datetime.now().isoformat()
    })

# Service redirects
@app.route('/dashboard')
def dashboard_redirect():
    return redirect("http://localhost:8126")

@app.route('/validation')
def validation_redirect():
    return redirect("http://localhost:8127")

@app.route('/monitoring')
def monitoring_redirect():
    return redirect("http://localhost:8125")

@app.route('/a2a')
def a2a_redirect():
    return redirect("http://localhost:8200")

@app.route('/voice')
def voice_redirect():
    return redirect("http://localhost:8300")

@app.route('/frontend')
def frontend_redirect():
    return redirect("http://localhost:5174")

@app.route('/backend')
def backend_redirect():
    return redirect("http://localhost:3000")

if __name__ == "__main__":
    print("🌐 STARTING SUPERMCP UNIFIED COMMAND CENTER")
    print("=" * 50)
    print("🚀 World's First MCP + LangGraph + Graphiti + A2A + Voice Enterprise System")
    print()
    print("🎯 Main Interface: http://localhost:9000")
    print("📊 System Status: http://localhost:9000/api/status")
    print()
    print("🔗 Quick Access:")
    print("  • Enterprise Dashboard: http://localhost:9000/dashboard")
    print("  • A2A System: http://localhost:9000/a2a")
    print("  • Voice System: http://localhost:9000/voice")
    print("  • Original Frontend: http://localhost:9000/frontend")
    print()
    
    app.run(host='0.0.0.0', port=9000, debug=False)
EOF

# 3. CREATE UNIFIED MANAGEMENT SCRIPTS
echo "🔧 Creating management scripts..."

# Start script
cat > supermcp_unified/scripts/start_unified_system.sh << 'EOF'
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
EOF

# Stop script
cat > supermcp_unified/scripts/stop_unified_system.sh << 'EOF'
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
EOF

# Status check script
cat > supermcp_unified/scripts/check_system_status.sh << 'EOF'
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
EOF

# Restart script
cat > supermcp_unified/scripts/restart_unified_system.sh << 'EOF'
#!/bin/bash
echo "🔄 RESTARTING SUPERMCP UNIFIED SYSTEM"
echo "===================================="

./supermcp_unified/scripts/stop_unified_system.sh
sleep 5
./supermcp_unified/scripts/start_unified_system.sh
EOF

# Make scripts executable
chmod +x supermcp_unified/scripts/*.sh

echo ""
echo "✅ UNIFIED SETUP COMPLETE!"
echo "========================="
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Start system: ./supermcp_unified/scripts/start_unified_system.sh"
echo "2. Check status: ./supermcp_unified/scripts/check_system_status.sh"
echo "3. Access dashboard: http://localhost:9000"
echo ""
echo "🌟 SuperMCP Unified Command Center is ready!"