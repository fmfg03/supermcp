#!/usr/bin/env python3
"""
Enterprise Unified Bridge - Gateway único para todo SuperMCP
Unifica todos los servicios en una sola API
"""

from flask import Flask, jsonify, request, redirect
from flask_cors import CORS
import requests
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class UnifiedBridge:
    """Bridge unificado para todos los servicios SuperMCP"""
    
    def __init__(self):
        self.services = {
            "mcp_backend": "http://localhost:3000",
            "dashboard": "http://localhost:8126",
            "validation": "http://localhost:8127",
            "monitoring": "http://localhost:8125", 
            "a2a_server": "http://localhost:8200",
            "googleai_agent": "http://localhost:8213"
        }
        
        self.service_status = {}
        logger.info("Unified Bridge initialized")
    
    def check_services_health(self):
        """Verificar salud de todos los servicios"""
        for service_name, url in self.services.items():
            try:
                response = requests.get(f"{url}/health", timeout=5)
                self.service_status[service_name] = {
                    "status": "healthy" if response.status_code == 200 else "unhealthy",
                    "url": url,
                    "last_check": datetime.now().isoformat()
                }
            except Exception as e:
                self.service_status[service_name] = {
                    "status": "offline",
                    "url": url,
                    "error": str(e),
                    "last_check": datetime.now().isoformat()
                }
        
        return self.service_status
    
    def route_request(self, service: str, endpoint: str, method: str = "GET", data: dict = None):
        """Enrutar request al servicio apropiado"""
        if service not in self.services:
            return {"error": f"Service {service} not found"}, 404
        
        service_url = self.services[service]
        url = f"{service_url}{endpoint}"
        
        try:
            if method == "GET":
                response = requests.get(url, timeout=30)
            elif method == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                return {"error": f"Method {method} not supported"}, 405
            
            return response.json(), response.status_code
            
        except Exception as e:
            logger.error(f"Error routing to {service}: {e}")
            return {"error": str(e)}, 500

# Instancia global del bridge
bridge = UnifiedBridge()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check del bridge unificado"""
    services_health = bridge.check_services_health()
    healthy_count = sum(1 for s in services_health.values() if s["status"] == "healthy")
    
    return jsonify({
        "bridge_status": "healthy",
        "services_healthy": f"{healthy_count}/{len(services_health)}",
        "services": services_health,
        "timestamp": datetime.now().isoformat()
    })

@app.route('/api/<service>/<path:endpoint>', methods=['GET', 'POST'])
def unified_api(service, endpoint):
    """API unificada para todos los servicios"""
    method = request.method
    data = request.get_json() if method == "POST" else None
    
    # Agregar prefijo /api si no existe
    if not endpoint.startswith('/'):
        endpoint = '/' + endpoint
    if not endpoint.startswith('/api') and service in ['validation', 'monitoring']:
        endpoint = '/api' + endpoint
    
    result, status_code = bridge.route_request(service, endpoint, method, data)
    return jsonify(result), status_code

@app.route('/a2a/delegate', methods=['POST'])
def delegate_a2a_task():
    """Delegación A2A a través del bridge"""
    task_data = request.get_json()
    
    if not task_data:
        return jsonify({"error": "No task data provided"}), 400
    
    # Enrutar al servidor A2A
    result, status_code = bridge.route_request("a2a_server", "/a2a/delegate", "POST", task_data)
    return jsonify(result), status_code

@app.route('/googleai/execute', methods=['POST'])
def execute_googleai():
    """Ejecutar tarea en GoogleAI Agent"""
    task_data = request.get_json()
    
    if not task_data:
        return jsonify({"error": "No task data provided"}), 400
    
    # Enrutar al agente GoogleAI
    result, status_code = bridge.route_request("googleai_agent", "/a2a/execute", "POST", task_data)
    return jsonify(result), status_code

@app.route('/dashboard')
def dashboard_redirect():
    """Redirect al dashboard enterprise"""
    return redirect("http://localhost:8126/dashboard")

@app.route('/monitoring')
def monitoring_redirect():
    """Redirect al monitoreo enterprise"""
    return redirect("http://localhost:8125/monitor")

@app.route('/validation')
def validation_redirect():
    """Redirect a validación enterprise"""
    return redirect("http://localhost:8127")

@app.route('/a2a')
def a2a_redirect():
    """Redirect al servidor A2A"""
    return redirect("http://localhost:8200")

@app.route('/')
def index():
    """Página principal del bridge unificado"""
    return jsonify({
        "service": "SuperMCP Unified Bridge",
        "version": "1.0.0",
        "description": "Gateway único para todos los servicios SuperMCP",
        "endpoints": {
            "health": "/health",
            "unified_api": "/api/<service>/<endpoint>",
            "a2a_delegation": "/a2a/delegate",
            "googleai_execution": "/googleai/execute"
        },
        "services": list(bridge.services.keys()),
        "redirects": {
            "dashboard": "/dashboard",
            "monitoring": "/monitoring", 
            "validation": "/validation",
            "a2a": "/a2a"
        },
        "timestamp": datetime.now().isoformat()
    })

if __name__ == "__main__":
    print("🌐 STARTING SUPERMCP UNIFIED BRIDGE")
    print("===================================")
    print("🔗 Single gateway for all SuperMCP services")
    print("🌟 Unified API: http://localhost:9000")
    print("")
    print("🎯 Services Integrated:")
    for service, url in bridge.services.items():
        print(f"  • {service}: {url}")
    print("")
    print("📋 Quick Access:")
    print("  • Dashboard:  http://localhost:9000/dashboard")
    print("  • Monitoring: http://localhost:9000/monitoring")
    print("  • A2A Server: http://localhost:9000/a2a")
    print("  • Health:     http://localhost:9000/health")
    print("")
    
    app.run(host='0.0.0.0', port=9000, debug=False)
