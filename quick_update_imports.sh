#!/bin/bash
# quick_update_imports.sh - Updates only critical application imports

set -e

echo "🔧 Quick Import Updates for Critical Files..."

# Update Docker Compose files
echo "📦 Updating Docker Compose configurations..."
for file in infrastructure/docker/docker-compose*.yml; do
    if [ -f "$file" ]; then
        echo "Updating: $file"
        # Update context paths
        sed -i 's|context: \./frontend|context: ../../apps/frontend|g' "$file"
        sed -i 's|context: \./backend|context: ../../apps/backend|g' "$file"
        sed -i 's|context: \./mcp-observatory|context: ../../apps/mcp-observatory|g' "$file"
        sed -i 's|context: \./voice_system|context: ../../services/voice-system|g' "$file"
        
        # Update volume paths
        sed -i 's|\./config:|../../config/environments:|g' "$file"
        sed -i 's|\./nginx:|../nginx:|g' "$file"
        sed -i 's|\./ssl:|../ssl:|g' "$file"
        sed -i 's|\./logs:|../../logs/production:|g' "$file"
    fi
done

# Update main Python services in services directory
echo "🐍 Updating Python service imports..."
for service_dir in services/*/; do
    if [ -d "$service_dir" ]; then
        echo "Checking service: $service_dir"
        for py_file in "$service_dir"*.py; do
            if [ -f "$py_file" ]; then
                echo "Updating imports in: $py_file"
                # Update relative imports to absolute ones
                sed -i 's|from mcp_orchestration_server|from services.orchestration.mcp_orchestration_server|g' "$py_file"
                sed -i 's|from sam_memory_analyzer|from services.memory_analyzer.sam_memory_analyzer|g' "$py_file"
                sed -i 's|from complete_webhook_agent_end_task_system|from services.webhook_system.complete_webhook_agent_end_task_system|g' "$py_file"
            fi
        done
    fi
done

# Update main app configurations
echo "⚙️ Updating app configurations..."

# Update frontend package.json if it exists
if [ -f "apps/frontend/package.json" ]; then
    echo "Frontend package.json found, updating proxy settings..."
    # Could add proxy configuration updates here if needed
fi

# Update backend service references
if [ -f "apps/backend/src/server.cjs" ]; then
    echo "Updating backend server references..."
    # Update any hardcoded paths in backend
    sed -i 's|"\.\.\/\.\.\/config\/|"../../../config/environments/|g' "apps/backend/src/server.cjs"
fi

# Create workspace package.json for monorepo
echo "📦 Creating monorepo package.json..."
cat > package.json << 'EOF'
{
  "name": "supermcp-monorepo",
  "version": "2.0.0",
  "description": "SuperMCP Multi-Agent Coordination Platform - Restructured",
  "private": true,
  "type": "module",
  "workspaces": [
    "apps/*",
    "services/*",
    "tools/*"
  ],
  "scripts": {
    "build": "npm run build --workspaces --if-present",
    "test": "npm run test --workspaces --if-present",
    "start": "npm run start --workspaces --if-present",
    "dev": "npm run dev --workspaces --if-present",
    "lint": "npm run lint --workspaces --if-present",
    "clean": "npm run clean --workspaces --if-present"
  },
  "engines": {
    "node": ">=18.0.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "typescript": "^5.0.0"
  }
}
EOF

# Create simple package.json files for services that don't have them
echo "📦 Creating service package.json files..."
for service_dir in services/*/; do
    if [ -d "$service_dir" ] && [ ! -f "$service_dir/package.json" ]; then
        service_name=$(basename "$service_dir")
        echo "Creating package.json for service: $service_name"
        cat > "$service_dir/package.json" << EOF
{
  "name": "@supermcp/service-$service_name",
  "version": "2.0.0",
  "private": true,
  "type": "module",
  "scripts": {
    "start": "python main.py",
    "dev": "python main.py --dev",
    "test": "python -m pytest"
  },
  "engines": {
    "python": ">=3.8"
  }
}
EOF
    fi
done

echo "✅ Quick import updates completed!"
echo ""
echo "📋 Updated:"
echo "   - Docker Compose configurations"
echo "   - Python service imports"
echo "   - Monorepo package.json structure"
echo "   - Service package.json files"
echo ""
echo "🔍 Next: Test the new structure!"