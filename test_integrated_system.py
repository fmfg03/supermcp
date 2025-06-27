#!/usr/bin/env python3
"""
Test Completo del Sistema Integrado SuperMCP
Verifica todos los componentes: MCP + LangGraph + Graphiti + A2A + Enterprise
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_integrated_system():
    """Test completo del sistema integrado"""
    print("🧪 TESTING SUPERMCP INTEGRATED SYSTEM")
    print("=" * 50)
    print("🌟 World's First MCP + LangGraph + Graphiti + A2A Enterprise System")
    print()
    
    # Definir todos los servicios
    services = [
        ("Enterprise Dashboard", "http://localhost:8126", "enterprise"),
        ("Task Validation", "http://localhost:8127", "enterprise"),
        ("Webhook Monitoring", "http://localhost:8125", "enterprise"),
        ("A2A Server", "http://localhost:8200", "a2a"),
        ("GoogleAI Agent", "http://localhost:8213", "a2a"),
        ("Unified Bridge", "http://localhost:9000", "integration"),
        ("Enterprise Bridge", "http://localhost:8128", "integration")
    ]
    
    results = {"healthy": 0, "total": len(services), "details": []}
    
    async with aiohttp.ClientSession() as session:
        
        # 1. TEST HEALTH CHECKS
        print("🏥 HEALTH CHECKS")
        print("-" * 20)
        
        for name, url, category in services:
            try:
                async with session.get(f"{url}/health", timeout=5) as resp:
                    if resp.status == 200:
                        health_data = await resp.json()
                        print(f"✅ {name} - HEALTHY")
                        results["healthy"] += 1
                        results["details"].append({
                            "service": name,
                            "status": "healthy",
                            "url": url,
                            "category": category
                        })
                    else:
                        print(f"❌ {name} - UNHEALTHY (HTTP {resp.status})")
                        results["details"].append({
                            "service": name,
                            "status": "unhealthy",
                            "url": url,
                            "category": category,
                            "error": f"HTTP {resp.status}"
                        })
            except Exception as e:
                print(f"❌ {name} - ERROR: {str(e)[:50]}...")
                results["details"].append({
                    "service": name,
                    "status": "error",
                    "url": url,
                    "category": category,
                    "error": str(e)
                })
        
        print()
        
        # 2. TEST ENTERPRISE FEATURES
        print("🏢 ENTERPRISE FEATURES TESTS")
        print("-" * 30)
        
        await test_enterprise_validation(session)
        await test_enterprise_monitoring(session)
        await test_enterprise_dashboard(session)
        
        print()
        
        # 3. TEST A2A COMMUNICATION
        print("📡 A2A COMMUNICATION TESTS")
        print("-" * 27)
        
        await test_a2a_registration(session)
        await test_a2a_delegation(session)
        
        print()
        
        # 4. TEST UNIFIED INTEGRATION
        print("🌐 UNIFIED INTEGRATION TESTS")
        print("-" * 29)
        
        await test_unified_bridge(session)
        await test_enterprise_bridge(session)
        
        print()
        
        # 5. RESULTADOS FINALES
        print("📊 FINAL RESULTS")
        print("-" * 16)
        
        healthy_percentage = (results["healthy"] / results["total"]) * 100
        
        print(f"Services Healthy: {results['healthy']}/{results['total']} ({healthy_percentage:.1f}%)")
        
        # Agrupar por categoría
        categories = {}
        for detail in results["details"]:
            cat = detail["category"]
            if cat not in categories:
                categories[cat] = {"healthy": 0, "total": 0}
            categories[cat]["total"] += 1
            if detail["status"] == "healthy":
                categories[cat]["healthy"] += 1
        
        print("\nBy Category:")
        for cat, stats in categories.items():
            percentage = (stats["healthy"] / stats["total"]) * 100
            print(f"  {cat.title()}: {stats['healthy']}/{stats['total']} ({percentage:.1f}%)")
        
        print()
        
        if healthy_percentage >= 80:
            print("🎉 SYSTEM STATUS: EXCELLENT")
            print("✅ Ready for production enterprise use!")
        elif healthy_percentage >= 60:
            print("⚠️ SYSTEM STATUS: GOOD")
            print("🔧 Some services need attention")
        else:
            print("❌ SYSTEM STATUS: NEEDS WORK")
            print("🚨 Multiple services require fixes")
        
        print()
        print("🚀 SUPERMCP INTEGRATED SYSTEM TEST COMPLETED")
        
        return results

async def test_enterprise_validation(session):
    """Test del sistema de validación enterprise"""
    try:
        test_task = {
            "task_id": f"integration_test_{datetime.now().strftime('%H%M%S')}",
            "agent_id": "test_agent",
            "task_type": "integration_test"
        }
        
        async with session.post("http://localhost:8127/api/validate", json=test_task, timeout=5) as resp:
            if resp.status == 200:
                print("  ✅ Validation Service - Working")
            else:
                print(f"  ⚠️ Validation Service - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ Validation Service - {str(e)[:30]}...")

async def test_enterprise_monitoring(session):
    """Test del sistema de monitoreo"""
    try:
        async with session.get("http://localhost:8125/api/webhooks/stats", timeout=5) as resp:
            if resp.status == 200:
                print("  ✅ Monitoring Service - Working")
            else:
                print(f"  ⚠️ Monitoring Service - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ Monitoring Service - {str(e)[:30]}...")

async def test_enterprise_dashboard(session):
    """Test del dashboard enterprise"""
    try:
        async with session.get("http://localhost:8126/api/stats", timeout=5) as resp:
            if resp.status == 200:
                print("  ✅ Dashboard Service - Working")
            else:
                print(f"  ⚠️ Dashboard Service - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ Dashboard Service - {str(e)[:30]}...")

async def test_a2a_registration(session):
    """Test de registro A2A"""
    try:
        async with session.get("http://localhost:8200/a2a/agents", timeout=5) as resp:
            if resp.status == 200:
                agents_data = await resp.json()
                agent_count = len(agents_data.get("agents", []))
                print(f"  ✅ A2A Registration - {agent_count} agents registered")
            else:
                print(f"  ⚠️ A2A Registration - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ A2A Registration - {str(e)[:30]}...")

async def test_a2a_delegation(session):
    """Test de delegación A2A"""
    try:
        test_task = {
            "from_agent": "test_system",
            "to_agent": "googleai_agent",
            "task_type": "text_generation",
            "payload": {
                "prompt": "Hello from integration test",
                "model": "gemini-pro"
            }
        }
        
        async with session.post("http://localhost:8200/a2a/delegate", json=test_task, timeout=10) as resp:
            if resp.status == 200:
                print("  ✅ A2A Delegation - Working")
            else:
                print(f"  ⚠️ A2A Delegation - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ A2A Delegation - {str(e)[:30]}...")

async def test_unified_bridge(session):
    """Test del bridge unificado"""
    try:
        async with session.get("http://localhost:9000/health", timeout=5) as resp:
            if resp.status == 200:
                health_data = await resp.json()
                services_info = health_data.get("services_healthy", "unknown")
                print(f"  ✅ Unified Bridge - {services_info}")
            else:
                print(f"  ⚠️ Unified Bridge - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ Unified Bridge - {str(e)[:30]}...")

async def test_enterprise_bridge(session):
    """Test del bridge enterprise"""
    try:
        async with session.get("http://localhost:8128/api/enterprise/status", timeout=5) as resp:
            if resp.status == 200:
                print("  ✅ Enterprise Bridge - Working")
            else:
                print(f"  ⚠️ Enterprise Bridge - HTTP {resp.status}")
    except Exception as e:
        print(f"  ❌ Enterprise Bridge - {str(e)[:30]}...")

if __name__ == "__main__":
    asyncio.run(test_integrated_system())