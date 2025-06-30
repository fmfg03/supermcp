#!/usr/bin/env python3
"""
🧪 Test Multi-Model System
Quick test script for the unified AI router
"""

import requests
import json
import time

def test_multimodel_system():
    """Test the multi-model system endpoints"""
    
    base_url = "http://localhost:8300"
    
    print("🧪 Testing SuperMCP Multi-Model System")
    print("=" * 50)
    
    # Test 1: Health check
    print("1️⃣ Testing health endpoint...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Health: {data['status']}")
            print(f"   📊 Models available: {data['models_available']}")
            print(f"   🔑 API keys configured: {data['api_keys_configured']}")
        else:
            print(f"   ❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"   ❌ Health check error: {e}")
        return False
    
    # Test 2: List models
    print("\n2️⃣ Testing models endpoint...")
    try:
        response = requests.get(f"{base_url}/models")
        if response.status_code == 200:
            data = response.json()
            total_models = data['total_usage']['total_requests']
            print(f"   ✅ Models listed successfully")
            print(f"   📋 Total models: {len(data['models'])}")
            
            # Show available models
            available = [m for m in data['models'] if m['available']]
            local_models = [m for m in available if m['cost_per_1k_tokens'] == 0.0]
            
            print(f"   ✅ Available models: {len(available)}")
            print(f"   💻 Local models: {len(local_models)}")
            
            if local_models:
                print("   🆓 Free local models:")
                for model in local_models:
                    print(f"      - {model['name']} ({', '.join(model['specializations'])})")
        else:
            print(f"   ❌ Models endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Models endpoint error: {e}")
    
    # Test 3: Generate with working API key
    print("\n3️⃣ Testing generation with OpenAI...")
    try:
        payload = {
            "prompt": "Write a simple Python function to add two numbers",
            "task_type": "code",
            "max_tokens": 200,
            "temperature": 0.3,
            "force_model": "gpt-3.5-turbo"
        }
        
        response = requests.post(f"{base_url}/code", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('error'):
                print(f"   ⚠️ Generation error: {data['error']}")
            else:
                print(f"   ✅ Code generation successful!")
                print(f"   🤖 Model used: {data['model_used']}")
                print(f"   🔢 Tokens: {data['tokens_used']}")
                print(f"   💰 Cost: ${data['cost_estimate']:.4f}")
                print(f"   ⏱️ Time: {data['response_time']:.2f}s")
                print(f"   📝 Response preview: {data['content'][:100]}...")
        else:
            print(f"   ❌ Generation failed: {response.status_code}")
            print(f"   📄 Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Generation error: {e}")
    
    # Test 4: Test local model (if available)
    print("\n4️⃣ Testing local model (Ollama)...")
    try:
        payload = {
            "prompt": "Hello! How are you today?",
            "task_type": "chat",
            "max_tokens": 100,
            "force_model": "llama3-70b"
        }
        
        response = requests.post(f"{base_url}/chat", json=payload)
        if response.status_code == 200:
            data = response.json()
            if data.get('error'):
                print(f"   ⚠️ Local model error: {data['error']}")
                print("   💡 Note: Install Ollama and run 'ollama pull llama3:70b' for local models")
            else:
                print(f"   ✅ Local model working!")
                print(f"   🤖 Model: {data['model_used']}")
                print(f"   💰 Cost: ${data['cost_estimate']:.4f} (FREE!)")
                print(f"   📝 Response: {data['content'][:100]}...")
        else:
            print(f"   ❌ Local model test failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Local model error: {e}")
    
    # Test 5: Stats
    print("\n5️⃣ Testing stats endpoint...")
    try:
        response = requests.get(f"{base_url}/stats")
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Stats retrieved successfully")
            print(f"   📊 Total requests: {data['total_requests']}")
            print(f"   🔢 Total tokens: {data['total_tokens']}")
            print(f"   💰 Total cost: ${data['total_cost']:.4f}")
        else:
            print(f"   ❌ Stats endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Stats error: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Multi-Model System Test Complete!")
    print("🔗 Integration ready for SuperMCP A2A system")
    print("💡 Configure more API keys in .env for full functionality")
    
    return True

if __name__ == "__main__":
    # Wait a moment for server to be ready
    print("⏳ Waiting for server to start...")
    time.sleep(2)
    
    test_multimodel_system()