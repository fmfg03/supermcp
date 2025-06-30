#!/bin/bash
# quick_validation_test.sh
# Test rápido para validar que todo funciona después de la limpieza

echo "🧪 QUICK VALIDATION TEST - POST CLEANUP"
echo "======================================="
echo "Date: $(date)"
echo "Directory: $(pwd)"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

TESTS_PASSED=0
TESTS_FAILED=0
WARNINGS=0

# Test function
test_check() {
    local test_name="$1"
    local command="$2"
    local expected="$3"
    
    echo -n "Testing $test_name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ PASS${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ FAIL${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
}

test_warn() {
    local test_name="$1"
    local command="$2"
    
    echo -n "Checking $test_name... "
    
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ OK${NC}"
    else
        echo -e "${YELLOW}⚠️ WARNING${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
}

echo "📂 STRUCTURE TESTS"
echo "=================="

# Test new directory structure
test_check "Apps directory" "[ -d 'apps' ]"
test_check "Services directory" "[ -d 'services' ]" 
test_check "Agents directory" "[ -d 'agents' ]"
test_check "Infrastructure directory" "[ -d 'infrastructure' ]"
test_check "Config directory" "[ -d 'config' ]"
test_check "Scripts directory" "[ -d 'scripts' ]"
test_check "Docs directory" "[ -d 'docs' ]"
test_check "Tests directory" "[ -d 'tests' ]"

echo ""
echo "🔧 CRITICAL SERVICES TESTS"
echo "=========================="

# Test critical service files
test_check "Orchestration Service" "[ -f 'services/orchestration/mcp_orchestration_server.py' ]"
test_check "Memory Analyzer" "[ -f 'services/memory-analyzer/sam_memory_analyzer.py' ]"
test_check "Webhook System" "[ -f 'services/webhook-system/complete_webhook_agent_end_task_system.py' ]"
test_check "Payload Schemas" "[ -f 'config/schemas/mcp_payload_schemas.py' ]"
test_check "API Validation" "[ -f 'config/security/api_validation_middleware.py' ]"

echo ""
echo "📱 APPLICATION TESTS"
echo "==================="

# Test applications
test_check "Frontend App" "[ -d 'apps/frontend' ]"
test_check "Backend App" "[ -d 'apps/backend' ]"
test_warn "Observatory App" "[ -d 'apps/mcp-observatory' ]"
test_warn "DevTool App" "[ -d 'apps/mcp-devtool' ]"

echo ""
echo "🤖 AGENT SYSTEMS TESTS"
echo "======================"

# Test agent directories
test_check "Core Agents" "[ -d 'agents/core' ]"
test_warn "Specialized Agents" "[ -d 'agents/specialized' ]" 
test_warn "Swarm Agents" "[ -d 'agents/swarm' ]"

# Count agent files
if [ -d "agents/core" ]; then
    agent_count=$(find agents/core -name "*.py" | wc -l)
    echo -e "Core agent files: ${BLUE}$agent_count${NC}"
fi

echo ""
echo "🏗️ INFRASTRUCTURE TESTS"
echo "======================="

# Test infrastructure
test_check "Docker configs" "[ -d 'infrastructure/docker' ]"
test_warn "Nginx configs" "[ -d 'infrastructure/nginx' ]"
test_warn "SSL configs" "[ -d 'infrastructure/ssl' ]"

# Test Docker files
test_warn "Docker Compose" "[ -f 'infrastructure/docker/docker-compose.yml' ]"
test_warn "Backend Dockerfile" "[ -f 'infrastructure/docker/Dockerfile.backend' ]"

echo ""
echo "⚙️ CONFIGURATION TESTS"
echo "======================"

# Test configurations
test_check "Config schemas" "[ -d 'config/schemas' ]"
test_check "Security configs" "[ -d 'config/security' ]"
test_warn "Environment configs" "[ -d 'config/environments' ]"

# Test essential files in root
test_check "README.md" "[ -f 'README.md' ]"
test_check "package.json" "[ -f 'package.json' ]"
test_check "requirements.txt" "[ -f 'requirements.txt' ]"

echo ""
echo "🔍 SYNTAX VALIDATION TESTS"
echo "=========================="

