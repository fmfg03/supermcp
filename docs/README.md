# SuperMCP - Enterprise AI Platform Documentation

![SuperMCP Logo](./assets/supermcp-logo.png)

**Version:** 2.0.0 Enterprise  
**Last Updated:** June 30, 2025  
**Status:** Production Ready  

---

## 🌟 **Overview**

SuperMCP is a comprehensive enterprise AI platform that combines microservices orchestration, multi-agent AI systems, and advanced automation capabilities. The platform includes **Agentius**, a specialized AI proposal evaluation and generation system designed for enterprise-scale deployment.

### **Key Features**
- 🏗️ **Microservices Architecture** - Scalable, independent services
- 🤖 **Multi-Agent AI Systems** - Autonomous decision-making agents
- 📊 **Advanced Analytics** - Real-time monitoring and insights
- 🔒 **Enterprise Security** - Role-based access and compliance
- 🚀 **Auto-Scaling** - Dynamic resource allocation
- 🌍 **Multi-Tenant** - Isolated customer environments
- 🧠 **Auto-Retraining System** - Continuous model improvement with feedback loops
- 🎭 **Buyer Simulator** - Advanced negotiation testing with 5+ buyer personalities
- 👁️ **Shadow Mode Learning** - Silent observation and learning from human decisions
- 📦 **Vertical Deployment** - Industry-specific containerized instances
- 📄 **Auto-Brief Extraction** - Zero-touch onboarding from any document format

### **Advanced AI Features**
- 🕸️ **Graphiti Knowledge Graph** - Temporal relationship management with Neo4j
- 🤝 **A2A Communication** - Direct agent-to-agent peer communication
- 🗣️ **Voice Processing** - Multi-agent voice system with LangWatch integration
- 🧬 **Swarm Intelligence** - Emergent collective behavior and optimization
- 🎯 **LangGraph Studio** - Visual debugging and graph monitoring
- 🌐 **MCP Observatory** - Nuclear-grade dashboard for system monitoring
- 💪 **Hardcore Training** - Continuous learning from success/failure patterns
- 🔍 **Testing Harness** - Automated stress testing and edge case detection

---

## 📚 **Documentation Index**

### **Getting Started**
- [Quick Start Guide](./getting-started/quick-start.md)
- [Installation Guide](./getting-started/installation.md)
- [Configuration](./getting-started/configuration.md)
- [First Deployment](./getting-started/first-deployment.md)

### **Architecture**
- [System Architecture](./architecture/system-overview.md)
- [Microservices Design](./architecture/microservices.md)
- [Event-Driven Architecture](./architecture/event-driven.md)
- [Security Architecture](./architecture/security.md)
- [Scaling Strategy](./architecture/scaling.md)

### **Core Services**
- [Orchestration Service](./services/orchestration.md)
- [Memory Analyzer](./services/memory-analyzer.md)
- [Webhook System](./services/webhook-system.md)
- [Authentication Service](./services/authentication.md)
- [Monitoring Service](./services/monitoring.md)
- [Graphiti Knowledge Graph](./services/graphiti-integration.md)
- [A2A Communication](./services/a2a-system.md)
- [Voice Processing System](./services/voice-system.md)
- [Swarm Intelligence](./services/swarm-intelligence.md)

### **Agentius AI Platform**
- [Agentius Overview](./agentius/overview.md)
- [Multi-Agent Pipeline](./agentius/pipeline.md)
- [Specialized Judges](./agentius/judges.md)
- [Training System](./agentius/training.md)
- [Vertical Deployment](./agentius/vertical-deployment.md)
- [Auto-Retraining Engine](./agentius/auto-retraining.md)
- [Buyer Simulator](./agentius/buyer-simulator.md)
- [Shadow Mode Learning](./agentius/shadow-mode.md)
- [Auto-Brief Extraction](./agentius/auto-brief.md)

### **API Reference**
- [REST API Documentation](./api/rest-api.md)
- [WebSocket API](./api/websocket-api.md)
- [GraphQL Schema](./api/graphql.md)
- [SDK Documentation](./api/sdk.md)

### **Deployment**
- [Docker Deployment](./deployment/docker.md)
- [Kubernetes Deployment](./deployment/kubernetes.md)
- [Cloud Deployment](./deployment/cloud.md)
- [Production Setup](./deployment/production.md)

### **Development**
- [Development Setup](./development/setup.md)
- [Contributing Guidelines](./development/contributing.md)
- [Testing Strategy](./development/testing.md)
- [Code Standards](./development/standards.md)
- [LangGraph Studio](./development/langgraph-studio.md)
- [MCP Observatory](./development/mcp-observatory.md)
- [Hardcore Training](./development/hardcore-training.md)
- [Testing Harness](./development/testing-harness.md)

### **Operations**
- [Monitoring & Alerting](./operations/monitoring.md)
- [Backup & Recovery](./operations/backup.md)
- [Performance Tuning](./operations/performance.md)
- [Troubleshooting](./operations/troubleshooting.md)

---

## 🏗️ **Architecture Overview**

