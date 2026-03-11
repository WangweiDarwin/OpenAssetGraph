"""Project scan API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio

from ..services.mock_data import mock_data_service

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


@router.post("/github", response_model=ScanResult)
async def scan_github_project(request: GitHubProjectRequest):
    """Scan a GitHub repository and import architecture"""
    try:
        if "mall" in request.repo_url.lower() or "macrozheng" in request.repo_url.lower():
            mock_data_service.set_project("mall")
            return ScanResult(
                status="success",
                nodes_added=len(mock_data_service.nodes),
                edges_added=len(mock_data_service.edges),
                message="Mall e-commerce project loaded successfully"
            )
        
        nodes = [
            {"id": "svc_main", "label": "Main Service", "type": "Service", "properties": {"language": "Unknown"}},
            {"id": "db_main", "label": "Main Database", "type": "Database", "properties": {"engine": "Unknown"}},
            {"id": "api_main", "label": "Main API", "type": "API", "properties": {}},
        ]
        edges = [
            {"source": "api_main", "target": "svc_main", "type": "EXPOSES", "properties": {}},
            {"source": "svc_main", "target": "db_main", "type": "CALLS", "properties": {}},
        ]
        
        await mock_data_service.clear_project()
        nodes_added = await mock_data_service.add_nodes(nodes)
        edges_added = await mock_data_service.add_edges(edges)
        
        return ScanResult(
            status="success",
            nodes_added=nodes_added,
            edges_added=edges_added,
            message=f"Scanned {request.repo_url} - basic structure imported"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/manual", response_model=ScanResult)
async def add_manual_nodes(request: ManualNodeRequest):
    """Manually add nodes and edges to the topology"""
    try:
        nodes_added = await mock_data_service.add_nodes(request.nodes)
        edges_added = 0
        if request.edges:
            edges_added = await mock_data_service.add_edges(request.edges)
        
        return ScanResult(
            status="success",
            nodes_added=nodes_added,
            edges_added=edges_added,
            message=f"Added {nodes_added} nodes and {edges_added} edges"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_topology():
    """Clear all topology data"""
    await mock_data_service.clear_project()
    return {"status": "success", "message": "Topology cleared"}


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