# Test Python syntax on critical files
python_files=(
    "services/orchestration/mcp_orchestration_server.py"
    "services/memory-analyzer/sam_memory_analyzer.py"
    "services/webhook-system/complete_webhook_agent_end_task_system.py"
    "config/schemas/mcp_payload_schemas.py"
    "config/security/api_validation_middleware.py"
)

syntax_errors=0
for py_file in "${python_files[@]}"; do
    if [ -f "$py_file" ]; then
        echo -n "Checking syntax: $(basename "$py_file")... "
        if python3 -m py_compile "$py_file" 2>/dev/null; then
            echo -e "${GREEN}✅ Valid${NC}"
        else
            echo -e "${RED}❌ Syntax Error${NC}"
            syntax_errors=$((syntax_errors + 1))
        fi
    fi
done

if [ $syntax_errors -eq 0 ]; then
    echo -e "${GREEN}✅ All Python files have valid syntax${NC}"
    TESTS_PASSED=$((TESTS_PASSED + 1))
else
    echo -e "${RED}❌ $syntax_errors Python files have syntax errors${NC}"
    TESTS_FAILED=$((TESTS_FAILED + 1))
fi

echo ""
echo "📦 PACKAGE VALIDATION TESTS"
echo "==========================="

# Test package.json
if [ -f "package.json" ]; then
    echo -n "Validating package.json... "
    if python3 -c "import json; json.load(open('package.json'))" 2>/dev/null; then
        echo -e "${GREEN}✅ Valid JSON${NC}"
        TESTS_PASSED=$((TESTS_PASSED + 1))
    else
        echo -e "${RED}❌ Invalid JSON${NC}"
        TESTS_FAILED=$((TESTS_FAILED + 1))
    fi
fi

# Test if node_modules exists
test_warn "Node modules" "[ -d 'node_modules' ]"

echo ""
echo "🛡️ BACKUP VALIDATION TESTS"
echo "=========================="

# Test backup and cleanup
test_check "Migration backup exists" "[ -d 'migration_backup' ]"
test_check "Cleanup archive exists" "[ -d 'cleanup_archive_20250630_211210' ]"
test_check "Cleanup report exists" "[ -f 'CLEANUP_REPORT.md' ]"

if [ -d "migration_backup" ]; then
    backup_count=$(find migration_backup -type f | wc -l)
    echo -e "Backup contains: ${BLUE}$backup_count files${NC}"
fi

echo ""
echo "📊 FINAL SUMMARY"
echo "================"

total_tests=$((TESTS_PASSED + TESTS_FAILED))
if [ $total_tests -gt 0 ]; then
    pass_percentage=$(( (TESTS_PASSED * 100) / total_tests ))
else
    pass_percentage=0
fi

echo -e "Total Tests: ${BLUE}$total_tests${NC}"
echo -e "Passed: ${GREEN}$TESTS_PASSED${NC} (${pass_percentage}%)"
echo -e "Failed: ${RED}$TESTS_FAILED${NC}"
echo -e "Warnings: ${YELLOW}$WARNINGS${NC}"

echo ""
if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL CRITICAL TESTS PASSED!${NC}"
    echo -e "${GREEN}✅ Your SuperMCP migration and cleanup was SUCCESSFUL!${NC}"
    echo ""
    echo "🚀 Ready for next steps:"
    echo "   1. Start services: ./scripts/deployment/start_system.sh"
    echo "   2. Run full test suite: ./tests/comprehensive_test_supermcp.sh"
    echo "   3. Check service status: ./scripts/monitoring/check_system_status.sh"
    echo ""
    echo "📂 Your new enterprise structure:"
    echo "   📱 apps/         - Main applications"
    echo "   ⚙️ services/     - Microservices"
    echo "   🤖 agents/       - AI agents"
    echo "   🏗️ infrastructure/ - Docker & configs"
    echo "   ⚙️ config/       - Configurations"
    echo "   📜 scripts/      - Automation tools"
    echo "   📚 docs/         - Documentation"
    echo "   🧪 tests/        - Testing framework"
    
    exit 0
else
    echo -e "${RED}❌ Some tests failed. Please review the issues above.${NC}"
    echo "🔍 Check the failed tests and fix any missing files or syntax errors."
    exit 1
fi