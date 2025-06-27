"""
Graphiti Knowledge Graph Integration for MCP Enterprise System
Provides temporal, relationship-aware memory with Neo4j backend
"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import json

from graphiti_core import Graphiti
from neo4j import GraphDatabase
import uuid

logger = logging.getLogger(__name__)

class MCPGraphitiIntegration:
    """
    Enhanced Graphiti integration for MCP Enterprise System
    
    Features:
    - Temporal knowledge management
    - User relationship mapping
    - Cross-agent knowledge sharing
    - Context-aware search
    - Enterprise-grade security
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize Graphiti integration with enterprise configuration"""
        
        self.config = config or {
            "neo4j_uri": os.getenv("NEO4J_URI", "bolt://localhost:7687"),
            "neo4j_username": os.getenv("NEO4J_USERNAME", "neo4j"),
            "neo4j_password": os.getenv("NEO4J_PASSWORD", "password"),
            "database_name": os.getenv("NEO4J_DATABASE", "mcp_knowledge_graph")
        }
        
        self.graphiti = None
        self.neo4j_driver = None
        self.initialized = False
        
        # Enterprise features
        self.user_context_cache = {}
        self.relationship_cache = {}
        self.temporal_index = {}
        
        logger.info("MCP Graphiti Integration initialized")
    
    async def initialize(self):
        """Initialize Graphiti and Neo4j connections"""
        
        try:
            # Initialize Graphiti client
            self.graphiti = Graphiti(
                neo4j_uri=self.config["neo4j_uri"],
                neo4j_username=self.config["neo4j_username"],
                neo4j_password=self.config["neo4j_password"]
            )
            
            # Initialize Neo4j driver for direct queries
            self.neo4j_driver = GraphDatabase.driver(
                self.config["neo4j_uri"],
                auth=(self.config["neo4j_username"], self.config["neo4j_password"])
            )
            
            # Build indices for performance
            await self.graphiti.build_indices()
            
            # Setup MCP-specific schema
            await self.setup_mcp_schema()
            
            self.initialized = True
            logger.info("Graphiti integration fully initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Graphiti: {e}")
            self.initialized = False
            raise
    
    async def setup_mcp_schema(self):
        """Setup MCP-specific knowledge graph schema"""
        
        schema_queries = [
            # User nodes with enhanced properties
            """
            CREATE CONSTRAINT user_id_unique IF NOT EXISTS
            FOR (u:MCPUser) REQUIRE u.user_id IS UNIQUE
            """,
            
            # Agent nodes for tracking different MCP agents
            """
            CREATE CONSTRAINT agent_name_unique IF NOT EXISTS
            FOR (a:MCPAgent) REQUIRE a.name IS UNIQUE
            """,
            
            # Interaction nodes for temporal tracking
            """
            CREATE INDEX interaction_timestamp IF NOT EXISTS
            FOR (i:MCPInteraction) ON (i.timestamp)
            """,
            
            # Task context nodes
            """
            CREATE INDEX task_type IF NOT EXISTS
            FOR (t:MCPTask) ON (t.type)
            """,
            
            # Memory nodes for different memory types
            """
            CREATE INDEX memory_type IF NOT EXISTS
            FOR (m:MCPMemory) ON (m.memory_type)
            """
        ]
        
        if self.neo4j_driver:
            with self.neo4j_driver.session() as session:
                for query in schema_queries:
                    try:
                        session.run(query)
                        logger.debug(f"Executed schema query: {query[:50]}...")
                    except Exception as e:
                        logger.warning(f"Schema query failed (may already exist): {e}")
    
    async def store_user_interaction(self, 
                                     user_id: str, 
                                     agent_name: str, 
                                     interaction_data: Dict) -> str:
        """Store user interaction with enhanced context"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Create episode with MCP-specific metadata
            episode = {
                "text": self._format_interaction_text(interaction_data),
                "metadata": {
                    "user_id": user_id,
                    "agent_name": agent_name,
                    "interaction_type": interaction_data.get("type", "general"),
                    "task_context": interaction_data.get("task_context", {}),
                    "tools_used": interaction_data.get("tools_used", []),
                    "memory_context": interaction_data.get("memory_context", {}),
                    "collaboration_context": interaction_data.get("collaboration_context", {}),
                    "timestamp": datetime.now().isoformat(),
                    "session_id": interaction_data.get("session_id", str(uuid.uuid4())),
                    "success": interaction_data.get("success", True),
                    "context_score": interaction_data.get("context_score", 0.0)
                }
            }
            
            # Store in Graphiti
            result = await self.graphiti.add_episode(episode)
            
            # Create additional MCP-specific relationships
            await self._create_mcp_relationships(user_id, agent_name, interaction_data, result.episode_id)
            
            logger.info(f"Stored interaction {result.episode_id} for user {user_id}")
            return result.episode_id
            
        except Exception as e:
            logger.error(f"Error storing user interaction: {e}")
            raise
    
    async def get_user_context(self, 
                               user_id: str, 
                               query: str, 
                               context_type: str = "comprehensive") -> Dict:
        """Get comprehensive user context with different granularities"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            context = {}
            
            # Get facts using hybrid search
            if context_type in ["comprehensive", "facts"]:
                context["facts"] = await self._get_user_facts(user_id, query)
            
            # Get relationships
            if context_type in ["comprehensive", "relationships"]:
                context["relationships"] = await self._get_user_relationships(user_id)
            
            # Get temporal context
            if context_type in ["comprehensive", "temporal"]:
                context["temporal_context"] = await self._get_temporal_context(user_id, query)
            
            # Get cross-agent insights
            if context_type in ["comprehensive", "collaboration"]:
                context["agent_insights"] = await self._get_cross_agent_insights(user_id)
            
            # Get interaction patterns
            if context_type in ["comprehensive", "patterns"]:
                context["interaction_patterns"] = await self._get_interaction_patterns(user_id)
            
            # Calculate relevance scores
            context["relevance_score"] = self._calculate_context_relevance(context, query)
            context["last_updated"] = datetime.now().isoformat()
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting user context: {e}")
            return {"error": str(e), "facts": [], "relationships": []}
    
    async def search_knowledge_graph(self, 
                                     query: str, 
                                     search_type: str = "hybrid",
                                     filters: Optional[Dict] = None,
                                     limit: int = 10) -> List[Dict]:
        """Advanced knowledge graph search with MCP-specific filters"""
        
        if not self.initialized:
            await self.initialize()
        
        try:
            # Apply MCP-specific filters
            enhanced_query = self._enhance_query_with_filters(query, filters or {})
            
            # Execute search based on type
            if search_type == "hybrid":
                results = await self.graphiti.search(
                    query=enhanced_query,
                    search_type="hybrid",
                    limit=limit
                )
            elif search_type == "temporal":
                results = await self._temporal_search(enhanced_query, filters, limit)
            elif search_type == "relationship":
                results = await self._relationship_search(enhanced_query, filters, limit)
            elif search_type == "collaboration":
                results = await self._collaboration_search(enhanced_query, filters, limit)
            else:
                results = await self.graphiti.search(
                    query=enhanced_query,
                    search_type=search_type,
                    limit=limit
                )
            
            # Enhance results with MCP context
            enhanced_results = await self._enhance_search_results(results, filters)
            
            return enhanced_results
            
        except Exception as e:
            logger.error(f"Error in knowledge graph search: {e}")
            return []
    
    async def create_user_relationship(self, 
                                       user_id: str, 
                                       relationship_type: str, 
                                       target_entity: str,
                                       metadata: Optional[Dict] = None) -> bool:
        """Create relationships between users and entities"""
        
        if not self.neo4j_driver:
            return False
        
        try:
            query = """
            MERGE (u:MCPUser {user_id: $user_id})
            MERGE (e:Entity {name: $target_entity})
            MERGE (u)-[r:RELATES_TO {type: $relationship_type}]->(e)
            SET r.created_at = datetime(),
                r.metadata = $metadata
            RETURN r
            """
            
            with self.neo4j_driver.session() as session:
                result = session.run(query, {
                    "user_id": user_id,
                    "relationship_type": relationship_type,
                    "target_entity": target_entity,
                    "metadata": json.dumps(metadata or {})
                })
                
                return result.single() is not None
                
        except Exception as e:
            logger.error(f"Error creating user relationship: {e}")
            return False
    
    async def get_agent_collaboration_context(self, 
                                              requesting_agent: str, 
                                              user_id: str,
                                              task_context: Dict) -> Dict:
        """Get collaboration context for multi-agent coordination"""
        
        try:
            # Find interactions with other agents for this user
            collab_query = f"""
            MATCH (u:MCPUser {{user_id: '{user_id}'}})-[:INTERACTED_WITH]->(a:MCPAgent)
            WHERE a.name <> '{requesting_agent}'
            MATCH (u)-[:HAD_INTERACTION]->(i:MCPInteraction)-[:WITH_AGENT]->(a)
            RETURN a.name as agent, i.task_context as context, i.timestamp as timestamp
            ORDER BY i.timestamp DESC
            LIMIT 10
            """
            
            if self.neo4j_driver:
                with self.neo4j_driver.session() as session:
                    result = session.run(collab_query)
                    
                    collaboration_data = []
                    for record in result:
                        collaboration_data.append({
                            "agent": record["agent"],
                            "context": json.loads(record["context"]) if record["context"] else {},
                            "timestamp": record["timestamp"]
                        })
                    
                    return {
                        "relevant_agents": list(set([item["agent"] for item in collaboration_data])),
                        "shared_contexts": collaboration_data[:5],
                        "collaboration_opportunities": self._identify_collaboration_opportunities(
                            collaboration_data, task_context
                        )
                    }
            
            return {"relevant_agents": [], "shared_contexts": [], "collaboration_opportunities": []}
            
        except Exception as e:
            logger.error(f"Error getting collaboration context: {e}")
            return {"relevant_agents": [], "shared_contexts": [], "collaboration_opportunities": []}
    
    # Private helper methods
    
    def _format_interaction_text(self, interaction_data: Dict) -> str:
        """Format interaction data for storage"""
        
        user_message = interaction_data.get("user_message", "")
        agent_response = interaction_data.get("agent_response", "")
        tools_used = interaction_data.get("tools_used", [])
        
        text = f"User: {user_message}\nAgent: {agent_response}"
        
        if tools_used:
            text += f"\nTools used: {', '.join(tools_used)}"
        
        return text
    
    async def _create_mcp_relationships(self, 
                                        user_id: str, 
                                        agent_name: str, 
                                        interaction_data: Dict,
                                        episode_id: str):
        """Create MCP-specific relationships in the knowledge graph"""
        
        if not self.neo4j_driver:
            return
        
        queries = [
            # User-Agent relationship
            """
            MERGE (u:MCPUser {user_id: $user_id})
            MERGE (a:MCPAgent {name: $agent_name})
            MERGE (u)-[r:INTERACTED_WITH]->(a)
            SET r.last_interaction = datetime(),
                r.interaction_count = COALESCE(r.interaction_count, 0) + 1
            """,
            
            # Interaction node
            """
            MERGE (u:MCPUser {user_id: $user_id})
            MERGE (a:MCPAgent {name: $agent_name})
            CREATE (i:MCPInteraction {
                episode_id: $episode_id,
                timestamp: datetime(),
                task_context: $task_context,
                success: $success
            })
            CREATE (u)-[:HAD_INTERACTION]->(i)
            CREATE (i)-[:WITH_AGENT]->(a)
            """,
            
            # Task context relationships
            """
            MATCH (i:MCPInteraction {episode_id: $episode_id})
            WITH i, $task_context as context
            WHERE context.type IS NOT NULL
            MERGE (t:MCPTask {type: context.type})
            CREATE (i)-[:RELATED_TO_TASK]->(t)
            """
        ]
        
        with self.neo4j_driver.session() as session:
            for query in queries:
                try:
                    session.run(query, {
                        "user_id": user_id,
                        "agent_name": agent_name,
                        "episode_id": episode_id,
                        "task_context": json.dumps(interaction_data.get("task_context", {})),
                        "success": interaction_data.get("success", True)
                    })
                except Exception as e:
                    logger.warning(f"Failed to create relationship: {e}")
    
    async def _get_user_facts(self, user_id: str, query: str) -> List[str]:
        """Get user-specific facts from knowledge graph"""
        
        try:
            search_query = f"user:{user_id} {query}"
            results = await self.graphiti.search(
                query=search_query,
                search_type="hybrid",
                limit=10
            )
            
            return [str(result) for result in results] if results else []
            
        except Exception as e:
            logger.error(f"Error getting user facts: {e}")
            return []
    
    async def _get_user_relationships(self, user_id: str) -> List[Dict]:
        """Get user relationships from knowledge graph"""
        
        if not self.neo4j_driver:
            return []
        
        query = """
        MATCH (u:MCPUser {user_id: $user_id})-[r]->(n)
        RETURN type(r) as relationship_type, n.name as entity_name, r.metadata as metadata
        LIMIT 10
        """
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query, {"user_id": user_id})
                
                relationships = []
                for record in result:
                    relationships.append({
                        "type": record["relationship_type"],
                        "entity": record["entity_name"],
                        "metadata": json.loads(record["metadata"]) if record["metadata"] else {}
                    })
                
                return relationships
                
        except Exception as e:
            logger.error(f"Error getting user relationships: {e}")
            return []
    
    async def _get_temporal_context(self, user_id: str, query: str) -> List[Dict]:
        """Get temporal context for user interactions"""
        
        if not self.neo4j_driver:
            return []
        
        # Get interactions from last week
        query_cypher = """
        MATCH (u:MCPUser {user_id: $user_id})-[:HAD_INTERACTION]->(i:MCPInteraction)
        WHERE i.timestamp >= datetime() - duration('P7D')
        RETURN i.episode_id as episode_id, i.timestamp as timestamp, i.task_context as task_context
        ORDER BY i.timestamp DESC
        LIMIT 5
        """
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(query_cypher, {"user_id": user_id})
                
                temporal_context = []
                for record in result:
                    temporal_context.append({
                        "episode_id": record["episode_id"],
                        "timestamp": record["timestamp"],
                        "task_context": json.loads(record["task_context"]) if record["task_context"] else {}
                    })
                
                return temporal_context
                
        except Exception as e:
            logger.error(f"Error getting temporal context: {e}")
            return []
    
    async def _get_cross_agent_insights(self, user_id: str) -> List[Dict]:
        """Get insights from different agents about the user"""
        
        try:
            # Search for interactions with different agents
            insights_query = f"user:{user_id} agent_type:Manus OR agent_type:WebSearch OR agent_type:Telegram"
            results = await self.graphiti.search(
                query=insights_query,
                search_type="hybrid",
                limit=5
            )
            
            return [{"insight": str(result), "source": "knowledge_graph"} for result in results] if results else []
            
        except Exception as e:
            logger.error(f"Error getting cross-agent insights: {e}")
            return []
    
    async def _get_interaction_patterns(self, user_id: str) -> Dict:
        """Analyze user interaction patterns"""
        
        if not self.neo4j_driver:
            return {}
        
        pattern_query = """
        MATCH (u:MCPUser {user_id: $user_id})-[:HAD_INTERACTION]->(i:MCPInteraction)-[:WITH_AGENT]->(a:MCPAgent)
        WITH u, a, count(i) as interaction_count, max(i.timestamp) as last_interaction
        RETURN a.name as agent, interaction_count, last_interaction
        ORDER BY interaction_count DESC
        """
        
        try:
            with self.neo4j_driver.session() as session:
                result = session.run(pattern_query, {"user_id": user_id})
                
                patterns = {
                    "preferred_agents": [],
                    "interaction_frequency": {},
                    "last_interactions": {}
                }
                
                for record in result:
                    agent = record["agent"]
                    count = record["interaction_count"]
                    last = record["last_interaction"]
                    
                    patterns["preferred_agents"].append(agent)
                    patterns["interaction_frequency"][agent] = count
                    patterns["last_interactions"][agent] = str(last)
                
                return patterns
                
        except Exception as e:
            logger.error(f"Error getting interaction patterns: {e}")
            return {}
    
    def _calculate_context_relevance(self, context: Dict, query: str) -> float:
        """Calculate relevance score for retrieved context"""
        
        if not query:
            return 0.0
        
        query_words = set(query.lower().split())
        total_score = 0.0
        total_items = 0
        
        # Score facts
        facts = context.get("facts", [])
        for fact in facts:
            fact_words = set(str(fact).lower().split())
            if query_words.intersection(fact_words):
                total_score += 1.0
            total_items += 1
        
        # Score relationships
        relationships = context.get("relationships", [])
        for rel in relationships:
            rel_text = f"{rel.get('type', '')} {rel.get('entity', '')}".lower()
            rel_words = set(rel_text.split())
            if query_words.intersection(rel_words):
                total_score += 0.8
            total_items += 1
        
        return total_score / total_items if total_items > 0 else 0.0
    
    def _enhance_query_with_filters(self, query: str, filters: Dict) -> str:
        """Enhance search query with MCP-specific filters"""
        
        enhanced_query = query
        
        if filters.get("agent_type"):
            enhanced_query += f" agent_type:{filters['agent_type']}"
        
        if filters.get("task_type"):
            enhanced_query += f" task_type:{filters['task_type']}"
        
        if filters.get("time_range"):
            enhanced_query += f" time_range:{filters['time_range']}"
        
        if filters.get("success_only"):
            enhanced_query += " success:true"
        
        return enhanced_query
    
    async def _temporal_search(self, query: str, filters: Dict, limit: int) -> List:
        """Perform temporal-specific search"""
        # Implementation would use Graphiti's temporal search capabilities
        # For now, return empty list as placeholder
        return []
    
    async def _relationship_search(self, query: str, filters: Dict, limit: int) -> List:
        """Perform relationship-specific search"""
        # Implementation would use Neo4j relationship traversal
        # For now, return empty list as placeholder
        return []
    
    async def _collaboration_search(self, query: str, filters: Dict, limit: int) -> List:
        """Perform collaboration-specific search"""
        # Implementation would find multi-agent contexts
        # For now, return empty list as placeholder
        return []
    
    async def _enhance_search_results(self, results: List, filters: Dict) -> List[Dict]:
        """Enhance search results with additional MCP context"""
        
        enhanced_results = []
        
        for result in results:
            enhanced_result = {
                "content": str(result),
                "source": "graphiti",
                "timestamp": datetime.now().isoformat(),
                "relevance_score": 0.8  # Placeholder scoring
            }
            
            # Add MCP-specific enhancements based on filters
            if filters.get("include_metadata"):
                enhanced_result["metadata"] = getattr(result, "metadata", {})
            
            enhanced_results.append(enhanced_result)
        
        return enhanced_results
    
    def _identify_collaboration_opportunities(self, collaboration_data: List[Dict], task_context: Dict) -> List[str]:
        """Identify opportunities for agent collaboration"""
        
        opportunities = []
        task_type = task_context.get("type", "").lower()
        
        # Analyze past collaborations for similar tasks
        similar_contexts = [
            item for item in collaboration_data
            if item.get("context", {}).get("type", "").lower() == task_type
        ]
        
        if similar_contexts:
            opportunities.append("Previous successful collaboration pattern identified")
        
        # Check for complementary agent capabilities
        agent_types = [item.get("agent") for item in collaboration_data]
        if "Manus" in agent_types and task_type in ["development", "analysis"]:
            opportunities.append("Manus collaboration recommended for technical tasks")
        
        if "WebSearch" in agent_types and task_type in ["research", "information"]:
            opportunities.append("WebSearch collaboration recommended for research tasks")
        
        return opportunities
    
    async def close(self):
        """Close connections and cleanup"""
        
        if self.neo4j_driver:
            self.neo4j_driver.close()
        
        # Note: Graphiti client doesn't have explicit close method
        self.initialized = False
        logger.info("Graphiti integration closed")

# Usage example
async def main():
    """Example usage of MCP Graphiti Integration"""
    
    # Initialize integration
    graphiti_integration = MCPGraphitiIntegration()
    await graphiti_integration.initialize()
    
    # Store a test interaction
    interaction_id = await graphiti_integration.store_user_interaction(
        user_id="user_123",
        agent_name="SAM",
        interaction_data={
            "user_message": "Help me optimize my FastAPI application",
            "agent_response": "I'll help you optimize your FastAPI app...",
            "type": "development_assistance",
            "task_context": {"type": "development", "framework": "FastAPI"},
            "tools_used": ["github", "documentation"],
            "success": True,
            "context_score": 0.85
        }
    )
    
    print(f"Stored interaction: {interaction_id}")
    
    # Get user context
    context = await graphiti_integration.get_user_context(
        user_id="user_123",
        query="FastAPI optimization performance",
        context_type="comprehensive"
    )
    
    print(f"User context: {context}")
    
    # Search knowledge graph
    search_results = await graphiti_integration.search_knowledge_graph(
        query="FastAPI performance optimization",
        search_type="hybrid",
        filters={"agent_type": "SAM", "task_type": "development"},
        limit=5
    )
    
    print(f"Search results: {search_results}")
    
    # Get collaboration context
    collab_context = await graphiti_integration.get_agent_collaboration_context(
        requesting_agent="SAM",
        user_id="user_123",
        task_context={"type": "development", "framework": "FastAPI"}
    )
    
    print(f"Collaboration context: {collab_context}")
    
    # Cleanup
    await graphiti_integration.close()

if __name__ == "__main__":
    asyncio.run(main())