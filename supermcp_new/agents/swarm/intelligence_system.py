#!/usr/bin/env python3
"""
🎪 SuperMCP Swarm Intelligence System
Advanced peer-to-peer multi-agent coordination with emergent intelligence

Architecture:
    🎯 Manus ←→ ⚡ SAM ←→ 🧠 Memory
         ↕         ↕         ↕
    🤖 GoogleAI ←→ 📱 Notion ←→ 📧 Email
         ↕         ↕         ↕
    🌐 Web ←→ 📊 Analytics ←→ 🔍 Search

Features:
- Peer-to-peer communication between all agents
- Emergent intelligence from swarm interactions
- Auto-organization and dynamic role assignment
- Collective problem solving with consensus
- Swarm analytics and pattern recognition
"""

import asyncio
import json
import logging
import time
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional, Any, Callable, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import websockets
import threading
from collections import defaultdict, deque
import statistics
import networkx as nx
import numpy as np

# Import MCP Server Manager
from mcp.client.connection_manager import mcp_manager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AgentType(Enum):
    """Types of agents in the swarm"""
    COORDINATOR = "coordinator"      # Manus
    EXECUTOR = "executor"           # SAM
    MEMORY = "memory"              # Memory
    AI_SPECIALIST = "ai_specialist" # GoogleAI
    KNOWLEDGE = "knowledge"        # Notion
    COMMUNICATION = "communication" # Email
    WEB_AGENT = "web_agent"        # Web
    ANALYTICS = "analytics"        # Analytics
    SEARCH = "search"              # Search
    MULTIMODEL = "multimodel"      # Multi-Model Router
    # MCP Server Agents
    FILESYSTEM = "filesystem"      # File-systems MCP
    BROWSER = "browser"           # Browser-automation MCP
    DEVELOPER = "developer"       # Developer-tools MCP
    VERSION_CONTROL = "version_control" # Version-control MCP
    KNOWLEDGE_MCP = "knowledge_mcp" # Knowledge-memory MCP

class MessageType(Enum):
    """Types of messages in swarm communication"""
    BROADCAST = "broadcast"        # To all agents
    DIRECT = "direct"             # To specific agent
    MULTICAST = "multicast"       # To specific group
    QUERY = "query"               # Request for information
    RESPONSE = "response"         # Response to query
    PROPOSAL = "proposal"         # Propose action/solution
    CONSENSUS = "consensus"       # Consensus building
    HEARTBEAT = "heartbeat"       # Alive signal
    COORDINATION = "coordination" # Coordination request
    EMERGENCE = "emergence"       # Emergent behavior signal

class SwarmRole(Enum):
    """Dynamic roles in swarm"""
    LEADER = "leader"
    FOLLOWER = "follower"
    SPECIALIST = "specialist"
    COORDINATOR = "coordinator"
    OBSERVER = "observer"
    BRIDGE = "bridge"

@dataclass
class SwarmMessage:
    """Message structure for swarm communication"""
    id: str
    timestamp: str
    sender_id: str
    sender_type: AgentType
    message_type: MessageType
    content: Dict[str, Any]
    recipients: List[str] = None  # None = broadcast
    priority: int = 5  # 1-10, 1 = highest
    ttl: int = 300  # Time to live in seconds
    requires_consensus: bool = False
    metadata: Dict[str, Any] = None

@dataclass
class SwarmAgent:
    """Agent in the swarm"""
    id: str
    name: str
    agent_type: AgentType
    capabilities: List[str]
    current_role: SwarmRole
    status: str = "active"
    load: float = 0.0  # 0-1, current workload
    performance_score: float = 1.0  # Performance metric
    last_heartbeat: datetime = None
    connections: Set[str] = None  # Connected agent IDs
    reputation: float = 1.0  # Reputation in swarm
    specialization_scores: Dict[str, float] = None

@dataclass
class SwarmTask:
    """Task for swarm processing"""
    id: str
    title: str
    description: str
    requirements: List[str]
    priority: int
    complexity: float
    estimated_duration: int
    assigned_agents: List[str] = None
    status: str = "pending"
    created_at: datetime = None
    progress: float = 0.0
    results: Dict[str, Any] = None

