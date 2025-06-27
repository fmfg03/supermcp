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
