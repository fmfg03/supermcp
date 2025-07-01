class SuperMCPDashboard {
    constructor() {
        this.socket = null;
        this.nodes = new Map();
        this.activities = [];
        this.metrics = {
            totalNodes: 0,
            activeTasks: 0,
            messageCount: 0,
            systemUptime: 0
        };
        this.performanceData = {
            labels: [],
            datasets: [{
                label: 'Nodes Online',
                data: [],
                borderColor: '#00ff88',
                backgroundColor: 'rgba(0, 255, 136, 0.1)',
                tension: 0.4
            }, {
                label: 'Active Tasks',
                data: [],
                borderColor: '#0088ff',
                backgroundColor: 'rgba(0, 136, 255, 0.1)',
                tension: 0.4
            }]
        };
        
        this.initializeWebSocket();
        this.initializeChart();
        this.startMetricsUpdater();
    }
    
    initializeWebSocket() {
        const brokerUrl = window.location.protocol === 'https:' 
            ? `wss://${window.location.host}` 
            : `ws://${window.location.hostname}:8080`;
        
        console.log('Connecting to broker at:', brokerUrl);
        
        this.socket = io(brokerUrl, {
            transports: ['websocket', 'polling'],
            timeout: 10000,
            forceNew: true
        });
        
        this.socket.on('connect', () => {
            console.log('Connected to MCP Broker');
            this.updateConnectionStatus(true);
            this.registerAsOperator();
            this.requestNetworkStatus();
        });
        
        this.socket.on('disconnect', () => {
            console.log('Disconnected from MCP Broker');
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('network_status', (data) => {
            console.log('Network status received:', data);
            this.updateNetworkStatus(data);
        });
        
        this.socket.on('node_joined', (nodeData) => {
            console.log('Node joined:', nodeData);
            this.addNode(nodeData);
            this.addActivity('join', `${nodeData.name} connected`, nodeData.type);
        });
        
        this.socket.on('node_left', (nodeData) => {
            console.log('Node left:', nodeData);
            this.removeNode(nodeData.id);
            this.addActivity('leave', `${nodeData.name} disconnected`, nodeData.type);
        });
        
        this.socket.on('message', (message) => {
            this.addActivity('message', `Message from ${message.from} to ${message.to}`, message.type);
            this.metrics.messageCount++;
        });
        
        this.socket.on('task_assigned', (task) => {
            this.addActivity('task', `Task assigned: ${task.capability}`, 'system');
            this.metrics.activeTasks++;
        });
        
        this.socket.on('task_completed', (task) => {
            this.addActivity('task', `Task completed: ${task.capability}`, 'system');
            this.metrics.activeTasks = Math.max(0, this.metrics.activeTasks - 1);
        });
        
        this.socket.on('connect_error', (error) => {
            console.error('Connection error:', error);
            this.updateConnectionStatus(false);
        });
    }
    
    registerAsOperator() {
        this.socket.emit('register', {
            type: 'operator',
            name: 'Dashboard',
            capabilities: ['monitoring', 'broadcasting', 'administration']
        });
    }
    
    requestNetworkStatus() {
        this.socket.emit('get_network_status');
    }
    
    updateConnectionStatus(connected) {
        const statusEl = document.getElementById('connectionStatus');
        const statusText = statusEl.querySelector('span');
        
        if (connected) {
            statusEl.className = 'status-indicator connected';
            statusText.textContent = 'Connected';
        } else {
            statusEl.className = 'status-indicator disconnected';
            statusText.textContent = 'Disconnected';
        }
    }
    
    updateNetworkStatus(data) {
        this.metrics.totalNodes = data.totalNodes;
        
        // Update nodes
        data.nodes.forEach(node => {
            this.addNode(node);
        });
        
        this.updateMetricsDisplay();
    }
    
    addNode(nodeData) {
        this.nodes.set(nodeData.id, nodeData);
        this.updateNodesList();
        this.updateMetricsDisplay();
    }
    
    removeNode(nodeId) {
        this.nodes.delete(nodeId);
        this.updateNodesList();
        this.updateMetricsDisplay();
    }
    
    updateNodesList() {
        const nodeListEl = document.getElementById('nodeList');
        nodeListEl.innerHTML = '';
        
        for (const [id, node] of this.nodes) {
            const nodeEl = document.createElement('div');
            nodeEl.className = `node-item ${node.status || 'offline'}`;
            nodeEl.innerHTML = `
                <div class="node-name">${node.name}</div>
                <div class="node-type">${node.type}</div>
                <div class="node-capabilities">${Array.isArray(node.capabilities) ? node.capabilities.join(', ') : 'No capabilities'}</div>
            `;
            
            nodeEl.addEventListener('click', () => {
                this.selectNode(id);
            });
            
            nodeListEl.appendChild(nodeEl);
        }
        
        this.metrics.totalNodes = this.nodes.size;
    }
    
    selectNode(nodeId) {
        // Remove previous selection
        document.querySelectorAll('.node-item').forEach(el => {
            el.classList.remove('selected');
        });
        
        // Add selection to clicked node
        event.currentTarget.classList.add('selected');
        
        // Show node details (could implement a modal or side panel)
        const node = this.nodes.get(nodeId);
        console.log('Selected node:', node);
    }
    
    addActivity(type, title, category) {
        const activity = {
            id: Date.now(),
            type,
            title,
            category,
            timestamp: new Date()
        };
        
        this.activities.unshift(activity);
        
        // Keep only last 50 activities
        if (this.activities.length > 50) {
            this.activities = this.activities.slice(0, 50);
        }
        
        this.updateActivityFeed();
    }
    
    updateActivityFeed() {
        const feedEl = document.getElementById('activityFeed');
        feedEl.innerHTML = '';
        
        this.activities.forEach(activity => {
            const activityEl = document.createElement('div');
            activityEl.className = 'activity-item';
            activityEl.innerHTML = `
                <div class="activity-icon ${activity.type}">
                    ${this.getActivityIcon(activity.type)}
                </div>
                <div class="activity-content">
                    <div class="activity-title">${activity.title}</div>
                    <div class="activity-time">${this.formatTime(activity.timestamp)}</div>
                </div>
            `;
            feedEl.appendChild(activityEl);
        });
    }
    
    getActivityIcon(type) {
        const icons = {
            join: '⚡',
            leave: '❌',
            task: '🎯',
            message: '💬'
        };
        return icons[type] || '📡';
    }
    
    formatTime(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        
        if (diff < 60000) { // Less than 1 minute
            return 'Just now';
        } else if (diff < 3600000) { // Less than 1 hour
            return `${Math.floor(diff / 60000)}m ago`;
        } else {
            return timestamp.toLocaleTimeString();
        }
    }
    
    updateMetricsDisplay() {
        document.getElementById('totalNodes').textContent = this.metrics.totalNodes;
        document.getElementById('activeTasks').textContent = this.metrics.activeTasks;
        document.getElementById('messageCount').textContent = this.metrics.messageCount;
        document.getElementById('systemUptime').textContent = this.formatUptime(this.metrics.systemUptime);
    }
    
    formatUptime(seconds) {
        if (seconds < 60) return `${seconds}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
        if (seconds < 86400) return `${Math.floor(seconds / 3600)}h`;
        return `${Math.floor(seconds / 86400)}d`;
    }
    
    initializeChart() {
        const ctx = document.getElementById('performanceChart').getContext('2d');
        this.chart = new Chart(ctx, {
            type: 'line',
            data: this.performanceData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    x: {
                        grid: { color: '#333' },
                        ticks: { color: '#999' }
                    },
                    y: {
                        grid: { color: '#333' },
                        ticks: { color: '#999' },
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        labels: { color: '#999' }
                    }
                }
            }
        });
    }
    
    updateChart() {
        const now = new Date().toLocaleTimeString();
        
        this.performanceData.labels.push(now);
        this.performanceData.datasets[0].data.push(this.metrics.totalNodes);
        this.performanceData.datasets[1].data.push(this.metrics.activeTasks);
        
        // Keep only last 20 data points
        if (this.performanceData.labels.length > 20) {
            this.performanceData.labels.shift();
            this.performanceData.datasets.forEach(dataset => {
                dataset.data.shift();
            });
        }
        
        this.chart.update();
    }
    
    startMetricsUpdater() {
        setInterval(() => {
            this.metrics.systemUptime++;
            this.updateMetricsDisplay();
            this.updateChart();
            
            // Reset message count every minute
            this.metrics.messageCount = 0;
        }, 1000);
        
        // Update activity times
        setInterval(() => {
            this.updateActivityFeed();
        }, 30000);
    }
    
    sendBroadcast() {
        const input = document.getElementById('broadcastInput');
        const message = input.value.trim();
        
        if (!message) return;
        
        this.socket.emit('message', {
            to: 'broadcast',
            type: 'operator_broadcast',
            payload: { message, timestamp: new Date().toISOString() }
        });
        
        this.addActivity('message', `Broadcasted: ${message}`, 'operator');
        input.value = '';
    }
    
    clearActivity() {
        this.activities = [];
        this.updateActivityFeed();
    }
}

// Global functions for HTML event handlers
function sendBroadcast() {
    dashboard.sendBroadcast();
}

function clearActivity() {
    dashboard.clearActivity();
}

// Initialize dashboard when page loads
let dashboard;
document.addEventListener('DOMContentLoaded', () => {
    dashboard = new SuperMCPDashboard();
});

// Handle broadcast input enter key
document.addEventListener('DOMContentLoaded', () => {
    const broadcastInput = document.getElementById('broadcastInput');
    broadcastInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') {
            sendBroadcast();
        }
    });
});