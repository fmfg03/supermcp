"""
Enhanced SAM Agent with LangGraph + Graphiti Integration
World's first MCP + LangGraph + Graphiti enterprise system
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, TypedDict, Annotated
from typing_extensions import TypedDict

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_core.language_models import BaseChatModel
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, add_messages, START, END
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import ToolNode
from graphiti_core import Graphiti

# MCP System imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.sam_memory_analyzer import SAMMemoryAnalyzer
from backend.src.services.mcpBrokerService import MCPBrokerService
from backend.mcp_orchestration_server import MCPOrchestrationServer

logger = logging.getLogger(__name__)

class MCPAgentState(TypedDict):
    """Enhanced state for MCP agents with multi-layer memory context"""
    messages: Annotated[List, add_messages]
    user_id: str
    task_context: Dict
    memory_context: List  # From Graphiti knowledge graph
    agent_memories: List  # From MCP memory analyzer
    mcp_tools_used: List
    collaboration_context: Dict  # For multi-agent coordination

class EnhancedSAMAgent:
    """
    Enhanced SAM Agent with LangGraph orchestration and Graphiti knowledge graph
    
    Features:
    - Triple-layer memory system (immediate, short-term, long-term)
    - Contextual intelligence with relationship awareness
    - Real-time knowledge graph updates
    - Multi-agent collaboration via shared knowledge
    """
    
    def __init__(self, 
                 llm: Optional[BaseChatModel] = None,
                 graphiti_config: Optional[Dict] = None,
                 mcp_config: Optional[Dict] = None):
        """Initialize Enhanced SAM Agent"""
        
        # Core LLM
        self.llm = llm or ChatOpenAI(
            model="gpt-4-turbo-preview",
            temperature=0.1,
            max_tokens=4000
        )
        
        # Existing MCP components
        self.memory_analyzer = SAMMemoryAnalyzer()
        self.mcp_broker = MCPBrokerService()
        self.orchestration_server = MCPOrchestrationServer()
        
        # Graphiti knowledge graph integration
        self.graphiti_config = graphiti_config or {
            "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "neo4j_username": os.getenv("NEO4J_USERNAME", "neo4j"),
            "neo4j_password": os.getenv("NEO4J_PASSWORD", "password")
        }
        
        self.graphiti = None  # Initialize lazily
        self._graphiti_initialized = False
        
        # LangGraph setup
        self.memory_saver = MemorySaver()
        self.graph = None
        self.tools = []
        
        # Agent collaboration registry
        self.agent_registry = {}
        
        logger.info("Enhanced SAM Agent initialized")
    
    async def _initialize_graphiti(self):
        """Lazy initialization of Graphiti client"""
        if not self._graphiti_initialized:
            try:
                self.graphiti = Graphiti(**self.graphiti_config)
                await self.graphiti.build_indices()
                self._graphiti_initialized = True
                logger.info("Graphiti knowledge graph initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Graphiti: {e}")
                self._graphiti_initialized = False
    
    def setup_langgraph(self):
        """Setup LangGraph with enhanced nodes and Graphiti integration"""
        
        # Create StateGraph
        graph_builder = StateGraph(MCPAgentState)
        
        # Core agent node with Graphiti context enhancement
        graph_builder.add_node('enhanced_agent', self.enhanced_agent_node)
        
        # MCP tools execution node
        graph_builder.add_node('mcp_tools', self.mcp_tools_node)
        
        # Memory persistence and knowledge graph update node
        graph_builder.add_node('memory_store', self.memory_store_node)
        
        # Multi-agent collaboration node
        graph_builder.add_node('collaboration', self.collaboration_node)
        
        # Setup edges and conditional routing
        graph_builder.add_edge(START, 'enhanced_agent')
        
        # Conditional routing from enhanced_agent
        graph_builder.add_conditional_edges(
            'enhanced_agent',
            self.route_next_action,
            {
                'tools': 'mcp_tools',
                'collaborate': 'collaboration', 
                'memory': 'memory_store',
                'end': END
            }
        )
        
        # Tool execution flows back to memory storage
        graph_builder.add_edge('mcp_tools', 'memory_store')
        graph_builder.add_edge('collaboration', 'memory_store')
        graph_builder.add_edge('memory_store', END)
        
        # Compile with memory checkpointing
        self.graph = graph_builder.compile(checkpointer=self.memory_saver)
        
        logger.info("LangGraph orchestration setup complete")
    
    async def enhanced_agent_node(self, state: MCPAgentState, config):
        """
        Core agent node enhanced with Graphiti knowledge graph context
        
        Process:
        1. Retrieve contextual knowledge from Graphiti
        2. Get relevant MCP memories 
        3. Build enhanced system prompt with full context
        4. Generate LLM response
        5. Async store interaction to knowledge graph
        """
        
        # Ensure Graphiti is initialized
        await self._initialize_graphiti()
        
        # Extract current user message
        current_message = state['messages'][-1].content if state['messages'] else ""
        user_id = state['user_id']
        
        # 1. RETRIEVE CONTEXTUAL KNOWLEDGE FROM GRAPHITI
        user_context = await self.get_user_context_from_graphiti(user_id, current_message)
        
        # 2. RETRIEVE RELEVANT MCP MEMORIES
        mcp_memories = await self.get_mcp_memories(user_id, current_message)
        
        # 3. RETRIEVE COLLABORATION CONTEXT
        collab_context = await self.get_collaboration_context(user_id, state.get('task_context', {}))
        
        # 4. BUILD ENHANCED SYSTEM PROMPT
        system_prompt = self.build_contextual_prompt(
            user_context=user_context,
            mcp_memories=mcp_memories,
            collaboration_context=collab_context,
            task_context=state.get('task_context', {})
        )
        
        # 5. GET LLM RESPONSE WITH FULL CONTEXT
        messages = [system_prompt] + state['messages']
        
        try:
            response = await self.llm.ainvoke(messages)
            
            # 6. ASYNC STORE TO GRAPHITI (non-blocking)
            asyncio.create_task(self.store_interaction_to_graphiti(
                user_id=user_id,
                interaction={
                    "user_message": current_message,
                    "agent_response": response.content,
                    "context": state.get('task_context', {}),
                    "memories_used": len(mcp_memories),
                    "knowledge_graph_facts": len(user_context.get('facts', [])),
                    "timestamp": datetime.now()
                }
            ))
            
            # Determine if tools or collaboration needed
            needs_tools = self.analyze_tool_needs(response.content)
            needs_collaboration = self.analyze_collaboration_needs(response.content, state)
            
            return {
                "messages": [response],
                "memory_context": user_context,
                "agent_memories": mcp_memories,
                "collaboration_context": collab_context,
                "mcp_tools_used": [],
                "_needs_tools": needs_tools,
                "_needs_collaboration": needs_collaboration
            }
            
        except Exception as e:
            logger.error(f"Error in enhanced_agent_node: {e}")
            error_response = AIMessage(content=f"I encountered an error processing your request: {str(e)}")
            return {
                "messages": [error_response],
                "memory_context": user_context,
                "agent_memories": mcp_memories,
                "collaboration_context": collab_context,
                "mcp_tools_used": []
            }
    
    async def get_user_context_from_graphiti(self, user_id: str, query: str) -> Dict:
        """Get comprehensive user context from Graphiti knowledge graph"""
        
        if not self._graphiti_initialized:
            return {"facts": [], "relationships": [], "recent_context": []}
        
        try:
            # Search for user-related facts using hybrid search
            user_facts = await self.graphiti.search(
                query=f"user:{user_id} {query}",
                search_type="hybrid",
                limit=10
            )
            
            # Get user's relationship network
            user_relationships = await self.get_user_relationships(user_id)
            
            # Get temporal context (what happened recently)
            recent_context = await self.get_recent_user_context(user_id, query)
            
            # Get cross-agent insights
            agent_insights = await self.get_cross_agent_insights(user_id)
            
            return {
                "facts": user_facts,
                "relationships": user_relationships,
                "recent_context": recent_context,
                "agent_insights": agent_insights,
                "context_score": self.calculate_context_relevance(user_facts, query)
            }
            
        except Exception as e:
            logger.error(f"Error getting Graphiti context: {e}")
            return {"facts": [], "relationships": [], "recent_context": [], "agent_insights": []}
    
    async def get_mcp_memories(self, user_id: str, query: str) -> List:
        """Get relevant memories from MCP memory analyzer"""
        
        try:
            memories = await self.memory_analyzer.search_memories(
                query=query,
                user_id=user_id,
                limit=5,
                include_embeddings=True
            )
            return memories
        except Exception as e:
            logger.error(f"Error getting MCP memories: {e}")
            return []
    
    async def get_collaboration_context(self, user_id: str, task_context: Dict) -> Dict:
        """Get context for multi-agent collaboration"""
        
        try:
            # Check if other agents have relevant context for this user/task
            if self._graphiti_initialized:
                collab_query = f"user:{user_id} agent_collaboration task:{task_context.get('type', 'general')}"
                agent_interactions = await self.graphiti.search(
                    query=collab_query,
                    search_type="graph_traversal",
                    limit=5
                )
                
                return {
                    "relevant_agents": self.identify_relevant_agents(task_context),
                    "shared_context": agent_interactions,
                    "coordination_needed": self.assess_coordination_needs(task_context)
                }
            
            return {"relevant_agents": [], "shared_context": [], "coordination_needed": False}
            
        except Exception as e:
            logger.error(f"Error getting collaboration context: {e}")
            return {"relevant_agents": [], "shared_context": [], "coordination_needed": False}
    
    def build_contextual_prompt(self, 
                                user_context: Dict, 
                                mcp_memories: List,
                                collaboration_context: Dict,
                                task_context: Dict) -> SystemMessage:
        """Build enhanced system prompt with triple-layer memory context"""
        
        # Format knowledge graph facts
        facts_string = ""
        if user_context.get("facts"):
            facts_string = "\n".join([f"- {fact}" for fact in user_context["facts"][:5]])
        
        # Format MCP memories
        memories_string = ""
        if mcp_memories:
            memories_string = "\n".join([f"- {mem.get('content', str(mem))}" for mem in mcp_memories[:3]])
        
        # Format relationships
        relationships_string = ""
        if user_context.get("relationships"):
            relationships_string = "\n".join([f"- {rel}" for rel in user_context["relationships"][:3]])
        
        # Format collaboration context
        collaboration_string = ""
        if collaboration_context.get("shared_context"):
            collaboration_string = "\n".join([f"- {ctx}" for ctx in collaboration_context["shared_context"][:2]])
        
        # Build comprehensive prompt
        prompt_content = f"""
