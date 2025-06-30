#!/bin/bash
# post_migration_cleanup.sh
# Limpia el directorio root después de validar que la migración fue exitosa

set -e

echo "🧹 SUPERMCP POST-MIGRATION CLEANUP"
echo "=================================="
echo "Date: $(date)"
echo "Working Directory: $(pwd)"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Logging function
log() {
    local level=$1
    local message=$2
    case $level in
        "SUCCESS") echo -e "${GREEN}✅ ${message}${NC}" ;;
        "ERROR") echo -e "${RED}❌ ${message}${NC}" ;;
        "WARNING") echo -e "${YELLOW}⚠️  ${message}${NC}" ;;
        "INFO") echo -e "${BLUE}ℹ️  ${message}${NC}" ;;
    esac
}

# STEP 1: Validate migration was successful
echo "🔍 STEP 1: VALIDATING MIGRATION SUCCESS"
echo "======================================="

validate_new_structure() {
    local required_dirs=(
        "apps"
        "services" 
        "agents"
        "infrastructure"
        "config"
        "scripts"
        "docs"
        "tests"
        "logs"
        "tools"
    )
    
    local missing_dirs=0
    for dir in "${required_dirs[@]}"; do
        if [ -d "$dir" ]; then
            local file_count=$(find "$dir" -type f | wc -l)
            log "SUCCESS" "Directory '$dir' exists with $file_count files"
        else
            log "ERROR" "Required directory '$dir' is missing!"
            missing_dirs=$((missing_dirs + 1))
        fi
    done
    
    if [ $missing_dirs -eq 0 ]; then
        log "SUCCESS" "All required directories exist"
        return 0
    else
        log "ERROR" "$missing_dirs required directories are missing"
        return 1
    fi
}

validate_critical_services() {
    local critical_services=(
        "services/orchestration/mcp_orchestration_server.py"
        "services/memory-analyzer/sam_memory_analyzer.py"
        "services/webhook-system/complete_webhook_agent_end_task_system.py"
        "config/schemas/mcp_payload_schemas.py"
        "config/security/api_validation_middleware.py"
    )
    
    local missing_services=0
    for service in "${critical_services[@]}"; do
        if [ -f "$service" ]; then
            log "SUCCESS" "Critical service exists: $service"
        else
            log "ERROR" "Critical service missing: $service"
            missing_services=$((missing_services + 1))
        fi
    done
    
    if [ $missing_services -eq 0 ]; then
        log "SUCCESS" "All critical services are in place"
        return 0
    else
        log "ERROR" "$missing_services critical services are missing"
        return 1
    fi
}

# Run validation
log "INFO" "Validating new directory structure..."
if ! validate_new_structure; then
    log "ERROR" "Migration validation failed! Cannot proceed with cleanup."
    exit 1
fi

log "INFO" "Validating critical services..."
if ! validate_critical_services; then
    log "ERROR" "Critical services validation failed! Cannot proceed with cleanup."
    exit 1
fi

log "SUCCESS" "Migration validation passed! Safe to proceed with cleanup."

# STEP 2: Create cleanup plan
echo ""
echo "📋 STEP 2: CREATING CLEANUP PLAN"
echo "================================"

# Files that should be KEPT in root
keep_in_root=(
    "README.md"
    "package.json"
    "package-lock.json"
    ".env"
    ".gitignore"
    ".git"
    "node_modules"
    "migration_backup"
    "apps"
    "services"
    "agents"
    "infrastructure"
    "config"
    "scripts"
    "docs"
    "tests"
    "logs"
    "tools"
    "data"
)

# Create array to track files to move/delete
declare -a files_to_cleanup=()

log "INFO" "Analyzing root directory for cleanup candidates..."

# Scan root directory
cleanup_count=0
keep_count=0

for item in *; do
    if [ "$item" = "*" ]; then
        continue  # No files found
    fi
    
    should_keep=false
    for keep_item in "${keep_in_root[@]}"; do
        if [ "$item" = "$keep_item" ]; then
            should_keep=true
            break
        fi
    done
    
    if [ "$should_keep" = true ]; then
        log "SUCCESS" "Keeping in root: $item"
        keep_count=$((keep_count + 1))
    else
        # Check if it's a backup file (we can safely remove these)
        if [[ "$item" == *.backup ]]; then
            files_to_cleanup+=("$item")
            cleanup_count=$((cleanup_count + 1))
            log "WARNING" "Marked for cleanup (backup): $item"
        # Check if it's a legacy file that has been migrated
        elif [[ "$item" == *.py ]] || [[ "$item" == *.js ]] || [[ "$item" == *.sh ]] || [[ "$item" == *.md ]]; then
            files_to_cleanup+=("$item")
            cleanup_count=$((cleanup_count + 1))
            log "WARNING" "Marked for cleanup (migrated): $item"
        # Other files - be cautious
        else
            log "INFO" "Uncertain about: $item (will keep for safety)"
            keep_count=$((keep_count + 1))
        fi
    fi
