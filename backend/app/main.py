"""
OpenAssetGraph Backend Application
"""
import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.scan import router as scan_router
from app.api.topology import router as topology_router
from app.api.chat import router as chat_router
from app.services.graph_service import Neo4jService
from app.services.mock_data import mock_data_service

logger = logging.getLogger(__name__)

neo4j_service: Neo4jService | None = None

app = FastAPI(
    title=settings.app_name,
    description="AI-Native Digital Twin for Enterprise Software",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(scan_router)
app.include_router(topology_router)
app.include_router(chat_router)


@app.on_event("startup")
async def startup_event():
    global neo4j_service
    logger.info("Application starting up...")
    
    neo4j_service = Neo4jService(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    
    try:
        await neo4j_service.connect()
        logger.info("Connected to Neo4j database")
        
        node_count = await neo4j_service.get_node_count()
        logger.info(f"Current Neo4j node count: {node_count}")
        
        if node_count == 0:
            logger.info("No nodes found in Neo4j, starting data migration...")
            result = await mock_data_service.migrate_all_projects_to_neo4j(neo4j_service)
            logger.info(f"Data migration completed: {result}")
        else:
            logger.info("Neo4j already contains data, skipping migration")
            
    except Exception as e:
        logger.error(f"Failed to connect to Neo4j or migrate data: {e}")
        neo4j_service = None


@app.on_event("shutdown")
async def shutdown_event():
    global neo4j_service
    logger.info("Application shutting down...")
    
    if neo4j_service:
        await neo4j_service.close()
        logger.info("Neo4j connection closed")


@app.get("/")
async def root():
    return {
        "message": "Welcome to OpenAssetGraph API",
        "version": "0.1.0",
        "docs": "/docs",
    }


@app.get("/health")
async def health_check():
    neo4j_connected = neo4j_service is not None and neo4j_service.driver is not None
    node_count = 0
    
    if neo4j_connected:
        try:
            node_count = await neo4j_service.get_node_count()
        except Exception:
            neo4j_connected = False
    
    return {
        "status": "healthy",
        "neo4j": {
            "connected": neo4j_connected,
            "node_count": node_count
        }
    }
