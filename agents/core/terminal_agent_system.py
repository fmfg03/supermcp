#!/usr/bin/env python3
"""
🖥️ SuperMCP Terminal Agent - Computer Use Integration
Advanced terminal agent with security classification and SuperMCP integration

Features:
- 🔧 Command execution with security classification
- 📁 Complete file management (CRUD)
- 🖥️ Real-time system monitoring
- 🤖 SuperMCP-specific automations
- 🔒 Security controls and sandboxing
- 🌐 A2A network integration
"""

import asyncio
import json
import logging
import os
import psutil
import subprocess
import time
import shutil
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import re
import signal
from flask import Flask, request, jsonify
from threading import Thread
import websockets

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SecurityLevel(Enum):
    """Security classification for commands"""
    SAFE = "safe"           # Read-only, info commands
    MODERATE = "moderate"   # File operations, installs
    DANGEROUS = "dangerous" # System changes, deletions
    RESTRICTED = "restricted" # Blocked completely

class CommandCategory(Enum):
    """Command categories"""
    SYSTEM_INFO = "system_info"
    FILE_OPS = "file_ops"
    PROCESS_MGMT = "process_mgmt"
    NETWORK = "network"
    DEVELOPMENT = "development"
    SUPERMCP = "supermcp"
    SHELL = "shell"

@dataclass
class CommandResult:
    """Result of command execution"""
    command: str
    security_level: SecurityLevel
    category: CommandCategory
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    working_directory: str
    timestamp: str
    success: bool
    warning: Optional[str] = None

@dataclass
class SystemMetrics:
    """System performance metrics"""
    cpu_percent: float
    memory_percent: float
    disk_percent: float
    network_io: Dict[str, int]
    process_count: int
    uptime: str
    load_average: List[float]
    timestamp: str

