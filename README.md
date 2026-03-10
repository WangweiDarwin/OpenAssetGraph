# OpenAssetGraph (OAG)

**AI-Native Digital Twin for Enterprise Software Architecture**

OpenAssetGraph is an intelligent platform that combines graph database technology with AI to provide comprehensive visibility into enterprise software assets and their relationships. It helps organizations understand, analyze, and optimize their software architecture through interactive visualization and natural language queries.

## Key Features

- **Topology Visualization**: Interactive graph visualization showing databases, services, APIs, and applications with their dependencies
- **AI-Powered Analysis**: Ask questions about your architecture in natural language and get intelligent insights
- **Dependency Tracking**: Understand how components connect and identify potential risks
- **Architecture Review**: AI-assisted evaluation of architectural proposals and changes

## Tech Stack

**Frontend**: React 18, TypeScript, Ant Design, @antv/g6
**Backend**: Python, FastAPI, Neo4j, OpenAI API

## Quick Start

```bash
# Backend
cd backend && pip install -r requirements.txt
python -m uvicorn app.main:app --port 8002

# Frontend
cd frontend && npm install && npm run dev
```

Access the application at http://localhost:3000

## Use Cases

- Document and visualize enterprise architecture
- Identify circular dependencies and bottlenecks
- Analyze impact of proposed changes
- Enable architecture knowledge sharing
- Support architecture decision making with AI insights

OpenAssetGraph bridges the gap between complex enterprise systems and human understanding, making architecture accessible to both technical and non-technical stakeholders.

**License**: Apache 2.0
