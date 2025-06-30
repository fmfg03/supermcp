#!/usr/bin/env python3
"""Test de integración enterprise"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_enterprise_stack():
    """Test completo del stack enterprise"""
    print("🧪 TESTING ENTERPRISE STACK INTEGRATION")
    print("=" * 40)
    
    services = [
        ("Dashboard", "http://localhost:8126"),
        ("Validation", "http://localhost:8127"), 
        ("Monitoring", "http://localhost:8125")
    ]
    
    async with aiohttp.ClientSession() as session:
        for name, url in services:
            try:
                # Health check
                async with session.get(f"{url}/health") as resp:
                    if resp.status == 200:
                        print(f"✅ {name} - HEALTHY")
                        
                        # Test específico por servicio
                        if "8127" in url:  # Validation
                            await test_validation_service(session, url)
                        elif "8125" in url:  # Monitoring  
                            await test_monitoring_service(session, url)
                        elif "8126" in url:  # Dashboard
                            await test_dashboard_service(session, url)
                    else:
                        print(f"❌ {name} - UNHEALTHY ({resp.status})")
                        
            except Exception as e:
                print(f"❌ {name} - ERROR: {e}")

async def test_validation_service(session, base_url):
    """Test del sistema de validación"""
    test_task_id = f"test_task_{datetime.now().strftime('%H%M%S')}"
    
    # Test crear task_id
    data = {
        "task_id": test_task_id,
        "agent_id": "test_agent",
        "task_type": "test"
    }
    
    async with session.post(f"{base_url}/tasks", json=data) as resp:
        if resp.status == 200:
            print(f"  ✅ Task creation test passed")
        else:
            print(f"  ❌ Task creation test failed")

async def test_monitoring_service(session, base_url):
    """Test del sistema de monitoreo"""
    # Test webhook health
    async with session.get(f"{base_url}/webhooks/stats") as resp:
        if resp.status == 200:
            print(f"  ✅ Webhook monitoring test passed")
        else:
            print(f"  ❌ Webhook monitoring test failed")

async def test_dashboard_service(session, base_url):
    """Test del dashboard"""
    # Test logs endpoint
    async with session.get(f"{base_url}/logs") as resp:
        if resp.status == 200:
            print(f"  ✅ Dashboard logs test passed")
        else:
            print(f"  ❌ Dashboard logs test failed")

if __name__ == "__main__":
    asyncio.run(test_enterprise_stack())
