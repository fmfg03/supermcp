#!/usr/bin/env node

const express = require('express');
const { createServer } = require('http');
const { Server } = require('socket.io');
const Redis = require('redis');
const { v4: uuidv4 } = require('uuid');

class MCPBroker {
  constructor() {
    this.app = express();
    this.server = createServer(this.app);
    this.io = new Server(this.server, {
      cors: {
        origin: process.env.CORS_ORIGIN || "*",
        methods: ["GET", "POST"]
      }
    });
    
    this.redis = Redis.createClient({
      url: process.env.REDIS_URL || 'redis://localhost:6379'
    });
    
    this.nodes = new Map(); // Connected nodes
    this.nodeCapabilities = new Map(); // Node capabilities
    this.messageQueue = new Map(); // Pending messages
    
    this.setupMiddleware();
    this.setupRedis();
    this.setupSocketHandlers();
    this.setupRoutes();
  }

  setupMiddleware() {
    this.app.use(express.json());
    this.app.use(express.urlencoded({ extended: true }));
    
    // Health check
    this.app.get('/health', (req, res) => {
      res.json({ 
        status: 'healthy', 
        nodes: this.nodes.size,
        uptime: process.uptime(),
        timestamp: new Date().toISOString()
      });
    });
  }

  async setupRedis() {
    try {
      await this.redis.connect();
      console.log('✅ Connected to Redis');
      
      // Subscribe to inter-service communication
      const subscriber = this.redis.duplicate();
      await subscriber.connect();
      await subscriber.subscribe('mcp:broadcast', (message) => {
        this.broadcastToNodes(JSON.parse(message));
      });
      
    } catch (error) {
      console.error('❌ Redis connection failed:', error);
    }
  }

  setupSocketHandlers() {
    this.io.on('connection', (socket) => {
      console.log(`🔗 Node connected: ${socket.id}`);
      
      // Node registration
      socket.on('register', (nodeInfo) => {
        this.registerNode(socket, nodeInfo);
      });
      
      // Message routing
      socket.on('message', (data) => {
        this.routeMessage(socket, data);
      });
      
      // Capability registration
      socket.on('capabilities', (capabilities) => {
        this.nodeCapabilities.set(socket.id, capabilities);
        console.log(`📋 Node ${socket.id} capabilities:`, capabilities);
      });
      
      // Task request
      socket.on('task', (task) => {
        this.handleTask(socket, task);
      });
      
      // Node disconnection
      socket.on('disconnect', () => {
        this.unregisterNode(socket);
      });
    });
  }

  registerNode(socket, nodeInfo) {
    const nodeData = {
      id: socket.id,
      type: nodeInfo.type || 'unknown',
      name: nodeInfo.name || `node-${socket.id.slice(0, 8)}`,
      capabilities: nodeInfo.capabilities || [],
      connectedAt: new Date().toISOString(),
      lastSeen: new Date().toISOString()
    };
    
    this.nodes.set(socket.id, nodeData);
    this.nodeCapabilities.set(socket.id, nodeInfo.capabilities || []);
    
    console.log(`✅ Node registered:`, nodeData);
    
    // Notify other nodes
    socket.broadcast.emit('node_joined', nodeData);
    
    // Send current network status
    socket.emit('network_status', {
      totalNodes: this.nodes.size,
      nodes: Array.from(this.nodes.values())
    });
    
    // Store in Redis for persistence
    this.redis.hSet('mcp:nodes', socket.id, JSON.stringify(nodeData));
  }

  unregisterNode(socket) {
    const nodeData = this.nodes.get(socket.id);
    if (nodeData) {
      console.log(`❌ Node disconnected: ${nodeData.name} (${socket.id})`);
      
      this.nodes.delete(socket.id);
      this.nodeCapabilities.delete(socket.id);
      
      // Notify other nodes
      socket.broadcast.emit('node_left', nodeData);
      
      // Remove from Redis
      this.redis.hDel('mcp:nodes', socket.id);
    }
  }

  routeMessage(fromSocket, data) {
    const { to, type, payload, messageId = uuidv4() } = data;
    
    console.log(`📨 Routing message ${messageId}: ${fromSocket.id} -> ${to || 'broadcast'}`);
    
    const message = {
      id: messageId,
      from: fromSocket.id,
      to,
      type,
      payload,
      timestamp: new Date().toISOString()
    };
    
    if (to === 'broadcast' || !to) {
      // Broadcast to all nodes except sender
      fromSocket.broadcast.emit('message', message);
    } else if (to.startsWith('type:')) {
      // Route to nodes of specific type
      const targetType = to.substring(5);
      this.routeToType(fromSocket, targetType, message);
    } else {
      // Route to specific node
      const targetSocket = this.io.sockets.sockets.get(to);
      if (targetSocket) {
        targetSocket.emit('message', message);
      } else {
        // Queue message if node not connected
        this.queueMessage(to, message);
        fromSocket.emit('message_queued', { messageId, to });
      }
    }
    
    // Store message for audit
    this.redis.lPush('mcp:messages', JSON.stringify(message));
  }

