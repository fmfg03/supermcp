#!/usr/bin/env python3
"""
🎪 Swarm Intelligence Web Dashboard
Real-time monitoring and analytics for the swarm intelligence system

Features:
- Real-time swarm visualization
- Agent status monitoring
- Communication pattern analysis
- Emergent behavior tracking
- Swarm performance metrics
"""

from flask import Flask, render_template_string, jsonify, request
from flask_socketio import SocketIO, emit
import asyncio
import json
import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any
import websockets
import networkx as nx
from collections import defaultdict, deque

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config['SECRET_KEY'] = 'swarm_dashboard_secret'
socketio = SocketIO(app, cors_allowed_origins="*")

class SwarmDashboard:
    """Dashboard for monitoring swarm intelligence"""
    
    def __init__(self, swarm_port: int = 8400):
        self.swarm_port = swarm_port
        self.websocket = None
        self.connected = False
        
        # Dashboard data
        self.agents: Dict[str, Any] = {}
        self.messages: deque = deque(maxlen=1000)
        self.tasks: Dict[str, Any] = {}
        self.consensus_sessions: Dict[str, Any] = {}
        
        # Analytics data
        self.communication_graph = nx.Graph()
        self.message_stats = defaultdict(int)
        self.performance_metrics = {
            "messages_per_minute": 0,
            "consensus_success_rate": 0,
            "task_completion_rate": 0,
            "swarm_coherence": 0,
            "emergent_behaviors": 0
        }
        
        # Start monitoring
        self.monitoring_thread = threading.Thread(target=self._start_monitoring, daemon=True)
        self.monitoring_thread.start()
    
    def _start_monitoring(self):
        """Start monitoring swarm in background thread"""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(self._monitor_swarm())
    
    async def _monitor_swarm(self):
        """Monitor swarm intelligence system"""
        while True:
            try:
                # Connect to swarm as observer
                self.websocket = await websockets.connect(f"ws://sam.chat:{self.swarm_port}")
                
                # Register as dashboard observer
                registration = {
                    "agent_id": "swarm_dashboard",
                    "agent_info": {
                        "name": "Swarm Dashboard",
                        "type": "observer",
                        "role": "observer",
                        "capabilities": ["monitoring", "analytics", "visualization"]
                    }
                }
                await self.websocket.send(json.dumps(registration))
                
                self.connected = True
                logger.info("📊 Dashboard connected to swarm")
                
                # Monitor messages
                async for message_data in self.websocket:
                    await self._process_swarm_message(message_data)
                    
            except websockets.exceptions.ConnectionClosed:
                logger.info("🔌 Dashboard disconnected from swarm")
                self.connected = False
            except Exception as e:
                logger.error(f"❌ Dashboard connection error: {e}")
                self.connected = False
            
            # Retry connection
            await asyncio.sleep(5)
    
    async def _process_swarm_message(self, message_data: str):
        """Process message from swarm"""
        try:
            message = json.loads(message_data)
            
            # Store message
            message["received_at"] = datetime.now().isoformat()
            self.messages.append(message)
            
            # Update analytics
            self._update_message_analytics(message)
            
            # Update agent status
            sender_id = message.get("sender_id")
            if sender_id and sender_id != "swarm_core":
                self._update_agent_status(sender_id, message)
            
            # Handle specific message types
            content = message.get("content", {})
            msg_type = content.get("type")
            
            if msg_type == "agent_joined":
                self._handle_agent_joined(content)
            elif msg_type == "agent_disconnected":
                self._handle_agent_disconnected(content)
            elif msg_type == "task_assignment":
                self._handle_task_assignment(content)
            elif msg_type == "consensus_result":
                self._handle_consensus_result(content)
            elif msg_type == "emergent_patterns_detected":
                self._handle_emergent_patterns(content)
            
            # Emit to web clients
            socketio.emit('swarm_update', {
                'type': 'message',
                'data': message
            })
            
        except Exception as e:
            logger.error(f"Error processing swarm message: {e}")
    
    def _update_message_analytics(self, message: Dict[str, Any]):
        """Update message analytics"""
        msg_type = message.get("message_type", "unknown")
        sender_id = message.get("sender_id", "unknown")
        
        # Count message types
        self.message_stats[msg_type] += 1
        self.message_stats["total"] += 1
        
        # Update communication graph
        recipients = message.get("recipients", [])
        if recipients:
            for recipient in recipients:
                if recipient != sender_id:
                    if self.communication_graph.has_edge(sender_id, recipient):
                        self.communication_graph[sender_id][recipient]["weight"] += 1
                    else:
                        self.communication_graph.add_edge(sender_id, recipient, weight=1)
        
        # Calculate messages per minute
        recent_messages = [
            msg for msg in list(self.messages)[-60:] 
            if (datetime.now() - datetime.fromisoformat(msg.get("received_at", datetime.now().isoformat()))).total_seconds() < 60
        ]
        self.performance_metrics["messages_per_minute"] = len(recent_messages)
    
    def _update_agent_status(self, agent_id: str, message: Dict[str, Any]):
        """Update agent status"""
        if agent_id not in self.agents:
            self.agents[agent_id] = {
                "id": agent_id,
                "name": agent_id,
                "type": "unknown",
                "status": "active",
                "last_seen": datetime.now().isoformat(),
                "message_count": 0,
                "performance": 1.0
            }
        
        agent = self.agents[agent_id]
        agent["last_seen"] = datetime.now().isoformat()
        agent["message_count"] += 1
        
        # Update agent info if available
        if "sender_type" in message:
            agent["type"] = message["sender_type"]
    
    def _handle_agent_joined(self, content: Dict[str, Any]):
        """Handle agent joined event"""
        agent_id = content.get("agent_id")
        agent_name = content.get("agent_name", agent_id)
        agent_type = content.get("agent_type", "unknown")
        capabilities = content.get("capabilities", [])
        
        self.agents[agent_id] = {
            "id": agent_id,
            "name": agent_name,
            "type": agent_type,
            "capabilities": capabilities,
            "status": "active",
            "joined_at": datetime.now().isoformat(),
            "last_seen": datetime.now().isoformat(),
            "message_count": 0,
            "performance": 1.0
        }
        
        logger.info(f"👋 Agent {agent_name} joined swarm")
    
    def _handle_agent_disconnected(self, content: Dict[str, Any]):
        """Handle agent disconnected event"""
        agent_id = content.get("agent_id")
        
        if agent_id in self.agents:
            self.agents[agent_id]["status"] = "disconnected"
            self.agents[agent_id]["disconnected_at"] = datetime.now().isoformat()
        
        logger.info(f"👋 Agent {agent_id} disconnected")
    
    def _handle_task_assignment(self, content: Dict[str, Any]):
        """Handle task assignment event"""
        task = content.get("task", {})
        task_id = task.get("id")
        
        if task_id:
            self.tasks[task_id] = {
                **task,
                "assigned_at": datetime.now().isoformat(),
                "status": "assigned"
            }
    
    def _handle_consensus_result(self, content: Dict[str, Any]):
        """Handle consensus result event"""
        session_id = content.get("session_id")
        result = content.get("result", {})
        
        if session_id:
            self.consensus_sessions[session_id] = {
                "session_id": session_id,
                "result": result,
                "completed_at": datetime.now().isoformat()
            }
            
            # Update consensus success rate
            total_sessions = len(self.consensus_sessions)
            successful_sessions = sum(
                1 for session in self.consensus_sessions.values()
                if session.get("result", {}).get("consensus_reached", False)
            )
            
            if total_sessions > 0:
                self.performance_metrics["consensus_success_rate"] = successful_sessions / total_sessions
    
    def _handle_emergent_patterns(self, content: Dict[str, Any]):
        """Handle emergent patterns detection"""
        patterns = content.get("patterns", [])
        self.performance_metrics["emergent_behaviors"] += len(patterns)
        
        logger.info(f"🧠 Detected {len(patterns)} emergent patterns")
    
    def get_dashboard_data(self) -> Dict[str, Any]:
        """Get dashboard data for web interface"""
        active_agents = [agent for agent in self.agents.values() if agent["status"] == "active"]
        recent_messages = list(self.messages)[-20:]
        
        # Calculate swarm coherence
        if len(active_agents) > 1:
            communication_density = self.communication_graph.number_of_edges() / max(1, len(active_agents) * (len(active_agents) - 1) / 2)
            self.performance_metrics["swarm_coherence"] = communication_density
        
        # Task completion rate
        completed_tasks = sum(1 for task in self.tasks.values() if task.get("status") == "completed")
        total_tasks = len(self.tasks)
        if total_tasks > 0:
            self.performance_metrics["task_completion_rate"] = completed_tasks / total_tasks
        
        return {
            "timestamp": datetime.now().isoformat(),
            "connected": self.connected,
            "agents": {
                "total": len(self.agents),
                "active": len(active_agents),
                "list": list(self.agents.values())
            },
            "messages": {
                "total": len(self.messages),
                "recent": recent_messages,
                "stats": dict(self.message_stats)
            },
            "tasks": {
                "total": len(self.tasks),
                "list": list(self.tasks.values())
            },
            "consensus": {
                "total": len(self.consensus_sessions),
                "list": list(self.consensus_sessions.values())
            },
            "performance": self.performance_metrics,
            "communication_graph": {
                "nodes": list(self.communication_graph.nodes()),
                "edges": [
                    {
                        "source": edge[0],
                        "target": edge[1],
                        "weight": self.communication_graph[edge[0]][edge[1]]["weight"]
                    }
                    for edge in self.communication_graph.edges()
                ]
            }
        }

