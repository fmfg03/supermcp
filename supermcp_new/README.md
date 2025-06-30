# 🎪 SuperMCP 2.0 - Advanced Multi-Agent AI System

## 🌟 Overview

SuperMCP is a comprehensive AI orchestration platform that combines swarm intelligence, multi-model AI routing, and specialized agent coordination through the Model Context Protocol (MCP). The system enables seamless interaction between multiple AI agents, models, and specialized services.

## 🏗️ Architecture

```
🎪 SuperMCP 2.0 Architecture
═══════════════════════════════════════════════════════════════════════════
🏛️ Core Layer
   ├── 🧠 Domain Logic (Entities, Use Cases, Interfaces)
   ├── 🔧 Infrastructure (Persistence, External APIs, Messaging)
   └── 🎯 Application Services (Orchestrator, Coordinator)

🤖 Agents Layer
   ├── 🎪 Swarm Intelligence (Emergent Behavior, Consensus, Role Optimization)
   ├── 🎭 Specialized Agents (SAM, Manus, Terminal, GoogleAI)
   └── 🔗 Coordination (Message Broker, Task Distribution)

🔗 MCP Layer (Model Context Protocol)
   ├── 🗄️ Servers (FileSystem, Browser, Knowledge, Developer, Git, Search)
   ├── 🌐 Client (Connection Manager, Request Router)
   └── 📋 Shared (Schemas, Protocols, Validators)

🧠 AI Layer
   ├── 🤖 Models (Router, Providers: OpenAI/Claude/Google/Local)
   ├── 💾 Memory (Semantic, Episodic, Working Memory)
   └── 🧩 Reasoning (Planner, Decision Engine)

🌐 API Layer
   ├── 🔄 REST APIs (v1, Middleware)
   ├── ⚡ WebSocket (Swarm Gateway, Real-time Updates)
   └── 🚀 gRPC (Future Expansion)

🔒 Security Layer
   ├── 🔐 Authentication (Enterprise, Providers, Tokens)
   ├── 🛡️ Authorization (RBAC, Policies)
   └── 🔑 Encryption (Data, Communication Security)

📊 Monitoring Layer
   ├── 📈 Metrics (Collectors, Exporters)
   ├── 📝 Logging (Formatters, Handlers)
   ├── 🔍 Tracing (Distributed Tracing)
   └── ❤️ Health (Health Checks)
═══════════════════════════════════════════════════════════════════════════
```

## ✨ Features

### 🎪 **Swarm Intelligence**
- **18+ Intelligent Agents** (12 swarm + 6 MCP specialized)
- **Emergent Behavior Detection** with pattern recognition
- **Democratic Consensus Building** for collective decisions
- **Auto-Role Optimization** and dynamic task assignment
- **Peer-to-Peer Communication** via WebSocket

### 🤖 **Multi-Model AI Router**
- **Universal AI Access** (OpenAI, Claude, Google AI, DeepSeek, Perplexity)
- **Local Model Support** (Llama 3, Codestral, Ollama)
- **Intelligent Routing** with cost optimization
- **Auto-Fallback** mechanisms across providers
- **Token Budget Management** and usage tracking

### 🔗 **MCP Server Integration**
- **📁 FileSystem Server**: Complete CRUD file operations
- **🌐 Browser Server**: Web automation and scraping
- **🧠 Knowledge Server**: Memory and knowledge management
- **🛠️ Developer Server**: Code tools, testing, building
- **📝 Version Control Server**: Git operations and repository management
- **🔍 Search Server**: Advanced indexing and semantic search

### 🖥️ **Terminal Agent**
- **Security Classification System** (SAFE, MODERATE, DANGEROUS, RESTRICTED)
- **Sandboxed Execution** environment
- **Command Security Analysis** with real-time validation
- **System Monitoring** and resource tracking

### 🔒 **Enterprise Security**
- **Role-Based Access Control** (RBAC)
- **Multi-Provider Authentication** 
- **Data Encryption** at rest and in transit
- **Security Audit Logging**

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+ (for frontend components)
- Redis
- PostgreSQL
- Docker (optional)

### Installation

1. **Clone and Setup**
   ```bash
   git clone <repository-url>
   cd supermcp
   pip install -r project/requirements/development.txt
   ```

2. **Configure Environment**
   ```bash
   cp project/.env.example .env
   # Edit .env with your API keys and configuration
   ```

3. **Start the System**
   ```bash
   # Development mode
   ./deployment/scripts/start_development.sh
   
   # Production mode  
   ./deployment/scripts/start_production.sh
   ```

4. **Access the Interfaces**
   - **Web Dashboard**: http://localhost:8401
   - **Terminal Agent**: http://localhost:8500
   - **Multi-Model Router**: http://localhost:8300
   - **Swarm Core**: ws://localhost:8400
   - **MCP Servers**: Ports 8600-8605

## 📁 Project Structure

```
supermcp/
├── 🏛️ core/                    # Core business logic and infrastructure
├── 🤖 agents/                  # Swarm intelligence and specialized agents
├── 🔗 mcp/                     # Model Context Protocol implementation
├── 🧠 ai/                      # AI models, memory, and reasoning
├── 🌐 api/                     # REST, WebSocket, and gRPC APIs
├── 🔒 security/                # Authentication, authorization, encryption
├── 📊 monitoring/              # Metrics, logging, tracing, health checks
├── 🧪 testing/                 # Comprehensive testing suite
├── 🚀 deployment/              # Docker, Kubernetes, deployment scripts
├── ⚙️ config/                  # Configuration management
├── 📚 docs/                    # Documentation
├── 🗄️ data/                    # Database migrations and seeds
├── 📦 packages/                # Shared utilities and external integrations
├── 🔧 tools/                   # Development and migration tools
└── 📋 project/                 # Project metadata and requirements
```

## 🔧 Configuration

The system uses a hierarchical configuration system:

1. **Default Configuration**: `config/defaults.yaml`
2. **Environment Specific**: `config/environments/{env}.yaml`  
3. **Environment Variables**: `.env` file
4. **Runtime Overrides**: Command line arguments

## 🧪 Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest testing/unit/          # Unit tests
pytest testing/integration/   # Integration tests
pytest testing/e2e/          # End-to-end tests

# Run with coverage
pytest --cov=. --cov-report=html
```

## 📊 Monitoring

The system includes comprehensive monitoring:

- **Metrics**: Prometheus-compatible metrics on port 9090
- **Logging**: Structured JSON logging with multiple levels
- **Health Checks**: Automated health monitoring for all services
- **Distributed Tracing**: OpenTelemetry integration

## 🔒 Security

SuperMCP implements enterprise-grade security:

- **Authentication**: Multiple providers (OAuth, JWT, API Keys)
- **Authorization**: Fine-grained RBAC system
- **Encryption**: AES-256 encryption for sensitive data
- **Audit Logging**: Complete audit trail of all operations
- **Network Security**: TLS/SSL for all communications

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run the test suite
6. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- **Documentation**: `docs/` directory
- **Issues**: GitHub Issues
- **Discussions**: GitHub Discussions

## 🎯 Key Use Cases

- **Multi-Agent AI Orchestration**
- **Intelligent Task Distribution** 
- **Code Generation and Analysis**
- **Web Automation and Scraping**
- **Knowledge Management**
- **Version Control Automation**
- **Enterprise AI Integration**
- **Research and Development**

---

**SuperMCP 2.0** - Empowering the next generation of AI collaboration through swarm intelligence and unified protocols.