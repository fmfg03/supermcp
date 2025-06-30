# 🖥️ SuperMCP Terminal Agent - Guía Completa

**Claude Code como Terminal Agent avanzado** - Sistema completo de ejecución de comandos con clasificación de seguridad e integración con SuperMCP.

---

## 🚀 Características Principales

### 🔧 **Ejecución de Comandos con Seguridad**
- **Clasificación automática** de comandos por nivel de seguridad
- **Timeout configurable** para prevenir comandos colgados
- **Historial completo** de todos los comandos ejecutados
- **Working directory** aislado y seguro

### 📁 **Gestión Completa de Archivos (CRUD)**
- ✅ **Crear**: Nuevos archivos con validación de tamaño
- ✅ **Leer**: Archivos con límite de líneas opcionales  
- ✅ **Actualizar**: Contenido con backup automático
- ✅ **Eliminar**: Con confirmación para archivos importantes
- ✅ **Listar**: Directorios con metadatos completos

### 🖥️ **Monitoreo de Sistema en Tiempo Real**
- **CPU, RAM, Disco**: Métricas de rendimiento en vivo
- **Procesos**: Lista completa con filtrado
- **Red**: Estadísticas de I/O de red
- **SuperMCP**: Estado específico de servicios SuperMCP

### 🔒 **Sistema de Seguridad Avanzado**

#### Clasificación de Comandos:

| Nivel | Comandos | Descripción |
|-------|----------|-------------|
| **🟢 SAFE** | `ls, cat, ps, top, df, git status` | Solo lectura, seguros |
| **🟡 MODERATE** | `mkdir, cp, mv, npm install` | Operaciones normales |
| **🟠 DANGEROUS** | `rm, kill, reboot, iptables` | Requieren confirmación |
| **🔴 RESTRICTED** | `rm -rf /`, format, fork bomb | Completamente bloqueados |

---

## 🌐 API Endpoints (Puerto 8500)

### 🔧 Ejecución de Comandos
```bash
# Ejecutar comando seguro
curl -X POST http://localhost:8500/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "ls -la",
    "timeout": 30
  }'

# Ejecutar comando peligroso (requiere force)
curl -X POST http://localhost:8500/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "rm file.txt",
    "force": true
  }'
```

### 📁 Gestión de Archivos
```bash
# Crear archivo
curl -X POST http://localhost:8500/files/create \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "test.txt",
    "content": "Hello World!"
  }'

# Leer archivo
curl "http://localhost:8500/files/read?file_path=test.txt&max_lines=100"

# Actualizar archivo
curl -X PUT http://localhost:8500/files/update \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "test.txt",
    "content": "Updated content"
  }'

# Eliminar archivo
curl -X DELETE "http://localhost:8500/files/delete?file_path=test.txt&force=true"

# Listar directorio
curl "http://localhost:8500/files/list?dir_path=."
```

### 🖥️ Monitoreo del Sistema
```bash
# Métricas del sistema
curl http://localhost:8500/system/metrics

# Lista de procesos
curl http://localhost:8500/system/processes

# Filtrar procesos
curl "http://localhost:8500/system/processes?filter=python"

# Estado de servicios SuperMCP
curl http://localhost:8500/supermcp/status
```

### 📝 Historial y Estado
```bash
# Historial de comandos
curl http://localhost:8500/history

# Últimos 10 comandos
curl "http://localhost:8500/history?limit=10"

# Health check
curl http://localhost:8500/health
```

---

## 🎪 Integración con Swarm Intelligence

El Terminal Agent se integra como un **agente especializado** en el swarm con las siguientes capacidades:

### 🤖 **Capacidades del Agente Swarm**
- `command_execution` - Ejecución segura de comandos
- `file_management` - Gestión completa de archivos
- `system_monitoring` - Monitoreo en tiempo real
- `process_control` - Control de procesos
- `supermcp_automation` - Automatizaciones específicas
- `security_enforcement` - Aplicación de políticas de seguridad
- `backup_restore` - Respaldo y restauración
- `log_management` - Gestión de logs
- `performance_monitoring` - Monitoreo de rendimiento
- `service_management` - Gestión de servicios

