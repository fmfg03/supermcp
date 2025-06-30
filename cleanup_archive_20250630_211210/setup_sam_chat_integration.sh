#!/bin/bash
# setup_sam_chat_integration.sh
# Configurar sam.chat como punto de acceso principal para SuperMCP

echo "🌐 CONFIGURANDO SAM.CHAT COMO CENTRO DE CONTROL SUPERMCP"
echo "======================================================="

cd /root/supermcp

# 1. Crear directorio web para sam.chat
echo "📁 Creando estructura web para sam.chat..."
mkdir -p /var/www/sam.chat/{dashboard,api,assets}

# 2. Crear página principal de sam.chat con acceso a todo SuperMCP
echo "🎨 Creando interfaz principal de sam.chat..."
cat > /var/www/sam.chat/index.html << 'EOF'
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SAM.CHAT - SuperMCP Command Center</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            color: white;
            min-height: 100vh;
            overflow-x: hidden;
        }
        
        .container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        
        .header { 
            text-align: center; 
            margin-bottom: 40px; 
            background: rgba(255,255,255,0.1);
            padding: 30px; 
            border-radius: 15px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        
        .header h1 { 
            font-size: 3em; 
            margin-bottom: 15px; 
            background: linear-gradient(45deg, #00f5ff, #00d4ff, #0099ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .header p { 
            font-size: 1.3em; 
            opacity: 0.9; 
            margin-bottom: 10px;
        }
        
        .status-bar {
            background: rgba(0,255,0,0.2);
            padding: 10px 20px;
            border-radius: 25px;
            display: inline-block;
            margin-top: 15px;
            border: 1px solid rgba(0,255,0,0.5);
        }
        
        .systems-grid { 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 25px; 
            margin-bottom: 40px; 
        }
        
        .system-card { 
            background: rgba(255,255,255,0.1); 
            padding: 25px; 
            border-radius: 15px;
            backdrop-filter: blur(20px);
            border: 1px solid rgba(255,255,255,0.2);
            transition: all 0.3s ease;
            cursor: pointer;
        }
        
        .system-card:hover {
            transform: translateY(-5px);
            background: rgba(255,255,255,0.15);
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }
        
        .system-icon {
            font-size: 3em;
            margin-bottom: 15px;
            display: block;
            text-align: center;
        }
        
        .system-title {
            font-size: 1.4em;
            font-weight: bold;
            margin-bottom: 10px;
            text-align: center;
        }
        
        .system-description {
            opacity: 0.8;
            margin-bottom: 15px;
            text-align: center;
            line-height: 1.4;
        }
        
        .system-url {
            background: rgba(0,0,0,0.3);
            padding: 8px 12px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            text-align: center;
            margin-bottom: 10px;
        }
        
        .system-status {
            text-align: center;
            padding: 5px 10px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
        }
        
        .status-online { background: #4CAF50; }
        .status-checking { background: #FF9800; }
        .status-offline { background: #F44336; }
        
        .quick-actions {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
            margin-top: 30px;
        }
        
        .action-btn {
            background: linear-gradient(45deg, #00f5ff, #0099ff);
            color: white;
            padding: 15px 25px;
            border: none;
            border-radius: 10px;
            font-size: 1em;
            font-weight: bold;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            text-align: center;
            display: block;
        }
        
        .action-btn:hover {
            background: linear-gradient(45deg, #0099ff, #0066cc);
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,153,255,0.3);
        }
        
        .footer {
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            background: rgba(255,255,255,0.05);
            border-radius: 10px;
            border-top: 1px solid rgba(255,255,255,0.1);
        }
        
        .loading { opacity: 0.7; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .pulse { animation: pulse 2s infinite; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 SAM.CHAT</h1>
            <p>SuperMCP Enterprise Command Center</p>
            <p style="font-size: 1em; opacity: 0.7;">World's First MCP + LangGraph + Graphiti + A2A + Voice Unified System</p>
            <div class="status-bar" id="system-status">
                🔄 Checking system status...
            </div>
        </div>
        
        <div class="systems-grid" id="systems-grid">
            <!-- Systems will be loaded here -->
        </div>
        
        <div class="quick-actions">
            <a href="#" onclick="openUnifiedDashboard()" class="action-btn">
                🌐 Open Unified Dashboard
            </a>
            <a href="#" onclick="openVoiceSystem()" class="action-btn">
                🎤 Voice System Control
            </a>
            <a href="#" onclick="openA2ANetwork()" class="action-btn">
                📡 A2A Agent Network
            </a>
            <a href="#" onclick="openEnterpriseMonitoring()" class="action-btn">
                📊 Enterprise Monitoring
            </a>
            <a href="#" onclick="refreshSystemStatus()" class="action-btn">
                🔄 Refresh Status
            </a>
            <a href="#" onclick="openSystemLogs()" class="action-btn">
                📋 View System Logs
            </a>
        </div>
        
        <div class="footer">
            <p>🚀 <strong>SuperMCP Unified System</strong> - Powered by SAM.CHAT</p>
            <p style="font-size: 0.9em; opacity: 0.7; margin-top: 10px;">
                Last updated: <span id="last-updated">Loading...</span>
            </p>
        </div>
    </div>

    <script>
        const systems = [
            {
                id: 'unified_dashboard',
                icon: '🌐',
                title: 'Unified Command Center',
                description: 'Main control interface for all SuperMCP systems',
                url: 'http://localhost:9000',
                port: 9000
            },
            {
                id: 'voice_system',
                icon: '🎤',
                title: 'Voice AI System',
                description: 'Multilingüe voice interactions (ES/EN) with LangWatch monitoring',
                url: 'http://localhost:8300',
                port: 8300
            },
            {
                id: 'a2a_network',
                icon: '📡',
                title: 'A2A Agent Network',
                description: 'Agent-to-Agent communication and task delegation',
                url: 'http://localhost:8200',
                port: 8200
            },
            {
                id: 'googleai_agent',
                icon: '🤖',
                title: 'GoogleAI Agent',
                description: 'Specialized AI agent with Gemini Pro/Vision capabilities',
                url: 'http://localhost:8213',
                port: 8213
            },
            {
                id: 'enterprise_dashboard',
                icon: '📊',
                title: 'Enterprise Dashboard',
                description: 'Real-time monitoring and observability platform',
                url: 'http://localhost:8126',
                port: 8126
            },
            {
                id: 'task_validation',
                icon: '✅',
                title: 'Task Validation',
                description: 'Cross-system task validation with offline mode',
                url: 'http://localhost:8127',
                port: 8127
            },
            {
                id: 'webhook_monitoring',
                icon: '👀',
                title: 'Webhook Monitoring',
                description: 'Active webhook monitoring with intelligent retries',
                url: 'http://localhost:8125',
                port: 8125
            },
            {
                id: 'enterprise_bridge',
                icon: '🌉',
                title: 'Enterprise Bridge',
                description: 'Integration bridge connecting all enterprise features',
                url: 'http://localhost:8128',
                port: 8128
            }
        ];

        async function checkSystemStatus() {
            const statusElement = document.getElementById('system-status');
            const systemsGrid = document.getElementById('systems-grid');
            
            statusElement.innerHTML = '🔄 Checking system status...';
            statusElement.className = 'status-bar pulse';
            
            let healthyCount = 0;
            let totalCount = systems.length;
            
            systemsGrid.innerHTML = '';
            
            for (const system of systems) {
                const systemCard = createSystemCard(system);
                systemsGrid.appendChild(systemCard);
                
                try {
                    const response = await fetch(`${system.url}/health`, { 
                        method: 'GET',
                        timeout: 3000 
                    });
                    
                    if (response.ok) {
                        updateSystemStatus(system.id, 'online');
                        healthyCount++;
                    } else {
                        updateSystemStatus(system.id, 'offline');
                    }
                } catch (error) {
                    updateSystemStatus(system.id, 'offline');
                }
            }
            
            // Update overall status
            const healthPercentage = Math.round((healthyCount / totalCount) * 100);
            
            if (healthPercentage >= 80) {
                statusElement.innerHTML = `✅ System Operational (${healthyCount}/${totalCount} services)`;
                statusElement.style.background = 'rgba(76, 175, 80, 0.3)';
                statusElement.style.borderColor = 'rgba(76, 175, 80, 0.8)';
            } else if (healthPercentage >= 50) {
                statusElement.innerHTML = `⚠️ Partial Operation (${healthyCount}/${totalCount} services)`;
                statusElement.style.background = 'rgba(255, 152, 0, 0.3)';
                statusElement.style.borderColor = 'rgba(255, 152, 0, 0.8)';
            } else {
                statusElement.innerHTML = `❌ System Issues (${healthyCount}/${totalCount} services)`;
                statusElement.style.background = 'rgba(244, 67, 54, 0.3)';
                statusElement.style.borderColor = 'rgba(244, 67, 54, 0.8)';
            }
            
            statusElement.classList.remove('pulse');
            document.getElementById('last-updated').textContent = new Date().toLocaleString();
        }

        function createSystemCard(system) {
            const card = document.createElement('div');
            card.className = 'system-card';
            card.id = `card-${system.id}`;
            card.onclick = () => openSystem(system.url);
            
            card.innerHTML = `
                <div class="system-icon">${system.icon}</div>
                <div class="system-title">${system.title}</div>
                <div class="system-description">${system.description}</div>
                <div class="system-url">${system.url}</div>
                <div class="system-status status-checking" id="status-${system.id}">
                    🔄 Checking...
                </div>
            `;
            
            return card;
        }

        function updateSystemStatus(systemId, status) {
            const statusElement = document.getElementById(`status-${systemId}`);
            
            if (status === 'online') {
                statusElement.innerHTML = '✅ Online';
                statusElement.className = 'system-status status-online';
            } else {
                statusElement.innerHTML = '❌ Offline';
                statusElement.className = 'system-status status-offline';
            }
        }

        function openSystem(url) {
            window.open(url, '_blank');
        }

        function openUnifiedDashboard() {
            window.open('http://localhost:9000', '_blank');
        }

        function openVoiceSystem() {
            window.open('http://localhost:8300', '_blank');
        }

        function openA2ANetwork() {
            window.open('http://localhost:8200', '_blank');
        }

        function openEnterpriseMonitoring() {
            window.open('http://localhost:8126', '_blank');
        }

        function refreshSystemStatus() {
            checkSystemStatus();
        }

        function openSystemLogs() {
            // Open logs in new tab (would need backend support)
            alert('System logs feature - would open centralized log viewer');
        }

        // Initialize
        checkSystemStatus();
        
        // Auto-refresh every 30 seconds
        setInterval(checkSystemStatus, 30000);
    </script>
</body>
</html>
EOF

# 3. Crear configuración nginx para sam.chat
echo "⚙️ Configurando nginx para sam.chat..."
cat > /etc/nginx/sites-available/sam.chat << 'EOF'
server {
    listen 80;
    server_name sam.chat www.sam.chat;
    root /var/www/sam.chat;
    index index.html;

    # Main dashboard
    location / {
        try_files $uri $uri/ =404;
        add_header Cache-Control "no-cache, no-store, must-revalidate";
        add_header Pragma "no-cache";
        add_header Expires "0";
    }

    # API proxy to unified dashboard
    location /api/ {
        proxy_pass http://127.0.0.1:9000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Direct access to unified dashboard
    location /unified/ {
        proxy_pass http://127.0.0.1:9000/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Voice system proxy
    location /voice/ {
        proxy_pass http://127.0.0.1:8300/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # A2A network proxy
    location /a2a/ {
        proxy_pass http://127.0.0.1:8200/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Enterprise monitoring proxy
    location /enterprise/ {
        proxy_pass http://127.0.0.1:8126/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Enable compression
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied expired no-cache no-store private must-revalidate auth;
    gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;
}
EOF

# 4. Activar sitio y reiniciar nginx
echo "🔄 Activando configuración de sam.chat..."
ln -sf /etc/nginx/sites-available/sam.chat /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 5. Ajustar permisos
echo "🔒 Configurando permisos..."
chown -R www-data:www-data /var/www/sam.chat
chmod -R 755 /var/www/sam.chat

# 6. Crear script de actualización de estado
echo "📊 Creando monitor de estado..."
cat > /var/www/sam.chat/status.json << 'EOF'
{
    "timestamp": "loading...",
    "systems": {},
    "overall_health": "checking"
}
EOF

# 7. Verificar estado del sistema
echo "🏥 Verificando estado del sistema SuperMCP..."
/root/supermcp/supermcp_unified/scripts/check_system_status.sh

echo ""
echo "✅ SAM.CHAT CONFIGURADO COMO CENTRO DE CONTROL SUPERMCP"
echo "======================================================"
echo ""
echo "🌐 ACCESO PRINCIPAL:"
echo "   http://sam.chat"
echo "   http://65.109.54.94"
echo ""
echo "🎯 CARACTERÍSTICAS:"
echo "   ✅ Interfaz web elegante y responsive"
echo "   ✅ Estado en tiempo real de todos los sistemas"
echo "   ✅ Acceso directo a cada componente"
echo "   ✅ Monitoreo automático cada 30 segundos"
echo "   ✅ Enlaces directos a funcionalidades"
echo ""
echo "🔗 RUTAS DE ACCESO DESDE SAM.CHAT:"
echo "   • Dashboard Unificado: http://sam.chat/unified/"
echo "   • Sistema de Voz: http://sam.chat/voice/"
echo "   • Red A2A: http://sam.chat/a2a/"
echo "   • Monitoreo Enterprise: http://sam.chat/enterprise/"
echo ""
echo "🎛️ GESTIÓN:"
echo "   • Estado del sistema: curl http://sam.chat/api/status"
echo "   • Recargar nginx: systemctl reload nginx"
echo "   • Logs nginx: tail -f /var/log/nginx/access.log"
echo ""
echo "🚀 ¡AHORA PUEDES OPERAR TODO SUPERMCP DESDE SAM.CHAT!"