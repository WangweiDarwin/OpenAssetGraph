# OpenAssetGraph (OAG)

**AI-Native Digital Twin for Enterprise Software Architecture**

OpenAssetGraph is an intelligent platform that combines graph database technology with AI to provide comprehensive visibility into enterprise software assets and their relationships.

## Features

- **Topology Visualization** - Interactive graph visualization showing databases, services, APIs, and applications with light tech-style UI
- **AI-Powered Analysis** - Ask questions about your architecture in natural language
- **Project Scanner** - Import architecture from GitHub repositories with auto-recognition or add nodes manually
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

### Option 1: Local Development

```bash
# Backend
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --port 8002

# Frontend (new terminal)
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

- **Demo Project** - Sample enterprise architecture
- **Mall E-Commerce** - Spring Boot microservices (macrozheng/mall)
- **Online Boutique** - Google Cloud microservices demo

Scan a GitHub repository URL or switch between projects in the Topology page.

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/topology` | Get full topology |
| `GET /api/topology/search?q=query` | Search nodes |
| `POST /api/scan/github` | Scan GitHub repository |
| `POST /api/chat` | AI chat |

Full API docs: http://localhost:8002/docs

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
NEO4J_PASSWORD=password
```

### Supported LLM Providers

| Provider | Models | API Key Source |
|----------|--------|----------------|
| **GLM (智谱AI)** | glm-4, glm-4-flash, glm-4-plus | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| **Kimi (月之暗面)** | moonshot-v1-8k, moonshot-v1-32k, moonshot-v1-128k | [platform.moonshot.cn](https://platform.moonshot.cn/) |
| **DeepSeek** | deepseek-chat, deepseek-coder | [platform.deepseek.com](https://platform.deepseek.com/) |
| **OpenAI** | gpt-4, gpt-4-turbo, gpt-4o | [platform.openai.com](https://platform.openai.com/) |

## Project Structure

```
OAG/
├── backend/
│   ├── app/
│   │   ├── api/           # API routes
│   │   ├── services/      # Business logic
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   ├── pages/         # Page components
│   │   └── services/      # API services
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

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

Apache License 2.0