### 📨 **Mensajes del Swarm**

#### Solicitar Ejecución de Comando
```json
{
  "type": "command_execution_request",
  "request_id": "cmd-123",
  "command": "git status",
  "timeout": 60,
  "force": false
}
```

#### Operación de Archivo
```json
{
  "type": "file_operation_request",
  "request_id": "file-456",
  "operation": "read",
  "file_path": "config.json",
  "max_lines": 50
}
```

#### Métricas del Sistema
```json
{
  "type": "system_metrics_request",
  "request_id": "metrics-789"
}
```

#### Mantenimiento SuperMCP
```json
{
  "type": "supermcp_maintenance_request",
  "request_id": "maint-101",
  "maintenance_type": "restart_services"
}
```

### 🔄 **Respuestas Automáticas**
El Terminal Agent responde automáticamente a:
- Solicitudes de comando de otros agentes
- Peticiones de información del sistema
- Tareas de mantenimiento automatizado
- Operaciones de archivo del swarm

---

## 🤖 Automatizaciones SuperMCP

### 🚀 **Deploy Completo**
```bash
# Despliegue automático completo
curl -X POST http://localhost:8500/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python3 supermcp_automations.py deploy_complete"
  }'
```

### 💾 **Backup Inteligente**
```bash
# Backup incremental automático
curl -X POST http://localhost:8500/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python3 supermcp_automations.py backup"
  }'
```

### 🧹 **Mantenimiento Smart**
```bash
# Limpieza y mantenimiento
curl -X POST http://localhost:8500/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python3 supermcp_automations.py cleanup"
  }'
```

### 📊 **Optimización de Rendimiento**
```bash
# Optimización automática
curl -X POST http://localhost:8500/execute \
  -H "Content-Type: application/json" \
  -d '{
    "command": "python3 supermcp_automations.py optimize"
  }'
```

---

## 🛡️ Características de Seguridad Avanzadas

### 🔒 **Sandbox de Seguridad**
- **Working directory aislado**: `/root/supermcp`
- **Prevención de path traversal**: No se puede salir del directorio
- **Límites de archivo**: Máximo 10MB por archivo
- **Timeout de comandos**: Previene comandos infinitos

### 🚫 **Comandos Bloqueados**
```python
# Patrones completamente restringidos:
"rm -rf /"           # Eliminación del sistema
"dd if=/dev/zero"    # Sobrescritura de disco
":(){ :|:& };"       # Fork bomb
"mkfs."              # Formateo de disco
"shutdown -h now"    # Apagado del sistema
```

### ⚠️ **Comandos Peligrosos** (requieren `force=true`)
```python
# Requieren confirmación explícita:
"rm"                 # Eliminación de archivos
"kill"               # Terminación de procesos
"iptables"           # Cambios de firewall
"systemctl"          # Control de servicios
"reboot"             # Reinicio del sistema
```

### 📊 **Monitoreo de Seguridad**
- **Registro completo** de todos los comandos ejecutados
- **Clasificación automática** de nivel de riesgo
- **Alertas proactivas** para comandos peligrosos
- **Historial de actividad** para auditoría

---

## 🎯 Casos de Uso Avanzados

### 1. **Administración del Sistema**
```bash
# Verificar estado completo del sistema
curl http://localhost:8500/system/metrics

# Restart servicios automáticamente
curl -X POST http://localhost:8500/execute \
  -d '{"command": "./start_swarm_demo.sh", "force": true}'
```

### 2. **Desarrollo y Debugging**
```bash
# Ver logs en tiempo real
curl -X POST http://localhost:8500/execute \
  -d '{"command": "tail -f logs/swarm_core.log"}'

# Ejecutar tests
curl -X POST http://localhost:8500/execute \
  -d '{"command": "python3 -m pytest tests/"}'
```

### 3. **Monitoreo y Alertas**
```bash
# Crear script de monitoreo
curl -X POST http://localhost:8500/files/create \
  -d '{
    "file_path": "monitor.sh",
    "content": "#!/bin/bash\nwhile true; do\n  curl http://localhost:8500/system/metrics\n  sleep 60\ndone"
  }'

# Ejecutar monitoreo
curl -X POST http://localhost:8500/execute \
  -d '{"command": "chmod +x monitor.sh && ./monitor.sh &"}'
```

