#!/usr/bin/env python3
"""
🎪 SAM.CHAT ←→ Swarm Intelligence Gateway
Provides seamless integration between sam.chat and the SuperMCP Swarm Intelligence System

Features:
- Natural language interface to swarm
- Real-time swarm status updates  
- Task delegation to appropriate agents
- Consensus facilitation
- Unified access to all swarm capabilities
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Any, Optional
from flask import Flask, request, jsonify
from flask_cors import CORS
import websockets
import threading
import time
from dataclasses import asdict
from swarm_intelligence_system import SwarmMessage, MessageType, AgentType, SwarmAgentClient

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

class SamChatSwarmGateway:
    """Gateway for sam.chat to interact with swarm intelligence"""
    
    def __init__(self, swarm_port: int = 8400, gateway_port: int = 8402):
        self.swarm_port = swarm_port
        self.gateway_port = gateway_port
        self.websocket = None
        self.connected = False
        
        # Load configuration
        self.config = self._load_config()
        
        # Gateway state
        self.swarm_status = {}
        self.active_tasks = {}
        self.recent_activities = []
        self.agent_capabilities = {}
        
        # Connect to swarm
        self.connection_thread = threading.Thread(target=self._start_swarm_connection, daemon=True)
        self.connection_thread.start()
    
    def _load_config(self) -> Dict[str, Any]:
        """Load sam.chat swarm configuration"""
        try:
            with open('sam_chat_swarm_config.json', 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return {}
    
    def _start_swarm_connection(self):
        """Start connection to swarm in background thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._connect_to_swarm())
    
    async def _connect_to_swarm(self):
        """Connect to swarm as sam.chat gateway agent"""
        while True:
            try:
                self.websocket = await websockets.connect(f"ws://sam.chat:{self.swarm_port}")
                
                # Register as sam.chat gateway
                registration = {
                    "agent_id": "sam_chat_gateway",
                    "agent_info": {
                        "name": "SAM.CHAT Gateway",
                        "type": "communication",
                        "role": "bridge",
                        "capabilities": [
                            "natural_language_interface",
                            "swarm_coordination", 
                            "task_delegation",
                            "real_time_monitoring",
                            "consensus_facilitation",
                            "external_integration"
                        ],
                        "specialization_scores": {
                            "communication": 0.95,
                            "coordination": 0.9,
                            "integration": 0.95
                        }
                    }
                }
                
                await self.websocket.send(json.dumps(registration))
                self.connected = True
                logger.info("🌉 SAM.CHAT Gateway connected to swarm")
                
                # Start monitoring swarm messages
                async for message_data in self.websocket:
                    await self._process_swarm_message(message_data)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info("🔌 SAM.CHAT Gateway disconnected from swarm")
                self.connected = False
            except Exception as e:
                logger.error(f"❌ Gateway connection error: {e}")
                self.connected = False
            
            # Retry connection
            await asyncio.sleep(5)
    
    async def _process_swarm_message(self, message_data: str):
        """Process messages from swarm"""
        try:
            message = json.loads(message_data)
            
            # Store recent activity
            activity = {
                "timestamp": datetime.now().isoformat(),
                "type": message.get("message_type", "unknown"),
                "sender": message.get("sender_id", "unknown"),
                "content": message.get("content", {})
            }
            
            self.recent_activities.append(activity)
            
            # Keep only last 100 activities
            if len(self.recent_activities) > 100:
                self.recent_activities.pop(0)
            
            # Update swarm status based on message
            await self._update_swarm_status(message)
            
        except Exception as e:
            logger.error(f"Error processing swarm message: {e}")
    
    async def _update_swarm_status(self, message: Dict[str, Any]):
        """Update swarm status from message"""
        content = message.get("content", {})
        msg_type = content.get("type")
        sender = message.get("sender_id")
        
        if msg_type == "agent_joined":
            agent_id = content.get("agent_id")
            agent_name = content.get("agent_name")
            capabilities = content.get("capabilities", [])
            
            self.agent_capabilities[agent_id] = {
                "name": agent_name,
                "capabilities": capabilities,
                "status": "active",
                "last_seen": datetime.now().isoformat()
            }
        
        elif msg_type == "agent_disconnected":
            agent_id = content.get("agent_id")
            if agent_id in self.agent_capabilities:
                self.agent_capabilities[agent_id]["status"] = "disconnected"
        
        elif msg_type == "task_assignment":
            task = content.get("task", {})
            task_id = task.get("id")
            if task_id:
                self.active_tasks[task_id] = {
                    **task,
                    "assigned_at": datetime.now().isoformat(),
                    "status": "active"
                }
        
        elif msg_type == "task_progress":
            task_id = content.get("task_id")
            if task_id in self.active_tasks:
                self.active_tasks[task_id]["progress"] = content.get("progress", 0)
                self.active_tasks[task_id]["status"] = content.get("status", "active")
    
    async def send_to_swarm(self, message: SwarmMessage):
        """Send message to swarm"""
        if self.websocket and self.connected:
            try:
                await self.websocket.send(json.dumps(asdict(message)))
                return True
            except Exception as e:
                logger.error(f"Error sending to swarm: {e}")
                return False
        return False
    
    def process_natural_language_request(self, user_input: str) -> Dict[str, Any]:
        """Process natural language request and convert to swarm action"""
        user_input = user_input.lower().strip()
        
        # Command patterns
        if user_input.startswith('/swarm-status') or 'swarm status' in user_input:
            return self.get_swarm_status()
        
        elif user_input.startswith('/swarm-agents') or 'list agents' in user_input:
            return self.get_agent_list()
        
        elif user_input.startswith('/swarm-task') or 'assign task' in user_input:
            task_description = user_input.replace('/swarm-task', '').replace('assign task', '').strip()
            return self.create_swarm_task(task_description)
        
        elif user_input.startswith('/swarm-consensus'):
            proposal = user_input.replace('/swarm-consensus', '').strip()
            return self.start_consensus(proposal)
        
        elif 'analyze' in user_input and ('market' in user_input or 'data' in user_input):
            return self.create_analysis_task(user_input)
        
        elif 'search' in user_input or 'find' in user_input:
            return self.create_search_task(user_input)
        
        elif 'help' in user_input or 'what can' in user_input:
            return self.get_help_info()
        
        else:
            # General task delegation
            return self.create_general_task(user_input)
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status"""
        active_agents = sum(1 for agent in self.agent_capabilities.values() if agent["status"] == "active")
        active_tasks = sum(1 for task in self.active_tasks.values() if task["status"] == "active")
        
        return {
            "success": True,
            "data": {
                "connection_status": "connected" if self.connected else "disconnected",
                "total_agents": len(self.agent_capabilities),
                "active_agents": active_agents,
                "active_tasks": active_tasks,
                "recent_activities": len(self.recent_activities),
                "swarm_features": self.config.get("supermcp_swarm_config", {}).get("swarm_features", {}),
                "timestamp": datetime.now().isoformat()
            },
            "message": f"🎪 Swarm is {'online' if self.connected else 'offline'} with {active_agents} active agents"
        }
    
    def get_agent_list(self) -> Dict[str, Any]:
        """Get list of all agents and their capabilities"""
        agents_info = []
        
        for agent_id, info in self.agent_capabilities.items():
            agent_config = self.config.get("supermcp_swarm_config", {}).get("agent_manifest", {}).get(agent_id, {})
            
            agents_info.append({
                "id": agent_id,
                "name": info["name"],
                "status": info["status"],
                "capabilities": info["capabilities"],
                "specialties": agent_config.get("specialties", []),
                "role": agent_config.get("role", "unknown"),
                "sam_chat_alias": agent_config.get("sam_chat_alias", agent_id)
            })
        
        return {
            "success": True,
            "data": {
                "agents": agents_info,
                "total_count": len(agents_info),
                "active_count": sum(1 for agent in agents_info if agent["status"] == "active")
            },
            "message": f"🤖 Found {len(agents_info)} agents in the swarm"
        }
    
    def create_swarm_task(self, description: str) -> Dict[str, Any]:
        """Create a new task for the swarm"""
        if not description:
            return {
                "success": False,
                "message": "❌ Task description is required",
                "usage": "/swarm-task [description]"
            }
        
        # Analyze description to determine required capabilities
        required_capabilities = self._analyze_task_requirements(description)
        
        task_message = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id="sam_chat_gateway",
            sender_type=AgentType.COMMUNICATION,
            message_type=MessageType.PROPOSAL,
            content={
                "type": "task_execution",
                "proposal_id": str(uuid.uuid4()),
                "task": {
                    "title": f"SAM.CHAT Task: {description[:50]}...",
                    "description": description,
                    "required_capabilities": required_capabilities,
                    "complexity": 0.7,
                    "estimated_duration": 1800,
                    "priority": 7,
                    "source": "sam_chat"
                }
            },
            requires_consensus=len(required_capabilities) > 3
        )
        
        # Send to swarm (async operation, so we'll use threading)
        def send_task():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.send_to_swarm(task_message))
        
        threading.Thread(target=send_task, daemon=True).start()
        
        return {
            "success": True,
            "data": {
                "task_id": task_message.content["proposal_id"],
                "description": description,
                "required_capabilities": required_capabilities,
                "requires_consensus": task_message.requires_consensus
            },
            "message": f"📋 Task submitted to swarm. Required capabilities: {', '.join(required_capabilities)}"
        }
    
    def _analyze_task_requirements(self, description: str) -> List[str]:
        """Analyze task description to determine required capabilities"""
        description = description.lower()
        capabilities = []
        
        # Mapping keywords to capabilities
        capability_keywords = {
            "analyze": ["data_analysis", "ai_inference"],
            "search": ["search", "web_scraping"], 
            "write": ["documentation", "communication"],
            "plan": ["strategic_planning", "task_coordination"],
            "data": ["data_analysis", "metrics"],
            "web": ["web_scraping", "research"],
            "email": ["communication", "messaging"],
            "schedule": ["scheduling", "organization"],
            "memory": ["context_management", "knowledge_retrieval"],
            "ai": ["ai_inference", "reasoning"],
            "notion": ["knowledge_management", "documentation"]
        }
        
        for keyword, caps in capability_keywords.items():
            if keyword in description:
                capabilities.extend(caps)
        
        # Remove duplicates
        capabilities = list(set(capabilities))
        
        # If no specific capabilities found, use general ones
        if not capabilities:
            capabilities = ["task_execution", "problem_solving"]
        
        return capabilities
    
    def start_consensus(self, proposal: str) -> Dict[str, Any]:
        """Start consensus process on a proposal"""
        if not proposal:
            return {
                "success": False,
                "message": "❌ Proposal description is required",
                "usage": "/swarm-consensus [proposal]"
            }
        
        consensus_message = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id="sam_chat_gateway",
            sender_type=AgentType.COMMUNICATION,
            message_type=MessageType.PROPOSAL,
            content={
                "type": "consensus_request",
                "proposal_id": str(uuid.uuid4()),
                "proposal": proposal,
                "initiated_by": "sam_chat",
                "timeout_minutes": 5
            },
            requires_consensus=True
        )
        
        # Send to swarm
        def send_consensus():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.send_to_swarm(consensus_message))
        
        threading.Thread(target=send_consensus, daemon=True).start()
        
        return {
            "success": True,
            "data": {
                "consensus_id": consensus_message.content["proposal_id"],
                "proposal": proposal,
                "timeout": "5 minutes"
            },
            "message": f"🗳️ Consensus started on: {proposal}"
        }
    
    def create_analysis_task(self, request: str) -> Dict[str, Any]:
        """Create specialized analysis task"""
        return self.create_swarm_task(f"Analysis Request: {request}")
    
    def create_search_task(self, request: str) -> Dict[str, Any]:
        """Create specialized search task"""
        return self.create_swarm_task(f"Search Request: {request}")
    
    def create_general_task(self, request: str) -> Dict[str, Any]:
        """Create general task from natural language"""
        return self.create_swarm_task(request)
    
    def get_help_info(self) -> Dict[str, Any]:
        """Get help information about swarm capabilities"""
        commands = self.config.get("supermcp_swarm_config", {}).get("unified_commands", {})
        features = self.config.get("supermcp_swarm_config", {}).get("swarm_features", {})
        
        return {
            "success": True,
            "data": {
                "available_commands": commands,
                "swarm_features": features,
                "agent_count": len(self.agent_capabilities),
                "dashboard_url": "http://sam.chat:8401"
            },
            "message": "🎪 SAM.CHAT Swarm Intelligence Integration - Available commands and features listed above"
        }

# Create global gateway instance
gateway = SamChatSwarmGateway()

# REST API endpoints for sam.chat integration
@app.route('/api/swarm/status', methods=['GET'])
def api_swarm_status():
    """Get swarm status"""
    return jsonify(gateway.get_swarm_status())

@app.route('/api/swarm/agents', methods=['GET'])
def api_swarm_agents():
    """Get agent list"""
    return jsonify(gateway.get_agent_list())

@app.route('/api/swarm/tasks', methods=['POST'])
def api_swarm_tasks():
    """Create new task"""
    data = request.get_json()
    description = data.get('description', '')
    return jsonify(gateway.create_swarm_task(description))

@app.route('/api/swarm/consensus', methods=['POST'])
def api_swarm_consensus():
    """Start consensus"""
    data = request.get_json()
    proposal = data.get('proposal', '')
    return jsonify(gateway.start_consensus(proposal))

@app.route('/api/swarm/process', methods=['POST'])
def api_process_request():
    """Process natural language request"""
    data = request.get_json()
    user_input = data.get('input', '')
    return jsonify(gateway.process_natural_language_request(user_input))

@app.route('/api/swarm/dashboard', methods=['GET'])
def api_swarm_dashboard():
    """Get dashboard URL"""
    return jsonify({
        "success": True,
        "data": {
            "dashboard_url": "http://sam.chat:8401",
            "description": "Real-time swarm monitoring dashboard"
        },
        "message": "📊 Dashboard available at http://localhost:8401"
    })

@app.route('/api/swarm/logs', methods=['GET'])
def api_swarm_logs():
    """Get recent swarm activities"""
    limit = request.args.get('limit', 20, type=int)
    recent_logs = gateway.recent_activities[-limit:]
    
    return jsonify({
        "success": True,
        "data": {
            "activities": recent_logs,
            "count": len(recent_logs),
            "total_activities": len(gateway.recent_activities)
        },
        "message": f"📝 Retrieved {len(recent_logs)} recent activities"
    })

@app.route('/api/swarm/config', methods=['GET'])
def api_swarm_config():
    """Get swarm configuration"""
    return jsonify({
        "success": True,
        "data": gateway.config,
        "message": "⚙️ Swarm configuration retrieved"
    })

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "swarm_connected": gateway.connected,
        "timestamp": datetime.now().isoformat(),
        "service": "SAM.CHAT Swarm Gateway"
    })

if __name__ == "__main__":
    print("🌉 SAM.CHAT ←→ Swarm Intelligence Gateway")
    print("=" * 50)
    print("🔗 Integration Features:")
    print("   • Natural language interface to swarm")
    print("   • Real-time swarm monitoring")
    print("   • Task delegation and coordination")
    print("   • Consensus facilitation")
    print("   • Unified API access")
    print("=" * 50)
    print("🌐 Gateway API: http://sam.chat:8402")
    print("🎪 Swarm Core: ws://sam.chat:8400")
    print("📊 Dashboard: http://sam.chat:8401")
    print("=" * 50)
    print("🚀 Starting SAM.CHAT gateway server...")
    
    # Start the gateway API server
    app.run(host='0.0.0.0', port=8402, debug=False)