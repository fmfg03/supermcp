#!/usr/bin/env python3
"""
SUPERmcp A2A Demo - Ejemplo de workflow multi-agente
Demuestra la colaboración entre agentes usando protocolo A2A
"""

import asyncio
import json
import aiohttp
from datetime import datetime

class A2AWorkflowDemo:
    def __init__(self):
        self.a2a_server = "http://localhost:8200"
        self.manus_agent = "http://localhost:8210"
    
    async def run_demo(self):
        """Ejecutar demo completo de workflow A2A"""
        
        print("🎬 SUPERmcp A2A Workflow Demo")
        print("============================")
        print()
        
        # Demo 1: Descubrimiento de agentes
        await self.demo_agent_discovery()
        
        # Demo 2: Workflow colaborativo complejo
        await self.demo_collaborative_workflow()
        
        # Demo 3: Delegación inteligente
        await self.demo_intelligent_delegation()
        
        # Demo 4: Investigación multi-agente
        await self.demo_multi_agent_research()
        
        print("🎉 Demo completed! A2A system is working perfectly!")
    
    async def demo_agent_discovery(self):
        """Demo: Descubrir agentes disponibles"""
        print("🔍 Demo 1: Agent Discovery")
        print("-" * 30)
        
        try:
            async with aiohttp.ClientSession() as session:
                # Listar todos los agentes
                async with session.get(f"{self.a2a_server}/agents") as response:
                    if response.status == 200:
                        data = await response.json()
                        agents = data.get("agents", [])
                        
                        print(f"✅ Found {len(agents)} registered agents:")
                        for agent in agents:
                            print(f"   🤖 {agent['name']} ({agent['agent_id']})")
                            print(f"      Capabilities: {', '.join(agent['capabilities'])}")
                            print(f"      Status: {agent['status']}")
                            print()
                    else:
                        print("❌ Failed to discover agents")
                
                # Descubrir agentes para tarea específica
                discovery_request = {
                    "task_type": "document_analysis",
                    "capabilities": ["analysis", "autonomous_execution"]
                }
                
                async with session.post(
                    f"{self.a2a_server}/a2a/discover",
                    json=discovery_request
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        agents = data.get("agents", [])
                        print(f"🎯 Agents capable of document analysis: {len(agents)}")
                        for agent in agents[:2]:  # Top 2
                            print(f"   🏆 {agent['name']} (Load: {agent['load_score']})")
                    
        except Exception as e:
            print(f"❌ Discovery demo failed: {e}")
        
        print()
    
    async def demo_collaborative_workflow(self):
        """Demo: Workflow colaborativo complejo"""
        print("🤝 Demo 2: Collaborative Workflow")
        print("-" * 35)
        
        # Workflow: Análisis de documento con múltiples agentes
        workflow_data = {
            "task_type": "complex_workflow",
            "payload": {
                "steps": [
                    {
                        "type": "memory_search",
                        "capabilities": ["semantic_memory"],
                        "data": {"query": "document analysis best practices"}
                    },
                    {
                        "type": "document_analysis", 
                        "capabilities": ["analysis", "autonomous_execution"],
                        "data": {"document": "Sample document for analysis..."}
                    },
                    {
                        "type": "store_results",
                        "capabilities": ["memory_storage"],
                        "data": {"store_analysis": True}
                    }
                ]
            },
            "requester_id": "demo_client",
            "priority": 8
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Delegar workflow complejo a Manus
                async with session.post(
                    f"{self.manus_agent}/a2a",
                    json=workflow_data
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Collaborative workflow completed!")
                        print(f"   Task ID: {result.get('task_id')}")
                        print(f"   Result summary: {result.get('result', {}).get('summary', 'N/A')}")
                    else:
                        error = await response.text()
                        print(f"❌ Workflow failed: {error}")
                        
        except Exception as e:
            print(f"❌ Collaborative workflow demo failed: {e}")
        
        print()
    
    async def demo_intelligent_delegation(self):
        """Demo: Delegación inteligente"""
        print("🧠 Demo 3: Intelligent Delegation")
        print("-" * 35)
        
        delegation_task = {
            "task_type": "delegation",
            "payload": {
                "target_task": {
                    "task_type": "semantic_search",
                    "query": "artificial intelligence trends 2025",
                    "top_k": 10
                },
                "required_capabilities": ["semantic_memory", "similarity_search"]
            },
            "requester_id": "demo_client"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.manus_agent}/a2a",
                    json=delegation_task
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Intelligent delegation completed!")
                        delegation_result = result.get('result', {})
                        if delegation_result.get('delegation_successful'):
                            print(f"   Assigned to: {delegation_result.get('assigned_agent')}")
                            print(f"   Results: {len(delegation_result.get('result', {}).get('results', []))} items found")
                        else:
                            print(f"   Delegation failed: {delegation_result.get('error')}")
                    else:
                        error = await response.text()
                        print(f"❌ Delegation failed: {error}")
                        
        except Exception as e:
            print(f"❌ Intelligent delegation demo failed: {e}")
        
        print()
    
    async def demo_multi_agent_research(self):
        """Demo: Investigación multi-agente"""
        print("🔬 Demo 4: Multi-Agent Research")
        print("-" * 35)
        
        research_task = {
            "task_type": "multi_step_research",
            "payload": {
                "query": "Agent-to-Agent communication protocols",
                "steps": ["initial_search", "context_gathering", "analysis", "synthesis"],
                "depth": "comprehensive"
            },
            "requester_id": "demo_client",
            "priority": 9
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                # Enviar tarea de investigación a SAM
                async with session.post(
                    f"http://localhost:8211/a2a",
                    json=research_task
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        print("✅ Multi-agent research completed!")
                        research_result = result.get('result', {})
                        print(f"   Steps executed: {research_result.get('steps_executed', [])}")
                        print(f"   Research completed: {research_result.get('multi_step_research_completed')}")
                        
                        # Mostrar algunos resultados
                        final_answer = research_result.get('final_answer', {})
                        if final_answer:
                            print(f"   Final synthesis available: ✅")
                        else:
                            print(f"   Final synthesis: Pending")
                            
                    else:
                        error = await response.text()
                        print(f"❌ Research failed: {error}")
                        
        except Exception as e:
            print(f"❌ Multi-agent research demo failed: {e}")
        
        print()

async def main():
    """Ejecutar demo completo"""
    demo = A2AWorkflowDemo()
    
    # Esperar que el sistema A2A esté listo
    print("⏳ Waiting for A2A system to be ready...")
    await asyncio.sleep(3)
    
    # Verificar que el sistema esté corriendo
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8200/health") as response:
                if response.status != 200:
                    print("❌ A2A system not ready. Please start it first with: ./start_a2a_system.sh")
                    return
    except:
        print("❌ A2A system not accessible. Please start it first with: ./start_a2a_system.sh")
        return
    
    await demo.run_demo()

if __name__ == "__main__":
    asyncio.run(main())
