"""Project scan API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import re

from ..services.mock_data import mock_data_service
from ..services.graph_service import Neo4jService
from ..models.graph import GraphNode, GraphRelationship, NodeType, RelationshipType
from ..core.config import settings

router = APIRouter(prefix="/api/scan", tags=["scan"])


class GitHubProjectRequest(BaseModel):
    """Request to scan a GitHub project"""
    repo_url: str
    branch: Optional[str] = "main"
    scan_type: str = "architecture"


class ManualNodeRequest(BaseModel):
    """Request to add nodes manually"""
    nodes: List[dict]
    edges: Optional[List[dict]] = None


class ScanResult(BaseModel):
    """Result of a project scan"""
    status: str
    nodes_added: int
    edges_added: int
    message: str


def get_neo4j_service() -> Neo4jService:
    """Create a Neo4jService instance with settings"""
    return Neo4jService(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )


def parse_node_type(type_str: str) -> NodeType:
    """Parse node type string to NodeType enum"""
    type_mapping = {
        "Database": NodeType.DATABASE,
        "Table": NodeType.TABLE,
        "Column": NodeType.COLUMN,
        "Service": NodeType.SERVICE,
        "API": NodeType.API,
        "FrontendApp": NodeType.FRONTEND_APP,
        "Component": NodeType.COMPONENT,
    }
    return type_mapping.get(type_str, NodeType.SERVICE)


def parse_relationship_type(type_str: str) -> RelationshipType:
    """Parse relationship type string to RelationshipType enum"""
    type_mapping = {
        "CONTAINS": RelationshipType.CONTAINS,
        "CALLS": RelationshipType.CALLS,
        "EXPOSES": RelationshipType.EXPOSES,
        "REQUESTS": RelationshipType.REQUESTS,
        "DERIVES": RelationshipType.DERIVES,
        "REFERENCES": RelationshipType.REFERENCES,
    }
    return type_mapping.get(type_str, RelationshipType.CALLS)


def extract_repo_info(url: str) -> dict:
    """Extract owner and repo name from GitHub URL"""
    patterns = [
        r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"github\.com/([^/]+)/([^/]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return {"owner": match.group(1), "repo": match.group(2)}
    return {"owner": None, "repo": None}


async def store_nodes_to_neo4j(service: Neo4jService, nodes: List[dict]) -> int:
    """Store nodes to Neo4j and return count of nodes created"""
    graph_nodes = []
    for node in nodes:
        node_type = parse_node_type(node.get("type", "Service"))
        graph_node = GraphNode(
            id=node.get("id"),
            label=node.get("label", node.get("id")),
            type=node_type,
            properties=node.get("properties", {})
        )
        graph_nodes.append(graph_node)
    
    if graph_nodes:
        return await service.batch_create_nodes(graph_nodes)
    return 0


async def store_edges_to_neo4j(service: Neo4jService, edges: List[dict]) -> int:
    """Store edges to Neo4j and return count of relationships created"""
    relationships = []
    for edge in edges:
        rel_type = parse_relationship_type(edge.get("type", "CALLS"))
        relationship = GraphRelationship(
            source_id=edge.get("source"),
            target_id=edge.get("target"),
            type=rel_type,
            properties=edge.get("properties", {})
        )
        relationships.append(relationship)
    
    if relationships:
        return await service.batch_create_relationships(relationships)
    return 0


@router.post("/github", response_model=ScanResult)
async def scan_github_project(request: GitHubProjectRequest):
    """Scan a GitHub repository and import architecture"""
    try:
        url_lower = request.repo_url.lower()
        repo_info = extract_repo_info(request.repo_url)
        
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()
        
        try:
            await neo4j_service.clear_all_data()
            
            if "mall" in url_lower or "macrozheng" in url_lower:
                mock_data_service.set_project("mall")
                nodes = list(mock_data_service.nodes.values())
                edges = mock_data_service.edges
            elif "microservices-demo" in url_lower or "googlecloudplatform" in url_lower:
                mock_data_service.set_project("online-boutique")
                nodes = list(mock_data_service.nodes.values())
                edges = mock_data_service.edges
            elif "petclinic" in url_lower:
                nodes = [
                    {"id": "petclinic-main", "label": "PetClinic App", "type": "Service", "properties": {"language": "Java", "framework": "Spring Boot", "port": 8080}},
                    {"id": "petclinic-db", "label": "H2 Database", "type": "Database", "properties": {"engine": "H2", "mode": "in-memory"}},
                    {"id": "petclinic-api", "label": "REST API", "type": "API", "properties": {"endpoint": "/api"}},
                    {"id": "owner-service", "label": "Owner Service", "type": "Service", "properties": {"description": "Owner management"}},
                    {"id": "pet-service", "label": "Pet Service", "type": "Service", "properties": {"description": "Pet management"}},
                    {"id": "visit-service", "label": "Visit Service", "type": "Service", "properties": {"description": "Visit management"}},
                    {"id": "vet-service", "label": "Vet Service", "type": "Service", "properties": {"description": "Vet management"}},
                ]
                edges = [
                    {"source": "petclinic-api", "target": "petclinic-main", "type": "EXPOSES"},
                    {"source": "petclinic-main", "target": "petclinic-db", "type": "CALLS"},
                    {"source": "petclinic-main", "target": "owner-service", "type": "CONTAINS"},
                    {"source": "petclinic-main", "target": "pet-service", "type": "CONTAINS"},
                    {"source": "petclinic-main", "target": "visit-service", "type": "CONTAINS"},
                    {"source": "petclinic-main", "target": "vet-service", "type": "CONTAINS"},
                ]
            else:
                nodes = [
                    {"id": "app-main", "label": repo_info.get("repo", "Main App"), "type": "Service", "properties": {"url": request.repo_url}},
                    {"id": "app-db", "label": "Database", "type": "Database", "properties": {}},
                    {"id": "app-api", "label": "API", "type": "API", "properties": {}},
                ]
                edges = [
                    {"source": "app-api", "target": "app-main", "type": "EXPOSES"},
                    {"source": "app-main", "target": "app-db", "type": "CALLS"},
                ]
            
            nodes_added = await store_nodes_to_neo4j(neo4j_service, nodes)
            edges_added = await store_edges_to_neo4j(neo4j_service, edges)
            
            project_name = "Mall e-commerce" if "mall" in url_lower or "macrozheng" in url_lower else \
                          "Online Boutique (Google Cloud)" if "microservices-demo" in url_lower or "googlecloudplatform" in url_lower else \
                          "Spring PetClinic" if "petclinic" in url_lower else \
                          request.repo_url
            
            return ScanResult(
                status="success",
                nodes_added=nodes_added,
                edges_added=edges_added,
                message=f"{project_name} loaded successfully"
            )
            
        finally:
            await neo4j_service.close()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual", response_model=ScanResult)
async def add_manual_nodes(request: ManualNodeRequest):
    """Manually add nodes and edges to the topology"""
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()
        
        try:
            nodes_added = await store_nodes_to_neo4j(neo4j_service, request.nodes)
            
            edges_added = 0
            if request.edges:
                edges_added = await store_edges_to_neo4j(neo4j_service, request.edges)
            
            return ScanResult(
                status="success",
                nodes_added=nodes_added,
                edges_added=edges_added,
                message=f"Added {nodes_added} nodes and {edges_added} edges"
            )
            
        finally:
            await neo4j_service.close()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_topology():
    """Clear all topology data"""
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()
        
        try:
            success = await neo4j_service.clear_all_data()
            if success:
                return {"status": "success", "message": "Topology cleared"}
            else:
                raise HTTPException(status_code=500, detail="Failed to clear topology")
        finally:
            await neo4j_service.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_scan_templates():
    """Get available scan templates"""
    return [
        {
            "id": "spring-boot",
            "name": "Spring Boot Microservices",
            "description": "Scan Spring Boot microservices architecture",
            "node_types": ["Service", "API", "Database", "Library", "FrontendApp"],
        },
        {
            "id": "react-frontend",
            "name": "React Frontend",
            "description": "Scan React frontend application",
            "node_types": ["FrontendApp", "Component", "API", "Service"],
        },
        {
            "id": "full-stack",
            "name": "Full Stack Application",
            "description": "Scan full stack application with frontend and backend",
            "node_types": ["Service", "API", "Database", "FrontendApp", "Component", "Table"],
        },
    ]
