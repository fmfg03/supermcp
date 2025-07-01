const { createClient } = require('@supabase/supabase-js');

class SupabasePersistence {
  constructor() {
    this.supabase = createClient(
      process.env.SUPABASE_URL,
      process.env.SUPABASE_KEY
    );
    
    this.retryConfig = {
      maxRetries: 3,
      retryDelay: 1000
    };
  }

  async withRetry(operation, context = '') {
    let lastError;
    
    for (let attempt = 1; attempt <= this.retryConfig.maxRetries; attempt++) {
      try {
        return await operation();
      } catch (error) {
        lastError = error;
        console.warn(`Attempt ${attempt} failed for ${context}:`, error.message);
        
        if (attempt < this.retryConfig.maxRetries) {
          await new Promise(resolve => 
            setTimeout(resolve, this.retryConfig.retryDelay * attempt)
          );
        }
      }
    }
    
    throw lastError;
  }

  // Node management
  async registerNode(nodeData) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('nodes')
        .upsert({
          socket_id: nodeData.id,
          node_type: nodeData.type,
          node_name: nodeData.name,
          capabilities: nodeData.capabilities,
          metadata: nodeData.metadata || {},
          status: 'online',
          last_seen: new Date().toISOString(),
          connected_at: nodeData.connectedAt
        }, { 
          onConflict: 'socket_id',
          ignoreDuplicates: false 
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'registerNode');
  }