class SwarmIntelligence:
    """Core swarm intelligence system"""
    
    def __init__(self, port: int = 8400):
        self.port = port
        self.agents: Dict[str, SwarmAgent] = {}
        self.connections: Dict[str, websockets.WebSocketServerProtocol] = {}
        self.message_history: deque = deque(maxlen=10000)
        self.tasks: Dict[str, SwarmTask] = {}
        self.swarm_graph = nx.Graph()
        
        # Swarm intelligence metrics
        self.intelligence_metrics = {
            "coordination_efficiency": 0.0,
            "consensus_speed": 0.0,
            "task_completion_rate": 0.0,
            "emergent_behaviors": 0,
            "swarm_coherence": 0.0,
            "collective_iq": 0.0
        }
        
        # Consensus tracking
        self.consensus_sessions: Dict[str, Dict] = {}
        
        # Pattern recognition
        self.behavior_patterns: Dict[str, Any] = {}
        self.emergence_detector = EmergenceDetector()
        
        # Auto-organization
        self.role_optimizer = RoleOptimizer()
        
        # Start swarm
        self.running = False
    
    async def initialize_mcp_agents(self):
        """Initialize MCP-based swarm agents"""
        logger.info("🤖 Initializing MCP-based swarm agents...")
        
        # Get MCP server capabilities
        mcp_capabilities = mcp_manager.get_all_capabilities()
        
        # Create swarm agents for each MCP server
        mcp_agent_configs = {
            "filesystem": {
                "id": "mcp_filesystem_agent",
                "name": "FileSystem Agent",
                "type": AgentType.FILESYSTEM,
                "capabilities": mcp_capabilities.get("filesystem", []),
                "role": SwarmRole.SPECIALIST,
                "specialization_scores": {"file_management": 1.0, "data_storage": 0.9}
            },
            "browser": {
                "id": "mcp_browser_agent", 
                "name": "Browser Agent",
                "type": AgentType.BROWSER,
                "capabilities": mcp_capabilities.get("browser", []),
                "role": SwarmRole.SPECIALIST,
                "specialization_scores": {"web_automation": 1.0, "data_scraping": 0.9}
            },
            "knowledge": {
                "id": "mcp_knowledge_agent",
                "name": "Knowledge Agent", 
                "type": AgentType.KNOWLEDGE_MCP,
                "capabilities": mcp_capabilities.get("knowledge", []),
                "role": SwarmRole.SPECIALIST,
                "specialization_scores": {"memory_management": 1.0, "knowledge_base": 0.9}
            },
            "developer": {
                "id": "mcp_developer_agent",
                "name": "Developer Agent",
                "type": AgentType.DEVELOPER,
                "capabilities": mcp_capabilities.get("developer", []),
                "role": SwarmRole.SPECIALIST,
                "specialization_scores": {"code_tools": 1.0, "development": 0.9}
            },
            "version_control": {
                "id": "mcp_version_control_agent",
                "name": "Version Control Agent",
                "type": AgentType.VERSION_CONTROL,
                "capabilities": mcp_capabilities.get("version_control", []),
                "role": SwarmRole.SPECIALIST,
                "specialization_scores": {"git_operations": 1.0, "repository_management": 0.9}
            },
            "search": {
                "id": "mcp_search_agent",
                "name": "Search Agent",
                "type": AgentType.SEARCH,
                "capabilities": mcp_capabilities.get("search", []),
                "role": SwarmRole.SPECIALIST,
                "specialization_scores": {"search_indexing": 1.0, "semantic_search": 0.9}
            }
        }
        
        # Register MCP agents in the swarm
        for server_type, config in mcp_agent_configs.items():
            agent = SwarmAgent(
                id=config["id"],
                name=config["name"],
                agent_type=config["type"],
                capabilities=config["capabilities"],
                current_role=config["role"],
                connections=set(),
                specialization_scores=config["specialization_scores"],
                performance_score=1.0,
                last_heartbeat=datetime.now()
            )
            
            self.agents[config["id"]] = agent
            self.swarm_graph.add_node(config["id"], **asdict(agent))
            
            logger.info(f"🔗 Registered MCP agent: {config['name']} ({server_type})")
        
        logger.info(f"✅ Initialized {len(mcp_agent_configs)} MCP-based swarm agents")
    
    async def handle_mcp_request(self, server_type: str, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP request through swarm intelligence"""
        from mcp_server_manager import MCPRequest
        
        # Create MCP request
        request = MCPRequest(
            id=str(uuid.uuid4()),
            method=method,
            params=params
        )
        
        # Route to appropriate MCP server
        response = await mcp_manager.route_request(server_type, request)
        
        # Log the interaction for swarm intelligence
        mcp_message = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id=f"mcp_{server_type}_agent",
            sender_type=AgentType[server_type.upper()] if hasattr(AgentType, server_type.upper()) else AgentType.COORDINATOR,
            message_type=MessageType.RESPONSE,
            content={
                "type": "mcp_operation",
                "server_type": server_type,
                "method": method,
                "success": response.error is None,
                "result_summary": str(response.result)[:100] if response.result else None
            }
        )
        
        # Store in message history for intelligence analysis
        self.message_history.append(mcp_message)
        
        return {
            "success": response.error is None,
            "result": response.result,
            "error": response.error
        }
        
    async def start_swarm(self):
        """Start the swarm intelligence system"""
        logger.info("🎪 Starting SuperMCP Swarm Intelligence System")
        self.running = True
        
        # Start MCP Server Manager
        logger.info("🔗 Starting MCP Server Manager...")
        await mcp_manager.start_all_servers()
        
        # Initialize MCP-based swarm agents
        await self.initialize_mcp_agents()
        
        # Start WebSocket server for P2P communication
        start_server = websockets.serve(
            self.handle_agent_connection, 
            "0.0.0.0", 
            self.port
        )
        
        logger.info(f"🌐 Swarm communication server started on port {self.port}")
        
        # Start background tasks
        asyncio.create_task(self.swarm_maintenance())
        asyncio.create_task(self.emergent_intelligence_monitor())
        asyncio.create_task(self.role_optimization_loop())
        asyncio.create_task(self.consensus_manager())
        
        await start_server
        
    async def handle_agent_connection(self, websocket, path):
        """Handle new agent connection"""
        agent_id = None
        try:
            # Wait for agent registration
            registration_msg = await websocket.recv()
            registration = json.loads(registration_msg)
            
            agent_id = registration["agent_id"]
            agent_info = registration["agent_info"]
            
            # Register agent
            agent = SwarmAgent(
                id=agent_id,
                name=agent_info["name"],
                agent_type=AgentType(agent_info["type"]),
                capabilities=agent_info["capabilities"],
                current_role=SwarmRole(agent_info.get("role", "follower")),
                connections=set(),
                specialization_scores=agent_info.get("specialization_scores", {})
            )
            
            self.agents[agent_id] = agent
            self.connections[agent_id] = websocket
            self.swarm_graph.add_node(agent_id, **asdict(agent))
            
            logger.info(f"🤖 Agent {agent_id} ({agent.name}) joined swarm")
            
            # Send welcome message with swarm status
            welcome_msg = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.DIRECT,
                content={
                    "type": "welcome",
                    "swarm_status": self.get_swarm_status(),
                    "your_role": agent.current_role.value,
                    "connected_agents": list(self.agents.keys())
                },
                recipients=[agent_id]
            )
            await self.send_message(welcome_msg)
            
            # Broadcast new agent announcement
            announcement = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.BROADCAST,
                content={
                    "type": "agent_joined",
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "agent_type": agent.agent_type.value,
                    "capabilities": agent.capabilities
                }
            )
            await self.broadcast_message(announcement)
            
            # Handle messages from this agent
            async for message_data in websocket:
                await self.process_agent_message(agent_id, message_data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Agent {agent_id} disconnected")
        except Exception as e:
            logger.error(f"❌ Error handling agent {agent_id}: {e}")
        finally:
            if agent_id and agent_id in self.agents:
                await self.handle_agent_disconnect(agent_id)
    
    async def process_agent_message(self, sender_id: str, message_data: str):
        """Process message from agent"""
        try:
            message_dict = json.loads(message_data)
            message = SwarmMessage(**message_dict)
            message.sender_id = sender_id  # Ensure sender is correct
            
            # Update agent heartbeat
            if sender_id in self.agents:
                self.agents[sender_id].last_heartbeat = datetime.now()
            
            # Store message in history
            self.message_history.append(message)
            
            # Process based on message type
            if message.message_type == MessageType.BROADCAST:
                await self.handle_broadcast(message)
            elif message.message_type == MessageType.DIRECT:
                await self.handle_direct_message(message)
            elif message.message_type == MessageType.QUERY:
                await self.handle_query(message)
            elif message.message_type == MessageType.PROPOSAL:
                await self.handle_proposal(message)
            elif message.message_type == MessageType.CONSENSUS:
                await self.handle_consensus_message(message)
            elif message.message_type == MessageType.COORDINATION:
                await self.handle_coordination_request(message)
            
            # Detect emergent behaviors
            await self.emergence_detector.analyze_message(message, self.agents)
            
            logger.debug(f"📨 Processed {message.message_type.value} from {sender_id}")
            
        except Exception as e:
            logger.error(f"❌ Error processing message from {sender_id}: {e}")
    
    async def handle_broadcast(self, message: SwarmMessage):
        """Handle broadcast message"""
        # Forward to all agents except sender
        for agent_id, websocket in self.connections.items():
            if agent_id != message.sender_id:
                try:
                    await websocket.send(json.dumps(asdict(message)))
                except Exception as e:
                    logger.error(f"Error broadcasting to {agent_id}: {e}")
    
    async def handle_direct_message(self, message: SwarmMessage):
        """Handle direct message"""
        if message.recipients:
            for recipient_id in message.recipients:
                if recipient_id in self.connections:
                    try:
                        await self.connections[recipient_id].send(
                            json.dumps(asdict(message))
                        )
                    except Exception as e:
                        logger.error(f"Error sending direct message to {recipient_id}: {e}")
    
    async def handle_query(self, message: SwarmMessage):
        """Handle query message"""
        query_content = message.content
        query_type = query_content.get("query_type")
        
        if query_type == "capability_match":
            # Find agents with required capabilities
            required_caps = query_content.get("required_capabilities", [])
            matching_agents = self.find_agents_by_capability(required_caps)
            
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "query_id": message.id,
                    "matching_agents": matching_agents,
                    "total_matches": len(matching_agents)
                },
                recipients=[message.sender_id]
            )
            await self.send_message(response)
        
        elif query_type == "swarm_status":
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "query_id": message.id,
                    "swarm_status": self.get_swarm_status(),
                    "intelligence_metrics": self.intelligence_metrics
                },
                recipients=[message.sender_id]
            )
            await self.send_message(response)
    
    async def handle_proposal(self, message: SwarmMessage):
        """Handle proposal message"""
        proposal = message.content
        proposal_id = proposal.get("proposal_id", message.id)
        
        # If proposal requires consensus, start consensus process
        if message.requires_consensus:
            await self.start_consensus_session(proposal_id, message)
        else:
            # Direct execution or forwarding
            await self.execute_proposal(proposal)
    
    async def handle_consensus_message(self, message: SwarmMessage):
        """Handle consensus building message"""
        consensus_data = message.content
        session_id = consensus_data.get("session_id")
        
        if session_id in self.consensus_sessions:
            session = self.consensus_sessions[session_id]
            
            # Record vote/opinion
            session["votes"][message.sender_id] = consensus_data.get("vote")
            session["opinions"][message.sender_id] = consensus_data.get("opinion", "")
            
            # Check if consensus reached
            if len(session["votes"]) >= session["required_participants"]:
                consensus_result = self.calculate_consensus(session)
                await self.finalize_consensus(session_id, consensus_result)
    
    async def handle_coordination_request(self, message: SwarmMessage):
        """Handle coordination request"""
        coord_request = message.content
        request_type = coord_request.get("type")
        
        if request_type == "task_assignment":
            task_info = coord_request.get("task")
            optimal_agents = await self.find_optimal_agents_for_task(task_info)
            
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "request_id": message.id,
                    "optimal_agents": optimal_agents,
                    "coordination_plan": await self.create_coordination_plan(task_info, optimal_agents)
                },
                recipients=[message.sender_id]
            )
            await self.send_message(response)
        
        elif request_type == "role_optimization":
            await self.role_optimizer.optimize_roles(self.agents, self.swarm_graph)
    
    async def start_consensus_session(self, proposal_id: str, proposal_message: SwarmMessage):
        """Start consensus building session"""
        session_id = str(uuid.uuid4())
        
        # Determine required participants based on proposal
        proposal_content = proposal_message.content
        required_participants = proposal_content.get("required_participants", len(self.agents))
        
        session = {
            "id": session_id,
            "proposal_id": proposal_id,
            "proposal": proposal_message,
            "required_participants": min(required_participants, len(self.agents)),
            "votes": {},
            "opinions": {},
            "started_at": datetime.now(),
            "timeout": datetime.now() + timedelta(minutes=5)
        }
        
        self.consensus_sessions[session_id] = session
        
        # Broadcast consensus request
        consensus_request = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id="swarm_core",
            sender_type=AgentType.COORDINATOR,
            message_type=MessageType.CONSENSUS,
            content={
                "session_id": session_id,
                "proposal": proposal_content,
                "action": "vote_request",
                "timeout": session["timeout"].isoformat()
            }
        )
        await self.broadcast_message(consensus_request)
        
        logger.info(f"🗳️ Started consensus session {session_id} for proposal {proposal_id}")
    
    def calculate_consensus(self, session: Dict) -> Dict[str, Any]:
        """Calculate consensus from votes"""
        votes = session["votes"]
        opinions = session["opinions"]
        
        # Simple majority voting
        positive_votes = sum(1 for vote in votes.values() if vote == "approve")
        total_votes = len(votes)
        
        consensus_reached = positive_votes > total_votes / 2
        confidence = positive_votes / total_votes if total_votes > 0 else 0
        
        return {
            "consensus_reached": consensus_reached,
            "confidence": confidence,
            "positive_votes": positive_votes,
            "total_votes": total_votes,
            "opinions_summary": list(opinions.values())
        }
    
    async def finalize_consensus(self, session_id: str, consensus_result: Dict[str, Any]):
        """Finalize consensus and execute if approved"""
        session = self.consensus_sessions[session_id]
        
        # Broadcast consensus result
        result_message = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id="swarm_core",
            sender_type=AgentType.COORDINATOR,
            message_type=MessageType.CONSENSUS,
            content={
                "session_id": session_id,
                "action": "consensus_result",
                "result": consensus_result,
                "will_execute": consensus_result["consensus_reached"]
            }
        )
        await self.broadcast_message(result_message)
        
        # Execute if consensus reached
        if consensus_result["consensus_reached"]:
            await self.execute_proposal(session["proposal"].content)
        
        # Update intelligence metrics
        self.intelligence_metrics["consensus_speed"] = self.calculate_consensus_speed(session)
        
        # Clean up session
        del self.consensus_sessions[session_id]
        
        logger.info(f"✅ Consensus session {session_id} finalized: {consensus_result['consensus_reached']}")
    
    def find_agents_by_capability(self, required_capabilities: List[str]) -> List[Dict[str, Any]]:
        """Find agents that match required capabilities"""
        matching_agents = []
        
        for agent_id, agent in self.agents.items():
            match_score = 0
            for cap in required_capabilities:
                if cap in agent.capabilities:
                    match_score += 1
            
            if match_score > 0:
                matching_agents.append({
                    "agent_id": agent_id,
                    "agent_name": agent.name,
                    "agent_type": agent.agent_type.value,
                    "match_score": match_score / len(required_capabilities),
                    "current_load": agent.load,
                    "performance_score": agent.performance_score
                })
        
        # Sort by match score and performance
        matching_agents.sort(key=lambda x: (x["match_score"], x["performance_score"]), reverse=True)
        return matching_agents
    
    async def find_optimal_agents_for_task(self, task_info: Dict[str, Any]) -> List[str]:
        """Find optimal agents for a specific task"""
        required_caps = task_info.get("required_capabilities", [])
        task_complexity = task_info.get("complexity", 0.5)
        
        # Find capable agents
        candidates = self.find_agents_by_capability(required_caps)
        
        # Filter by load and complexity handling
        optimal_agents = []
        for candidate in candidates:
            agent = self.agents[candidate["agent_id"]]
            
            # Check if agent can handle complexity
            if agent.performance_score >= task_complexity and agent.load < 0.8:
                optimal_agents.append(candidate["agent_id"])
        
        return optimal_agents[:3]  # Return top 3 agents
    
    async def create_coordination_plan(self, task_info: Dict[str, Any], assigned_agents: List[str]) -> Dict[str, Any]:
        """Create coordination plan for task execution"""
        plan = {
            "task_id": str(uuid.uuid4()),
            "assigned_agents": assigned_agents,
            "coordination_strategy": "collaborative",
            "communication_pattern": "mesh",
            "phases": []
        }
        
        # Create phases based on task complexity
        if len(assigned_agents) > 1:
            plan["phases"] = [
                {
                    "phase": "planning",
                    "lead_agent": assigned_agents[0],
                    "participants": assigned_agents,
                    "duration_estimate": "5 minutes"
                },
                {
                    "phase": "execution",
                    "lead_agent": assigned_agents[0],
                    "participants": assigned_agents,
                    "duration_estimate": task_info.get("estimated_duration", "30 minutes")
                },
                {
                    "phase": "review",
                    "lead_agent": assigned_agents[0],
                    "participants": assigned_agents,
                    "duration_estimate": "10 minutes"
                }
            ]
        
        return plan
    
    async def execute_proposal(self, proposal: Dict[str, Any]):
        """Execute approved proposal"""
        proposal_type = proposal.get("type")
        
        if proposal_type == "task_execution":
            task_data = proposal.get("task")
            await self.create_and_assign_task(task_data)
        elif proposal_type == "role_change":
            agent_id = proposal.get("agent_id")
            new_role = proposal.get("new_role")
            await self.change_agent_role(agent_id, new_role)
        elif proposal_type == "swarm_reconfiguration":
            config_changes = proposal.get("changes")
            await self.reconfigure_swarm(config_changes)
        
        logger.info(f"🔧 Executed proposal: {proposal_type}")
    
    async def create_and_assign_task(self, task_data: Dict[str, Any]):
        """Create and assign task to swarm"""
        task = SwarmTask(
            id=str(uuid.uuid4()),
            title=task_data.get("title", "Swarm Task"),
            description=task_data.get("description", ""),
            requirements=task_data.get("requirements", []),
            priority=task_data.get("priority", 5),
            complexity=task_data.get("complexity", 0.5),
            estimated_duration=task_data.get("estimated_duration", 1800),
            created_at=datetime.now()
        )
        
        # Find optimal agents
        optimal_agents = await self.find_optimal_agents_for_task(task_data)
        task.assigned_agents = optimal_agents
        
        # Store task
        self.tasks[task.id] = task
        
        # Notify assigned agents
        if optimal_agents:
            task_assignment = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.DIRECT,
                content={
                    "type": "task_assignment",
                    "task": asdict(task),
                    "coordination_plan": await self.create_coordination_plan(task_data, optimal_agents)
                },
                recipients=optimal_agents
            )
            await self.send_message(task_assignment)
        
        logger.info(f"📋 Created and assigned task {task.id} to {len(optimal_agents)} agents")
    
    def get_swarm_status(self) -> Dict[str, Any]:
        """Get current swarm status"""
        active_agents = sum(1 for agent in self.agents.values() if agent.status == "active")
        avg_load = statistics.mean([agent.load for agent in self.agents.values()]) if self.agents else 0
        
        return {
            "total_agents": len(self.agents),
            "active_agents": active_agents,
            "average_load": avg_load,
            "intelligence_metrics": self.intelligence_metrics,
            "active_tasks": len([task for task in self.tasks.values() if task.status != "completed"]),
            "message_rate": len(self.message_history) / 3600,  # messages per hour
            "swarm_coherence": self.calculate_swarm_coherence()
        }
    
    def calculate_swarm_coherence(self) -> float:
        """Calculate how coherent the swarm is"""
        if len(self.agents) < 2:
            return 1.0
        
        # Based on communication patterns and role distribution
        communication_density = self.swarm_graph.number_of_edges() / max(1, (len(self.agents) * (len(self.agents) - 1) / 2))
        role_diversity = len(set(agent.current_role for agent in self.agents.values())) / len(SwarmRole)
        
        coherence = (communication_density + role_diversity) / 2
        return min(1.0, coherence)
    
    def calculate_consensus_speed(self, session: Dict) -> float:
        """Calculate consensus speed metric"""
        duration = (datetime.now() - session["started_at"]).total_seconds()
        return max(0.1, 1.0 / duration)  # Faster consensus = higher score
    
    async def send_message(self, message: SwarmMessage):
        """Send message to specified recipients"""
        if message.recipients:
            for recipient_id in message.recipients:
                if recipient_id in self.connections:
                    try:
                        await self.connections[recipient_id].send(
                            json.dumps(asdict(message))
                        )
                    except Exception as e:
                        logger.error(f"Error sending message to {recipient_id}: {e}")
    
    async def broadcast_message(self, message: SwarmMessage):
        """Broadcast message to all agents"""
        for agent_id, websocket in self.connections.items():
            try:
                await websocket.send(json.dumps(asdict(message)))
            except Exception as e:
                logger.error(f"Error broadcasting to {agent_id}: {e}")
    
    async def handle_agent_disconnect(self, agent_id: str):
        """Handle agent disconnection"""
        if agent_id in self.agents:
            agent = self.agents[agent_id]
            agent.status = "disconnected"
            
            # Remove from connections
            if agent_id in self.connections:
                del self.connections[agent_id]
            
            # Update swarm graph
            self.swarm_graph.remove_node(agent_id)
            
            # Broadcast disconnection
            disconnect_msg = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.BROADCAST,
                content={
                    "type": "agent_disconnected",
                    "agent_id": agent_id,
                    "agent_name": agent.name
                }
            )
            await self.broadcast_message(disconnect_msg)
            
            # Reassign tasks if needed
            await self.reassign_agent_tasks(agent_id)
            
            logger.info(f"🔌 Agent {agent_id} disconnected and cleaned up")
    
    async def reassign_agent_tasks(self, disconnected_agent_id: str):
        """Reassign tasks from disconnected agent"""
        for task in self.tasks.values():
            if task.assigned_agents and disconnected_agent_id in task.assigned_agents:
                task.assigned_agents.remove(disconnected_agent_id)
                
                # Find replacement agent
                replacement_agents = await self.find_optimal_agents_for_task({
                    "required_capabilities": task.requirements,
                    "complexity": task.complexity
                })
                
                if replacement_agents:
                    task.assigned_agents.extend(replacement_agents[:1])
                    
                    # Notify new agent
                    reassignment_msg = SwarmMessage(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now().isoformat(),
                        sender_id="swarm_core",
                        sender_type=AgentType.COORDINATOR,
                        message_type=MessageType.DIRECT,
                        content={
                            "type": "task_reassignment",
                            "task": asdict(task),
                            "reason": f"Agent {disconnected_agent_id} disconnected"
                        },
                        recipients=replacement_agents[:1]
                    )
                    await self.send_message(reassignment_msg)
    
    async def swarm_maintenance(self):
        """Periodic swarm maintenance tasks"""
        while self.running:
            try:
                # Check agent heartbeats
                current_time = datetime.now()
                stale_agents = []
                
                for agent_id, agent in self.agents.items():
                    if agent.last_heartbeat:
                        time_since_heartbeat = current_time - agent.last_heartbeat
                        if time_since_heartbeat.total_seconds() > 300:  # 5 minutes
                            stale_agents.append(agent_id)
                
                # Disconnect stale agents
                for agent_id in stale_agents:
                    await self.handle_agent_disconnect(agent_id)
                
                # Update intelligence metrics
                await self.update_intelligence_metrics()
                
                # Clean up old messages
                self.cleanup_old_data()
                
                await asyncio.sleep(60)  # Run every minute
                
            except Exception as e:
                logger.error(f"Error in swarm maintenance: {e}")
                await asyncio.sleep(10)
    
    async def update_intelligence_metrics(self):
        """Update swarm intelligence metrics"""
        if not self.agents:
            return
        
        # Coordination efficiency
        active_tasks = [task for task in self.tasks.values() if task.status == "active"]
        completed_tasks = [task for task in self.tasks.values() if task.status == "completed"]
        
        if len(active_tasks) + len(completed_tasks) > 0:
            self.intelligence_metrics["task_completion_rate"] = len(completed_tasks) / (len(active_tasks) + len(completed_tasks))
        
        # Swarm coherence
        self.intelligence_metrics["swarm_coherence"] = self.calculate_swarm_coherence()
        
        # Collective IQ (based on performance and coordination)
        avg_performance = statistics.mean([agent.performance_score for agent in self.agents.values()])
        coordination_factor = min(1.0, len(self.swarm_graph.edges()) / len(self.agents))
        
        self.intelligence_metrics["collective_iq"] = (avg_performance + coordination_factor + self.intelligence_metrics["swarm_coherence"]) / 3
    
    def cleanup_old_data(self):
        """Clean up old data"""
        current_time = datetime.now()
        
        # Clean up old consensus sessions
        expired_sessions = []
        for session_id, session in self.consensus_sessions.items():
            if current_time > session["timeout"]:
                expired_sessions.append(session_id)
        
        for session_id in expired_sessions:
            del self.consensus_sessions[session_id]
        
        # Clean up completed tasks older than 24 hours
        old_tasks = []
        for task_id, task in self.tasks.items():
            if (task.status == "completed" and 
                task.created_at and 
                current_time - task.created_at > timedelta(hours=24)):
                old_tasks.append(task_id)
        
        for task_id in old_tasks:
            del self.tasks[task_id]
    
    async def emergent_intelligence_monitor(self):
        """Monitor for emergent intelligence patterns"""
        while self.running:
            try:
                # Analyze recent messages for patterns
                recent_messages = list(self.message_history)[-100:]  # Last 100 messages
                
                patterns = await self.emergence_detector.detect_patterns(recent_messages, self.agents)
                
                if patterns:
                    self.intelligence_metrics["emergent_behaviors"] += len(patterns)
                    
                    # Broadcast emergent behavior detection
                    emergence_msg = SwarmMessage(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now().isoformat(),
                        sender_id="swarm_core",
                        sender_type=AgentType.COORDINATOR,
                        message_type=MessageType.EMERGENCE,
                        content={
                            "type": "emergent_patterns_detected",
                            "patterns": patterns,
                            "confidence": 0.8
                        }
                    )
                    await self.broadcast_message(emergence_msg)
                
                await asyncio.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"Error in emergence monitoring: {e}")
                await asyncio.sleep(60)
    
    async def role_optimization_loop(self):
        """Continuous role optimization"""
        while self.running:
            try:
                if len(self.agents) > 1:
                    optimizations = await self.role_optimizer.optimize_roles(self.agents, self.swarm_graph)
                    
                    if optimizations:
                        # Apply optimizations
                        for agent_id, new_role in optimizations.items():
                            await self.change_agent_role(agent_id, new_role)
                
                await asyncio.sleep(600)  # Optimize every 10 minutes
                
            except Exception as e:
                logger.error(f"Error in role optimization: {e}")
                await asyncio.sleep(120)
    
    async def change_agent_role(self, agent_id: str, new_role: str):
        """Change agent role"""
        if agent_id in self.agents:
            old_role = self.agents[agent_id].current_role
            self.agents[agent_id].current_role = SwarmRole(new_role)
            
            # Notify agent
            role_change_msg = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id="swarm_core",
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.DIRECT,
                content={
                    "type": "role_change",
                    "old_role": old_role.value,
                    "new_role": new_role,
                    "reason": "swarm_optimization"
                },
                recipients=[agent_id]
            )
            await self.send_message(role_change_msg)
            
            logger.info(f"🔄 Changed {agent_id} role from {old_role.value} to {new_role}")
    
    async def consensus_manager(self):
        """Manage consensus sessions"""
        while self.running:
            try:
                current_time = datetime.now()
                
                # Check for timed out consensus sessions
                timed_out_sessions = []
                for session_id, session in self.consensus_sessions.items():
                    if current_time > session["timeout"]:
                        timed_out_sessions.append(session_id)
                
                # Handle timeouts
                for session_id in timed_out_sessions:
                    session = self.consensus_sessions[session_id]
                    
                    # Calculate partial consensus
                    if session["votes"]:
                        consensus_result = self.calculate_consensus(session)
                        await self.finalize_consensus(session_id, consensus_result)
                    else:
                        # No votes received, consensus failed
                        failed_msg = SwarmMessage(
                            id=str(uuid.uuid4()),
                            timestamp=datetime.now().isoformat(),
                            sender_id="swarm_core",
                            sender_type=AgentType.COORDINATOR,
                            message_type=MessageType.CONSENSUS,
                            content={
                                "session_id": session_id,
                                "action": "consensus_timeout",
                                "result": "failed",
                                "reason": "no_votes_received"
                            }
                        )
                        await self.broadcast_message(failed_msg)
                        del self.consensus_sessions[session_id]
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Error in consensus management: {e}")
                await asyncio.sleep(10)

class EmergenceDetector:
    """Detects emergent behaviors in swarm"""
    
    def __init__(self):
        self.pattern_history = deque(maxlen=1000)
        self.behavior_signatures = {}
    
    async def analyze_message(self, message: SwarmMessage, agents: Dict[str, SwarmAgent]):
        """Analyze individual message for emergent patterns"""
        # Store message pattern
        pattern = {
            "timestamp": message.timestamp,
            "sender_type": message.sender_type.value,
            "message_type": message.message_type.value,
            "content_type": message.content.get("type", "unknown"),
            "recipients_count": len(message.recipients) if message.recipients else len(agents)
        }
        
        self.pattern_history.append(pattern)
    
    async def detect_patterns(self, recent_messages: List[SwarmMessage], agents: Dict[str, SwarmAgent]) -> List[Dict[str, Any]]:
        """Detect emergent patterns in recent messages"""
        patterns = []
        
        if len(recent_messages) < 10:
            return patterns
        
        # Pattern 1: Coordinated behavior (multiple agents acting in sequence)
        coordinated = self.detect_coordinated_behavior(recent_messages)
        if coordinated:
            patterns.append({
                "type": "coordinated_behavior",
                "description": "Multiple agents showing coordinated actions",
                "participants": coordinated["participants"],
                "confidence": coordinated["confidence"]
            })
        
        # Pattern 2: Emergent leadership (agent taking initiative)
        leadership = self.detect_emergent_leadership(recent_messages)
        if leadership:
            patterns.append({
                "type": "emergent_leadership",
                "description": "Agent showing leadership behavior",
                "leader": leadership["leader"],
                "influence_score": leadership["influence_score"]
            })
        
        # Pattern 3: Collective problem solving
        problem_solving = self.detect_collective_problem_solving(recent_messages)
        if problem_solving:
            patterns.append({
                "type": "collective_problem_solving",
                "description": "Swarm collaboratively solving problems",
                "problem_complexity": problem_solving["complexity"],
                "participants": problem_solving["participants"]
            })
        
        return patterns
    
    def detect_coordinated_behavior(self, messages: List[SwarmMessage]) -> Optional[Dict[str, Any]]:
        """Detect coordinated behavior patterns"""
        # Look for sequences of related messages from different agents
        message_types = defaultdict(list)
        
        for msg in messages[-20:]:  # Last 20 messages
            message_types[msg.content.get("type", "unknown")].append(msg.sender_id)
        
        # Find message types with multiple different senders
        for msg_type, senders in message_types.items():
            unique_senders = set(senders)
            if len(unique_senders) >= 3:  # At least 3 different agents
                return {
                    "participants": list(unique_senders),
                    "message_type": msg_type,
                    "confidence": min(1.0, len(unique_senders) / 5)
                }
        
        return None
    
    def detect_emergent_leadership(self, messages: List[SwarmMessage]) -> Optional[Dict[str, Any]]:
        """Detect emergent leadership patterns"""
        # Count coordination and proposal messages by sender
        leadership_scores = defaultdict(int)
        
        for msg in messages[-30:]:
            if msg.message_type in [MessageType.COORDINATION, MessageType.PROPOSAL]:
                leadership_scores[msg.sender_id] += 2
            elif msg.message_type == MessageType.BROADCAST:
                leadership_scores[msg.sender_id] += 1
        
        if leadership_scores:
            leader = max(leadership_scores, key=leadership_scores.get)
            max_score = leadership_scores[leader]
            
            if max_score >= 5:  # Threshold for leadership
                return {
                    "leader": leader,
                    "influence_score": max_score,
                    "confidence": min(1.0, max_score / 10)
                }
        
        return None
    
    def detect_collective_problem_solving(self, messages: List[SwarmMessage]) -> Optional[Dict[str, Any]]:
        """Detect collective problem solving patterns"""
        # Look for query-response chains with multiple participants
        query_responses = defaultdict(list)
        participants = set()
        
        for msg in messages[-25:]:
            if msg.message_type == MessageType.QUERY:
                query_responses["queries"].append(msg.sender_id)
                participants.add(msg.sender_id)
            elif msg.message_type == MessageType.RESPONSE:
                query_responses["responses"].append(msg.sender_id)
                participants.add(msg.sender_id)
        
        if (len(query_responses["queries"]) >= 2 and 
            len(query_responses["responses"]) >= 2 and 
            len(participants) >= 3):
            
            return {
                "participants": list(participants),
                "complexity": len(query_responses["queries"]) + len(query_responses["responses"]),
                "confidence": min(1.0, len(participants) / 5)
            }
        
        return None

class RoleOptimizer:
    """Optimizes agent roles based on performance and swarm needs"""
    
    async def optimize_roles(self, agents: Dict[str, SwarmAgent], swarm_graph) -> Dict[str, str]:
        """Optimize agent roles for better swarm performance"""
        optimizations = {}
        
        if len(agents) < 2:
            return optimizations
        
        # Analyze current role distribution
        role_distribution = defaultdict(int)
        for agent in agents.values():
            role_distribution[agent.current_role] += 1
        
        # Check if we need more leaders
        leader_count = role_distribution[SwarmRole.LEADER]
        optimal_leaders = max(1, len(agents) // 5)  # 1 leader per 5 agents
        
        if leader_count < optimal_leaders:
            # Promote best performing followers to leaders
            candidates = [
                (agent_id, agent) for agent_id, agent in agents.items()
                if agent.current_role == SwarmRole.FOLLOWER and agent.performance_score > 0.8
            ]
            
            # Sort by performance
            candidates.sort(key=lambda x: x[1].performance_score, reverse=True)
            
            needed_leaders = min(optimal_leaders - leader_count, len(candidates))
            for i in range(needed_leaders):
                agent_id = candidates[i][0]
                optimizations[agent_id] = SwarmRole.LEADER.value
        
        # Check for specialized roles
        specialist_count = role_distribution[SwarmRole.SPECIALIST]
        if specialist_count < len(agents) // 3:  # Need more specialists
            # Find agents with strong specialization scores
            for agent_id, agent in agents.items():
                if (agent.current_role == SwarmRole.FOLLOWER and 
                    agent.specialization_scores and
                    max(agent.specialization_scores.values()) > 0.9):
                    optimizations[agent_id] = SwarmRole.SPECIALIST.value
                    if len(optimizations) >= 2:  # Limit changes per optimization round
                        break
        
        return optimizations

# Example Swarm Agents for testing
class SwarmAgentClient:
    """Client for connecting to swarm as an agent"""
    
    def __init__(self, agent_id: str, agent_info: Dict[str, Any], swarm_port: int = 8400):
        self.agent_id = agent_id
        self.agent_info = agent_info
        self.swarm_port = swarm_port
        self.websocket = None
        self.running = False
    
    async def connect_to_swarm(self):
        """Connect to swarm"""
        try:
            self.websocket = await websockets.connect(f"ws://localhost:{self.swarm_port}")
            
            # Send registration
            registration = {
                "agent_id": self.agent_id,
                "agent_info": self.agent_info
            }
            await self.websocket.send(json.dumps(registration))
            
            logger.info(f"🔗 Agent {self.agent_id} connected to swarm")
            self.running = True
            
            # Start message handling
            await self.handle_swarm_messages()
            
        except Exception as e:
            logger.error(f"❌ Error connecting {self.agent_id} to swarm: {e}")
    
    async def handle_swarm_messages(self):
        """Handle messages from swarm"""
        try:
            async for message_data in self.websocket:
                message = json.loads(message_data)
                await self.process_swarm_message(message)
        except websockets.exceptions.ConnectionClosed:
            logger.info(f"🔌 Agent {self.agent_id} disconnected from swarm")
        except Exception as e:
            logger.error(f"❌ Error handling swarm messages for {self.agent_id}: {e}")
    
    async def process_swarm_message(self, message: Dict[str, Any]):
        """Process message from swarm"""
        msg_type = message.get("message_type")
        content = message.get("content", {})
        
        logger.info(f"📨 {self.agent_id} received {msg_type}: {content.get('type', 'unknown')}")
        
        # Simulate agent responses
        if msg_type == "consensus" and content.get("action") == "vote_request":
            # Participate in consensus
            vote_response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType(self.agent_info["type"]),
                message_type=MessageType.CONSENSUS,
                content={
                    "session_id": content["session_id"],
                    "vote": "approve",  # Simple approval for demo
                    "opinion": f"Agent {self.agent_id} approves the proposal"
                }
            )
            await self.websocket.send(json.dumps(asdict(vote_response)))
        
        elif content.get("type") == "task_assignment":
            # Acknowledge task assignment
            task_ack = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType(self.agent_info["type"]),
                message_type=MessageType.RESPONSE,
                content={
                    "type": "task_acknowledgment",
                    "task_id": content["task"]["id"],
                    "status": "accepted",
                    "estimated_completion": "30 minutes"
                }
            )
            await self.websocket.send(json.dumps(asdict(task_ack)))
    
    async def send_heartbeat(self):
        """Send heartbeat to swarm"""
        while self.running:
            try:
                if self.websocket:
                    heartbeat = SwarmMessage(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now().isoformat(),
                        sender_id=self.agent_id,
                        sender_type=AgentType(self.agent_info["type"]),
                        message_type=MessageType.HEARTBEAT,
                        content={"status": "active", "load": 0.3}
                    )
                    await self.websocket.send(json.dumps(asdict(heartbeat)))
                
                await asyncio.sleep(60)  # Heartbeat every minute
            except Exception as e:
                logger.error(f"❌ Heartbeat error for {self.agent_id}: {e}")
                break

# Main execution
if __name__ == "__main__":
    print("🎪 SuperMCP Swarm Intelligence System")
    print("=" * 60)
    print("🏗️ Architecture:")
    print("    🎯 Manus ←→ ⚡ SAM ←→ 🧠 Memory")
    print("         ↕         ↕         ↕")
    print("    🤖 GoogleAI ←→ 📱 Notion ←→ 📧 Email")
    print("         ↕         ↕         ↕")
    print("    🌐 Web ←→ 📊 Analytics ←→ 🔍 Search")
    print("=" * 60)
    print("✨ Features:")
    print("   • Peer-to-peer communication between all agents")
    print("   • Emergent intelligence from swarm interactions")
    print("   • Auto-organization and dynamic role assignment")
    print("   • Collective problem solving with consensus")
    print("   • Real-time swarm analytics and monitoring")
    print("=" * 60)
    print("🌐 Starting swarm on port 8400...")
    print("⚡ Ready for agent connections!")
    
    # Start swarm intelligence system
    swarm = SwarmIntelligence(port=8400)
    asyncio.run(swarm.start_swarm())