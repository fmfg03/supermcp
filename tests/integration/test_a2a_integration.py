#!/usr/bin/env python3
"""
SUPERmcp A2A Integration Tests
Suite completa de pruebas para verificar funcionalidad A2A
"""

import asyncio
import aiohttp
import json
import time
from typing import Dict, Any

class A2AIntegrationTester:
    def __init__(self):
        self.a2a_server = "http://localhost:8200"
        self.agents = {
            "manus": "http://localhost:8210",
            "sam": "http://localhost:8211", 
            "memory": "http://localhost:8212"
        }
        self.test_results = []
    
    async def run_all_tests(self):
        """Ejecutar suite completa de tests"""
        print("🧪 SUPERmcp A2A Integration Tests")
        print("=================================")
        print()
        
        tests = [
            ("Server Health", self.test_server_health),
            ("Agent Registration", self.test_agent_registration),
            ("Agent Discovery", self.test_agent_discovery),
            ("Task Delegation", self.test_task_delegation),
            ("Inter-Agent Communication", self.test_inter_agent_communication),
            ("Workflow Orchestration", self.test_workflow_orchestration),
            ("Error Handling", self.test_error_handling),
            ("Performance", self.test_performance)
        ]
        
        for test_name, test_func in tests:
            print(f"🔬 Running: {test_name}")
            try:
                start_time = time.time()
                result = await test_func()
                duration = time.time() - start_time
                
                if result:
                    print(f"   ✅ PASSED ({duration:.2f}s)")
                    self.test_results.append({"test": test_name, "status": "PASSED", "duration": duration})
                else:
                    print(f"   ❌ FAILED ({duration:.2f}s)")
                    self.test_results.append({"test": test_name, "status": "FAILED", "duration": duration})
                    
            except Exception as e:
                print(f"   💥 ERROR: {e}")
                self.test_results.append({"test": test_name, "status": "ERROR", "error": str(e)})
            
            print()
        
        self.print_summary()
    
    async def test_server_health(self) -> bool:
        """Test: Verificar salud del servidor A2A"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.a2a_server}/health") as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("status") == "healthy"
            return False
        except:
            return False
    
    async def test_agent_registration(self) -> bool:
        """Test: Verificar registro de agentes"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.a2a_server}/agents") as response:
                    if response.status == 200:
                        data = await response.json()
                        agents = data.get("agents", [])
                        
                        # Verificar que los 3 agentes principales estén registrados
                        agent_ids = [agent["agent_id"] for agent in agents]
                        required_agents = ["manus_orchestrator_v2", "sam_executor_v2", "memory_analyzer_v2"]
                        
                        return all(agent_id in agent_ids for agent_id in required_agents)
            return False
        except:
            return False
    
    async def test_agent_discovery(self) -> bool:
        """Test: Verificar descubrimiento de agentes"""
        try:
            async with aiohttp.ClientSession() as session:
                discovery_request = {
                    "task_type": "analysis",
                    "capabilities": ["autonomous_execution"]
                }
                
                async with session.post(
                    f"{self.a2a_server}/a2a/discover",
                    json=discovery_request
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        agents = data.get("agents", [])
                        return len(agents) > 0  # Al menos un agente encontrado
            return False
        except:
            return False
    
    async def test_task_delegation(self) -> bool:
        """Test: Verificar delegación básica de tareas"""
        try:
            async with aiohttp.ClientSession() as session:
                delegation_request = {
                    "task_type": "test_task",
                    "payload": {"test_data": "integration_test"},
                    "requester_id": "test_client",
                    "priority": 5
                }
                
                async with session.post(
                    f"{self.a2a_server}/a2a/delegate",
                    json=delegation_request
                ) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("success", False) and "task_id" in data
            return False
        except:
            return False
    
    async def test_inter_agent_communication(self) -> bool:
        """Test: Verificar comunicación entre agentes"""
        try:
            async with aiohttp.ClientSession() as session:
                # Test directo con agente Manus
                test_task = {
                    "task_type": "coordination",
                    "payload": {
                        "coordination_plan": {
                            "agents": [
                                {
                                    "role": "analyzer",
                                    "capabilities": ["analysis"],
                                    "task": {"task_type": "test_analysis"}
                                }
                            ]
                        }
                    },
                    "requester_id": "test_client"
                }
                
                async with session.post(f"{self.agents['manus']}/a2a", json=test_task) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("success", False)
            return False
        except:
            return False
    
    async def test_workflow_orchestration(self) -> bool:
        """Test: Verificar orquestación de workflows"""
        try:
            async with aiohttp.ClientSession() as session:
                workflow_task = {
                    "task_type": "complex_workflow",
                    "payload": {
                        "steps": [
                            {"type": "step1", "data": {"test": True}},
                            {"type": "step2", "data": {"test": True}}
                        ]
                    },
                    "requester_id": "test_client"
                }
                
                async with session.post(f"{self.agents['manus']}/a2a", json=workflow_task) as response:
                    return response.status == 200
        except:
            return False
    
    async def test_error_handling(self) -> bool:
        """Test: Verificar manejo de errores"""
        try:
            async with aiohttp.ClientSession() as session:
                # Enviar tarea inválida
                invalid_task = {
                    "invalid_field": "test"
                    # Falta campos requeridos
                }
                
                async with session.post(f"{self.a2a_server}/a2a/delegate", json=invalid_task) as response:
                    # Debe retornar error (no 200)
                    return response.status != 200
        except:
            return True  # Exception es comportamiento esperado
    
    async def test_performance(self) -> bool:
        """Test: Verificar performance básica"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Test de descubrimiento múltiple
                tasks = []
                for i in range(5):
                    task = session.post(f"{self.a2a_server}/a2a/discover", json={
                        "task_type": f"test_{i}",
                        "capabilities": ["test"]
                    })
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks, return_exceptions=True)
                duration = time.time() - start_time
                
                # Performance aceptable: < 5 segundos para 5 requests
                return duration < 5.0
        except:
            return False
    
    def print_summary(self):
        """Imprimir resumen de resultados"""
        print("📊 Test Results Summary")
        print("======================")
        
        passed = len([r for r in self.test_results if r["status"] == "PASSED"])
        failed = len([r for r in self.test_results if r["status"] == "FAILED"]) 
        errors = len([r for r in self.test_results if r["status"] == "ERROR"])
        total = len(self.test_results)
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"💥 Errors: {errors}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        print()
        
        if failed > 0 or errors > 0:
            print("Failed/Error Tests:")
            for result in self.test_results:
                if result["status"] != "PASSED":
                    print(f"   {result['status']}: {result['test']}")
                    if "error" in result:
                        print(f"      Error: {result['error']}")
        
        print()
        if passed == total:
            print("🎉 All tests passed! A2A integration is working perfectly!")
        else:
            print("⚠️  Some tests failed. Please check the system.")

async def main():
    """Ejecutar tests de integración"""
    tester = A2AIntegrationTester()
    
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
    
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