  async updateNodeStatus(socketId, status, metadata = {}) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('nodes')
        .update({
          status,
          metadata: { ...metadata },
          last_seen: new Date().toISOString()
        })
        .eq('socket_id', socketId)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'updateNodeStatus');
  }

  async unregisterNode(socketId) {
    return this.withRetry(async () => {
      const { error } = await this.supabase
        .from('nodes')
        .update({
          status: 'offline',
          last_seen: new Date().toISOString()
        })
        .eq('socket_id', socketId);
      
      if (error) throw error;
    }, 'unregisterNode');
  }

  async getActiveNodes() {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('nodes')
        .select('*')
        .eq('status', 'online')
        .order('last_seen', { ascending: false });
      
      if (error) throw error;
      return data || [];
    }, 'getActiveNodes');
  }

  // Message persistence
  async storeMessage(message) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('messages')
        .insert({
          message_id: message.id,
          from_node: message.from,
          to_node: message.to,
          message_type: message.type,
          payload: message.payload,
          status: 'sent',
          priority: message.priority || 'normal',
          expires_at: message.expiresAt
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'storeMessage');
  }

  async updateMessageStatus(messageId, status, deliveredAt = null) {
    return this.withRetry(async () => {
      const updateData = { status };
      if (deliveredAt) {
        updateData.delivered_at = deliveredAt;
      }
      
      const { data, error } = await this.supabase
        .from('messages')
        .update(updateData)
        .eq('message_id', messageId)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'updateMessageStatus');
  }

  async getQueuedMessages(nodeId) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('messages')
        .select('*')
        .eq('to_node', nodeId)
        .eq('status', 'queued')
        .order('created_at', { ascending: true });
      
      if (error) throw error;
      return data || [];
    }, 'getQueuedMessages');
  }

  // Task management
  async createTask(task) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('tasks')
        .insert({
          task_id: task.taskId,
          requester_node: task.from,
          capability: task.capability,
          payload: task.payload,
          priority: task.priority || 'normal',
          timeout_ms: task.timeout || 30000,
          status: 'pending'
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'createTask');
  }

  async assignTask(taskId, assignedNode) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('tasks')
        .update({
          assigned_node: assignedNode,
          status: 'assigned',
          assigned_at: new Date().toISOString()
        })
        .eq('task_id', taskId)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'assignTask');
  }

  async updateTaskStatus(taskId, status, result = null, errorMessage = null) {
    return this.withRetry(async () => {
      const updateData = { status };
      
      if (status === 'running') {
        updateData.started_at = new Date().toISOString();
      } else if (status === 'completed' || status === 'failed') {
        updateData.completed_at = new Date().toISOString();
        if (result) updateData.result = result;
        if (errorMessage) updateData.error_message = errorMessage;
      }
      
      const { data, error } = await this.supabase
        .from('tasks')
        .update(updateData)
        .eq('task_id', taskId)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'updateTaskStatus');
  }

  async getTasksByNode(nodeId, status = null) {
    return this.withRetry(async () => {
      let query = this.supabase
        .from('tasks')
        .select('*')
        .eq('assigned_node', nodeId);
      
      if (status) {
        query = query.eq('status', status);
      }
      
      const { data, error } = await query.order('created_at', { ascending: false });
      
      if (error) throw error;
      return data || [];
    }, 'getTasksByNode');
  }

  // Agent session management
  async createAgentSession(sessionData) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('agent_sessions')
        .insert({
          session_id: sessionData.sessionId,
          user_id: sessionData.userId,
          agent_type: sessionData.agentType,
          node_id: sessionData.nodeId,
          context: sessionData.context || {},
          memory: sessionData.memory || {}
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'createAgentSession');
  }

  async updateAgentSession(sessionId, updates) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('agent_sessions')
        .update({
          ...updates,
          updated_at: new Date().toISOString()
        })
        .eq('session_id', sessionId)
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'updateAgentSession');
  }

  async getAgentSession(sessionId) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('agent_sessions')
        .select('*')
        .eq('session_id', sessionId)
        .single();
      
      if (error && error.code !== 'PGRST116') throw error;
      return data;
    }, 'getAgentSession');
  }

  // Command logging
  async logCommand(commandData) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('command_logs')
        .insert({
          session_id: commandData.sessionId,
          node_id: commandData.nodeId,
          command: commandData.command,
          response: commandData.response,
          user_id: commandData.userId,
          llm_used: commandData.llmUsed,
          agent_used: commandData.agentUsed,
          execution_time_ms: commandData.executionTimeMs,
          tokens_used: commandData.tokensUsed,
          cost_usd: commandData.costUsd,
          success: commandData.success !== false,
          error_message: commandData.errorMessage
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'logCommand');
  }

  // Node metrics
  async recordMetric(nodeId, metricType, value, metadata = {}) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('node_metrics')
        .insert({
          node_id: nodeId,
          metric_type: metricType,
          value: value,
          metadata: metadata
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'recordMetric');
  }

  // System events
  async logEvent(eventType, description, sourceNode = null, targetNode = null, metadata = {}, severity = 'info') {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('system_events')
        .insert({
          event_type: eventType,
          source_node: sourceNode,
          target_node: targetNode,
          description: description,
          metadata: metadata,
          severity: severity
        })
        .select()
        .single();
      
      if (error) throw error;
      return data;
    }, 'logEvent');
  }

  // Analytics and monitoring
  async getSystemHealth() {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('system_health')
        .select('*')
        .single();
      
      if (error) throw error;
      return data;
    }, 'getSystemHealth');
  }

  async getNodeSummary() {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .from('node_summary')
        .select('*')
        .order('last_seen', { ascending: false });
      
      if (error) throw error;
      return data || [];
    }, 'getNodeSummary');
  }

  // Cleanup utilities
  async cleanupOldMessages(daysOld = 30) {
    return this.withRetry(async () => {
      const { data, error } = await this.supabase
        .rpc('cleanup_old_messages', { days_old: daysOld });
      
      if (error) throw error;
      return data;
    }, 'cleanupOldMessages');
  }

  async getConnectionStatus() {
    try {
      const { data, error } = await this.supabase
        .from('nodes')
        .select('count')
        .limit(1);
      
      return !error;
    } catch (error) {
      return false;
    }
  }
}

module.exports = SupabasePersistence;