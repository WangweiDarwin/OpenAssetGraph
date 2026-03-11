# Quick Start Guide

## Prerequisites

- Docker and Docker Compose
- Git
- (Optional) OpenAI API key for AI features

## 1. Clone the Repository

```bash
git clone https://github.com/WangweiDarwin/OpenAssetGraph.git
cd OpenAssetGraph
```

## 2. Configure Environment

```bash
cp backend/.env.example backend/.env
# Edit backend/.env and add your OpenAI API key (optional)
```

## 3. Start Services

### Development Mode

```bash
docker-compose up -d neo4j postgres redis
docker-compose up -d backend frontend
```

### Production Mode

```bash
docker-compose --profile production up -d
```

## 4. Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (user: neo4j, password: password123)

## 5. Import Sample Data

```bash
# Import mall project architecture
docker-compose exec backend python scripts/import_mall_project.py
```

## 6. Verify Installation

1. Open http://localhost:3000/topology
2. You should see the topology visualization
3. Click on nodes to see details
4. Use the search panel to find specific components

## Troubleshooting

### Neo4j Connection Issues

```bash
# Check Neo4j status
docker-compose logs neo4j

# Restart Neo4j
docker-compose restart neo4j
```

### Frontend Not Loading

```bash
# Rebuild frontend
docker-compose build frontend
docker-compose up -d frontend
```

### API Errors

```bash
# Check backend logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

## Local Development (without Docker)

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Next Steps

1. Connect your own databases using the scan API
2. Configure OpenAI API key for AI-powered analysis
3. Import your project architecture
4. Customize the visualization