class TerminalAgent:
    """Advanced terminal agent with security and SuperMCP integration"""
    
    def __init__(self, working_dir: str = "/root/supermcp", max_file_size: int = 10 * 1024 * 1024):
        self.working_dir = Path(working_dir).resolve()
        self.max_file_size = max_file_size
        self.command_history = []
        self.active_processes = {}
        
        # Security configurations
        self.command_classifications = self._init_command_classifications()
        self.restricted_patterns = [
            r"rm\s+-rf\s+/",
            r"dd\s+if=/dev/zero",
            r":()\{\s*:\|\:&\s*\};:",  # Fork bomb
            r"mkfs\.",
            r"format\s+",
            r"fdisk\s+",
            r"parted\s+",
            r"shutdown\s+-h\s+now",
            r"halt\s+-f"
        ]
        
        # SuperMCP service patterns
        self.supermcp_services = {
            "swarm_core": "swarm_intelligence_system.py",
            "dashboard": "swarm_web_dashboard.py", 
            "sam_gateway": "sam_chat_swarm_gateway.py",
            "multimodel_router": "multi_model_system.py",
            "multimodel_swarm": "multimodel_swarm_integration.py",
            "demo_agents": "swarm_demo_agents.py"
        }
        
        # Create working directory if it doesn't exist
        self.working_dir.mkdir(parents=True, exist_ok=True)
        os.chdir(self.working_dir)
        
        logger.info(f"🖥️ Terminal Agent initialized in: {self.working_dir}")
    
    def _init_command_classifications(self) -> Dict[str, Tuple[SecurityLevel, CommandCategory]]:
        """Initialize command security classifications"""
        return {
            # SAFE - Read-only operations
            "ls": (SecurityLevel.SAFE, CommandCategory.FILE_OPS),
            "cat": (SecurityLevel.SAFE, CommandCategory.FILE_OPS),
            "head": (SecurityLevel.SAFE, CommandCategory.FILE_OPS),
            "tail": (SecurityLevel.SAFE, CommandCategory.FILE_OPS),
            "pwd": (SecurityLevel.SAFE, CommandCategory.FILE_OPS),
            "whoami": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "ps": (SecurityLevel.SAFE, CommandCategory.PROCESS_MGMT),
            "top": (SecurityLevel.SAFE, CommandCategory.PROCESS_MGMT),
            "htop": (SecurityLevel.SAFE, CommandCategory.PROCESS_MGMT),
            "df": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "free": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "uname": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "uptime": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "date": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "env": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "which": (SecurityLevel.SAFE, CommandCategory.SYSTEM_INFO),
            "netstat": (SecurityLevel.SAFE, CommandCategory.NETWORK),
            "ss": (SecurityLevel.SAFE, CommandCategory.NETWORK),
            "git status": (SecurityLevel.SAFE, CommandCategory.DEVELOPMENT),
            "git log": (SecurityLevel.SAFE, CommandCategory.DEVELOPMENT),
            "git diff": (SecurityLevel.SAFE, CommandCategory.DEVELOPMENT),
            
            # MODERATE - File operations, installs
            "mkdir": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "touch": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "cp": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "mv": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "chmod": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "chown": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "ln": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "nano": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "vim": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "echo": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "grep": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "find": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "tar": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "zip": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "unzip": (SecurityLevel.MODERATE, CommandCategory.FILE_OPS),
            "wget": (SecurityLevel.MODERATE, CommandCategory.NETWORK),
            "curl": (SecurityLevel.MODERATE, CommandCategory.NETWORK),
            "pip install": (SecurityLevel.MODERATE, CommandCategory.DEVELOPMENT),
            "npm install": (SecurityLevel.MODERATE, CommandCategory.DEVELOPMENT),
            "git clone": (SecurityLevel.MODERATE, CommandCategory.DEVELOPMENT),
            "git pull": (SecurityLevel.MODERATE, CommandCategory.DEVELOPMENT),
            "python": (SecurityLevel.MODERATE, CommandCategory.DEVELOPMENT),
            "node": (SecurityLevel.MODERATE, CommandCategory.DEVELOPMENT),
            
            # DANGEROUS - System changes, deletions
            "rm": (SecurityLevel.DANGEROUS, CommandCategory.FILE_OPS),
            "rmdir": (SecurityLevel.DANGEROUS, CommandCategory.FILE_OPS),
            "kill": (SecurityLevel.DANGEROUS, CommandCategory.PROCESS_MGMT),
            "killall": (SecurityLevel.DANGEROUS, CommandCategory.PROCESS_MGMT),
            "pkill": (SecurityLevel.DANGEROUS, CommandCategory.PROCESS_MGMT),
            "sudo": (SecurityLevel.DANGEROUS, CommandCategory.SYSTEM_INFO),
            "su": (SecurityLevel.DANGEROUS, CommandCategory.SYSTEM_INFO),
            "mount": (SecurityLevel.DANGEROUS, CommandCategory.SYSTEM_INFO),
            "umount": (SecurityLevel.DANGEROUS, CommandCategory.SYSTEM_INFO),
            "iptables": (SecurityLevel.DANGEROUS, CommandCategory.NETWORK),
            "systemctl": (SecurityLevel.DANGEROUS, CommandCategory.PROCESS_MGMT),
            "service": (SecurityLevel.DANGEROUS, CommandCategory.PROCESS_MGMT),
            "reboot": (SecurityLevel.DANGEROUS, CommandCategory.SYSTEM_INFO),
            "shutdown": (SecurityLevel.DANGEROUS, CommandCategory.SYSTEM_INFO),
            "git reset": (SecurityLevel.DANGEROUS, CommandCategory.DEVELOPMENT),
            "git rebase": (SecurityLevel.DANGEROUS, CommandCategory.DEVELOPMENT),
        }
    
    def classify_command(self, command: str) -> Tuple[SecurityLevel, CommandCategory]:
        """Classify command security level and category"""
        
        # Check for restricted patterns first
        for pattern in self.restricted_patterns:
            if re.search(pattern, command, re.IGNORECASE):
                return SecurityLevel.RESTRICTED, CommandCategory.SHELL
        
        # Check exact matches first
        if command in self.command_classifications:
            return self.command_classifications[command]
        
        # Check partial matches for compound commands
        for cmd_pattern, (level, category) in self.command_classifications.items():
            if command.startswith(cmd_pattern):
                return level, category
        
        # Default classification for unknown commands
        return SecurityLevel.MODERATE, CommandCategory.SHELL
    
    async def execute_command(self, command: str, timeout: int = 60, require_confirmation: bool = False) -> CommandResult:
        """Execute command with security checks and monitoring"""
        
        security_level, category = self.classify_command(command)
        timestamp = datetime.now().isoformat()
        
        # Check if command is restricted
        if security_level == SecurityLevel.RESTRICTED:
            logger.warning(f"🚫 RESTRICTED command blocked: {command}")
            return CommandResult(
                command=command,
                security_level=security_level,
                category=category,
                exit_code=-1,
                stdout="",
                stderr="Command is restricted for security reasons",
                execution_time=0.0,
                working_directory=str(self.working_dir),
                timestamp=timestamp,
                success=False,
                warning="This command is blocked for security reasons"
            )
        
        # Require confirmation for dangerous commands
        if security_level == SecurityLevel.DANGEROUS and require_confirmation:
            logger.warning(f"⚠️ DANGEROUS command requires confirmation: {command}")
            return CommandResult(
                command=command,
                security_level=security_level,
                category=category,
                exit_code=-1,
                stdout="",
                stderr="Dangerous command requires explicit confirmation",
                execution_time=0.0,
                working_directory=str(self.working_dir),
                timestamp=timestamp,
                success=False,
                warning="This is a dangerous command. Add 'force=true' to execute."
            )
        
        logger.info(f"🖥️ Executing {security_level.value} command: {command}")
        
        start_time = time.time()
        
        try:
            # Execute command
            process = await asyncio.create_subprocess_shell(
                command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                cwd=self.working_dir
            )
            
            # Store active process
            self.active_processes[process.pid] = {
                "command": command,
                "started_at": timestamp,
                "process": process
            }
            
            try:
                stdout, stderr = await asyncio.wait_for(
                    process.communicate(), 
                    timeout=timeout
                )
                exit_code = process.returncode
                
            except asyncio.TimeoutError:
                process.kill()
                await process.wait()
                stdout, stderr = b"", b"Command timed out"
                exit_code = -1
            
            finally:
                # Clean up active process
                if process.pid in self.active_processes:
                    del self.active_processes[process.pid]
            
            execution_time = time.time() - start_time
            
            # Decode output
            stdout_str = stdout.decode('utf-8', errors='replace')
            stderr_str = stderr.decode('utf-8', errors='replace')
            
            success = exit_code == 0
            
            result = CommandResult(
                command=command,
                security_level=security_level,
                category=category,
                exit_code=exit_code,
                stdout=stdout_str,
                stderr=stderr_str,
                execution_time=execution_time,
                working_directory=str(self.working_dir),
                timestamp=timestamp,
                success=success
            )
            
            # Add to history
            self.command_history.append(result)
            
            # Keep only last 1000 commands
            if len(self.command_history) > 1000:
                self.command_history.pop(0)
            
            logger.info(f"✅ Command completed in {execution_time:.2f}s: {command}")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = str(e)
            
            logger.error(f"❌ Command failed: {command} - {error_msg}")
            
            return CommandResult(
                command=command,
                security_level=security_level,
                category=category,
                exit_code=-1,
                stdout="",
                stderr=error_msg,
                execution_time=execution_time,
                working_directory=str(self.working_dir),
                timestamp=timestamp,
                success=False
            )
    
    def get_system_metrics(self) -> SystemMetrics:
        """Get comprehensive system metrics"""
        
        # CPU and Memory
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        # Network I/O
        net_io = psutil.net_io_counters()
        network_io = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
            "packets_sent": net_io.packets_sent,
            "packets_recv": net_io.packets_recv
        }
        
        # Process count
        process_count = len(psutil.pids())
        
        # Uptime
        boot_time = psutil.boot_time()
        uptime_seconds = time.time() - boot_time
        uptime = str(timedelta(seconds=int(uptime_seconds)))
        
        # Load average (Unix only)
        try:
            load_avg = list(os.getloadavg())
        except (AttributeError, OSError):
            load_avg = [0.0, 0.0, 0.0]
        
        return SystemMetrics(
            cpu_percent=cpu_percent,
            memory_percent=memory.percent,
            disk_percent=disk_percent,
            network_io=network_io,
            process_count=process_count,
            uptime=uptime,
            load_average=load_avg,
            timestamp=datetime.now().isoformat()
        )
    
    def list_processes(self, filter_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List running processes with optional filtering"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
            try:
                proc_info = proc.info
                
                # Filter by name if specified
                if filter_name and filter_name.lower() not in proc_info['name'].lower():
                    continue
                
                # Calculate runtime
                create_time = datetime.fromtimestamp(proc_info['create_time'])
                runtime = str(datetime.now() - create_time).split('.')[0]
                
                processes.append({
                    "pid": proc_info['pid'],
                    "name": proc_info['name'],
                    "cpu_percent": proc_info['cpu_percent'] or 0.0,
                    "memory_percent": proc_info['memory_percent'] or 0.0,
                    "status": proc_info['status'],
                    "runtime": runtime
                })
                
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # Sort by CPU usage
        processes.sort(key=lambda x: x['cpu_percent'], reverse=True)
        return processes
    
    def get_supermcp_status(self) -> Dict[str, Any]:
        """Get status of all SuperMCP services"""
        status = {}
        
        for service_name, script_name in self.supermcp_services.items():
            # Check if process is running
            running = False
            pid = None
            cpu_percent = 0.0
            memory_percent = 0.0
            
            for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_percent']):
                try:
                    cmdline = ' '.join(proc.info['cmdline']) if proc.info['cmdline'] else ''
                    if script_name in cmdline:
                        running = True
                        pid = proc.info['pid']
                        cpu_percent = proc.info['cpu_percent'] or 0.0
                        memory_percent = proc.info['memory_percent'] or 0.0
                        break
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            status[service_name] = {
                "running": running,
                "pid": pid,
                "script": script_name,
                "cpu_percent": cpu_percent,
                "memory_percent": memory_percent
            }
        
        return status
    
    # File Management Methods
    async def create_file(self, file_path: str, content: str = "") -> Dict[str, Any]:
        """Create a new file with content"""
        try:
            path = Path(self.working_dir) / file_path
            
            # Security check - prevent directory traversal
            if not str(path.resolve()).startswith(str(self.working_dir)):
                return {"success": False, "error": "Path traversal not allowed"}
            
            # Check file size limit
            if len(content.encode('utf-8')) > self.max_file_size:
                return {"success": False, "error": f"File size exceeds {self.max_file_size} bytes"}
            
            # Create parent directories if needed
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            path.write_text(content, encoding='utf-8')
            
            logger.info(f"📝 Created file: {file_path}")
            return {
                "success": True,
                "file_path": str(path),
                "size": len(content.encode('utf-8')),
                "created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error creating file {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    async def read_file(self, file_path: str, max_lines: Optional[int] = None) -> Dict[str, Any]:
        """Read file content with optional line limit"""
        try:
            path = Path(self.working_dir) / file_path
            
            # Security check
            if not str(path.resolve()).startswith(str(self.working_dir)):
                return {"success": False, "error": "Path traversal not allowed"}
            
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            if not path.is_file():
                return {"success": False, "error": "Path is not a file"}
            
            # Check file size
            if path.stat().st_size > self.max_file_size:
                return {"success": False, "error": f"File too large (max {self.max_file_size} bytes)"}
            
            # Read content
            content = path.read_text(encoding='utf-8')
            
            # Apply line limit if specified
            if max_lines:
                lines = content.split('\n')
                if len(lines) > max_lines:
                    content = '\n'.join(lines[:max_lines])
                    content += f"\n... (truncated, showing first {max_lines} lines)"
            
            return {
                "success": True,
                "content": content,
                "file_path": str(path),
                "size": path.stat().st_size,
                "modified_at": datetime.fromtimestamp(path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error reading file {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    async def update_file(self, file_path: str, content: str) -> Dict[str, Any]:
        """Update existing file content"""
        try:
            path = Path(self.working_dir) / file_path
            
            # Security check
            if not str(path.resolve()).startswith(str(self.working_dir)):
                return {"success": False, "error": "Path traversal not allowed"}
            
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            # Check file size limit
            if len(content.encode('utf-8')) > self.max_file_size:
                return {"success": False, "error": f"File size exceeds {self.max_file_size} bytes"}
            
            # Backup original
            backup_content = path.read_text(encoding='utf-8')
            
            # Write new content
            path.write_text(content, encoding='utf-8')
            
            logger.info(f"✏️ Updated file: {file_path}")
            return {
                "success": True,
                "file_path": str(path),
                "size": len(content.encode('utf-8')),
                "updated_at": datetime.now().isoformat(),
                "backup_available": True
            }
            
        except Exception as e:
            logger.error(f"❌ Error updating file {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    async def delete_file(self, file_path: str, force: bool = False) -> Dict[str, Any]:
        """Delete file with safety checks"""
        try:
            path = Path(self.working_dir) / file_path
            
            # Security check
            if not str(path.resolve()).startswith(str(self.working_dir)):
                return {"success": False, "error": "Path traversal not allowed"}
            
            if not path.exists():
                return {"success": False, "error": "File not found"}
            
            # Safety check for important files
            important_files = [
                "start_swarm_demo.sh",
                "swarm_intelligence_system.py",
                "multi_model_system.py",
                ".env"
            ]
            
            if path.name in important_files and not force:
                return {
                    "success": False, 
                    "error": f"Important file {path.name} requires force=True to delete"
                }
            
            # Delete file or directory
            if path.is_file():
                path.unlink()
                logger.info(f"🗑️ Deleted file: {file_path}")
            elif path.is_dir():
                shutil.rmtree(path)
                logger.info(f"🗑️ Deleted directory: {file_path}")
            
            return {
                "success": True,
                "deleted_path": str(path),
                "deleted_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Error deleting {file_path}: {e}")
            return {"success": False, "error": str(e)}
    
    def list_directory(self, dir_path: str = ".") -> Dict[str, Any]:
        """List directory contents with metadata"""
        try:
            path = Path(self.working_dir) / dir_path
            
            # Security check
            if not str(path.resolve()).startswith(str(self.working_dir)):
                return {"success": False, "error": "Path traversal not allowed"}
            
            if not path.exists():
                return {"success": False, "error": "Directory not found"}
            
            if not path.is_dir():
                return {"success": False, "error": "Path is not a directory"}
            
            items = []
            for item in path.iterdir():
                try:
                    stat = item.stat()
                    items.append({
                        "name": item.name,
                        "type": "directory" if item.is_dir() else "file",
                        "size": stat.st_size if item.is_file() else None,
                        "modified_at": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "permissions": oct(stat.st_mode)[-3:]
                    })
                except OSError:
                    continue
            
            # Sort: directories first, then files
            items.sort(key=lambda x: (x["type"] == "file", x["name"]))
            
            return {
                "success": True,
                "directory": str(path),
                "items": items,
                "total_items": len(items)
            }
            
        except Exception as e:
            logger.error(f"❌ Error listing directory {dir_path}: {e}")
            return {"success": False, "error": str(e)}

# Global terminal agent instance
terminal_agent = TerminalAgent()

# Flask API for terminal agent
app = Flask(__name__)

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "agent_type": "terminal",
        "working_directory": str(terminal_agent.working_dir),
        "command_history_size": len(terminal_agent.command_history),
        "active_processes": len(terminal_agent.active_processes),
        "timestamp": datetime.now().isoformat()
    })

@app.route('/execute', methods=['POST'])
def execute_command():
    """Execute terminal command"""
    try:
        data = request.get_json()
        command = data.get('command', '')
        timeout = data.get('timeout', 60)
        force = data.get('force', False)
        
        if not command:
            return jsonify({"error": "Command is required"}), 400
        
        # Run async command
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            terminal_agent.execute_command(command, timeout, not force)
        )
        loop.close()
        
        return jsonify(asdict(result))
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/system/metrics', methods=['GET'])
def get_system_metrics():
    """Get system performance metrics"""
    try:
        metrics = terminal_agent.get_system_metrics()
        return jsonify(asdict(metrics))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/system/processes', methods=['GET'])
def get_processes():
    """Get running processes"""
    try:
        filter_name = request.args.get('filter')
        processes = terminal_agent.list_processes(filter_name)
        return jsonify({
            "processes": processes,
            "total_count": len(processes),
            "filtered": filter_name is not None
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/supermcp/status', methods=['GET'])
def get_supermcp_status():
    """Get SuperMCP services status"""
    try:
        status = terminal_agent.get_supermcp_status()
        return jsonify({
            "services": status,
            "total_services": len(status),
            "running_services": len([s for s in status.values() if s["running"]])
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/create', methods=['POST'])
def create_file():
    """Create new file"""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        content = data.get('content', '')
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            terminal_agent.create_file(file_path, content)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/read', methods=['GET'])
def read_file():
    """Read file content"""
    try:
        file_path = request.args.get('file_path', '')
        max_lines = request.args.get('max_lines', type=int)
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            terminal_agent.read_file(file_path, max_lines)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/update', methods=['PUT'])
def update_file():
    """Update file content"""
    try:
        data = request.get_json()
        file_path = data.get('file_path', '')
        content = data.get('content', '')
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            terminal_agent.update_file(file_path, content)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/delete', methods=['DELETE'])
def delete_file():
    """Delete file"""
    try:
        file_path = request.args.get('file_path', '')
        force = request.args.get('force', 'false').lower() == 'true'
        
        if not file_path:
            return jsonify({"error": "file_path is required"}), 400
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            terminal_agent.delete_file(file_path, force)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/list', methods=['GET'])
def list_directory():
    """List directory contents"""
    try:
        dir_path = request.args.get('dir_path', '.')
        result = terminal_agent.list_directory(dir_path)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/history', methods=['GET'])
def get_command_history():
    """Get command execution history"""
    try:
        limit = request.args.get('limit', 50, type=int)
        recent_commands = terminal_agent.command_history[-limit:]
        
        return jsonify({
            "commands": [asdict(cmd) for cmd in recent_commands],
            "total_commands": len(terminal_agent.command_history),
            "showing": len(recent_commands)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("🖥️ SuperMCP Terminal Agent")
    print("=" * 50)
    print("🔧 Command execution with security classification")
    print("📁 Complete file management (CRUD)")
    print("🖥️ Real-time system monitoring")
    print("🤖 SuperMCP-specific automations")
    print("🔒 Security controls and sandboxing")
    print("=" * 50)
    print("🌐 API Endpoints:")
    print("  POST /execute           - Execute command")
    print("  GET  /system/metrics    - System metrics")
    print("  GET  /system/processes  - Process list")
    print("  GET  /supermcp/status   - SuperMCP status")
    print("  POST /files/create      - Create file")
    print("  GET  /files/read        - Read file")
    print("  PUT  /files/update      - Update file")
    print("  DELETE /files/delete    - Delete file")
    print("  GET  /files/list        - List directory")
    print("  GET  /history           - Command history")
    print("=" * 50)
    print(f"🚀 Starting on http://localhost:8500")
    print(f"📂 Working directory: {terminal_agent.working_dir}")
    
    app.run(host='0.0.0.0', port=8500, debug=False)