  routeToType(fromSocket, targetType, message) {
    let routedCount = 0;
    
    for (const [socketId, nodeData] of this.nodes) {
      if (nodeData.type === targetType && socketId !== fromSocket.id) {
        const targetSocket = this.io.sockets.sockets.get(socketId);
        if (targetSocket) {
          targetSocket.emit('message', message);
          routedCount++;
        }
      }
    }
    
    fromSocket.emit('message_routed', { 
      messageId: message.id, 
      targetType, 
      routedCount 
    });
  }

  handleTask(fromSocket, task) {
    const { capability, payload, priority = 'normal', timeout = 30000 } = task;
    const taskId = uuidv4();
    
    console.log(`🎯 Task request: ${capability} from ${fromSocket.id}`);
    
    // Find capable nodes
    const capableNodes = [];
    for (const [socketId, capabilities] of this.nodeCapabilities) {
      if (capabilities.includes(capability) && socketId !== fromSocket.id) {
        capableNodes.push(socketId);
      }
    }
    
    if (capableNodes.length === 0) {
      fromSocket.emit('task_error', {
        taskId,
        error: `No nodes available with capability: ${capability}`
      });
      return;
    }
    
    // Select best node (simple round-robin for now)
    const selectedNode = capableNodes[Math.floor(Math.random() * capableNodes.length)];
    const targetSocket = this.io.sockets.sockets.get(selectedNode);
    
    if (targetSocket) {
      const taskMessage = {
        taskId,
        capability,
        payload,
        priority,
        from: fromSocket.id,
        timestamp: new Date().toISOString()
      };
      
      targetSocket.emit('task_assigned', taskMessage);
      fromSocket.emit('task_dispatched', { taskId, assignedTo: selectedNode });
      
      // Set timeout
      setTimeout(() => {
        fromSocket.emit('task_timeout', { taskId });
      }, timeout);
      
    } else {
      fromSocket.emit('task_error', {
        taskId,
        error: 'Selected node not available'
      });
    }
  }

  queueMessage(nodeId, message) {
    if (!this.messageQueue.has(nodeId)) {
      this.messageQueue.set(nodeId, []);
    }
    this.messageQueue.get(nodeId).push(message);
    
    // Store in Redis for persistence
    this.redis.lPush(`mcp:queue:${nodeId}`, JSON.stringify(message));
  }

  broadcastToNodes(message) {
    this.io.emit('broadcast', message);
  }

  setupRoutes() {
    // REST API for management
    this.app.get('/api/nodes', (req, res) => {
      res.json({
        total: this.nodes.size,
        nodes: Array.from(this.nodes.values())
      });
    });
    
    this.app.get('/api/capabilities', (req, res) => {
      const capabilities = {};
      for (const [nodeId, caps] of this.nodeCapabilities) {
        const nodeData = this.nodes.get(nodeId);
        capabilities[nodeId] = {
          node: nodeData?.name || nodeId,
          capabilities: caps
        };
      }
      res.json(capabilities);
    });
    
    this.app.post('/api/broadcast', (req, res) => {
      const message = req.body;
      this.broadcastToNodes(message);
      res.json({ status: 'broadcast_sent', timestamp: new Date().toISOString() });
    });
    
    this.app.get('/api/messages/:nodeId', async (req, res) => {
      const { nodeId } = req.params;
      try {
        const messages = await this.redis.lRange(`mcp:queue:${nodeId}`, 0, -1);
        res.json(messages.map(m => JSON.parse(m)));
      } catch (error) {
        res.status(500).json({ error: error.message });
      }
    });
  }

  async start() {
    const port = process.env.BROKER_PORT || 8080;
    
    this.server.listen(port, () => {
      console.log(`🚀 MCP Broker running on port ${port}`);
      console.log(`📡 WebSocket endpoint: ws://localhost:${port}`);
      console.log(`🌐 REST API: http://localhost:${port}/api`);
    });
    
    // Graceful shutdown
    process.on('SIGTERM', () => {
      console.log('📤 Shutting down MCP Broker...');
      this.server.close(() => {
        this.redis.quit();
        process.exit(0);
      });
    });
  }
}

// Start broker if run directly
if (require.main === module) {
  const broker = new MCPBroker();
  broker.start().catch(console.error);
}

module.exports = MCPBroker;