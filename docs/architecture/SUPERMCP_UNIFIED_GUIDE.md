# 🚀 SuperMCP - Sistema Unificado de IA

**TODO lo que necesitas en una interfaz unificada:**
- 🎪 **Swarm Intelligence**: 11 agentes inteligentes con comportamiento emergente
- 🤖 **Multi-Model Router**: Todos los modelos (APIs + locales) con optimización automática
- 🌉 **SAM.CHAT Integration**: Interfaz natural de lenguaje
- 💰 **Cost Optimization**: Prioriza modelos locales gratuitos

---

## 🎯 Lo que el sistema integra:

### 🔥 APIs Externas:
- **OpenAI** (GPT-4o, GPT-3.5)
- **Claude** (Opus, Sonnet) 
- **DeepSeek** (DeepSeek-Coder)
- **Perplexity** (Sonar)
- **Google AI** (Gemini Pro)

### 💻 Modelos Locales:
- **Llama 3** (70B) - GRATIS
- **Codestral** (22B) - GRATIS
- **Cualquier modelo Ollama** - GRATIS

### 🧠 Router Inteligente:
```python
# Selección automática por especialización:
- Código → DeepSeek Coder (prioridad 1)
- Research → Perplexity (prioridad 1) 
- Análisis → Claude Opus (prioridad 1)
- Chat general → Local models (gratis)
- Traducción → Google AI (barato)
```

### 💰 Optimización de Costos:
```python
# Sistema prioriza por:
1. Modelos locales (costo = $0)
2. Modelos baratos para tareas simples  
3. Modelos premium solo cuando sea necesario
4. Fallback automático si falla un modelo
```

---

## 🚀 Inicio Rápido

### 1. Configurar APIs (opcional)
```bash
# Copiar plantilla de configuración
cp .env.template .env

# Editar .env y agregar tus API keys (dejar en blanco para saltar)
nano .env
```

### 2. Instalar modelos locales (opcional pero recomendado)
```bash
# Instalar Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelos gratuitos
ollama pull llama3:70b      # Modelo general
ollama pull codestral:22b   # Modelo para código
```

### 3. Iniciar el sistema completo
```bash
chmod +x start_swarm_demo.sh
./start_swarm_demo.sh
```

### 4. Acceder a las interfaces
- 🤖 **Multi-Model Router**: http://localhost:8300
- 🌉 **SAM.CHAT Gateway**: http://localhost:8402  
- 📊 **Dashboard Visual**: http://localhost:8401
- 🔌 **Swarm Core**: ws://localhost:8400

---

## 🌐 Endpoints Unificados

### Multi-Model Router (Puerto 8300)

#### Generación General
```bash
curl -X POST http://localhost:8300/generate \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Explica la teoría de relatividad",
    "task_type": "general",
    "max_tokens": 1000
  }'
```

#### Generación de Código (usa DeepSeek automáticamente)
```bash
curl -X POST http://localhost:8300/code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Crea una función Python para calcular fibonacci",
    "max_tokens": 500
  }'
```

#### Research (usa Perplexity automáticamente)
```bash
curl -X POST http://localhost:8300/research \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Últimas tendencias en inteligencia artificial 2024",
    "max_tokens": 2000
  }'
```

#### Análisis (usa Claude Opus automáticamente)
```bash
curl -X POST http://localhost:8300/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analiza los pros y contras de los microservicios",
    "max_tokens": 1500
  }'
```

#### Chat (usa modelos locales primero)
```bash
curl -X POST http://localhost:8300/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Hola, ¿cómo estás?",
    "max_tokens": 500
  }'
```

### SAM.CHAT Gateway (Puerto 8402)

#### Procesamiento de Lenguaje Natural
```bash
curl -X POST http://localhost:8402/api/swarm/process \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Necesito que el swarm analice datos de mercado"
  }'
```

#### Control del Swarm
```bash
# Estado del swarm
curl http://localhost:8402/api/swarm/status

# Lista de agentes
curl http://localhost:8402/api/swarm/agents

# Crear tarea
curl -X POST http://localhost:8402/api/swarm/tasks \
  -H "Content-Type: application/json" \
  -d '{"description": "Analizar tendencias de IA"}'
```

---

## 🎪 Agentes del Swarm

| Agente | Especialidad | Casos de Uso |
|--------|-------------|--------------|
| **Manus** | Coordinación estratégica | Planificación, gestión |
| **SAM** | Ejecución autónoma | Automatización, tareas complejas |
| **Memory** | Gestión de contexto | Historial, aprendizaje |
| **GoogleAI** | IA especializada | Análisis, inferencia |
| **Notion** | Gestión del conocimiento | Documentación |
| **Email** | Comunicación | Notificaciones |
| **Web** | Investigación web | Scraping, datos |
| **Analytics** | Análisis de datos | Métricas, insights |
| **Search** | Búsqueda y filtrado | Descubrimiento |
| **MultiModel** | Router de IA | Selección automática de modelos |

---

## 💡 Ejemplos de Uso

### Ejemplo 1: Desarrollo de Software
```bash
# El sistema automáticamente usa DeepSeek para código
curl -X POST http://localhost:8300/code \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Crear una API REST en Python con FastAPI para gestión de usuarios",
    "max_tokens": 2000
  }'
```

### Ejemplo 2: Investigación
```bash
# El sistema automáticamente usa Perplexity para research
curl -X POST http://localhost:8300/research \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Últimos avances en computación cuántica y sus aplicaciones",
    "max_tokens": 3000
  }'
```