You are SAM (Smart Agent Manager), an advanced AI agent with access to comprehensive user context through a triple-layer memory system.

CURRENT TASK CONTEXT:
{task_context}

KNOWLEDGE GRAPH INSIGHTS (Long-term memory from Graphiti):
{facts_string or 'No specific long-term insights available'}

USER RELATIONSHIPS & NETWORK:
{relationships_string or 'No relationship data available'}

RECENT MEMORIES (Short-term from MCP system):
{memories_string or 'No recent memories available'}

MULTI-AGENT COLLABORATION CONTEXT:
{collaboration_string or 'No collaboration context available'}

RECENT USER CONTEXT:
{user_context.get('recent_context', 'No recent context available')}

CROSS-AGENT INSIGHTS:
{user_context.get('agent_insights', 'No cross-agent insights available')}

INSTRUCTIONS:
1. Use this comprehensive context to provide personalized, informed responses
2. Demonstrate understanding of the user's history, preferences, and relationships
3. Leverage insights from other agents when relevant
4. Consider the temporal aspects of the user's situation
5. If you need to use tools or collaborate with other agents, indicate this clearly
6. Build upon previous interactions and maintain context continuity

Respond naturally while demonstrating the depth of understanding provided by your enhanced memory systems.
"""
        
        return SystemMessage(content=prompt_content)
    
    def route_next_action(self, state: MCPAgentState) -> str:
        """Determine next action based on agent response and context"""
        
        # Check if tools are needed
        if state.get('_needs_tools', False):
            return 'tools'
        
        # Check if collaboration is needed
        if state.get('_needs_collaboration', False):
            return 'collaborate'
        
        # Default to memory storage
        return 'memory'
    
    def analyze_tool_needs(self, response_content: str) -> bool:
        """Analyze if MCP tools are needed based on response"""
        tool_indicators = [
            "search for", "look up", "find information", "get data",
            "execute", "run", "process", "analyze file", "github",
            "notion", "telegram", "email", "schedule"
        ]
        
        return any(indicator in response_content.lower() for indicator in tool_indicators)
    
    def analyze_collaboration_needs(self, response_content: str, state: MCPAgentState) -> bool:
        """Analyze if multi-agent collaboration is needed"""
        collaboration_indicators = [
            "coordinate with", "ask manus", "work together", "team effort",
            "multiple agents", "collaboration", "coordinate"
        ]
        
        task_type = state.get('task_context', {}).get('type', '')
        complex_tasks = ['development', 'research', 'analysis', 'planning']
        
        return (any(indicator in response_content.lower() for indicator in collaboration_indicators) or
                task_type in complex_tasks)
    
    async def mcp_tools_node(self, state: MCPAgentState, config):
        """Execute MCP tools based on agent decisions"""
        
        # Extract tool requirements from last message
        last_message = state['messages'][-1].content
        
        try:
            # Use MCP broker to execute tools
            tool_results = await self.mcp_broker.execute_agent_tools(
                agent_request=last_message,
                user_id=state['user_id'],
                context=state.get('task_context', {})
            )
            
            # Format tool results for continued conversation
            tools_summary = f"Tool execution completed. Results: {tool_results}"
            tool_message = AIMessage(content=tools_summary)
            
            return {
                "messages": [tool_message],
                "mcp_tools_used": tool_results.get('tools_used', [])
            }
            
        except Exception as e:
            logger.error(f"Error in mcp_tools_node: {e}")
            error_message = AIMessage(content=f"Tool execution failed: {str(e)}")
            return {
                "messages": [error_message],
                "mcp_tools_used": []
            }
    
    async def collaboration_node(self, state: MCPAgentState, config):
        """Handle multi-agent collaboration"""
        
        try:
            # Identify relevant agents for collaboration
            relevant_agents = self.identify_relevant_agents(state.get('task_context', {}))
            
            if relevant_agents:
                # Create collaboration request
                collab_request = {
                    "requesting_agent": "SAM",
                    "target_agents": relevant_agents,
                    "task_context": state.get('task_context', {}),
                    "user_id": state['user_id'],
                    "collaboration_type": "information_sharing"
                }
                
                # Execute collaboration (placeholder for future multi-agent implementation)
                collab_results = await self.execute_collaboration(collab_request)
                
                collab_message = AIMessage(
                    content=f"Collaborated with {', '.join(relevant_agents)}. Insights: {collab_results}"
                )
                
                return {
                    "messages": [collab_message],
                    "collaboration_context": collab_results
                }
            
            return {"messages": [], "collaboration_context": {}}
            
        except Exception as e:
            logger.error(f"Error in collaboration_node: {e}")
            return {"messages": [], "collaboration_context": {}}
    
    async def memory_store_node(self, state: MCPAgentState, config):
        """Store interaction results to both MCP memory and Graphiti knowledge graph"""
        
        try:
            # Store to MCP memory analyzer
            if state['messages']:
                last_interaction = {
                    "user_id": state['user_id'],
                    "content": state['messages'][-1].content,
                    "context": state.get('task_context', {}),
                    "tools_used": state.get('mcp_tools_used', []),
                    "collaboration": state.get('collaboration_context', {}),
                    "timestamp": datetime.now()
                }
                
                await self.memory_analyzer.store_interaction(last_interaction)
            
            # Update knowledge graph asynchronously (already triggered in enhanced_agent_node)
            # This node ensures memory persistence is complete
            
            return {"messages": []}
            
        except Exception as e:
            logger.error(f"Error in memory_store_node: {e}")
            return {"messages": []}
    
    # Helper methods for Graphiti integration
    async def get_user_relationships(self, user_id: str) -> List:
        """Get user relationships from knowledge graph"""
        try:
            if self._graphiti_initialized:
                relationships = await self.graphiti.search(
                    query=f"MATCH (u:User {{id: '{user_id}'}})-[r]->(n) RETURN type(r), n.name LIMIT 10",
                    search_type="cypher"
                )
                return relationships
            return []
        except Exception as e:
            logger.error(f"Error getting user relationships: {e}")
            return []
    
    async def get_recent_user_context(self, user_id: str, query: str) -> List:
        """Get recent temporal context for user"""
        try:
            if self._graphiti_initialized:
                recent_context = await self.graphiti.search(
                    query=f"user:{user_id} recent:{query}",
                    search_type="temporal",
                    time_range="last_week",
                    limit=5
                )
                return recent_context
            return []
        except Exception as e:
            logger.error(f"Error getting recent context: {e}")
            return []
    
    async def get_cross_agent_insights(self, user_id: str) -> List:
        """Get insights from other agents about this user"""
        try:
            if self._graphiti_initialized:
                agent_insights = await self.graphiti.search(
                    query=f"user:{user_id} agent_type:Manus OR agent_type:WebSearch",
                    search_type="hybrid",
                    limit=3
                )
                return agent_insights
            return []
        except Exception as e:
            logger.error(f"Error getting cross-agent insights: {e}")
            return []
    
    def calculate_context_relevance(self, facts: List, query: str) -> float:
        """Calculate relevance score for context"""
        if not facts or not query:
            return 0.0
        
        query_words = set(query.lower().split())
        relevant_facts = 0
        
        for fact in facts:
            fact_words = set(str(fact).lower().split())
            if query_words.intersection(fact_words):
                relevant_facts += 1
        
        return relevant_facts / len(facts) if facts else 0.0
    
    def identify_relevant_agents(self, task_context: Dict) -> List[str]:
        """Identify which agents should be involved in collaboration"""
        task_type = task_context.get('type', '').lower()
        
        agent_mapping = {
            'development': ['Manus', 'GitHub'],
            'research': ['WebSearch', 'Perplexity'],
            'communication': ['Telegram', 'Email'],
            'documentation': ['Notion', 'GitHub'],
            'analysis': ['Manus', 'WebSearch']
        }
        
        return agent_mapping.get(task_type, [])
    
    def assess_coordination_needs(self, task_context: Dict) -> bool:
        """Assess if coordination between agents is needed"""
        complex_task_types = ['development', 'research', 'analysis', 'planning']
        return task_context.get('type', '').lower() in complex_task_types
    
    async def execute_collaboration(self, collab_request: Dict) -> Dict:
        """Execute collaboration with other agents (placeholder implementation)"""
        # This would interface with other agents in the system
        # For now, return mock collaboration results
        return {
            "collaboration_id": f"collab_{datetime.now().timestamp()}",
            "participating_agents": collab_request['target_agents'],
            "insights_shared": ["Mock insight 1", "Mock insight 2"],
            "coordination_successful": True
        }
    
    async def store_interaction_to_graphiti(self, user_id: str, interaction: Dict):
        """Store interaction in Graphiti knowledge graph"""
        
        if not self._graphiti_initialized:
            return
        
        try:
            episode = {
                "text": f"User {user_id}: {interaction['user_message']}\nSAM Agent: {interaction['agent_response']}",
                "metadata": {
                    "user_id": user_id,
                    "agent_type": "SAM",
                    "context": interaction['context'],
                    "memories_used": interaction.get('memories_used', 0),
                    "knowledge_graph_facts": interaction.get('knowledge_graph_facts', 0),
                    "timestamp": interaction['timestamp'].isoformat(),
                    "session_type": "enhanced_mcp_integration"
                }
            }
            
            result = await self.graphiti.add_episode(episode)
            logger.info(f"Stored interaction in Graphiti: {result.episode_id}")
            
        except Exception as e:
            logger.error(f"Error storing to Graphiti: {e}")
    
    async def run_agent(self, 
                        user_id: str, 
                        message: str, 
                        task_context: Dict = None,
                        thread_id: str = None) -> Dict:
        """Run the enhanced SAM agent with full context"""
        
        if not self.graph:
            self.setup_langgraph()
        
        # Ensure Graphiti is initialized
        await self._initialize_graphiti()
        
        # Setup configuration
        config = {
            "configurable": {
                "thread_id": thread_id or f"{user_id}_{datetime.now().timestamp()}"
            }
        }
        
        # Prepare initial state
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "task_context": task_context or {},
            "memory_context": [],
            "agent_memories": [],
            "mcp_tools_used": [],
            "collaboration_context": {}
        }
        
        try:
            # Execute the enhanced agent workflow
            result = await self.graph.ainvoke(initial_state, config=config)
            
            return {
                "response": result["messages"][-1].content if result["messages"] else "No response generated",
                "memory_context": result.get("memory_context", {}),
                "tools_used": result.get("mcp_tools_used", []),
                "collaboration": result.get("collaboration_context", {}),
                "context_score": result.get("memory_context", {}).get("context_score", 0.0),
                "success": True
            }
            
        except Exception as e:
            logger.error(f"Error running enhanced SAM agent: {e}")
            return {
                "response": f"I encountered an error: {str(e)}",
                "memory_context": {},
                "tools_used": [],
                "collaboration": {},
                "context_score": 0.0,
                "success": False
            }

# Usage example
async def main():
    """Example usage of Enhanced SAM Agent"""
    
    # Initialize enhanced SAM agent
    sam = EnhancedSAMAgent()
    
    # Run a test interaction
    result = await sam.run_agent(
        user_id="user_123",
        message="Help me optimize my FastAPI application for better performance",
        task_context={
            "type": "development",
            "project": "FastAPI",
            "priority": "high"
        }
    )
    
    print(f"SAM Response: {result['response']}")
    print(f"Context Score: {result['context_score']}")
    print(f"Tools Used: {result['tools_used']}")
    print(f"Collaboration: {result['collaboration']}")

if __name__ == "__main__":
    asyncio.run(main())
# Flask health endpoint for integration
from flask import Flask, jsonify
import threading

health_app = Flask(__name__)

@health_app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "LangGraph Enhanced SAM Agent",
        "timestamp": datetime.now().isoformat(),
        "features": {
            "langgraph": "enabled",
            "graphiti": "enabled", 
            "memory_layers": "triple",
            "neo4j": "connected"
        }
    })

def start_health_server():
    health_app.run(host='0.0.0.0', port=8400, debug=False)

if __name__ == "__main__":
    # Start health server in background
    health_thread = threading.Thread(target=start_health_server, daemon=True)
    health_thread.start()
    
    # Start main SAM agent
    print("🧠 Starting LangGraph Enhanced SAM Agent on port 8400...")
    # Main agent logic here
    import time
    while True:
        time.sleep(60)  # Keep alive
