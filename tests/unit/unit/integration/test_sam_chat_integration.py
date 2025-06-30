#!/usr/bin/env python3
"""
Test SAM.CHAT Integration with SuperMCP Unified System
Verifica que sam.chat funcione correctamente como centro de control
"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_sam_chat_integration():
    """Test completo de integración sam.chat -> SuperMCP"""
    print("🧪 TESTING SAM.CHAT INTEGRATION WITH SUPERMCP")
    print("=" * 60)
    print("🌐 sam.chat as SuperMCP Command Center")
    print()
    
    # URLs to test
    test_urls = [
        ("SAM.CHAT Main", "http://localhost"),
        ("Direct IP Access", "http://65.109.54.94"),
        ("Unified Dashboard Direct", "http://localhost:9000"),
        ("Voice System Direct", "http://localhost:8300"),
        ("A2A Network Direct", "http://localhost:8200"),
        ("Enterprise Dashboard", "http://localhost:8126"),
    ]
    
    # Proxy URLs through sam.chat
    proxy_urls = [
        ("Unified via SAM.CHAT", "http://localhost/unified/"),
        ("Voice via SAM.CHAT", "http://localhost/voice/"),
        ("A2A via SAM.CHAT", "http://localhost/a2a/"),
        ("Enterprise via SAM.CHAT", "http://localhost/enterprise/"),
        ("API via SAM.CHAT", "http://localhost/api/status"),
    ]
    
    results = {"direct": [], "proxy": []}
    
    async with aiohttp.ClientSession() as session:
        
        # 1. TEST DIRECT ACCESS
        print("🔗 DIRECT ACCESS TESTS")
        print("-" * 30)
        
        for name, url in test_urls:
            try:
                async with session.get(url, timeout=5) as resp:
                    status = "✅ OK" if resp.status == 200 else f"⚠️ HTTP {resp.status}"
                    print(f"  {status} {name}")
                    results["direct"].append({
                        "name": name,
                        "url": url,
                        "status": resp.status,
                        "success": resp.status == 200
                    })
            except Exception as e:
                print(f"  ❌ FAIL {name} - {str(e)[:50]}...")
                results["direct"].append({
                    "name": name,
                    "url": url,
                    "status": 0,
                    "success": False,
                    "error": str(e)
                })
        
        print()
        
        # 2. TEST PROXY ACCESS VIA SAM.CHAT
        print("🌐 SAM.CHAT PROXY TESTS")
        print("-" * 30)
        
        for name, url in proxy_urls:
            try:
                async with session.get(url, timeout=5) as resp:
                    status = "✅ OK" if resp.status == 200 else f"⚠️ HTTP {resp.status}"
                    print(f"  {status} {name}")
                    results["proxy"].append({
                        "name": name,
                        "url": url,
                        "status": resp.status,
                        "success": resp.status == 200
                    })
            except Exception as e:
                print(f"  ❌ FAIL {name} - {str(e)[:50]}...")
                results["proxy"].append({
                    "name": name,
                    "url": url,
                    "status": 0,
                    "success": False,
                    "error": str(e)
                })
        
        print()
        
        # 3. TEST SAM.CHAT SPECIFIC FEATURES
        print("🎯 SAM.CHAT FEATURES TESTS")
        print("-" * 30)
        
        # Test main dashboard content
        try:
            async with session.get("http://localhost/", timeout=5) as resp:
                if resp.status == 200:
                    content = await resp.text()
                    if "SAM.CHAT" in content and "SuperMCP" in content:
                        print("  ✅ Main dashboard content correct")
                    else:
                        print("  ⚠️ Main dashboard content incomplete")
                else:
                    print(f"  ❌ Main dashboard failed: HTTP {resp.status}")
        except Exception as e:
            print(f"  ❌ Main dashboard error: {str(e)[:50]}...")
        
        # Test if nginx is serving static files
        try:
            async with session.get("http://localhost/", timeout=5) as resp:
                headers = dict(resp.headers)
                if "nginx" in headers.get("Server", "").lower():
                    print("  ✅ Nginx serving correctly")
                else:
                    print("  ⚠️ Nginx server header not found")
        except Exception as e:
            print(f"  ❌ Nginx test error: {str(e)[:50]}...")
        
        print()
        
        # 4. RESULTADOS FINALES
        print("📊 FINAL RESULTS")
        print("-" * 20)
        
        direct_success = sum(1 for r in results["direct"] if r["success"])
        direct_total = len(results["direct"])
        proxy_success = sum(1 for r in results["proxy"] if r["success"])
        proxy_total = len(results["proxy"])
        
        print(f"Direct Access: {direct_success}/{direct_total} successful")
        print(f"Proxy Access: {proxy_success}/{proxy_total} successful")
        
        overall_success = direct_success + proxy_success
        overall_total = direct_total + proxy_total
        success_rate = (overall_success / overall_total) * 100
        
        print(f"Overall Success Rate: {success_rate:.1f}%")
        
        print()
        
        if success_rate >= 80:
            print("🎉 SAM.CHAT INTEGRATION: EXCELLENT")
            print("✅ Ready for production use as SuperMCP command center!")
        elif success_rate >= 60:
            print("⚠️ SAM.CHAT INTEGRATION: GOOD")
            print("🔧 Some components need attention")
        else:
            print("❌ SAM.CHAT INTEGRATION: NEEDS WORK")
            print("🚨 Multiple components require fixes")
        
        print()
        print("🌐 ACCESS INSTRUCTIONS:")
        print("=" * 25)
        print("🔗 Primary: http://sam.chat (when DNS resolves)")
        print("🔗 Direct:  http://65.109.54.94")
        print("🔗 Local:   http://localhost")
        print()
        print("🎯 From sam.chat you can access:")
        print("  • Unified Dashboard: /unified/")
        print("  • Voice System: /voice/")
        print("  • A2A Network: /a2a/")
        print("  • Enterprise Monitoring: /enterprise/")
        print()
        
        return results

if __name__ == "__main__":
    asyncio.run(test_sam_chat_integration())