```mermaid
graph TB
    subgraph "Frontend Layer"
        UI[Web UI]
        OBS[MCP Observatory]
        STUDIO[LangGraph Studio]
        API[API Gateway]
        WS[WebSocket Gateway]
        VOICE[Voice Interface]
    end
    
    subgraph "Application Layer"
        ORCH[Orchestration Service]
        MEM[Memory Analyzer]
        HOOK[Webhook System]
        AUTH[Authentication]
        A2A[A2A Communication]
        SWARM[Swarm Intelligence]
    end
    
    subgraph "Agentius AI Platform"
        BUILDER[Builder Agent]
        JUDGES[Judge Agents]
        REFINER[Refiner Agent]
        TRAINER[Auto-Retraining Engine]
        BUYER[Buyer Simulator]
        SHADOW[Shadow Mode]
    end
    
    subgraph "Advanced AI Systems"
        GRAPHITI[Graphiti Knowledge Graph]
        VOICE_SYS[Voice Processing System]
        HARDCORE[Hardcore Training Loop]
        TEST_HARNESS[Testing Harness]
        LANGWATCH[LangWatch Integration]
    end
    
    subgraph "Data Layer"
        NEO4J[(Neo4j Graph DB)]
        DB[(PostgreSQL)]
        CACHE[(Redis Cache)]
        STORAGE[(File Storage)]
        VECTOR[(Vector DB)]
    end
    
    UI --> API
    OBS --> ORCH
    STUDIO --> LANGWATCH
    API --> ORCH
    WS --> HOOK
    VOICE --> VOICE_SYS
    
    ORCH --> MEM
    ORCH --> AUTH
    ORCH --> A2A
    HOOK --> BUILDER
    A2A --> SWARM
    
    BUILDER --> JUDGES
    JUDGES --> REFINER
    REFINER --> TRAINER
    TRAINER --> HARDCORE
    BUYER --> SHADOW
    
    VOICE_SYS --> LANGWATCH
    SWARM --> GRAPHITI
    TEST_HARNESS --> HARDCORE
    
    ORCH --> DB
    MEM --> CACHE
    GRAPHITI --> NEO4J
    VOICE_SYS --> VECTOR
    HOOK --> STORAGE
```

---

## 🚀 **Quick Start**

### **Prerequisites**
- Docker 24.0+
- Node.js 18+
- Python 3.11+
- PostgreSQL 15+

### **Installation**
```bash
# Clone repository
git clone https://github.com/fmfg03/supermcp.git
cd supermcp

# Install dependencies
npm install
pip install -r requirements.txt

# Start services
docker-compose up -d

# Verify installation
./quick_validation_test.sh
```

### **First API Call**
```bash
curl -X POST http://localhost:8000/api/v1/orchestration/execute \
  -H "Content-Type: application/json" \
  -d '{
    "action": "health_check",
    "parameters": {}
  }'
```

---

## 🤖 **Agentius AI Platform**

### **Overview**
Agentius is SuperMCP's flagship AI platform for proposal evaluation and generation. It uses a multi-agent approach with psychological modeling to create enterprise-grade business proposals.

### **Key Components**
- **Builder Agent** - Generates initial proposals
- **Judge Agents** - Evaluates from different perspectives
- **Refiner Agent** - Iteratively improves proposals
- **Training Engine** - Continuous learning system with auto-retraining
- **Deployment System** - Industry-specific containers
- **Buyer Simulator** - 5+ buyer personalities with negotiation tactics
- **Shadow Mode** - Silent learning from human decisions
- **Auto-Brief Extractor** - Multi-format document processing

### **Getting Started with Agentius**
```bash
# Navigate to Agentius
cd services/proposal-evaluator

# Start evaluation
python main.py evaluate \
  --client "TechCorp" \
  --context "SaaS platform migration" \
  --objectives "Reduce costs,Improve performance"

# Start webhook API
python adapters/webhook_adapter.py

# Deploy vertical instance
python deployment/vertical_deployer.py \
  --vertical healthcare \
  --client hospital-abc
```

---

## 🔧 **Services Architecture**

### **Core Services**
| Service | Port | Description |
|---------|------|-------------|
| Orchestration | 8000 | Main coordination service with MCP protocol |
| Memory Analyzer | 8001 | Context and memory management with vectorial search |
| Webhook System | 8002 | Event processing and webhooks |
| Authentication | 8003 | Identity and access management |
| Monitoring | 8004 | Metrics and health checks |
| A2A Communication | 8005 | Agent-to-agent peer communication |
| Swarm Intelligence | 8006 | Collective behavior coordination |

### **Agentius Services**
| Service | Port | Description |
|---------|------|-------------|
| Proposal Evaluator | 8100 | Main Agentius service with multi-agent pipeline |
| Webhook Adapter | 8101 | RESTful API interface |
| Telegram Adapter | 8102 | Telegram bot integration |
| Auto-Retraining Engine | 8103 | ML training pipeline with continuous learning |
| Buyer Simulator | 8104 | Advanced negotiation testing |
| Shadow Mode | 8105 | Silent learning and observation |

