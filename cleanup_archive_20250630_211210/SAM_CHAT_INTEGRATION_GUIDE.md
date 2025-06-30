# 🌉 SAM.CHAT ←→ SuperMCP Swarm Intelligence Integration

Esta guía explica cómo usar el sistema Swarm Intelligence desde sam.chat de manera unificada.

## 🚀 Inicio Rápido

1. **Inicia el sistema completo:**
   ```bash
   chmod +x start_swarm_demo.sh
   ./start_swarm_demo.sh
   ```

2. **Verifica que todos los servicios estén ejecutándose:**
   - 🌉 SAM.CHAT Gateway: http://localhost:8402
   - 🌐 Dashboard Visual: http://localhost:8401
   - 🔌 Swarm Core: ws://localhost:8400

## 🎯 Comandos Disponibles desde SAM.CHAT

### 📊 Comandos de Estado
```
/swarm-status
¿Cuál es el estado del swarm?
Mostrar estado del swarm
```

### 🤖 Gestión de Agentes
```
/swarm-agents
Listar todos los agentes
¿Qué agentes están disponibles?
```

### 📋 Asignación de Tareas
```
/swarm-task Analizar tendencias del mercado
/swarm-task Buscar información sobre IA
/swarm-task Crear un informe de ventas

Asignar tarea: [descripción]
Necesito que el swarm analice datos
```

### 🗳️ Consenso y Decisiones
```
/swarm-consensus Cambiar a arquitectura distribuida
/swarm-consensus Actualizar el sistema de comunicación

Iniciar consenso sobre: [propuesta]
```

### 📊 Monitoreo
```
/swarm-dashboard
/swarm-logs
Mostrar actividad reciente
```

## 🎪 Ejemplos de Uso Avanzado

### 1. Análisis de Datos Colaborativo
```
Usuario: "Necesito un análisis completo de las tendencias del mercado tecnológico"

SAM.CHAT → Swarm:
- 🤖 GoogleAI: Análisis con IA
- 🌐 Web: Recopilación de datos
- 📊 Analytics: Métricas y visualizaciones
- 📱 Notion: Documentación de resultados
```

### 2. Investigación Distribuida
```
Usuario: "Buscar información sobre blockchain y criptomonedas"

SAM.CHAT → Swarm:
- 🔍 Search: Indexación y filtrado
- 🌐 Web: Scraping de fuentes
- 🧠 Memory: Contextualización histórica
- 📧 Email: Notificaciones de resultados
```

### 3. Planificación Estratégica
```
Usuario: "Desarrollar plan de marketing para nuevo producto"

SAM.CHAT → Swarm:
- 🎯 Manus: Coordinación estratégica
- 📊 Analytics: Análisis de mercado
- 🤖 GoogleAI: Generación de ideas
- 📱 Notion: Estructuración del plan
```

## 🌐 API REST para Integración

### Endpoints Disponibles

```http
# Estado del swarm
GET http://localhost:8402/api/swarm/status

# Lista de agentes
GET http://localhost:8402/api/swarm/agents

# Crear tarea
POST http://localhost:8402/api/swarm/tasks
{
  "description": "Analizar datos de ventas"
}

# Iniciar consenso
POST http://localhost:8402/api/swarm/consensus
{
  "proposal": "Implementar nueva arquitectura"
}

# Procesar lenguaje natural
POST http://localhost:8402/api/swarm/process
{
  "input": "Necesito ayuda con análisis de datos"
}

# Obtener logs
GET http://localhost:8402/api/swarm/logs?limit=20

# Health check
GET http://localhost:8402/health
```

### Respuestas de Ejemplo

```json
{
  "success": true,
  "data": {
    "connection_status": "connected",
    "active_agents": 10,
    "active_tasks": 3,
    "swarm_features": {...}
  },
  "message": "🎪 Swarm is online with 10 active agents"
}
```

## 🎭 Agentes Disponibles