### Ejemplo 3: Análisis Empresarial
```bash
# El sistema automáticamente usa Claude Opus para análisis
curl -X POST http://localhost:8300/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Analizar impacto de la IA en el sector financiero",
    "max_tokens": 2500
  }'
```

### Ejemplo 4: Chat Casual (GRATIS)
```bash
# El sistema usa modelos locales (costo = $0)
curl -X POST http://localhost:8300/chat \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Cuenta un chiste sobre programadores",
    "max_tokens": 300
  }'
```

### Ejemplo 5: Coordinación del Swarm
```bash
# Asignar tarea compleja al swarm completo
curl -X POST http://localhost:8402/api/swarm/process \
  -H "Content-Type: application/json" \
  -d '{
    "input": "Crear un plan de marketing completo para una startup de IA"
  }'
```

---

## 🎯 Comandos desde SAM.CHAT

### Comandos Directos
```
/swarm-status                    # Estado del swarm
/swarm-agents                    # Lista de agentes
/swarm-task [descripción]        # Asignar tarea
/swarm-consensus [propuesta]     # Iniciar consenso
/swarm-dashboard                 # URL del dashboard
```

### Lenguaje Natural
```
"Analiza las tendencias del mercado de criptomonedas"
"Genera código Python para una calculadora"
"Busca información sobre energías renovables"
"El swarm debería decidir sobre migrar a microservicios"
"Necesito ayuda con análisis de datos"
```

---

## 🔧 Características Avanzadas

### 🤖 Selección Automática de Modelos
- **Código**: DeepSeek-Coder (especializado + barato)
- **Research**: Perplexity (acceso a web + actualizado)
- **Análisis**: Claude Opus (razonamiento superior)
- **Chat**: Llama3 local (gratis + rápido)
- **Traducción**: Google AI (especializado + barato)

### 💰 Optimización de Costos
```json
{
  "priority_order": [
    "1. Modelos locales (Llama3, Codestral) - $0",
    "2. Modelos baratos (Google AI, DeepSeek) - $0.0005-0.0014",
    "3. Modelos premium (Claude, GPT-4) - $0.003-0.015",
    "4. Fallback automático si falla modelo"
  ]
}
```

### 🔄 Fallback Automático
1. Intenta modelo primario
2. Si falla → modelo secundario
3. Si falla → modelo terciario
4. Reporta errores y estadísticas

### 🧠 Inteligencia Emergente
- Detección de patrones de comportamiento
- Liderazgo emergente automático
- Optimización dinámica de roles
- Consenso democrático

---

## 📊 Monitoreo y Métricas

### Dashboard Web (http://localhost:8401)
- Vista en tiempo real del swarm
- Métricas de rendimiento
- Gráfico de comunicaciones
- Estadísticas de costos

### API de Estadísticas
```bash
# Estadísticas del router
curl http://localhost:8300/stats

# Estado del swarm
curl http://localhost:8402/api/swarm/status

# Modelos disponibles
curl http://localhost:8300/models
```

### Logs del Sistema
```bash
# Ver logs en tiempo real
tail -f logs/multimodel_router.log    # Router de IA
tail -f logs/swarm_core.log          # Core del swarm
tail -f logs/sam_chat_gateway.log    # Gateway SAM.CHAT
tail -f logs/swarm_agents.log        # Agentes demo
```

---

## 🚨 Solución de Problemas

### Problema: "No models available"
```bash
# Verificar configuración de APIs
grep -v "^#" .env

# Verificar Ollama local
ollama list
ollama serve
```

### Problema: "Swarm disconnected"
```bash
# Verificar puerto del swarm
netstat -tlnp | grep 8400

# Reiniciar sistema
./start_swarm_demo.sh
```

### Problema: "High costs"
```bash
# Usar solo modelos locales
curl -X POST http://localhost:8300/generate \
  -d '{"prompt":"test", "budget_limit":0.0}'

# Verificar uso de modelos gratuitos
curl http://localhost:8300/stats
```

---

## 🎯 Casos de Uso Empresariales

### 1. Centro de Desarrollo
- **Código**: DeepSeek automático
- **Review**: Claude Opus para análisis
- **Docs**: Modelos locales para ahorro
- **Research**: Perplexity para tecnologías

### 2. Departamento de Marketing
- **Análisis**: Claude Opus para insights
- **Creatividad**: Modelos locales gratuitos
- **Research**: Perplexity para tendencias
- **Coordinación**: Swarm para proyectos complejos

### 3. Equipos de Investigación
- **Research**: Perplexity para papers recientes
- **Análisis**: Claude Opus para interpretación
- **Traducción**: Google AI multiidioma
- **Colaboración**: Swarm para consenso

---

## 🎪 ¡Sistema Completo Listo!

El SuperMCP es tu **centro de comando unificado** para toda la inteligencia artificial:

✅ **11 agentes inteligentes** trabajando en equipo  
✅ **Todos los modelos principales** con selección automática  
✅ **Optimización de costos** que prefiere modelos locales gratuitos  
✅ **Fallback automático** entre modelos  
✅ **Interfaz natural** desde SAM.CHAT  
✅ **Monitoreo en tiempo real** con dashboard web  
✅ **Inteligencia emergente** del swarm  

**¡Accede a todo desde una sola interfaz!** 🚀