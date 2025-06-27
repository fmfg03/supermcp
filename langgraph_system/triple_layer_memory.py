"""
Triple-Layer Memory System for MCP Enterprise
Combines immediate (LangGraph), short-term (MCP), and long-term (Graphiti) memory
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
import json
import numpy as np
from dataclasses import dataclass

# MCP System imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from backend.sam_memory_analyzer import SAMMemoryAnalyzer
from langgraph_system.graphiti_integration import MCPGraphitiIntegration

logger = logging.getLogger(__name__)

@dataclass
class MemoryContext:
    """Data class for memory context with relevance scoring"""
    content: str
    source: str  # 'immediate', 'short_term', 'long_term'
    timestamp: datetime
    relevance_score: float
    metadata: Dict[str, Any]
    memory_type: str  # 'conversation', 'factual', 'procedural', 'relational'

class TripleLayerMemorySystem:
    """
    Advanced triple-layer memory system for MCP Enterprise
    
    Architecture:
    - IMMEDIATE (LangGraph): Current conversation state and context
    - SHORT-TERM (MCP): Recent interactions, embeddings, and working memory  
    - LONG-TERM (Graphiti): Relationships, temporal patterns, and knowledge graph
    
    Features:
    - Intelligent memory consolidation
    - Contextual relevance scoring
    - Memory type classification
    - Temporal decay modeling
    - Cross-layer memory synthesis
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """Initialize triple-layer memory system"""
        
        self.config = config or {}
        
        # Initialize memory layers
        self.immediate_memory = {}  # LangGraph state memory
        self.short_term_memory = SAMMemoryAnalyzer()  # MCP memory system
        self.long_term_memory = MCPGraphitiIntegration()  # Graphiti knowledge graph
        
        # Memory configuration
        self.immediate_capacity = self.config.get("immediate_capacity", 50)
        self.short_term_capacity = self.config.get("short_term_capacity", 1000)
        self.consolidation_threshold = self.config.get("consolidation_threshold", 0.7)
        self.relevance_threshold = self.config.get("relevance_threshold", 0.5)
        
        # Memory weights for different types
        self.memory_weights = {
            "conversation": 1.0,
            "factual": 0.9,
            "procedural": 0.8,
            "relational": 0.85
        }
        
        # Temporal decay parameters
        self.temporal_decay = {
            "immediate": timedelta(hours=2),
            "short_term": timedelta(days=30),
            "long_term": timedelta(days=365)
        }
        
        self.initialized = False
        logger.info("Triple-layer memory system initialized")
    
    async def initialize(self):
        """Initialize all memory layers"""
        
        try:
            # Initialize long-term memory (Graphiti)
            await self.long_term_memory.initialize()
            
            # Short-term memory (MCP) is typically initialized elsewhere
            # Immediate memory is in-memory dictionary
            
            self.initialized = True
            logger.info("All memory layers initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize memory layers: {e}")
            raise
    
    async def store_memory(self, 
                           user_id: str, 
                           content: str, 
                           memory_type: str = "conversation",
                           context: Optional[Dict] = None,
                           agent_name: str = "SAM") -> str:
        """Store memory across all appropriate layers"""
        
        if not self.initialized:
            await self.initialize()
        
        memory_id = f"mem_{datetime.now().timestamp()}_{user_id}"
        timestamp = datetime.now()
        
        # Prepare memory data
        memory_data = {
            "content": content,
            "memory_type": memory_type,
            "context": context or {},
            "timestamp": timestamp,
            "user_id": user_id,
            "agent_name": agent_name
        }
        
        # Store in immediate memory (always)
        await self._store_immediate_memory(user_id, memory_id, memory_data)
        
        # Determine if should store in short-term memory
        if await self._should_store_short_term(memory_data):
            await self._store_short_term_memory(user_id, memory_data)
        
        # Determine if should store in long-term memory
        if await self._should_store_long_term(memory_data):
            await self._store_long_term_memory(user_id, memory_data)
        
        # Trigger memory consolidation if needed
        await self._consolidate_memories(user_id)
        
        logger.debug(f"Stored memory {memory_id} for user {user_id}")
        return memory_id
    
    async def retrieve_contextual_memory(self, 
                                         user_id: str, 
                                         query: str,
                                         max_memories: int = 10,
                                         memory_types: Optional[List[str]] = None) -> List[MemoryContext]:
        """Retrieve contextually relevant memories from all layers"""
        
        if not self.initialized:
            await self.initialize()
        
        all_memories = []
        
        # Retrieve from immediate memory
        immediate_memories = await self._retrieve_immediate_memory(user_id, query)
        all_memories.extend(immediate_memories)
        
        # Retrieve from short-term memory
        short_term_memories = await self._retrieve_short_term_memory(user_id, query)
        all_memories.extend(short_term_memories)
        
        # Retrieve from long-term memory
        long_term_memories = await self._retrieve_long_term_memory(user_id, query)
        all_memories.extend(long_term_memories)
        
        # Filter by memory types if specified
        if memory_types:
            all_memories = [m for m in all_memories if m.memory_type in memory_types]
        
        # Score and rank memories by relevance
        scored_memories = await self._score_memory_relevance(all_memories, query)
        
        # Apply temporal decay
        decayed_memories = self._apply_temporal_decay(scored_memories)
        
        # Sort by final relevance score and return top memories
        final_memories = sorted(decayed_memories, key=lambda m: m.relevance_score, reverse=True)
        
        return final_memories[:max_memories]
    
    async def synthesize_memory_context(self, 
                                        user_id: str, 
                                        query: str,
                                        synthesis_type: str = "comprehensive") -> Dict[str, Any]:
        """Synthesize memory context across all layers for enhanced prompts"""
        
        # Retrieve memories from all layers
        memories = await self.retrieve_contextual_memory(user_id, query, max_memories=15)
        
        # Group memories by layer and type
        synthesis = {
            "immediate_context": [],
            "short_term_insights": [],
            "long_term_knowledge": [],
            "memory_summary": {},
            "contextual_score": 0.0,
            "synthesis_metadata": {
                "synthesis_type": synthesis_type,
                "total_memories": len(memories),
                "timestamp": datetime.now().isoformat()
            }
        }
        
        # Categorize memories by source
        for memory in memories:
            if memory.source == "immediate":
                synthesis["immediate_context"].append({
                    "content": memory.content,
                    "relevance": memory.relevance_score,
                    "type": memory.memory_type
                })
            elif memory.source == "short_term":
                synthesis["short_term_insights"].append({
                    "content": memory.content,
                    "relevance": memory.relevance_score,
                    "type": memory.memory_type
                })
            elif memory.source == "long_term":
                synthesis["long_term_knowledge"].append({
                    "content": memory.content,
                    "relevance": memory.relevance_score,
                    "type": memory.memory_type
                })
        
        # Create memory summary by type
        memory_by_type = {}
        for memory in memories:
            if memory.memory_type not in memory_by_type:
                memory_by_type[memory.memory_type] = []
            memory_by_type[memory.memory_type].append(memory)
        
        synthesis["memory_summary"] = {
            mem_type: {
                "count": len(mems),
                "avg_relevance": np.mean([m.relevance_score for m in mems]),
                "top_content": [m.content for m in sorted(mems, key=lambda x: x.relevance_score, reverse=True)[:3]]
            }
            for mem_type, mems in memory_by_type.items()
        }
        
        # Calculate overall contextual score
        if memories:
            synthesis["contextual_score"] = np.mean([m.relevance_score for m in memories])
        
        # Enhanced synthesis for different types
        if synthesis_type == "comprehensive":
            synthesis.update(await self._comprehensive_synthesis(memories, user_id, query))
        elif synthesis_type == "focused":
            synthesis.update(await self._focused_synthesis(memories, user_id, query))
        elif synthesis_type == "collaborative":
            synthesis.update(await self._collaborative_synthesis(memories, user_id, query))
        
        return synthesis
    
    async def consolidate_memories(self, user_id: str) -> Dict[str, int]:
        """Manually trigger memory consolidation process"""
        
        consolidation_stats = {
            "immediate_to_short": 0,
            "short_to_long": 0,
            "consolidated_patterns": 0,
            "removed_duplicates": 0
        }
        
        # Consolidate immediate to short-term
        immediate_memories = self.immediate_memory.get(user_id, {})
        for memory_id, memory_data in immediate_memories.items():
            if await self._should_consolidate_to_short_term(memory_data):
                await self._store_short_term_memory(user_id, memory_data)
                consolidation_stats["immediate_to_short"] += 1
        
        # Consolidate short-term to long-term
        short_term_memories = await self._get_short_term_memories(user_id)
        for memory in short_term_memories:
            if await self._should_consolidate_to_long_term(memory):
                await self._store_long_term_memory(user_id, memory)
                consolidation_stats["short_to_long"] += 1
        
        # Identify and consolidate patterns
        patterns = await self._identify_memory_patterns(user_id)
        for pattern in patterns:
            await self._consolidate_pattern(user_id, pattern)
            consolidation_stats["consolidated_patterns"] += 1
        
        # Remove duplicates
        duplicates_removed = await self._remove_duplicate_memories(user_id)
        consolidation_stats["removed_duplicates"] = duplicates_removed
        
        logger.info(f"Memory consolidation completed for user {user_id}: {consolidation_stats}")
        return consolidation_stats
    
    # Private methods for memory layer operations
    
    async def _store_immediate_memory(self, user_id: str, memory_id: str, memory_data: Dict):
        """Store memory in immediate layer (LangGraph state)"""
        
        if user_id not in self.immediate_memory:
            self.immediate_memory[user_id] = {}
        
        # Enforce capacity limits
        if len(self.immediate_memory[user_id]) >= self.immediate_capacity:
            # Remove oldest memory
            oldest_id = min(self.immediate_memory[user_id].keys(), 
                           key=lambda x: self.immediate_memory[user_id][x]["timestamp"])
            del self.immediate_memory[user_id][oldest_id]
        
        self.immediate_memory[user_id][memory_id] = memory_data
    
    async def _store_short_term_memory(self, user_id: str, memory_data: Dict):
        """Store memory in short-term layer (MCP system)"""
        
        try:
            await self.short_term_memory.store_interaction({
                "user_id": user_id,
                "content": memory_data["content"],
                "memory_type": memory_data["memory_type"],
                "context": memory_data["context"],
                "timestamp": memory_data["timestamp"],
                "agent_name": memory_data["agent_name"]
            })
        except Exception as e:
            logger.error(f"Error storing short-term memory: {e}")
    
    async def _store_long_term_memory(self, user_id: str, memory_data: Dict):
        """Store memory in long-term layer (Graphiti knowledge graph)"""
        
        try:
            interaction_data = {
                "user_message": memory_data.get("context", {}).get("user_message", ""),
                "agent_response": memory_data["content"],
                "type": memory_data["memory_type"],
                "task_context": memory_data.get("context", {}),
                "success": True,
                "timestamp": memory_data["timestamp"]
            }
            
            await self.long_term_memory.store_user_interaction(
                user_id=user_id,
                agent_name=memory_data["agent_name"],
                interaction_data=interaction_data
            )
        except Exception as e:
            logger.error(f"Error storing long-term memory: {e}")
    
    async def _retrieve_immediate_memory(self, user_id: str, query: str) -> List[MemoryContext]:
        """Retrieve memories from immediate layer"""
        
        memories = []
        user_memories = self.immediate_memory.get(user_id, {})
        
        for memory_id, memory_data in user_memories.items():
            relevance = self._calculate_text_similarity(query, memory_data["content"])
            
            if relevance >= self.relevance_threshold:
                memory_context = MemoryContext(
                    content=memory_data["content"],
                    source="immediate",
                    timestamp=memory_data["timestamp"],
                    relevance_score=relevance,
                    metadata=memory_data.get("context", {}),
                    memory_type=memory_data["memory_type"]
                )
                memories.append(memory_context)
        
        return memories
    
    async def _retrieve_short_term_memory(self, user_id: str, query: str) -> List[MemoryContext]:
        """Retrieve memories from short-term layer"""
        
        memories = []
        
        try:
            # Use MCP memory analyzer to search
            mcp_memories = await self.short_term_memory.search_memories(
                query=query,
                user_id=user_id,
                limit=10
            )
            
            for mcp_memory in mcp_memories:
                memory_context = MemoryContext(
                    content=str(mcp_memory.get("content", mcp_memory)),
                    source="short_term",
                    timestamp=mcp_memory.get("timestamp", datetime.now()),
                    relevance_score=mcp_memory.get("relevance_score", 0.7),
                    metadata=mcp_memory.get("metadata", {}),
                    memory_type=mcp_memory.get("memory_type", "conversation")
                )
                memories.append(memory_context)
        
        except Exception as e:
            logger.error(f"Error retrieving short-term memories: {e}")
        
        return memories
    
    async def _retrieve_long_term_memory(self, user_id: str, query: str) -> List[MemoryContext]:
        """Retrieve memories from long-term layer"""
        
        memories = []
        
        try:
            # Get comprehensive context from Graphiti
            context = await self.long_term_memory.get_user_context(
                user_id=user_id,
                query=query,
                context_type="comprehensive"
            )
            
            # Convert facts to memory contexts
            for fact in context.get("facts", []):
                memory_context = MemoryContext(
                    content=str(fact),
                    source="long_term",
                    timestamp=datetime.now() - timedelta(days=7),  # Approximate
                    relevance_score=context.get("relevance_score", 0.6),
                    metadata={"source": "knowledge_graph"},
                    memory_type="factual"
                )
                memories.append(memory_context)
            
            # Convert relationships to memory contexts
            for relationship in context.get("relationships", []):
                memory_context = MemoryContext(
                    content=f"Relationship: {relationship.get('type')} with {relationship.get('entity')}",
                    source="long_term",
                    timestamp=datetime.now() - timedelta(days=14),  # Approximate
                    relevance_score=context.get("relevance_score", 0.5),
                    metadata=relationship,
                    memory_type="relational"
                )
                memories.append(memory_context)
        
        except Exception as e:
            logger.error(f"Error retrieving long-term memories: {e}")
        
        return memories
    
    async def _score_memory_relevance(self, memories: List[MemoryContext], query: str) -> List[MemoryContext]:
        """Score and adjust memory relevance based on query"""
        
        scored_memories = []
        
        for memory in memories:
            # Calculate semantic similarity
            semantic_score = self._calculate_text_similarity(query, memory.content)
            
            # Apply memory type weights
            type_weight = self.memory_weights.get(memory.memory_type, 0.7)
            
            # Apply source weights (more recent layers get higher weight)
            source_weights = {"immediate": 1.0, "short_term": 0.8, "long_term": 0.6}
            source_weight = source_weights.get(memory.source, 0.5)
            
            # Calculate final relevance score
            final_score = semantic_score * type_weight * source_weight
            
            # Create new memory context with updated score
            scored_memory = MemoryContext(
                content=memory.content,
                source=memory.source,
                timestamp=memory.timestamp,
                relevance_score=final_score,
                metadata=memory.metadata,
                memory_type=memory.memory_type
            )
            
            scored_memories.append(scored_memory)
        
        return scored_memories
    
    def _apply_temporal_decay(self, memories: List[MemoryContext]) -> List[MemoryContext]:
        """Apply temporal decay to memory relevance scores"""
        
        decayed_memories = []
        current_time = datetime.now()
        
        for memory in memories:
            # Calculate time difference
            time_diff = current_time - memory.timestamp
            
            # Get decay threshold for memory source
            decay_threshold = self.temporal_decay.get(memory.source, timedelta(days=7))
            
            # Calculate decay factor (0.1 to 1.0)
            if time_diff <= decay_threshold:
                decay_factor = 1.0 - (time_diff.total_seconds() / decay_threshold.total_seconds()) * 0.9
            else:
                decay_factor = 0.1
            
            # Apply decay to relevance score
            decayed_score = memory.relevance_score * max(decay_factor, 0.1)
            
            # Create new memory context with decayed score
            decayed_memory = MemoryContext(
                content=memory.content,
                source=memory.source,
                timestamp=memory.timestamp,
                relevance_score=decayed_score,
                metadata=memory.metadata,
                memory_type=memory.memory_type
            )
            
            decayed_memories.append(decayed_memory)
        
        return decayed_memories
    
    def _calculate_text_similarity(self, text1: str, text2: str) -> float:
        """Calculate semantic similarity between two texts"""
        
        # Simple word overlap similarity (in production, use embeddings)
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union) if union else 0.0
    
    async def _should_store_short_term(self, memory_data: Dict) -> bool:
        """Determine if memory should be stored in short-term layer"""
        
        # Store in short-term if:
        # 1. Memory type is important (conversation, factual, procedural)
        # 2. Content is substantial
        # 3. Has contextual information
        
        important_types = ["conversation", "factual", "procedural"]
        
        return (memory_data["memory_type"] in important_types and
                len(memory_data["content"]) > 10 and
                bool(memory_data.get("context")))
    
    async def _should_store_long_term(self, memory_data: Dict) -> bool:
        """Determine if memory should be stored in long-term layer"""
        
        # Store in long-term if:
        # 1. Memory type is relational or factual
        # 2. Content indicates learning or relationship building
        # 3. Has rich context
        
        long_term_types = ["factual", "relational", "procedural"]
        long_term_indicators = ["learned", "relationship", "pattern", "insight", "knowledge"]
        
        content_indicates_importance = any(
            indicator in memory_data["content"].lower() 
            for indicator in long_term_indicators
        )
        
        return (memory_data["memory_type"] in long_term_types or
                content_indicates_importance)
    
    async def _consolidate_memories(self, user_id: str):
        """Trigger memory consolidation if thresholds are met"""
        
        # Check if consolidation is needed
        immediate_count = len(self.immediate_memory.get(user_id, {}))
        
        if immediate_count >= self.immediate_capacity * 0.8:
            await self.consolidate_memories(user_id)
    
    async def _comprehensive_synthesis(self, memories: List[MemoryContext], user_id: str, query: str) -> Dict:
        """Comprehensive memory synthesis for detailed context"""
        
        return {
            "synthesis_approach": "comprehensive",
            "memory_layers_analysis": {
                "immediate_weight": 0.4,
                "short_term_weight": 0.4,
                "long_term_weight": 0.2
            },
            "contextual_insights": self._extract_contextual_insights(memories),
            "temporal_patterns": self._identify_temporal_patterns(memories),
            "relationship_map": self._build_relationship_map(memories)
        }
    
    async def _focused_synthesis(self, memories: List[MemoryContext], user_id: str, query: str) -> Dict:
        """Focused memory synthesis for specific tasks"""
        
        # Filter to most relevant memories
        top_memories = sorted(memories, key=lambda m: m.relevance_score, reverse=True)[:5]
        
        return {
            "synthesis_approach": "focused",
            "focus_area": query,
            "key_memories": [{"content": m.content, "relevance": m.relevance_score} for m in top_memories],
            "primary_insights": self._extract_primary_insights(top_memories)
        }
    
    async def _collaborative_synthesis(self, memories: List[MemoryContext], user_id: str, query: str) -> Dict:
        """Collaborative memory synthesis for multi-agent coordination"""
        
        agent_memories = {}
        for memory in memories:
            agent = memory.metadata.get("agent_name", "unknown")
            if agent not in agent_memories:
                agent_memories[agent] = []
            agent_memories[agent].append(memory)
        
        return {
            "synthesis_approach": "collaborative",
            "agent_perspectives": {
                agent: {
                    "memory_count": len(mems),
                    "avg_relevance": np.mean([m.relevance_score for m in mems]),
                    "key_insights": [m.content for m in sorted(mems, key=lambda x: x.relevance_score, reverse=True)[:2]]
                }
                for agent, mems in agent_memories.items()
            },
            "cross_agent_patterns": self._identify_cross_agent_patterns(agent_memories)
        }
    
    # Helper methods for synthesis
    
    def _extract_contextual_insights(self, memories: List[MemoryContext]) -> List[str]:
        """Extract key contextual insights from memories"""
        insights = []
        for memory in memories[:5]:  # Top 5 most relevant
            if memory.relevance_score > 0.7:
                insights.append(f"High relevance: {memory.content[:100]}...")
        return insights
    
    def _identify_temporal_patterns(self, memories: List[MemoryContext]) -> Dict:
        """Identify temporal patterns in memories"""
        
        # Group memories by time periods
        recent = [m for m in memories if (datetime.now() - m.timestamp).days <= 1]
        weekly = [m for m in memories if 1 < (datetime.now() - m.timestamp).days <= 7]
        older = [m for m in memories if (datetime.now() - m.timestamp).days > 7]
        
        return {
            "recent_activity": len(recent),
            "weekly_pattern": len(weekly),
            "historical_context": len(older),
            "trend": "increasing" if len(recent) > len(weekly) else "stable"
        }
    
    def _build_relationship_map(self, memories: List[MemoryContext]) -> Dict:
        """Build relationship map from memory content"""
        
        relationships = {}
        for memory in memories:
            if memory.memory_type == "relational":
                # Extract relationship information
                relationships[memory.content] = {
                    "strength": memory.relevance_score,
                    "timestamp": memory.timestamp.isoformat()
                }
        
        return relationships
    
    def _extract_primary_insights(self, memories: List[MemoryContext]) -> List[str]:
        """Extract primary insights from top memories"""
        return [memory.content for memory in memories if memory.relevance_score > 0.8]
    
    def _identify_cross_agent_patterns(self, agent_memories: Dict) -> List[str]:
        """Identify patterns across different agents"""
        patterns = []
        
        if len(agent_memories) > 1:
            patterns.append("Multi-agent collaboration detected")
        
        # Check for complementary capabilities
        agent_names = list(agent_memories.keys())
        if "SAM" in agent_names and "Manus" in agent_names:
            patterns.append("Technical coordination pattern identified")
        
        return patterns
    
    # Placeholder methods for advanced consolidation features
    
    async def _should_consolidate_to_short_term(self, memory_data: Dict) -> bool:
        """Determine if immediate memory should be consolidated to short-term"""
        return True  # Simplified logic
    
    async def _should_consolidate_to_long_term(self, memory: Dict) -> bool:
        """Determine if short-term memory should be consolidated to long-term"""
        return True  # Simplified logic
    
    async def _get_short_term_memories(self, user_id: str) -> List[Dict]:
        """Get memories from short-term storage"""
        return []  # Placeholder
    
    async def _identify_memory_patterns(self, user_id: str) -> List[Dict]:
        """Identify patterns in user memories for consolidation"""
        return []  # Placeholder
    
    async def _consolidate_pattern(self, user_id: str, pattern: Dict):
        """Consolidate identified pattern into knowledge graph"""
        pass  # Placeholder
    
    async def _remove_duplicate_memories(self, user_id: str) -> int:
        """Remove duplicate memories across layers"""
        return 0  # Placeholder

