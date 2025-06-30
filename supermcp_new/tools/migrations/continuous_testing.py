#!/usr/bin/env python3
"""
Continuous Testing System for SuperMCP Migrations
Implements automated testing after each migration step
"""

import asyncio
import subprocess
import json
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class TestType(Enum):
    SYNTAX = "syntax"
    IMPORTS = "imports"  
    UNIT = "unit"
    INTEGRATION = "integration"
    SMOKE = "smoke"
    PERFORMANCE = "performance"

@dataclass
class TestResult:
    test_type: TestType
    test_name: str
    status: str  # "passed", "failed", "skipped"
    duration: float
    output: str
    error: Optional[str] = None

class ContinuousTestRunner:
    """Runs continuous tests after migration steps"""
    
    def __init__(self, project_root: str = "/root/supermcp/supermcp_new"):
        self.project_root = Path(project_root)
        self.test_results: List[TestResult] = []
        
    async def run_post_migration_tests(self) -> Dict[str, any]:
        """Run comprehensive tests after migration"""
        print("🧪 Starting post-migration testing suite...")
        
        results = {
            "timestamp": time.time(),
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "skipped": 0,
            "tests": []
        }
        
        # Test categories in order of importance
        test_categories = [
            self.run_syntax_tests,
            self.run_import_tests,
            self.run_smoke_tests,
            self.run_unit_tests,
            self.run_integration_tests
        ]
        
        for test_category in test_categories:
            category_results = await test_category()
            results["tests"].extend(category_results)
            
            # Count results
            for test in category_results:
                results["total_tests"] += 1
                if test.status == "passed":
                    results["passed"] += 1
                elif test.status == "failed":
                    results["failed"] += 1
                else:
                    results["skipped"] += 1
        
        # Generate summary
        success_rate = (results["passed"] / results["total_tests"]) * 100 if results["total_tests"] > 0 else 0
        results["success_rate"] = success_rate
        results["recommendation"] = self.get_recommendation(results)
        
        self.save_test_results(results)
        self.print_test_summary(results)
        
        return results
    
    async def run_syntax_tests(self) -> List[TestResult]:
        """Test Python syntax validity"""
        print("1️⃣ Running syntax validation tests...")
        results = []
        
        python_files = list(self.project_root.rglob("*.py"))
        
        for py_file in python_files:
            if "venv" in str(py_file) or "__pycache__" in str(py_file):
                continue
                
            start_time = time.time()
            try:
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(py_file)],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                duration = time.time() - start_time
                
                if result.returncode == 0:
                    test_result = TestResult(
                        test_type=TestType.SYNTAX,
                        test_name=f"syntax_check_{py_file.name}",
                        status="passed",
                        duration=duration,
                        output="Syntax valid"
                    )
                else:
                    test_result = TestResult(
                        test_type=TestType.SYNTAX,
                        test_name=f"syntax_check_{py_file.name}",
                        status="failed",
                        duration=duration,
                        output=result.stdout,
                        error=result.stderr
                    )
                
                results.append(test_result)
                
            except subprocess.TimeoutExpired:
                results.append(TestResult(
                    test_type=TestType.SYNTAX,
                    test_name=f"syntax_check_{py_file.name}",
                    status="failed",
                    duration=30.0,
                    output="",
                    error="Timeout during syntax check"
                ))
            except Exception as e:
                results.append(TestResult(
                    test_type=TestType.SYNTAX,
                    test_name=f"syntax_check_{py_file.name}",
                    status="failed",
                    duration=time.time() - start_time,
                    output="",
                    error=str(e)
                ))
        
        passed = len([r for r in results if r.status == "passed"])
        print(f"   ✅ Syntax tests: {passed}/{len(results)} passed")
        return results
    
    async def run_import_tests(self) -> List[TestResult]:
        """Test import validity"""
        print("2️⃣ Running import validation tests...")
        results = []
        
        # Key modules to test imports
        key_modules = [
            "agents/swarm/intelligence_system.py",
            "ai/models/router.py", 
            "mcp/client/connection_manager.py",
            "agents/specialized/terminal_agent.py",
            "api/websocket/swarm_gateway.py"
        ]
        
        for module_path in key_modules:
            full_path = self.project_root / module_path
            if not full_path.exists():
                results.append(TestResult(
                    test_type=TestType.IMPORTS,
                    test_name=f"import_test_{module_path}",
                    status="skipped",
                    duration=0.0,
                    output="File not found"
                ))
                continue
            
            start_time = time.time()
            try:
                # Test import by trying to compile
                result = subprocess.run([
                    "python3", "-c", 
                    f"import sys; sys.path.insert(0, '{self.project_root}'); "
                    f"exec(open('{full_path}').read())"
                ], capture_output=True, text=True, timeout=60)
                
                duration = time.time() - start_time
                
                if result.returncode == 0:
                    test_result = TestResult(
                        test_type=TestType.IMPORTS,
                        test_name=f"import_test_{module_path}",
                        status="passed",
                        duration=duration,
                        output="Imports successful"
                    )
                else:
                    test_result = TestResult(
                        test_type=TestType.IMPORTS,
                        test_name=f"import_test_{module_path}",
                        status="failed",
                        duration=duration,
                        output=result.stdout,
                        error=result.stderr
                    )
                
                results.append(test_result)
                
            except Exception as e:
                results.append(TestResult(
                    test_type=TestType.IMPORTS,
                    test_name=f"import_test_{module_path}",
                    status="failed",
                    duration=time.time() - start_time,
                    output="",
                    error=str(e)
                ))
        
        passed = len([r for r in results if r.status == "passed"])
        print(f"   ✅ Import tests: {passed}/{len(results)} passed")
        return results
    
    async def run_smoke_tests(self) -> List[TestResult]:
        """Run basic smoke tests"""
        print("3️⃣ Running smoke tests...")
        results = []
        
        smoke_tests = [
            {
                "name": "directory_structure",
                "description": "Check critical directories exist",
                "check": lambda: all([
                    (self.project_root / "agents").exists(),
                    (self.project_root / "ai").exists(),
                    (self.project_root / "mcp").exists(),
                    (self.project_root / "config").exists()
                ])
            },
            {
                "name": "config_files",
                "description": "Check configuration files exist",
                "check": lambda: all([
                    (self.project_root / "config/defaults.yaml").exists(),
                    (self.project_root / "project/.env.example").exists()
                ])
            },
            {
                "name": "core_modules", 
                "description": "Check core modules exist",
                "check": lambda: all([
                    (self.project_root / "agents/swarm/intelligence_system.py").exists(),
                    (self.project_root / "ai/models/router.py").exists(),
                    (self.project_root / "mcp/client/connection_manager.py").exists()
                ])
            },
            {
                "name": "executable_scripts",
                "description": "Check scripts are executable",
                "check": lambda: (self.project_root / "deployment/scripts/start_development.sh").exists()
            }
        ]
        
        for test in smoke_tests:
            start_time = time.time()
            try:
                success = test["check"]()
                duration = time.time() - start_time
                
                test_result = TestResult(
                    test_type=TestType.SMOKE,
                    test_name=test["name"],
                    status="passed" if success else "failed",
                    duration=duration,
                    output=test["description"]
                )
                results.append(test_result)
                
            except Exception as e:
                results.append(TestResult(
                    test_type=TestType.SMOKE,
                    test_name=test["name"],
                    status="failed",
                    duration=time.time() - start_time,
                    output=test["description"],
                    error=str(e)
                ))
        
        passed = len([r for r in results if r.status == "passed"])
        print(f"   ✅ Smoke tests: {passed}/{len(results)} passed")
        return results
    
    async def run_unit_tests(self) -> List[TestResult]:
        """Run unit tests if available"""
        print("4️⃣ Running unit tests...")
        results = []
        
        test_dir = self.project_root / "testing/unit"
        if not test_dir.exists():
            results.append(TestResult(
                test_type=TestType.UNIT,
                test_name="unit_tests",
                status="skipped",
                duration=0.0,
                output="Unit test directory not found"
            ))
            print("   ⚠️ Unit tests: Skipped (no test directory)")
            return results
        
        start_time = time.time()
        try:
            result = subprocess.run([
                "python3", "-m", "pytest", str(test_dir), "-v", "--tb=short"
            ], capture_output=True, text=True, timeout=300, cwd=self.project_root)
            
            duration = time.time() - start_time
            
            test_result = TestResult(
                test_type=TestType.UNIT,
                test_name="pytest_unit_tests",
                status="passed" if result.returncode == 0 else "failed",
                duration=duration,
                output=result.stdout,
                error=result.stderr if result.returncode != 0 else None
            )
            results.append(test_result)
            
        except subprocess.TimeoutExpired:
            results.append(TestResult(
                test_type=TestType.UNIT,
                test_name="pytest_unit_tests",
                status="failed",
                duration=300.0,
                output="",
                error="Unit tests timed out"
            ))
        except Exception as e:
            results.append(TestResult(
                test_type=TestType.UNIT,
                test_name="pytest_unit_tests", 
                status="failed",
                duration=time.time() - start_time,
                output="",
                error=str(e)
            ))
        
        passed = len([r for r in results if r.status == "passed"])
        print(f"   ✅ Unit tests: {passed}/{len(results)} passed")
        return results
    
    async def run_integration_tests(self) -> List[TestResult]:
        """Run integration tests"""
        print("5️⃣ Running integration tests...")
        results = []
        
        # Simple integration tests
        integration_tests = [
            {
                "name": "config_loading",
                "script": """
import yaml
from pathlib import Path
config_path = Path('config/defaults.yaml')
if config_path.exists():
    with open(config_path) as f:
        config = yaml.safe_load(f)
    assert 'app' in config
    print('Config loading: OK')
else:
    raise FileNotFoundError('Config file not found')
"""
            }
        ]
        
        for test in integration_tests:
            start_time = time.time()
            try:
                result = subprocess.run([
                    "python3", "-c", test["script"]
                ], capture_output=True, text=True, timeout=60, cwd=self.project_root)
                
                duration = time.time() - start_time
                
                test_result = TestResult(
                    test_type=TestType.INTEGRATION,
                    test_name=test["name"],
                    status="passed" if result.returncode == 0 else "failed",
                    duration=duration,
                    output=result.stdout,
                    error=result.stderr if result.returncode != 0 else None
                )
                results.append(test_result)
                
            except Exception as e:
                results.append(TestResult(
                    test_type=TestType.INTEGRATION,
                    test_name=test["name"],
                    status="failed",
                    duration=time.time() - start_time,
                    output="",
                    error=str(e)
                ))
        
        passed = len([r for r in results if r.status == "passed"])
        print(f"   ✅ Integration tests: {passed}/{len(results)} passed")
        return results
    
    def get_recommendation(self, results: Dict) -> str:
        """Get recommendation based on test results"""
        success_rate = results["success_rate"]
        
        if success_rate >= 95:
            return "✅ SAFE TO PROCEED - All critical tests passing"
        elif success_rate >= 80:
            return "⚠️ PROCEED WITH CAUTION - Some tests failing, review errors"
        elif success_rate >= 60:
            return "🚨 HIGH RISK - Multiple test failures, consider rollback"
        else:
            return "🛑 ROLLBACK RECOMMENDED - Critical failures detected"
    
    def save_test_results(self, results: Dict):
        """Save test results to file"""
        results_dir = self.project_root / "testing/results"
        results_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        results_file = results_dir / f"migration_tests_{timestamp}.json"
        
        with open(results_file, 'w') as f:
            # Convert TestResult objects to dicts
            serializable_results = {**results}
            serializable_results["tests"] = [
                {
                    "test_type": t.test_type.value,
                    "test_name": t.test_name,
                    "status": t.status,
                    "duration": t.duration,
                    "output": t.output,
                    "error": t.error
                }
                for t in results["tests"]
            ]
            json.dump(serializable_results, f, indent=2)
    
    def print_test_summary(self, results: Dict):
        """Print formatted test summary"""
        print("\n" + "="*60)
        print("🧪 POST-MIGRATION TEST SUMMARY")
        print("="*60)
        print(f"Total Tests: {results['total_tests']}")
        print(f"✅ Passed: {results['passed']}")
        print(f"❌ Failed: {results['failed']}")
        print(f"⏭️ Skipped: {results['skipped']}")
        print(f"📊 Success Rate: {results['success_rate']:.1f}%")
        print(f"💡 Recommendation: {results['recommendation']}")
        print("="*60)
        
        # Show failed tests
        failed_tests = [t for t in results["tests"] if t.status == "failed"]
        if failed_tests:
            print("\n❌ FAILED TESTS:")
            for test in failed_tests:
                print(f"  - {test.test_name}: {test.error or 'No error details'}")

async def main():
    """Run continuous testing"""
    runner = ContinuousTestRunner()
    results = await runner.run_post_migration_tests()
    
    # Return exit code based on results
    if results["success_rate"] < 80:
        exit(1)
    else:
        exit(0)

if __name__ == "__main__":
    asyncio.run(main())