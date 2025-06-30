#!/usr/bin/env python3
"""
SuperMCP A2A (Agent-to-Agent) Central Server
Primera implementación MCP + A2A del mundo
"""

import asyncio
import json
import sqlite3
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import logging
import uuid

from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AgentInfo:
    """Información de un agente A2A"""
    agent_id: str
    name: str
    host: str
    port: int
    capabilities: List[str]
    status: str = "active"
    last_heartbeat: Optional[str] = None
    mcp_url: Optional[str] = None

@dataclass  
class A2ATask:
    """Tarea entre agentes"""
    task_id: str
    from_agent: str
    to_agent: str
    task_type: str
    payload: Dict[str, Any]
    status: str = "pending"
    created_at: Optional[str] = None
    completed_at: Optional[str] = None
    result: Optional[Dict] = None

class A2AServer:
    """Servidor central A2A para comunicación entre agentes"""
    
    def __init__(self, config_path: str = "configs/a2a_config.json"):
        self.config = self._load_config(config_path)
        self.db_path = self.config["a2a_server"]["db_path"]
        self.agents: Dict[str, AgentInfo] = {}
        self.tasks: Dict[str, A2ATask] = {}
        
        # Inicializar base de datos
        self._init_database()
        
        logger.info("A2A Server initialized")
    
    def _load_config(self, config_path: str) -> Dict:
        """Cargar configuración A2A"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {
                "a2a_server": {"host": "0.0.0.0", "port": 8200, "db_path": "data/a2a_agents.db"},
                "system": {"heartbeat_interval": 30, "task_timeout": 300, "max_concurrent_tasks": 100}
            }
    
    def _init_database(self):
        """Inicializar base de datos SQLite para A2A"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tabla de agentes
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS agents (
                agent_id TEXT PRIMARY KEY,
                name TEXT,
                host TEXT,
                port INTEGER,
                capabilities TEXT,
                status TEXT,
                last_heartbeat TEXT,
                mcp_url TEXT,
                registered_at TEXT
            )
        ''')
        
        # Tabla de tareas A2A
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS a2a_tasks (
                task_id TEXT PRIMARY KEY,
                from_agent TEXT,
                to_agent TEXT,
                task_type TEXT,
                payload TEXT,
                status TEXT,
                created_at TEXT,
                completed_at TEXT,
                result TEXT
            )
        ''')
        
        # Tabla de métricas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS a2a_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT,
                metric_type TEXT,
                agent_id TEXT,
                value REAL,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("A2A Database initialized")
    
    def register_agent(self, agent_info: Dict) -> bool:
        """Registrar nuevo agente en el sistema A2A"""
        try:
            agent = AgentInfo(
                agent_id=agent_info["agent_id"],
                name=agent_info["name"],
                host=agent_info["host"], 
                port=agent_info["port"],
                capabilities=agent_info["capabilities"],
                status="active",
                last_heartbeat=datetime.now().isoformat(),
                mcp_url=agent_info.get("mcp_url")
            )
            
            self.agents[agent.agent_id] = agent
            
            # Guardar en BD
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT OR REPLACE INTO agents 
                (agent_id, name, host, port, capabilities, status, last_heartbeat, mcp_url, registered_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                agent.agent_id, agent.name, agent.host, agent.port,
                json.dumps(agent.capabilities), agent.status, agent.last_heartbeat,
                agent.mcp_url, datetime.now().isoformat()
            ))
            conn.commit()
            conn.close()
            
            logger.info(f"Agent {agent.name} ({agent.agent_id}) registered successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error registering agent: {e}")
            return False
    
    def create_a2a_task(self, task_data: Dict) -> str:
        """Crear nueva tarea A2A entre agentes"""
        task_id = f"a2a_{uuid.uuid4().hex[:8]}"
        
        task = A2ATask(
            task_id=task_id,
            from_agent=task_data["from_agent"],
            to_agent=task_data["to_agent"],
            task_type=task_data["task_type"],
            payload=task_data["payload"],
            status="pending",
            created_at=datetime.now().isoformat()
        )
        
        self.tasks[task_id] = task
        
        # Guardar en BD
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO a2a_tasks 
            (task_id, from_agent, to_agent, task_type, payload, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            task.task_id, task.from_agent, task.to_agent, task.task_type,
            json.dumps(task.payload), task.status, task.created_at
        ))
        conn.commit()
        conn.close()
        
        logger.info(f"A2A Task {task_id} created: {task.from_agent} -> {task.to_agent}")
        return task_id
    
    def delegate_to_agent(self, task_id: str) -> Dict:
        """Delegar tarea a agente específico"""
        if task_id not in self.tasks:
            return {"success": False, "error": "Task not found"}
        
        task = self.tasks[task_id]
        target_agent = self.agents.get(task.to_agent)
        
        if not target_agent:
            return {"success": False, "error": f"Target agent {task.to_agent} not found"}
        
        try:
            # Enviar tarea al agente
            agent_url = f"http://{target_agent.host}:{target_agent.port}/a2a/execute"
            payload = {
                "task_id": task_id,
                "from_agent": task.from_agent,
                "task_type": task.task_type,
                "payload": task.payload
            }
            
            response = requests.post(agent_url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                task.status = "delegated"
                task.result = result
                
                logger.info(f"Task {task_id} successfully delegated to {task.to_agent}")
                return {"success": True, "result": result}
            else:
                task.status = "failed"
                logger.error(f"Failed to delegate task {task_id}: HTTP {response.status_code}")
                return {"success": False, "error": f"HTTP {response.status_code}"}
                
        except Exception as e:
            task.status = "failed"
            logger.error(f"Error delegating task {task_id}: {e}")
            return {"success": False, "error": str(e)}
    
    def get_system_status(self) -> Dict:
        """Obtener estado del sistema A2A"""
        active_agents = [a for a in self.agents.values() if a.status == "active"]
        pending_tasks = [t for t in self.tasks.values() if t.status == "pending"]
        
        return {
            "timestamp": datetime.now().isoformat(),
            "total_agents": len(self.agents),
            "active_agents": len(active_agents),
            "total_tasks": len(self.tasks),
            "pending_tasks": len(pending_tasks),
            "agents": {agent.agent_id: {"name": agent.name, "status": agent.status, "capabilities": agent.capabilities} 
                     for agent in active_agents},
            "server_uptime": "active"
        }

# Flask API para el servidor A2A
app = Flask(__name__)
CORS(app)

# Instancia global del servidor A2A
a2a_server = A2AServer()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check del servidor A2A"""
    return jsonify({
        "status": "healthy",
        "service": "SuperMCP A2A Server",
        "timestamp": datetime.now().isoformat()
    })

@app.route('/a2a/register', methods=['POST'])
def register_agent():
    """Registrar nuevo agente A2A"""
    agent_data = request.get_json()
    
    if not agent_data:
        return jsonify({"error": "No agent data provided"}), 400
    
    required_fields = ["agent_id", "name", "host", "port", "capabilities"]
    if not all(field in agent_data for field in required_fields):
        return jsonify({"error": f"Missing required fields: {required_fields}"}), 400
    
    success = a2a_server.register_agent(agent_data)
    
    if success:
        return jsonify({"success": True, "message": "Agent registered successfully"})
    else:
        return jsonify({"error": "Failed to register agent"}), 500

@app.route('/a2a/agents', methods=['GET'])
def get_agents():
    """Obtener lista de agentes registrados"""
    return jsonify({
        "agents": [asdict(agent) for agent in a2a_server.agents.values()]
    })

@app.route('/a2a/delegate', methods=['POST'])
def delegate_task():
    """Crear y delegar tarea entre agentes"""
    task_data = request.get_json()
    
    if not task_data:
        return jsonify({"error": "No task data provided"}), 400
    
    # Crear tarea A2A
    task_id = a2a_server.create_a2a_task(task_data)
    
    # Delegar inmediatamente
    result = a2a_server.delegate_to_agent(task_id)
    
    return jsonify({
        "task_id": task_id,
        "delegation_result": result
    })

@app.route('/a2a/status', methods=['GET'])
def system_status():
    """Estado del sistema A2A"""
    return jsonify(a2a_server.get_system_status())

@app.route('/a2a/tasks', methods=['GET'])
def get_tasks():
    """Obtener lista de tareas A2A"""
    return jsonify({
        "tasks": [asdict(task) for task in a2a_server.tasks.values()]
    })

if __name__ == "__main__":
    print("📡 STARTING SUPERMCP A2A SERVER")
    print("==============================")
    print("🔗 Agent-to-Agent Communication Hub")
    print("🌐 Server: http://localhost:8200")
    print("")
    print("🎯 Endpoints:")
    print("  • POST /a2a/register  - Register agent")
    print("  • GET  /a2a/agents    - List agents")
    print("  • POST /a2a/delegate  - Delegate task")
    print("  • GET  /a2a/status    - System status")
    print("  • GET  /a2a/tasks     - List tasks")
    print("")
    
    config = a2a_server.config["a2a_server"]
    app.run(host=config["host"], port=config["port"], debug=False)
