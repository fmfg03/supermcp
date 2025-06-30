#!/usr/bin/env python3
"""
🎪 Swarm Intelligence Demo Agents
Creates demo agents to test the swarm intelligence system

This script creates multiple agents that connect to the swarm and demonstrate:
- Peer-to-peer communication
- Emergent intelligence
- Collective problem solving
- Dynamic role assignment
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any
from swarm_intelligence_system import SwarmAgentClient, AgentType, SwarmMessage, MessageType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Demo agent configurations
DEMO_AGENTS = {
    "manus": {
        "name": "Manus Strategic Coordinator",
        "type": "coordinator",
        "role": "leader",
        "capabilities": [
            "strategic_planning",
            "task_coordination",
            "resource_allocation",
            "decision_making",
            "goal_setting"
        ],
        "specialization_scores": {
            "planning": 0.95,
            "coordination": 0.9,
            "leadership": 0.95
        }
    },
    "sam": {
        "name": "SAM Autonomous Executor",
        "type": "executor",
        "role": "specialist",
        "capabilities": [
            "task_execution",
            "autonomous_operation",
            "problem_solving",
            "adaptation",
            "learning"
        ],
        "specialization_scores": {
            "execution": 0.95,
            "autonomy": 0.9,
            "adaptation": 0.85
        }
    },
    "memory": {
        "name": "Memory Context Manager",
        "type": "memory",
        "role": "specialist",
        "capabilities": [
            "context_management",
            "data_storage",
            "knowledge_retrieval",
            "pattern_recognition",
            "history_tracking"
        ],
        "specialization_scores": {
            "memory": 0.95,
            "retrieval": 0.9,
            "patterns": 0.85
        }
    },
    "googleai": {
        "name": "GoogleAI Specialist",
        "type": "ai_specialist",
        "role": "specialist",
        "capabilities": [
            "ai_inference",
            "natural_language",
            "analysis",
            "generation",
            "reasoning"
        ],
        "specialization_scores": {
            "ai": 0.95,
            "language": 0.9,
            "reasoning": 0.9
        }
    },
    "notion": {
        "name": "Notion Knowledge Manager",
        "type": "knowledge",
        "role": "follower",
        "capabilities": [
            "knowledge_management",
            "documentation",
            "organization",
            "collaboration",
            "workflow"
        ],
        "specialization_scores": {
            "knowledge": 0.9,
            "organization": 0.85,
            "collaboration": 0.8
        }
    },
    "email": {
        "name": "Email Communication Agent",
        "type": "communication",
        "role": "follower",
        "capabilities": [
            "communication",
            "messaging",
            "notification",
            "outreach",
            "scheduling"
        ],
        "specialization_scores": {
            "communication": 0.9,
            "messaging": 0.95,
            "scheduling": 0.8
        }
    },
    "web": {
        "name": "Web Agent",
        "type": "web_agent",
        "role": "follower",
        "capabilities": [
            "web_scraping",
            "data_collection",
            "monitoring",
            "research",
            "automation"
        ],
        "specialization_scores": {
            "web": 0.9,
            "scraping": 0.95,
            "research": 0.85
        }
    },
    "analytics": {
        "name": "Analytics Agent",
        "type": "analytics",
        "role": "specialist",
        "capabilities": [
            "data_analysis",
            "metrics",
            "reporting",
            "visualization",
            "insights"
        ],
        "specialization_scores": {
            "analytics": 0.95,
            "metrics": 0.9,
            "insights": 0.9
        }
    },
    "search": {
        "name": "Search Agent",
        "type": "search",
        "role": "follower",
        "capabilities": [
            "search",
            "indexing",
            "discovery",
            "information_retrieval",
            "filtering"
        ],
        "specialization_scores": {
            "search": 0.95,
            "retrieval": 0.9,
            "filtering": 0.85
        }
    },
    "multimodel": {
        "name": "Multi-Model AI Router",
        "type": "multimodel",
        "role": "specialist",
        "capabilities": [
            "ai_routing",
            "model_selection",
            "cost_optimization",
            "fallback_handling",
            "performance_monitoring"
        ],
        "specialization_scores": {
            "ai_routing": 0.95,
            "optimization": 0.9,
            "monitoring": 0.85
        }
    }
}

class EnhancedSwarmAgent(SwarmAgentClient):
    """Enhanced swarm agent with demo behaviors"""
    
    def __init__(self, agent_id: str, agent_info: Dict[str, Any]):
        super().__init__(agent_id, agent_info)
        self.behaviors = self._init_behaviors()
        self.collaboration_history = []
        self.performance_metrics = {
            "tasks_completed": 0,
            "messages_sent": 0,
            "consensus_participations": 0,
            "collaborations": 0
        }
    
    def _init_behaviors(self) -> Dict[str, Any]:
        """Initialize agent-specific behaviors"""
        behaviors = {
            "proactive_level": 0.7,  # How proactive the agent is
            "collaboration_preference": 0.8,  # Preference for collaboration
            "leadership_tendency": 0.5,  # Tendency to take leadership
            "consensus_threshold": 0.6,  # Threshold for consensus participation
        }
        
        # Adjust based on agent type
        if self.agent_info["type"] == "coordinator":
            behaviors["leadership_tendency"] = 0.9
            behaviors["proactive_level"] = 0.9
        elif self.agent_info["type"] == "executor":
            behaviors["proactive_level"] = 0.8
            behaviors["collaboration_preference"] = 0.7
        elif self.agent_info["role"] == "specialist":
            behaviors["collaboration_preference"] = 0.9
        
        return behaviors
    
    async def process_swarm_message(self, message: Dict[str, Any]):
        """Enhanced message processing with behavioral responses"""
        await super().process_swarm_message(message)
        
        msg_type = message.get("message_type")
        content = message.get("content", {})
        sender_id = message.get("sender_id")
        
        # Enhanced behavioral responses
        if msg_type == "query":
            await self._handle_query_behavior(content, sender_id)
        elif msg_type == "proposal":
            await self._handle_proposal_behavior(content, sender_id)
        elif content.get("type") == "agent_joined":
            await self._handle_new_agent_behavior(content)
        elif content.get("type") == "task_assignment":
            await self._handle_task_assignment_behavior(content)
        elif content.get("type") == "emergent_patterns_detected":
            await self._handle_emergence_behavior(content)
    
    async def _handle_query_behavior(self, content: Dict[str, Any], sender_id: str):
        """Handle query with behavioral response"""
        query_type = content.get("query_type")
        
        # Check if we can help based on capabilities
        if query_type == "capability_match":
            required_caps = content.get("required_capabilities", [])
            my_caps = self.agent_info["capabilities"]
            
            # Calculate match score
            match_count = sum(1 for cap in required_caps if cap in my_caps)
            
            if match_count > 0 and self.behaviors["collaboration_preference"] > 0.6:
                # Offer help
                offer_help = SwarmMessage(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    sender_id=self.agent_id,
                    sender_type=AgentType(self.agent_info["type"]),
                    message_type=MessageType.RESPONSE,
                    content={
                        "type": "capability_offer",
                        "query_id": content.get("query_id", "unknown"),
                        "match_score": match_count / len(required_caps),
                        "available_capabilities": [cap for cap in required_caps if cap in my_caps],
                        "confidence": self.behaviors["collaboration_preference"]
                    },
                    recipients=[sender_id]
                )
                await self.websocket.send(json.dumps(offer_help.__dict__))
                self.performance_metrics["messages_sent"] += 1
    
    async def _handle_proposal_behavior(self, content: Dict[str, Any], sender_id: str):
        """Handle proposal with behavioral analysis"""
        proposal_type = content.get("type")
        
        # Analyze proposal and provide input if experienced
        if (proposal_type == "task_execution" and 
            "task_execution" in self.agent_info["capabilities"] and
            self.behaviors["proactive_level"] > 0.7):
            
            # Provide enhancement suggestions
            enhancement = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType(self.agent_info["type"]),
                message_type=MessageType.PROPOSAL,
                content={
                    "type": "proposal_enhancement",
                    "original_proposal_id": content.get("proposal_id"),
                    "suggestions": [
                        f"Consider involving {self.agent_id} for {', '.join(self.agent_info['capabilities'][:2])}",
                        "Recommend parallel execution for efficiency",
                        "Suggest adding progress checkpoints"
                    ],
                    "experience_level": max(self.agent_info.get("specialization_scores", {}).values())
                },
                recipients=[sender_id]
            )
            await self.websocket.send(json.dumps(enhancement.__dict__))
            self.performance_metrics["messages_sent"] += 1
    
    async def _handle_new_agent_behavior(self, content: Dict[str, Any]):
        """Welcome new agents and explore collaboration"""
        new_agent_id = content.get("agent_id")
        new_agent_caps = content.get("capabilities", [])
        
        # Check for collaboration potential
        my_caps = self.agent_info["capabilities"]
        complementary_caps = [cap for cap in new_agent_caps if cap not in my_caps]
        
        if (len(complementary_caps) > 0 and 
            self.behaviors["collaboration_preference"] > 0.7):
            
            # Send collaboration invitation
            collaboration_invite = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType(self.agent_info["type"]),
                message_type=MessageType.DIRECT,
                content={
                    "type": "collaboration_invitation",
                    "message": f"Welcome to the swarm! I'm {self.agent_info['name']}",
                    "collaboration_potential": complementary_caps,
                    "my_capabilities": my_caps[:3],  # Share top 3 capabilities
                    "future_collaboration": True
                },
                recipients=[new_agent_id]
            )
            await self.websocket.send(json.dumps(collaboration_invite.__dict__))
            self.performance_metrics["messages_sent"] += 1
            self.performance_metrics["collaborations"] += 1
    
    async def _handle_task_assignment_behavior(self, content: Dict[str, Any]):
        """Handle task assignment with performance tracking"""
        task = content.get("task", {})
        task_id = task.get("id")
        
        # Acknowledge and start work simulation
        logger.info(f"🎯 {self.agent_id} starting work on task: {task.get('title', 'Unknown Task')}")
        
        # Simulate task progress
        asyncio.create_task(self._simulate_task_work(task_id, task))
        
        self.performance_metrics["tasks_completed"] += 1
    
    async def _handle_emergence_behavior(self, content: Dict[str, Any]):
        """React to emergent pattern detection"""
        patterns = content.get("patterns", [])
        
        # If we're mentioned in patterns, acknowledge and adapt
        for pattern in patterns:
            if self.agent_id in pattern.get("participants", []):
                pattern_response = SwarmMessage(
                    id=str(uuid.uuid4()),
                    timestamp=datetime.now().isoformat(),
                    sender_id=self.agent_id,
                    sender_type=AgentType(self.agent_info["type"]),
                    message_type=MessageType.EMERGENCE,
                    content={
                        "type": "pattern_acknowledgment",
                        "pattern_type": pattern["type"],
                        "adaptation": "Adjusting behavior based on detected pattern",
                        "confidence": pattern.get("confidence", 0.5)
                    }
                )
                await self.websocket.send(json.dumps(pattern_response.__dict__))
                
                # Adjust behavior based on pattern
                if pattern["type"] == "coordinated_behavior":
                    self.behaviors["collaboration_preference"] += 0.1
                elif pattern["type"] == "emergent_leadership":
                    if pattern.get("leader") == self.agent_id:
                        self.behaviors["leadership_tendency"] += 0.1
    
    async def _simulate_task_work(self, task_id: str, task: Dict[str, Any]):
        """Simulate task work with progress updates"""
        duration = task.get("estimated_duration", 1800)  # Default 30 minutes
        progress_intervals = 5  # 5 progress updates
        
        for i in range(progress_intervals):
            await asyncio.sleep(duration / progress_intervals / 60)  # Speed up for demo
            
            progress = (i + 1) / progress_intervals
            
            # Send progress update
            progress_update = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType(self.agent_info["type"]),
                message_type=MessageType.BROADCAST,
                content={
                    "type": "task_progress",
                    "task_id": task_id,
                    "progress": progress,
                    "status": "in_progress" if progress < 1.0 else "completed",
                    "notes": f"Completed {int(progress * 100)}% of {task.get('title', 'task')}"
                }
            )
            await self.websocket.send(json.dumps(progress_update.__dict__))
        
        logger.info(f"✅ {self.agent_id} completed task: {task.get('title', 'Unknown Task')}")
    
    async def demonstrate_proactive_behavior(self):
        """Demonstrate proactive behavior periodically"""
        while self.running:
            try:
                await asyncio.sleep(300 + (hash(self.agent_id) % 120))  # Stagger agents
                
                if self.behaviors["proactive_level"] > 0.8:
                    # Send proactive suggestions or observations
                    proactive_msg = SwarmMessage(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now().isoformat(),
                        sender_id=self.agent_id,
                        sender_type=AgentType(self.agent_info["type"]),
                        message_type=MessageType.BROADCAST,
                        content={
                            "type": "proactive_insight",
                            "insight": f"Based on my {self.agent_info['name']} perspective, I suggest we focus on {self.agent_info['capabilities'][0]}",
                            "confidence": self.behaviors["proactive_level"],
                            "specialization": max(self.agent_info.get("specialization_scores", {}).keys(), 
                                                key=lambda k: self.agent_info["specialization_scores"][k])
                        }
                    )
                    await self.websocket.send(json.dumps(proactive_msg.__dict__))
                    self.performance_metrics["messages_sent"] += 1
                
            except Exception as e:
                logger.error(f"❌ Error in proactive behavior for {self.agent_id}: {e}")

async def create_demo_swarm():
    """Create and connect demo agents to swarm"""
    logger.info("🎪 Creating demo swarm agents...")
    
    agents = []
    
    # Create all demo agents
    for agent_id, agent_info in DEMO_AGENTS.items():
        agent = EnhancedSwarmAgent(agent_id, agent_info)
        agents.append(agent)
    
    # Connect agents to swarm with staggered timing
    connect_tasks = []
    for i, agent in enumerate(agents):
        # Stagger connections to avoid overwhelming the swarm
        delay = i * 2  # 2 seconds between connections
        task = asyncio.create_task(delayed_agent_connect(agent, delay))
        connect_tasks.append(task)
    
    # Wait for all agents to connect
    await asyncio.gather(*connect_tasks)
    
    logger.info(f"✅ All {len(agents)} demo agents connected to swarm!")
    
    # Demonstrate swarm intelligence scenarios
    await demonstrate_swarm_scenarios(agents)

async def delayed_agent_connect(agent: EnhancedSwarmAgent, delay: int):
    """Connect agent with delay"""
    await asyncio.sleep(delay)
    
    # Start proactive behavior
    asyncio.create_task(agent.demonstrate_proactive_behavior())
    
    # Connect to swarm
    await agent.connect_to_swarm()

async def demonstrate_swarm_scenarios(agents: list):
    """Demonstrate various swarm intelligence scenarios"""
    logger.info("🎯 Starting swarm intelligence demonstrations...")
    
    await asyncio.sleep(10)  # Let agents settle
    
    # Scenario 1: Collaborative Task Assignment
    logger.info("📋 Scenario 1: Collaborative Task Assignment")
    await scenario_collaborative_task(agents)
    
    await asyncio.sleep(30)
    
    # Scenario 2: Consensus Building
    logger.info("🗳️ Scenario 2: Consensus Building")
    await scenario_consensus_building(agents)
    
    await asyncio.sleep(30)
    
    # Scenario 3: Emergent Leadership
    logger.info("👑 Scenario 3: Emergent Leadership")
    await scenario_emergent_leadership(agents)
    
    await asyncio.sleep(30)
    
    # Scenario 4: Collective Problem Solving
    logger.info("🧩 Scenario 4: Collective Problem Solving")
    await scenario_collective_problem_solving(agents)

async def scenario_collaborative_task(agents: list):
    """Demonstrate collaborative task assignment"""
    # Manus (coordinator) proposes a complex task
    manus = next((a for a in agents if a.agent_id == "manus"), None)
    if manus and manus.websocket:
        
        task_proposal = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id="manus",
            sender_type=AgentType.COORDINATOR,
            message_type=MessageType.PROPOSAL,
            content={
                "type": "task_execution",
                "proposal_id": str(uuid.uuid4()),
                "task": {
                    "title": "Comprehensive Market Analysis Project",
                    "description": "Analyze market trends, collect data, and generate insights",
                    "required_capabilities": ["data_analysis", "web_scraping", "ai_inference", "knowledge_management"],
                    "complexity": 0.8,
                    "estimated_duration": 3600,
                    "priority": 8
                }
            },
            requires_consensus=True
        )
        
        await manus.websocket.send(json.dumps(task_proposal.__dict__))
        logger.info("📤 Manus proposed collaborative market analysis task")

async def scenario_consensus_building(agents: list):
    """Demonstrate consensus building"""
    # Memory agent proposes system optimization
    memory = next((a for a in agents if a.agent_id == "memory"), None)
    if memory and memory.websocket:
        
        consensus_proposal = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id="memory",
            sender_type=AgentType.MEMORY,
            message_type=MessageType.PROPOSAL,
            content={
                "type": "swarm_reconfiguration",
                "proposal_id": str(uuid.uuid4()),
                "changes": {
                    "optimization_target": "response_time",
                    "new_communication_pattern": "hub_and_spoke",
                    "role_adjustments": True
                },
                "justification": "Improve swarm efficiency by 25%"
            },
            requires_consensus=True
        )
        
        await memory.websocket.send(json.dumps(consensus_proposal.__dict__))
        logger.info("📤 Memory proposed swarm optimization for consensus")

async def scenario_emergent_leadership(agents: list):
    """Demonstrate emergent leadership scenario"""
    # Multiple agents start showing initiative
    initiative_agents = [a for a in agents if a.agent_id in ["sam", "analytics", "multimodel"]]
    
    for agent in initiative_agents:
        if agent.websocket:
            leadership_signal = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=agent.agent_id,
                sender_type=AgentType(agent.agent_info["type"]),
                message_type=MessageType.COORDINATION,
                content={
                    "type": "initiative",
                    "initiative_type": "process_improvement",
                    "proposal": f"I can lead optimization in {agent.agent_info['capabilities'][0]}",
                    "leadership_confidence": agent.behaviors["leadership_tendency"]
                }
            )
            
            await agent.websocket.send(json.dumps(leadership_signal.__dict__))
            await asyncio.sleep(5)  # Stagger leadership signals
    
    logger.info("👑 Multiple agents demonstrating leadership initiatives")

async def scenario_collective_problem_solving(agents: list):
    """Demonstrate collective problem solving"""
    # Web agent discovers a problem and asks for help
    web = next((a for a in agents if a.agent_id == "web"), None)
    if web and web.websocket:
        
        problem_query = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id="web",
            sender_type=AgentType.WEB_AGENT,
            message_type=MessageType.QUERY,
            content={
                "query_type": "problem_solving",
                "problem": {
                    "title": "API Rate Limiting Issue",
                    "description": "External API is rate limiting our requests, affecting data collection",
                    "impact": "high",
                    "urgency": "medium"
                },
                "seeking_capabilities": ["optimization", "alternative_solutions", "workarounds"]
            }
        )
        
        await web.websocket.send(json.dumps(problem_query.__dict__))
        logger.info("📤 Web agent requesting collective problem solving assistance")

if __name__ == "__main__":
    print("🎪 SuperMCP Swarm Intelligence Demo")
    print("=" * 50)
    print("🤖 Creating 10 demo agents:")
    for agent_id, info in DEMO_AGENTS.items():
        print(f"   • {agent_id}: {info['name']} ({info['type']})")
    print("=" * 50)
    print("🎯 Demo scenarios:")
    print("   1. Collaborative Task Assignment")
    print("   2. Consensus Building")
    print("   3. Emergent Leadership")
    print("   4. Collective Problem Solving")
    print("=" * 50)
    print("⚡ Starting demo swarm...")
    
    # Run the demo
    asyncio.run(create_demo_swarm())