### **Advanced AI Services**
| Service | Port | Description |
|---------|------|-------------|
| Graphiti Knowledge Graph | 7200 | Neo4j-backed temporal knowledge management |
| Voice Processing | 8200 | Multi-agent voice system with LangWatch |
| LangGraph Studio | 8201 | Visual debugging and graph monitoring |
| MCP Observatory | 5173 | Nuclear-grade system monitoring dashboard |
| Hardcore Training | 8202 | Success/failure pattern learning |
| Testing Harness | 8203 | Automated stress testing and validation |

---

## 📊 **Monitoring & Metrics**

### **Health Endpoints**
- **System Health:** `GET /health`
- **Service Status:** `GET /api/v1/status`
- **Metrics:** `GET /metrics`

### **Key Metrics**
- Request latency (p50, p95, p99)
- Error rates by service
- Agent evaluation success rates
- Training pipeline performance
- Resource utilization

---

## 🔒 **Security**

### **Authentication**
- JWT-based authentication
- Role-based access control (RBAC)
- API key management
- OAuth 2.0 integration

### **Data Protection**
- End-to-end encryption
- Data at rest encryption
- PII anonymization
- Audit logging

### **Compliance**
- GDPR compliance
- HIPAA ready
- SOC 2 Type II
- ISO 27001 alignment

---

## 🌍 **Deployment Options**

### **Development**
```bash
docker-compose -f docker-compose.dev.yml up
```

### **Production**
```bash
docker-compose -f docker-compose.production.yml up
```

### **Kubernetes**
```bash
kubectl apply -f infrastructure/kubernetes/
```

### **Cloud Providers**
- AWS ECS/EKS
- Google Cloud Run/GKE
- Azure Container Instances/AKS
- DigitalOcean App Platform

---

## 📝 **Configuration**

### **Environment Variables**
```bash
# Core Configuration
SUPERMCP_ENV=production
SUPERMCP_LOG_LEVEL=info
SUPERMCP_SECRET_KEY=your-secret-key

# Database
DATABASE_URL=postgresql://user:pass@host:5432/supermcp
REDIS_URL=redis://localhost:6379

# AI Configuration
OPENAI_API_KEY=your-openai-key
ANTHROPIC_API_KEY=your-anthropic-key

# Security
JWT_SECRET=your-jwt-secret
ENCRYPTION_KEY=your-encryption-key
```

### **Service Configuration**
Each service can be configured via:
- Environment variables
- Configuration files (`config/`)
- Command-line arguments
- Runtime API calls

---

## 🔗 **Integration**

### **REST API**
```javascript
// JavaScript example
const response = await fetch('/api/v1/agentius/evaluate', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'Authorization': 'Bearer ' + token
  },
  body: JSON.stringify({
    client: 'TechCorp',
    context: 'Digital transformation project',
    objectives: ['Reduce costs', 'Improve efficiency']
  })
});
```

### **WebSocket**
```javascript
const ws = new WebSocket('ws://localhost:8000/ws/agentius/stream');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Evaluation progress:', data);
};
```

### **Python SDK**
```python
from supermcp import SuperMCPClient

client = SuperMCPClient(
    base_url='http://localhost:8000',
    api_key='your-api-key'
)

result = await client.agentius.evaluate(
    client='TechCorp',
    context='Digital transformation',
    objectives=['Reduce costs', 'Improve efficiency']
)
```

---

## 📞 **Support**

### **Documentation**
- [Full Documentation](./docs/)
- [API Reference](./api/)
- [Examples](./examples/)
- [Troubleshooting](./operations/troubleshooting.md)

### **Community**
- GitHub Issues
- Discord Community
- Stack Overflow (tag: supermcp)
- Community Forum

### **Enterprise Support**
- 24/7 Technical Support
- Dedicated Success Manager
- Custom Training
- Professional Services

---

## 📄 **License**

SuperMCP is licensed under the MIT License. See [LICENSE](../LICENSE) for details.

---

## 🤝 **Contributing**

We welcome contributions! Please see our [Contributing Guidelines](./development/contributing.md) for details.

### **Quick Contribution Steps**
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

---

## 🏆 **Enterprise Features**

### **Advanced Analytics**
- Real-time dashboards with performance metrics
- Custom metrics and KPI tracking
- Predictive analytics with 94% accuracy
- Business intelligence with ROI tracking
- Auto-retraining performance monitoring
- Shadow mode learning analytics

### **High Availability**
- 99.99% uptime SLA
- Auto-failover with buyer simulation backup
- Load balancing across vertical deployments
- Disaster recovery with context preservation

### **Scalability**
- Horizontal scaling with container orchestration
- Auto-scaling policies based on evaluation load
- Multi-region deployment with data synchronization
- CDN integration for document processing
- Vertical-specific scaling configurations

### **Enterprise Integrations**  
- SSO/SAML with role-based access
- LDAP/Active Directory integration
- Slack/Teams with real-time notifications
- Salesforce/HubSpot with proposal tracking
- Document management system integration
- Voice transcription service integration

---

**🚀 Ready to transform your business with AI? Get started with SuperMCP today!**