# Usage example
async def main():
    """Example usage of Triple-Layer Memory System"""
    
    # Initialize memory system
    memory_system = TripleLayerMemorySystem()
    await memory_system.initialize()
    
    # Store some test memories
    await memory_system.store_memory(
        user_id="user_123",
        content="User is working on FastAPI optimization project",
        memory_type="factual",
        context={"project": "FastAPI", "goal": "optimization"},
        agent_name="SAM"
    )
    
    await memory_system.store_memory(
        user_id="user_123", 
        content="Discussed database indexing strategies",
        memory_type="procedural",
        context={"topic": "database", "subtopic": "indexing"},
        agent_name="SAM"
    )
    
    # Retrieve contextual memories
    relevant_memories = await memory_system.retrieve_contextual_memory(
        user_id="user_123",
        query="FastAPI performance database optimization",
        max_memories=5
    )
    
    print(f"Retrieved {len(relevant_memories)} relevant memories:")
    for memory in relevant_memories:
        print(f"- {memory.source}: {memory.content} (relevance: {memory.relevance_score:.2f})")
    
    # Synthesize memory context for enhanced prompts
    synthesis = await memory_system.synthesize_memory_context(
        user_id="user_123",
        query="FastAPI optimization help",
        synthesis_type="comprehensive"
    )
    
    print(f"\nMemory synthesis:")
    print(f"- Contextual score: {synthesis['contextual_score']:.2f}")
    print(f"- Total memories: {synthesis['synthesis_metadata']['total_memories']}")
    print(f"- Memory summary: {synthesis['memory_summary']}")

if __name__ == "__main__":
    asyncio.run(main())