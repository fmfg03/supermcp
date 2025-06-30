#!/usr/bin/env python3
"""
🖥️ Terminal Agent ←→ Swarm Intelligence Integration
Integrates the Terminal Agent as a specialized system agent in the swarm

Features:
- System operations for the swarm
- File management for swarm agents
- Process monitoring and control
- SuperMCP maintenance and automation
- Security-controlled command execution
"""

import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
from dataclasses import asdict
import threading
import websockets

from swarm_intelligence_system import SwarmAgentClient, SwarmMessage, MessageType, AgentType
from terminal_agent_system import TerminalAgent

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TerminalSwarmAgent(SwarmAgentClient):
    """Terminal agent integrated with swarm intelligence"""
    
    def __init__(self, swarm_port: int = 8400):
        # Initialize as swarm agent
        agent_info = {
            "name": "Terminal System Agent",
            "type": "system",
            "role": "specialist",
            "capabilities": [
                "command_execution",
                "file_management",
                "system_monitoring",
                "process_control",
                "supermcp_automation",
                "security_enforcement",
                "backup_restore",
                "log_management",
                "performance_monitoring",
                "service_management"
            ],
            "specialization_scores": {
                "system_ops": 0.95,
                "file_management": 0.9,
                "monitoring": 0.85,
                "automation": 0.9
            }
        }
        
        super().__init__("terminal", agent_info, swarm_port)
        
        # Initialize terminal agent
        self.terminal = TerminalAgent()
        self.swarm_metrics = {
            "commands_executed": 0,
            "files_managed": 0,
            "system_checks": 0,
            "automations_run": 0,
            "services_monitored": 0
        }
    
    async def process_swarm_message(self, message: Dict[str, Any]):
        """Enhanced message processing for system tasks"""
        await super().process_swarm_message(message)
        
        msg_type = message.get("message_type")
        content = message.get("content", {})
        sender_id = message.get("sender_id")
        
        # Handle terminal-specific requests
        if content.get("type") == "command_execution_request":
            await self._handle_command_request(content, sender_id)
        elif content.get("type") == "file_operation_request":
            await self._handle_file_operation(content, sender_id)
        elif content.get("type") == "system_metrics_request":
            await self._handle_system_metrics_request(content, sender_id)
        elif content.get("type") == "supermcp_maintenance_request":
            await self._handle_maintenance_request(content, sender_id)
        elif content.get("type") == "task_assignment" and self.agent_id in content.get("task", {}).get("assigned_agents", []):
            await self._handle_system_task_assignment(content)
        elif content.get("type") == "backup_request":
            await self._handle_backup_request(content, sender_id)
        elif content.get("type") == "service_control_request":
            await self._handle_service_control(content, sender_id)
    
    async def _handle_command_request(self, content: Dict[str, Any], sender_id: str):
        """Handle command execution request from swarm"""
        request_id = content.get("request_id", str(uuid.uuid4()))
        command = content.get("command", "")
        timeout = content.get("timeout", 60)
        force = content.get("force", False)
        
        if not command:
            await self._send_error_response(sender_id, request_id, "Command is required")
            return
        
        logger.info(f"🖥️ Executing command for {sender_id}: {command}")
        
        try:
            # Execute command through terminal agent
            result = await self.terminal.execute_command(command, timeout, not force)
            
            # Update metrics
            self.swarm_metrics["commands_executed"] += 1
            
            # Send response back to requester
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.COORDINATOR,  # Acting as system coordinator
                message_type=MessageType.RESPONSE,
                content={
                    "type": "command_execution_response",
                    "request_id": request_id,
                    "command": result.command,
                    "success": result.success,
                    "exit_code": result.exit_code,
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "execution_time": result.execution_time,
                    "security_level": result.security_level.value,
                    "warning": result.warning
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(response)))
            logger.info(f"✅ Command response sent to {sender_id}")
            
        except Exception as e:
            logger.error(f"❌ Error executing command: {e}")
            await self._send_error_response(sender_id, request_id, str(e))
    
    async def _handle_file_operation(self, content: Dict[str, Any], sender_id: str):
        """Handle file operation request"""
        request_id = content.get("request_id", str(uuid.uuid4()))
        operation = content.get("operation", "")
        file_path = content.get("file_path", "")
        
        try:
            result = None
            
            if operation == "create":
                file_content = content.get("content", "")
                result = await self.terminal.create_file(file_path, file_content)
            elif operation == "read":
                max_lines = content.get("max_lines")
                result = await self.terminal.read_file(file_path, max_lines)
            elif operation == "update":
                file_content = content.get("content", "")
                result = await self.terminal.update_file(file_path, file_content)
            elif operation == "delete":
                force = content.get("force", False)
                result = await self.terminal.delete_file(file_path, force)
            elif operation == "list":
                result = self.terminal.list_directory(file_path or ".")
            else:
                await self._send_error_response(sender_id, request_id, f"Unknown operation: {operation}")
                return
            
            # Update metrics
            self.swarm_metrics["files_managed"] += 1
            
            # Send response
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "type": "file_operation_response",
                    "request_id": request_id,
                    "operation": operation,
                    "file_path": file_path,
                    "result": result
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(response)))
            logger.info(f"📁 File operation {operation} completed for {sender_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in file operation: {e}")
            await self._send_error_response(sender_id, request_id, str(e))
    
    async def _handle_system_metrics_request(self, content: Dict[str, Any], sender_id: str):
        """Handle system metrics request"""
        request_id = content.get("request_id", str(uuid.uuid4()))
        
        try:
            # Get comprehensive system info
            metrics = self.terminal.get_system_metrics()
            processes = self.terminal.list_processes()
            supermcp_status = self.terminal.get_supermcp_status()
            
            # Update metrics
            self.swarm_metrics["system_checks"] += 1
            
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "type": "system_metrics_response",
                    "request_id": request_id,
                    "system_metrics": asdict(metrics),
                    "top_processes": processes[:10],  # Top 10 processes
                    "supermcp_status": supermcp_status,
                    "terminal_metrics": self.swarm_metrics
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(response)))
            logger.info(f"📊 System metrics sent to {sender_id}")
            
        except Exception as e:
            logger.error(f"❌ Error getting system metrics: {e}")
            await self._send_error_response(sender_id, request_id, str(e))
    
    async def _handle_maintenance_request(self, content: Dict[str, Any], sender_id: str):
        """Handle SuperMCP maintenance request"""
        request_id = content.get("request_id", str(uuid.uuid4()))
        maintenance_type = content.get("maintenance_type", "")
        
        try:
            result = {}
            
            if maintenance_type == "restart_services":
                result = await self._restart_supermcp_services()
            elif maintenance_type == "cleanup_logs":
                result = await self._cleanup_logs()
            elif maintenance_type == "health_check":
                result = await self._perform_health_check()
            elif maintenance_type == "update_system":
                result = await self._update_system()
            else:
                await self._send_error_response(sender_id, request_id, f"Unknown maintenance type: {maintenance_type}")
                return
            
            # Update metrics
            self.swarm_metrics["automations_run"] += 1
            
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "type": "maintenance_response",
                    "request_id": request_id,
                    "maintenance_type": maintenance_type,
                    "result": result,
                    "completed_at": datetime.now().isoformat()
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(response)))
            logger.info(f"🔧 Maintenance {maintenance_type} completed for {sender_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in maintenance: {e}")
            await self._send_error_response(sender_id, request_id, str(e))
    
    async def _handle_backup_request(self, content: Dict[str, Any], sender_id: str):
        """Handle backup/restore request"""
        request_id = content.get("request_id", str(uuid.uuid4()))
        backup_type = content.get("backup_type", "full")
        
        try:
            if backup_type == "full":
                result = await self._create_full_backup()
            elif backup_type == "config":
                result = await self._backup_configs()
            elif backup_type == "logs":
                result = await self._backup_logs()
            else:
                await self._send_error_response(sender_id, request_id, f"Unknown backup type: {backup_type}")
                return
            
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "type": "backup_response",
                    "request_id": request_id,
                    "backup_type": backup_type,
                    "result": result
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(response)))
            logger.info(f"💾 Backup {backup_type} completed for {sender_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in backup: {e}")
            await self._send_error_response(sender_id, request_id, str(e))
    
    async def _handle_service_control(self, content: Dict[str, Any], sender_id: str):
        """Handle service control request"""
        request_id = content.get("request_id", str(uuid.uuid4()))
        action = content.get("action", "")  # start, stop, restart, status
        service = content.get("service", "")  # specific service or "all"
        
        try:
            result = {}
            
            if action == "status":
                result = self.terminal.get_supermcp_status()
            elif action == "restart":
                if service == "all":
                    result = await self._restart_supermcp_services()
                else:
                    result = await self._restart_specific_service(service)
            elif action == "stop":
                result = await self._stop_services(service)
            elif action == "start":
                result = await self._start_services(service)
            else:
                await self._send_error_response(sender_id, request_id, f"Unknown action: {action}")
                return
            
            # Update metrics
            self.swarm_metrics["services_monitored"] += 1
            
            response = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.RESPONSE,
                content={
                    "type": "service_control_response",
                    "request_id": request_id,
                    "action": action,
                    "service": service,
                    "result": result
                },
                recipients=[sender_id]
            )
            
            await self.websocket.send(json.dumps(asdict(response)))
            logger.info(f"⚙️ Service {action} completed for {sender_id}")
            
        except Exception as e:
            logger.error(f"❌ Error in service control: {e}")
            await self._send_error_response(sender_id, request_id, str(e))
    
    async def _handle_system_task_assignment(self, content: Dict[str, Any]):
        """Handle system task assignment from swarm coordinator"""
        task = content.get("task", {})
        task_id = task.get("id")
        task_description = task.get("description", "")
        requirements = task.get("requirements", [])
        
        logger.info(f"📋 Assigned system task: {task.get('title', 'Unknown Task')}")
        
        try:
            result = None
            
            # Analyze task requirements and execute appropriate action
            if "system_monitoring" in requirements:
                result = await self._perform_comprehensive_monitoring()
            elif "file_management" in requirements:
                result = await self._organize_system_files()
            elif "maintenance" in requirements:
                result = await self._perform_system_maintenance()
            elif "backup" in requirements:
                result = await self._create_full_backup()
            elif "security_check" in requirements:
                result = await self._perform_security_check()
            else:
                # General system task
                result = await self._execute_general_system_task(task_description)
            
            # Report task completion
            completion_msg = SwarmMessage(
                id=str(uuid.uuid4()),
                timestamp=datetime.now().isoformat(),
                sender_id=self.agent_id,
                sender_type=AgentType.COORDINATOR,
                message_type=MessageType.BROADCAST,
                content={
                    "type": "task_completion",
                    "task_id": task_id,
                    "result": result,
                    "completed_by": "terminal_agent",
                    "success": True
                }
            )
            
            await self.websocket.send(json.dumps(asdict(completion_msg)))
            logger.info(f"✅ Completed system task {task_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to complete system task {task_id}: {e}")
    
    # Automation methods
    async def _restart_supermcp_services(self) -> Dict[str, Any]:
        """Restart all SuperMCP services"""
        results = {}
        
        # Stop services first
        stop_result = await self.terminal.execute_command("pkill -f 'python3.*swarm|python3.*multi_model'")
        results["stop_command"] = {
            "success": stop_result.success,
            "output": stop_result.stdout
        }
        
        # Wait a moment
        await asyncio.sleep(3)
        
        # Start services
        start_result = await self.terminal.execute_command("./start_swarm_demo.sh &")
        results["start_command"] = {
            "success": start_result.success,
            "output": start_result.stdout
        }
        
        return {
            "action": "restart_services",
            "success": True,
            "details": results,
            "timestamp": datetime.now().isoformat()
        }
    
    async def _cleanup_logs(self) -> Dict[str, Any]:
        """Clean up old log files"""
        results = {}
        
        # Clean old logs (keep last 7 days)
        cleanup_cmd = "find logs/ -name '*.log' -mtime +7 -delete"
        cleanup_result = await self.terminal.execute_command(cleanup_cmd)
        
        # Rotate current logs
        rotate_cmd = "for log in logs/*.log; do [ -s \"$log\" ] && mv \"$log\" \"${log}.$(date +%Y%m%d_%H%M%S).bak\"; done"
        rotate_result = await self.terminal.execute_command(rotate_cmd)
        
        results = {
            "cleanup": {"success": cleanup_result.success, "output": cleanup_result.stdout},
            "rotate": {"success": rotate_result.success, "output": rotate_result.stdout},
            "timestamp": datetime.now().isoformat()
        }
        
        return results
    
    async def _perform_health_check(self) -> Dict[str, Any]:
        """Perform comprehensive health check"""
        health_data = {}
        
        # System metrics
        metrics = self.terminal.get_system_metrics()
        health_data["system_metrics"] = asdict(metrics)
        
        # Service status
        services = self.terminal.get_supermcp_status()
        health_data["services"] = services
        
        # Disk space check
        disk_result = await self.terminal.execute_command("df -h")
        health_data["disk_space"] = disk_result.stdout
        
        # Memory usage
        mem_result = await self.terminal.execute_command("free -h")
        health_data["memory"] = mem_result.stdout
        
        # Check for errors in logs
        error_check = await self.terminal.execute_command("grep -i error logs/*.log | tail -10")
        health_data["recent_errors"] = error_check.stdout
        
        # Overall health score
        running_services = sum(1 for s in services.values() if s["running"])
        total_services = len(services)
        health_score = (running_services / total_services) * 100 if total_services > 0 else 0
        
        # Add warnings
        warnings = []
        if metrics.cpu_percent > 80:
            warnings.append("High CPU usage")
        if metrics.memory_percent > 80:
            warnings.append("High memory usage")
        if metrics.disk_percent > 80:
            warnings.append("High disk usage")
        if health_score < 80:
            warnings.append("Some services not running")
        
        health_data["health_score"] = health_score
        health_data["warnings"] = warnings
        health_data["timestamp"] = datetime.now().isoformat()
        
        return health_data
    
    async def _create_full_backup(self) -> Dict[str, Any]:
        """Create full system backup"""
        backup_name = f"supermcp_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Create backup directory
        mkdir_result = await self.terminal.execute_command(f"mkdir -p backups/{backup_name}")
        
        # Backup configuration files
        config_backup = await self.terminal.execute_command(
            f"cp -r *.py *.json *.sh *.md .env* backups/{backup_name}/ 2>/dev/null || true"
        )
        
        # Backup logs
        logs_backup = await self.terminal.execute_command(f"cp -r logs/ backups/{backup_name}/")
        
        # Create archive
        archive_result = await self.terminal.execute_command(
            f"cd backups && tar -czf {backup_name}.tar.gz {backup_name}/"
        )
        
        # Get backup size
        size_result = await self.terminal.execute_command(f"du -h backups/{backup_name}.tar.gz")
        
        return {
            "backup_name": backup_name,
            "archive_created": archive_result.success,
            "backup_size": size_result.stdout.split()[0] if size_result.success else "unknown",
            "timestamp": datetime.now().isoformat()
        }
    
    async def _send_error_response(self, sender_id: str, request_id: str, error: str):
        """Send error response to requester"""
        error_response = SwarmMessage(
            id=str(uuid.uuid4()),
            timestamp=datetime.now().isoformat(),
            sender_id=self.agent_id,
            sender_type=AgentType.COORDINATOR,
            message_type=MessageType.RESPONSE,
            content={
                "type": "error_response",
                "request_id": request_id,
                "error": error,
                "success": False
            },
            recipients=[sender_id]
        )
        
        await self.websocket.send(json.dumps(asdict(error_response)))
    
    async def send_proactive_system_updates(self):
        """Send proactive system status updates to swarm"""
        while self.running:
            try:
                await asyncio.sleep(300)  # Every 5 minutes
                
                # Get system status
                metrics = self.terminal.get_system_metrics()
                supermcp_status = self.terminal.get_supermcp_status()
                
                # Check for issues
                issues = []
                if metrics.cpu_percent > 80:
                    issues.append(f"High CPU usage: {metrics.cpu_percent:.1f}%")
                if metrics.memory_percent > 80:
                    issues.append(f"High memory usage: {metrics.memory_percent:.1f}%")
                if metrics.disk_percent > 80:
                    issues.append(f"High disk usage: {metrics.disk_percent:.1f}%")
                
                # Check for stopped services
                stopped_services = [name for name, status in supermcp_status.items() if not status["running"]]
                if stopped_services:
                    issues.append(f"Stopped services: {', '.join(stopped_services)}")
                
                # Send update if there are issues or periodically
                if issues or self.swarm_metrics["system_checks"] % 12 == 0:  # Every hour
                    update_msg = SwarmMessage(
                        id=str(uuid.uuid4()),
                        timestamp=datetime.now().isoformat(),
                        sender_id=self.agent_id,
                        sender_type=AgentType.COORDINATOR,
                        message_type=MessageType.BROADCAST,
                        content={
                            "type": "proactive_system_update",
                            "system_metrics": asdict(metrics),
                            "service_status": supermcp_status,
                            "issues": issues,
                            "recommendations": [
                                "Consider log cleanup if disk usage is high",
                                "Monitor resource usage trends",
                                "Restart services if needed"
                            ] if issues else ["System running normally"]
                        }
                    )
                    
                    await self.websocket.send(json.dumps(asdict(update_msg)))
                    logger.info("📊 Sent proactive system update to swarm")
                
                self.swarm_metrics["system_checks"] += 1
                
            except Exception as e:
                logger.error(f"Error sending system updates: {e}")

async def main():
    """Main function to run the terminal swarm agent"""
    print("🖥️ Terminal Agent ←→ Swarm Integration")
    print("=" * 60)
    print("🎯 Features:")
    print("   • System operations for swarm")
    print("   • File management for agents")
    print("   • Process monitoring and control")
    print("   • SuperMCP maintenance automation")
    print("   • Security-controlled execution")
    print("=" * 60)
    print("🔗 Connecting to swarm...")
    
    # Create and start the terminal swarm agent
    agent = TerminalSwarmAgent()
    
    # Start proactive system monitoring
    asyncio.create_task(agent.send_proactive_system_updates())
    
    # Connect to swarm
    await agent.connect_to_swarm()

if __name__ == "__main__":
    asyncio.run(main())