### 4. **Automatización DevOps**
```bash
# Deploy automatizado
curl -X POST http://localhost:8500/execute \
  -d '{"command": "git pull && ./deploy.sh"}'

# Backup antes de cambios
curl -X POST http://localhost:8500/execute \
  -d '{"command": "python3 supermcp_automations.py backup"}'
```

---

## 📊 Respuestas de Ejemplo

### ✅ **Comando Exitoso**
```json
{
  "command": "ls -la",
  "security_level": "safe",
  "category": "file_ops",
  "exit_code": 0,
  "stdout": "total 48\ndrwxr-xr-x 5 root root 4096 Dec  1 10:30 .\n...",
  "stderr": "",
  "execution_time": 0.023,
  "working_directory": "/root/supermcp",
  "timestamp": "2024-12-01T10:30:15.123456",
  "success": true
}
```

### ⚠️ **Comando Peligroso**
```json
{
  "command": "rm important_file.txt",
  "security_level": "dangerous",
  "category": "file_ops",
  "exit_code": -1,
  "stdout": "",
  "stderr": "Dangerous command requires explicit confirmation",
  "execution_time": 0.001,
  "working_directory": "/root/supermcp",
  "timestamp": "2024-12-01T10:30:15.123456",
  "success": false,
  "warning": "This is a dangerous command. Add 'force=true' to execute."
}
```

### 🚫 **Comando Restringido**
```json
{
  "command": "rm -rf /",
  "security_level": "restricted",
  "category": "shell",
  "exit_code": -1,
  "stdout": "",
  "stderr": "Command is restricted for security reasons",
  "execution_time": 0.000,
  "working_directory": "/root/supermcp",
  "timestamp": "2024-12-01T10:30:15.123456",
  "success": false,
  "warning": "This command is blocked for security reasons"
}
```

### 📊 **Métricas del Sistema**
```json
{
  "cpu_percent": 25.4,
  "memory_percent": 67.8,
  "disk_percent": 45.2,
  "network_io": {
    "bytes_sent": 1024000,
    "bytes_recv": 2048000,
    "packets_sent": 500,
    "packets_recv": 750
  },
  "process_count": 156,
  "uptime": "2 days, 14:30:25",
  "load_average": [1.2, 0.8, 0.6],
  "timestamp": "2024-12-01T10:30:15.123456"
}
```

---

## 🔧 Configuración y Personalización

### 📁 **Configurar Working Directory**
```python
# Cambiar directorio de trabajo
terminal_agent = TerminalAgent(working_dir="/custom/path")
```

### 🔒 **Ajustar Límites de Seguridad**
```python
# Modificar límite de archivo (default: 10MB)
terminal_agent = TerminalAgent(max_file_size=50*1024*1024)  # 50MB
```

### ⏱️ **Timeouts Personalizados**
```bash
# Timeout específico para comandos largos
curl -X POST http://localhost:8500/execute \
  -d '{"command": "long_running_task.sh", "timeout": 300}'  # 5 minutos
```

### 🎯 **Clasificaciones Personalizadas**
```python
# Agregar nuevas clasificaciones de comandos
terminal_agent.command_classifications.update({
    "my_safe_command": (SecurityLevel.SAFE, CommandCategory.CUSTOM),
    "my_dangerous_command": (SecurityLevel.DANGEROUS, CommandCategory.CUSTOM)
})
```

---

## 🚀 **¡Terminal Agent Completo Listo!**

El **SuperMCP Terminal Agent** es tu interfaz completa para:

✅ **Ejecución segura** de comandos con clasificación automática  
✅ **Gestión completa** de archivos con protecciones  
✅ **Monitoreo en tiempo real** del sistema  
✅ **Integración total** con Swarm Intelligence  
✅ **Automatizaciones avanzadas** para SuperMCP  
✅ **Seguridad enterprise** con sandbox y auditoría  

**¡Claude Code como Terminal Agent es la herramienta definitiva para administración de sistemas!** 🖥️✨