# Global dashboard instance
dashboard = SwarmDashboard()

# Web routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template_string(DASHBOARD_HTML_TEMPLATE)

@app.route('/api/dashboard')
def api_dashboard():
    """API endpoint for dashboard data"""
    return jsonify(dashboard.get_dashboard_data())

@app.route('/api/agents')
def api_agents():
    """API endpoint for agents data"""
    return jsonify(list(dashboard.agents.values()))

@app.route('/api/messages')
def api_messages():
    """API endpoint for messages data"""
    limit = request.args.get('limit', 50, type=int)
    messages = list(dashboard.messages)[-limit:]
    return jsonify(messages)

@app.route('/api/performance')
def api_performance():
    """API endpoint for performance metrics"""
    return jsonify(dashboard.performance_metrics)

# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info("📱 Dashboard client connected")
    emit('status', {'connected': dashboard.connected})
    emit('dashboard_data', dashboard.get_dashboard_data())

@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info("📱 Dashboard client disconnected")

@socketio.on('request_update')
def handle_request_update():
    """Handle update request from client"""
    emit('dashboard_data', dashboard.get_dashboard_data())

# HTML Template for Dashboard
DASHBOARD_HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>🎪 Swarm Intelligence Dashboard</title>
    <script src="https://cdn.socket.io/4.0.0/socket.io.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script src="https://d3js.org/d3.v7.min.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            min-height: 100vh;
        }
        
        .dashboard {
            padding: 20px;
            max-width: 1400px;
            margin: 0 auto;
        }
        
        .header {
            text-align: center;
            margin-bottom: 30px;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            background: linear-gradient(45deg, #FFD700, #FFA500);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }
        
        .status-indicator {
            display: inline-block;
            width: 12px;
            height: 12px;
            border-radius: 50%;
            margin-right: 8px;
            animation: pulse 2s infinite;
        }
        
        .status-connected { background: #4CAF50; }
        .status-disconnected { background: #f44336; }
        
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }
        
        .card {
            background: rgba(255, 255, 255, 0.1);
            border-radius: 15px;
            padding: 20px;
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        .card h3 {
            margin-bottom: 15px;
            color: #FFD700;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .metric {
            display: flex;
            justify-content: space-between;
            margin-bottom: 10px;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .metric:last-child {
            border-bottom: none;
        }
        
        .metric-value {
            font-weight: bold;
            color: #4CAF50;
        }
        
        .agents-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
            gap: 10px;
        }
        
        .agent-card {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 15px;
            text-align: center;
            border: 2px solid transparent;
            transition: all 0.3s ease;
        }
        
        .agent-card.active {
            border-color: #4CAF50;
            box-shadow: 0 0 10px rgba(76, 175, 80, 0.3);
        }
        
        .agent-card.disconnected {
            border-color: #f44336;
            opacity: 0.6;
        }
        
        .agent-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .agent-type {
            font-size: 0.9em;
            opacity: 0.8;
            margin-bottom: 10px;
        }
        
        .agent-stats {
            font-size: 0.8em;
            display: flex;
            justify-content: space-between;
        }
        
        .messages-list {
            max-height: 300px;
            overflow-y: auto;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 15px;
        }
        
        .message {
            margin-bottom: 10px;
            padding: 8px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 5px;
            font-size: 0.9em;
        }
        
        .message-header {
            display: flex;
            justify-content: space-between;
            margin-bottom: 5px;
            font-weight: bold;
        }
        
        .message-sender {
            color: #FFD700;
        }
        
        .message-type {
            color: #4CAF50;
        }
        
        .message-time {
            color: #888;
            font-size: 0.8em;
        }
        
        .communication-graph {
            width: 100%;
            height: 400px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
        }
        
        .chart-container {
            position: relative;
            height: 300px;
            background: rgba(0, 0, 0, 0.2);
            border-radius: 10px;
            padding: 10px;
        }
        
        .refresh-btn {
            background: linear-gradient(45deg, #4CAF50, #45a049);
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
            margin: 10px 0;
            transition: all 0.3s ease;
        }
        
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        }
        
        .full-width {
            grid-column: 1 / -1;
        }
    </style>
</head>
<body>
    <div class="dashboard">
        <div class="header">
            <h1>🎪 Swarm Intelligence Dashboard</h1>
            <p>
                <span id="connection-status" class="status-indicator status-disconnected"></span>
                <span id="connection-text">Connecting to swarm...</span>
            </p>
            <button class="refresh-btn" onclick="requestUpdate()">🔄 Refresh</button>
        </div>
        
        <div class="grid">
            <!-- Performance Metrics -->
            <div class="card">
                <h3>📊 Performance Metrics</h3>
                <div id="performance-metrics">
                    <div class="metric">
                        <span>Messages/min:</span>
                        <span class="metric-value" id="messages-per-minute">0</span>
                    </div>
                    <div class="metric">
                        <span>Consensus Success:</span>
                        <span class="metric-value" id="consensus-rate">0%</span>
                    </div>
                    <div class="metric">
                        <span>Task Completion:</span>
                        <span class="metric-value" id="task-completion">0%</span>
                    </div>
                    <div class="metric">
                        <span>Swarm Coherence:</span>
                        <span class="metric-value" id="swarm-coherence">0%</span>
                    </div>
                    <div class="metric">
                        <span>Emergent Behaviors:</span>
                        <span class="metric-value" id="emergent-behaviors">0</span>
                    </div>
                </div>
            </div>
            
            <!-- Agent Status -->
            <div class="card">
                <h3>🤖 Agent Status</h3>
                <div class="metric">
                    <span>Total Agents:</span>
                    <span class="metric-value" id="total-agents">0</span>
                </div>
                <div class="metric">
                    <span>Active Agents:</span>
                    <span class="metric-value" id="active-agents">0</span>
                </div>
                <div id="agents-container" class="agents-grid">
                    <!-- Agents will be populated here -->
                </div>
            </div>
            
            <!-- Recent Messages -->
            <div class="card">
                <h3>📨 Recent Messages</h3>
                <div id="messages-container" class="messages-list">
                    <!-- Messages will be populated here -->
                </div>
            </div>
            
            <!-- Communication Graph -->
            <div class="card full-width">
                <h3>🌐 Communication Network</h3>
                <div id="communication-graph" class="communication-graph"></div>
            </div>
            
            <!-- Message Statistics -->
            <div class="card">
                <h3>📈 Message Statistics</h3>
                <div class="chart-container">
                    <canvas id="message-stats-chart"></canvas>
                </div>
            </div>
            
            <!-- Performance Trends -->
            <div class="card">
                <h3>📊 Performance Trends</h3>
                <div class="chart-container">
                    <canvas id="performance-chart"></canvas>
                </div>
            </div>
        </div>
    </div>

    <script>
        // Socket.IO connection
        const socket = io();
        
        // Dashboard data
        let dashboardData = {};
        let messageStatsChart = null;
        let performanceChart = null;
        
        // Socket event handlers
        socket.on('connect', function() {
            console.log('Connected to dashboard');
        });
        
        socket.on('status', function(data) {
            updateConnectionStatus(data.connected);
        });
        
        socket.on('dashboard_data', function(data) {
            dashboardData = data;
            updateDashboard(data);
        });
        
        socket.on('swarm_update', function(update) {
            console.log('Swarm update:', update);
            // Handle real-time updates
            if (update.type === 'message') {
                addRealtimeMessage(update.data);
            }
        });
        
        // Update functions
        function updateConnectionStatus(connected) {
            const indicator = document.getElementById('connection-status');
            const text = document.getElementById('connection-text');
            
            if (connected) {
                indicator.className = 'status-indicator status-connected';
                text.textContent = 'Connected to swarm';
            } else {
                indicator.className = 'status-indicator status-disconnected';
                text.textContent = 'Disconnected from swarm';
            }
        }
        
        function updateDashboard(data) {
            updatePerformanceMetrics(data.performance);
            updateAgentStatus(data.agents);
            updateMessages(data.messages.recent);
            updateCommunicationGraph(data.communication_graph);
            updateMessageStatsChart(data.messages.stats);
            updatePerformanceChart(data.performance);
        }
        
        function updatePerformanceMetrics(performance) {
            document.getElementById('messages-per-minute').textContent = Math.round(performance.messages_per_minute);
            document.getElementById('consensus-rate').textContent = Math.round(performance.consensus_success_rate * 100) + '%';
            document.getElementById('task-completion').textContent = Math.round(performance.task_completion_rate * 100) + '%';
            document.getElementById('swarm-coherence').textContent = Math.round(performance.swarm_coherence * 100) + '%';
            document.getElementById('emergent-behaviors').textContent = performance.emergent_behaviors;
        }
        
        function updateAgentStatus(agents) {
            document.getElementById('total-agents').textContent = agents.total;
            document.getElementById('active-agents').textContent = agents.active;
            
            const container = document.getElementById('agents-container');
            container.innerHTML = '';
            
            agents.list.forEach(agent => {
                const agentCard = document.createElement('div');
                agentCard.className = `agent-card ${agent.status}`;
                agentCard.innerHTML = `
                    <div class="agent-name">${agent.name}</div>
                    <div class="agent-type">${agent.type}</div>
                    <div class="agent-stats">
                        <span>Msgs: ${agent.message_count || 0}</span>
                        <span>${agent.status}</span>
                    </div>
                `;
                container.appendChild(agentCard);
            });
        }
        
        function updateMessages(messages) {
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            
            messages.reverse().forEach(message => {
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message';
                
                const time = new Date(message.timestamp).toLocaleTimeString();
                const content = message.content || {};
                
                messageDiv.innerHTML = `
                    <div class="message-header">
                        <span class="message-sender">${message.sender_id}</span>
                        <span class="message-type">${message.message_type}</span>
                        <span class="message-time">${time}</span>
                    </div>
                    <div>${content.type || 'Message'}: ${content.message || JSON.stringify(content).substring(0, 100)}</div>
                `;
                container.appendChild(messageDiv);
            });
        }
        
        function addRealtimeMessage(message) {
            const container = document.getElementById('messages-container');
            const messageDiv = document.createElement('div');
            messageDiv.className = 'message';
            
            const time = new Date().toLocaleTimeString();
            const content = message.content || {};
            
            messageDiv.innerHTML = `
                <div class="message-header">
                    <span class="message-sender">${message.sender_id}</span>
                    <span class="message-type">${message.message_type}</span>
                    <span class="message-time">${time}</span>
                </div>
                <div>${content.type || 'Message'}: ${content.message || JSON.stringify(content).substring(0, 100)}</div>
            `;
            
            container.insertBefore(messageDiv, container.firstChild);
            
            // Keep only last 20 messages
            while (container.children.length > 20) {
                container.removeChild(container.lastChild);
            }
        }
        
        function updateCommunicationGraph(graphData) {
            // Simple network visualization using D3.js
            const container = document.getElementById('communication-graph');
            container.innerHTML = '';
            
            if (!graphData.nodes.length) return;
            
            const svg = d3.select('#communication-graph')
                .append('svg')
                .attr('width', '100%')
                .attr('height', '100%');
            
            const width = container.clientWidth;
            const height = 400;
            
            const simulation = d3.forceSimulation(graphData.nodes)
                .force('link', d3.forceLink(graphData.edges).id(d => d).distance(100))
                .force('charge', d3.forceManyBody().strength(-300))
                .force('center', d3.forceCenter(width / 2, height / 2));
            
            const link = svg.append('g')
                .selectAll('line')
                .data(graphData.edges)
                .enter().append('line')
                .attr('stroke', '#999')
                .attr('stroke-opacity', 0.6)
                .attr('stroke-width', d => Math.sqrt(d.weight));
            
            const node = svg.append('g')
                .selectAll('circle')
                .data(graphData.nodes)
                .enter().append('circle')
                .attr('r', 20)
                .attr('fill', '#FFD700')
                .call(d3.drag()
                    .on('start', dragstarted)
                    .on('drag', dragged)
                    .on('end', dragended));
            
            const label = svg.append('g')
                .selectAll('text')
                .data(graphData.nodes)
                .enter().append('text')
                .text(d => d.substring(0, 8))
                .attr('font-size', '10px')
                .attr('text-anchor', 'middle')
                .attr('fill', '#000');
            
            simulation.on('tick', () => {
                link
                    .attr('x1', d => d.source.x)
                    .attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x)
                    .attr('y2', d => d.target.y);
                
                node
                    .attr('cx', d => d.x)
                    .attr('cy', d => d.y);
                
                label
                    .attr('x', d => d.x)
                    .attr('y', d => d.y + 4);
            });
            
            function dragstarted(event, d) {
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x;
                d.fy = d.y;
            }
            
            function dragged(event, d) {
                d.fx = event.x;
                d.fy = event.y;
            }
            
            function dragended(event, d) {
                if (!event.active) simulation.alphaTarget(0);
                d.fx = null;
                d.fy = null;
            }
        }
        
        function updateMessageStatsChart(stats) {
            const ctx = document.getElementById('message-stats-chart').getContext('2d');
            
            if (messageStatsChart) {
                messageStatsChart.destroy();
            }
            
            const labels = Object.keys(stats).filter(key => key !== 'total');
            const data = labels.map(label => stats[label]);
            
            messageStatsChart = new Chart(ctx, {
                type: 'doughnut',
                data: {
                    labels: labels,
                    datasets: [{
                        data: data,
                        backgroundColor: [
                            '#FF6384',
                            '#36A2EB',
                            '#FFCE56',
                            '#4BC0C0',
                            '#9966FF',
                            '#FF9F40'
                        ]
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: {
                            labels: {
                                color: 'white'
                            }
                        }
                    }
                }
            });
        }
        
        function updatePerformanceChart(performance) {
            // Implementation for performance trends chart
            // This would show historical performance data
        }
        
        function requestUpdate() {
            socket.emit('request_update');
        }
        
        // Auto-refresh every 5 seconds
        setInterval(requestUpdate, 5000);
    </script>
</body>
</html>
'''

if __name__ == "__main__":
    print("🎪 Starting Swarm Intelligence Dashboard")
    print("=" * 50)
    print("📊 Features:")
    print("   • Real-time swarm visualization")
    print("   • Agent status monitoring")
    print("   • Communication pattern analysis")
    print("   • Emergent behavior tracking")
    print("   • Performance metrics")
    print("=" * 50)
    print("🌐 Dashboard: http://sam.chat:8401")
    print("📡 Connecting to swarm on port 8400")
    print("⚡ Starting dashboard server...")
    
    # Start the dashboard
    socketio.run(app, host='0.0.0.0', port=8401, debug=False)