| Agente | Alias | Especialidades | Casos de Uso |
|--------|-------|----------------|--------------|
| **Manus** | `manus` | Planificación, Coordinación, Liderazgo | Estrategia, Gestión de proyectos |
| **SAM** | `sam-agent` | Ejecución, Autonomía, Adaptación | Automatización, Tareas complejas |
| **Memory** | `memory` | Memoria, Recuperación, Patrones | Contexto, Historial, Aprendizaje |
| **GoogleAI** | `googleai` | IA, Lenguaje, Razonamiento | Análisis, Generación, Inferencia |
| **Notion** | `notion` | Conocimiento, Organización | Documentación, Estructuración |
| **Email** | `email` | Comunicación, Mensajería | Notificaciones, Outreach |
| **Web** | `web` | Scraping, Investigación | Recopilación de datos web |
| **Analytics** | `analytics` | Análisis, Métricas, Insights | Reporting, Visualizaciones |
| **Search** | `search` | Búsqueda, Indexación, Filtrado | Descubrimiento, Recuperación |
| **MultiModel** | `multimodel` | Enrutado de IA, Optimización | Selección de modelos, Costos |

## 🧠 Inteligencia Emergente

El swarm detecta y reporta comportamientos emergentes:

- **Coordinación Espontánea**: Agentes trabajando juntos sin instrucciones explícitas
- **Liderazgo Emergente**: Agentes tomando iniciativa naturalmente
- **Resolución Colectiva**: El swarm resolviendo problemas de forma colaborativa
- **Optimización Automática**: Mejora continua de roles y eficiencia

## 📊 Monitoreo en Tiempo Real

### Dashboard Web (http://localhost:8401)
- Vista en tiempo real del swarm
- Gráfico de comunicaciones
- Métricas de rendimiento
- Actividad de agentes

### Métricas Clave
- **Coherencia del Swarm**: Qué tan coordinado está el sistema
- **Velocidad de Consenso**: Rapidez en toma de decisiones
- **Tasa de Completitud**: Porcentaje de tareas completadas
- **Comportamientos Emergentes**: Conteo de patrones detectados
- **IQ Colectivo**: Nivel de inteligencia del conjunto

## 🔧 Configuración Avanzada

### Personalizar Agentes
Editar `sam_chat_swarm_config.json` para:
- Modificar capacidades de agentes
- Ajustar roles y especialidades
- Configurar aliases para sam.chat
- Personalizar comandos

### Escalabilidad
- Agregar nuevos tipos de agentes
- Configurar múltiples swarms
- Integrar con otros sistemas
- Establecer federación de swarms

## 🚨 Solución de Problemas

### Verificar Conexiones
```bash
# Estado de servicios
ps aux | grep python3

# Verificar puertos
netstat -tlnp | grep -E '8400|8401|8402'

# Logs de diagnóstico
tail -f logs/swarm_core.log
tail -f logs/sam_chat_gateway.log
```

### Problemas Comunes

1. **"Swarm no responde"**
   - Verificar que el core esté ejecutándose en puerto 8400
   - Revisar logs/swarm_core.log

2. **"Gateway desconectado"**
   - Reiniciar sam_chat_swarm_gateway.py
   - Verificar conectividad WebSocket

3. **"Agentes no aparecen"**
   - Esperar 10-15 segundos para conexión completa
   - Verificar logs/swarm_agents.log

## 🎉 Casos de Uso Avanzados

### Automatización de Workflows
```
SAM.CHAT: "Crear workflow automatizado para análisis diario"
→ Swarm configura tareas recurrentes
→ Agentes coordinan ejecución
→ Resultados entregados automáticamente
```

### Investigación Colaborativa
```
SAM.CHAT: "Investigar impacto de la IA en educación"
→ Web busca fuentes académicas
→ GoogleAI analiza contenido
→ Analytics genera métricas
→ Notion estructura reporte final
```

### Toma de Decisiones Grupales
```
SAM.CHAT: "¿Deberíamos migrar a microservicios?"
→ Inicia proceso de consenso
→ Agentes analizan pros/contras
→ Votación democrática
→ Decisión basada en evidencia
```

---

🎪 **¡El sistema SuperMCP Swarm Intelligence está listo para uso desde SAM.CHAT!**

Accede a todo el poder de la inteligencia colectiva a través de comandos naturales y APIs unificadas.