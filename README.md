# OpenAssetGraph (OAG)

**AI-Native Digital Twin for Enterprise Software Architecture**

OpenAssetGraph is an intelligent platform that combines graph database technology with AI to provide comprehensive visibility into enterprise software assets and their relationships.

## Features

- **Topology Visualization** - Interactive graph visualization showing databases, services, APIs, and applications with light tech-style UI
- **AI-Powered Analysis** - Ask questions about your architecture in natural language with project context
- **Project Scanner** - Import architecture from GitHub repositories with auto-recognition or add nodes manually
- **Project Management** - Persistent storage and management of scanned project architecture assets
- **Recent Projects** - Quick access to recently viewed projects in topology navigation
- **Dependency Tracking** - Understand how components connect and identify risks
- **Architecture Review** - AI-assisted evaluation of architectural proposals
- **Collapsible Sidebar** - Clean navigation with expandable menu

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| Frontend | React 18, TypeScript, Ant Design, @antv/g6 |
| Backend | Python 3.11+, FastAPI, Neo4j |
| LLM | GLM-4, Kimi, DeepSeek, OpenAI (multi-provider support) |
| Deploy | Docker, Docker Compose, GitHub Actions |

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Neo4j 5.x (via Docker or local installation)

### Option 1: Local Development

```bash
# 1. Start Neo4j (Docker)
docker-compose up -d neo4j

# 2. Backend (new terminal)
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# 3. Frontend (new terminal)
cd frontend
npm install
npm run dev
```

Access: http://localhost:3000

### Option 2: Docker

```bash
docker-compose up -d
```

Access: http://localhost:3000

## Demo Projects

The application includes built-in demo data:

- **Mall E-Commerce** - Spring Boot microservices (macrozheng/mall)
- **Online Boutique** - Google Cloud microservices demo
- **Spring PetClinic** - Spring Boot demo application

Scan a GitHub repository URL or switch between projects in the Topology page.

## Navigation

| Page | Description |
|------|-------------|
| **Home** | Dashboard with quick access to all features |
| **Topology** | Interactive graph visualization with project switching |
| **AI Chat** | Natural language queries about your architecture |
| **Scan** | Import architecture from GitHub or add manually |
| **Projects** | Manage scanned project architecture assets |
| **Review** | AI-assisted architecture review |

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/topology` | Get full topology |
| `GET /api/topology/search?q=query` | Search nodes |
| `GET /api/projects` | List all projects |
| `GET /api/projects/{name}/stats` | Get project statistics |
| `POST /api/scan/github` | Scan GitHub repository |
| `DELETE /api/scan/project/{name}` | Delete a project |
| `POST /api/chat` | AI chat with project context |

Full API docs: http://localhost:8000/docs

## Configuration

Create `.env` file in backend directory:

```env
# LLM Provider (openai, glm, kimi, deepseek)
LLM_PROVIDER=glm
LLM_MODEL=glm-4-flash

# API Keys
GLM_API_KEY=your-glm-api-key      # https://open.bigmodel.cn/
KIMI_API_KEY=your-kimi-api-key    # https://platform.moonshot.cn/
OPENAI_API_KEY=your-openai-key    # Optional fallback

# Database
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

### Supported LLM Providers

| Provider | Models | API Key Source |
|----------|--------|----------------|
| **GLM (智谱AI)** | glm-4, glm-4-flash, glm-4-plus | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| **Kimi (月之暗面)** | moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k | [platform.moonshot.cn](https://platform.moonshot.cn/) |
| **DeepSeek** | deepseek-chat, deepseek-coder | [platform.deepseek.com](https://platform.deepseek.com/) |
| **OpenAI** | gpt-4, gpt-4-turbo, gpt-4o | [platform.openai.com](https://platform.openai.com/) |

## Project Reference in AI Chat

Use `#project-name#` syntax to reference specific projects in AI Chat:

```
分析 #mall# 的架构
比较 #mall# 和 #online-boutique# 的区别
```

## Project Structure

```
OAG/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── services/      # Business logic
│   │   ├── models/        # Data models
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   ├── services/      # API services
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

## Use Cases

- Document and visualize enterprise architecture
- Identify circular dependencies and bottlenecks
- Analyze impact of proposed changes
- Enable architecture knowledge sharing
- Support architecture decision making with AI insights
- Track and manage multiple project architectures

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0
