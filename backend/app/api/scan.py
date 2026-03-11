"""Project scan API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio
import re

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


@router.post("/github", response_model=ScanResult)
async def scan_github_project(request: GitHubProjectRequest):
    """Scan a GitHub repository and import architecture"""
    try:
        url_lower = request.repo_url.lower()
        repo_info = extract_repo_info(request.repo_url)
        
        if "mall" in url_lower or "macrozheng" in url_lower:
            mock_data_service.set_project("mall")
            return ScanResult(
                status="success",
                nodes_added=len(mock_data_service.nodes),
                edges_added=len(mock_data_service.edges),
                message="Mall e-commerce project loaded successfully"
            )
        
        if "microservices-demo" in url_lower or "googlecloudplatform" in url_lower:
            mock_data_service.set_project("online-boutique")
            return ScanResult(
                status="success",
                nodes_added=len(mock_data_service.nodes),
                edges_added=len(mock_data_service.edges),
                message="Online Boutique (Google Cloud) loaded successfully"
            )
        
        if "petclinic" in url_lower:
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
            await mock_data_service.clear_project()
            nodes_added = await mock_data_service.add_nodes(nodes)
            edges_added = await mock_data_service.add_edges(edges)
            return ScanResult(
                status="success",
                nodes_added=nodes_added,
                edges_added=edges_added,
                message="Spring PetClinic loaded successfully"
            )
        
        nodes = [
            {"id": "app-main", "label": repo_info.get("repo", "Main App"), "type": "Service", "properties": {"url": request.repo_url}},
            {"id": "app-db", "label": "Database", "type": "Database", "properties": {}},
            {"id": "app-api", "label": "API", "type": "API", "properties": {}},
        ]
        edges = [
            {"source": "app-api", "target": "app-main", "type": "EXPOSES"},
            {"source": "app-main", "target": "app-db", "type": "CALLS"},
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