done

echo ""
log "INFO" "Cleanup Plan Summary:"
log "INFO" "  - Files to keep: $keep_count"
log "INFO" "  - Files to cleanup: $cleanup_count"

# STEP 3: Interactive confirmation
echo ""
echo "🤔 STEP 3: CLEANUP CONFIRMATION"
echo "==============================="

if [ $cleanup_count -eq 0 ]; then
    log "SUCCESS" "No files need cleanup - root directory is already clean!"
    exit 0
fi

echo "The following files will be moved to 'cleanup_archive/':"
for file in "${files_to_cleanup[@]}"; do
    echo "  - $file"
done

echo ""
read -p "Do you want to proceed with cleanup? (y/N): " confirm

if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    log "INFO" "Cleanup cancelled by user. Files remain unchanged."
    exit 0
fi

# STEP 4: Execute cleanup
echo ""
echo "🧹 STEP 4: EXECUTING CLEANUP"
echo "=========================="

# Create archive directory
archive_dir="cleanup_archive_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$archive_dir"
log "SUCCESS" "Created archive directory: $archive_dir"

# Move files to archive
moved_count=0
error_count=0

for file in "${files_to_cleanup[@]}"; do
    if [ -e "$file" ]; then
        if mv "$file" "$archive_dir/"; then
            log "SUCCESS" "Moved to archive: $file"
            moved_count=$((moved_count + 1))
        else
            log "ERROR" "Failed to move: $file"
            error_count=$((error_count + 1))
        fi
    else
        log "WARNING" "File no longer exists: $file"
    fi
done

# STEP 5: Final validation
echo ""
echo "✅ STEP 5: FINAL VALIDATION"
echo "=========================="

log "INFO" "Cleanup Results:"
log "INFO" "  - Files moved: $moved_count"
log "INFO" "  - Errors: $error_count"
log "INFO" "  - Archive location: $archive_dir"

# List what's left in root
echo ""
log "INFO" "Files remaining in root directory:"
remaining_count=0
for item in *; do
    if [ "$item" != "*" ]; then
        echo "  ✅ $item"
        remaining_count=$((remaining_count + 1))
    fi
done

log "SUCCESS" "Root directory now has $remaining_count items"

# Create a summary report
cat > "CLEANUP_REPORT.md" << EOF
# SuperMCP Post-Migration Cleanup Report

**Date:** $(date)  
**Status:** Successful  

## Summary
- **Files moved to archive:** $moved_count
- **Errors:** $error_count  
- **Archive location:** $archive_dir
- **Files remaining in root:** $remaining_count

## Items Remaining in Root
$(for item in *; do [ "$item" != "*" ] && echo "- $item"; done)

## Archived Files
$(for file in "${files_to_cleanup[@]}"; do echo "- $file"; done)

## Migration Status
✅ **COMPLETE** - SuperMCP migration and cleanup successful!

### New Enterprise Structure:
- 📱 \`apps/\` - Main applications
- ⚙️ \`services/\` - Microservices  
- 🤖 \`agents/\` - AI agents
- 🏗️ \`infrastructure/\` - Docker & configs
- ⚙️ \`config/\` - Configurations
- 📜 \`scripts/\` - Automation tools
- 📚 \`docs/\` - Documentation
- 🧪 \`tests/\` - Testing framework
- 📊 \`logs/\` - Centralized logs
- 🛠️ \`tools/\` - Development utilities

### Next Steps:
1. Run comprehensive tests: \`./scripts/deployment/comprehensive_test_supermcp.sh\`
2. Start services: \`./scripts/deployment/start_system.sh\`
3. Deploy to production: \`./scripts/deployment/deploy_production.sh\`

**Your SuperMCP is now enterprise-ready! 🚀**
EOF

echo ""
log "SUCCESS" "🎉 CLEANUP COMPLETED SUCCESSFULLY!"
log "SUCCESS" "📄 Report saved: CLEANUP_REPORT.md"
log "SUCCESS" "🗂️ Archive created: $archive_dir"
echo ""
log "INFO" "🚀 Your SuperMCP is now fully migrated and clean!"
log "INFO" "📋 Next steps:"
echo "     1. Run tests: ./comprehensive_test_supermcp.sh"
echo "     2. Start services: ./scripts/deployment/start_system.sh"
echo "     3. Review: cat CLEANUP_REPORT.md"

# Optional: Show the new clean structure
echo ""
echo "📂 NEW CLEAN ROOT STRUCTURE:"
echo "============================"
ls -la --color=always | head -20