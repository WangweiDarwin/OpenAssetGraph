"""Projects API routes"""
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ..core.config import settings
from ..services.graph_service import Neo4jService
from ..services.project_reference import ProjectReferenceParser

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/projects", tags=["projects"])


def get_neo4j_service() -> Neo4jService:
    """Get Neo4j service instance"""
    return Neo4jService(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )


def get_project_parser() -> ProjectReferenceParser:
    """Get project reference parser instance"""
    neo4j_service = get_neo4j_service()
    return ProjectReferenceParser(neo4j_service)


class ProjectsResponse(BaseModel):
    """Projects list response model"""
    projects: list[str]


class ProjectReferenceRequest(BaseModel):
    """Project reference parsing request"""
    text: str


class ProjectReferenceResponse(BaseModel):
    """Project reference parsing response"""
    parsed: list[str]
    valid: list[str]
    invalid: list[str]


class ProjectStatsResponse(BaseModel):
    """Project statistics response"""
    node_count: int
    edge_count: int
    last_scanned: str
    node_types: dict[str, int]


@router.get("", response_model=ProjectsResponse)
async def get_all_projects():
    """
    Get all projects from the database.

    Returns a list of all distinct project names stored in Neo4j.
    """
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()

        try:
            parser = ProjectReferenceParser(neo4j_service)
            projects = await parser.get_all_projects()

            return ProjectsResponse(projects=projects)
        finally:
            await neo4j_service.close()

    except Exception as e:
        logger.error(f"Failed to get projects: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.post("/parse", response_model=ProjectReferenceResponse)
async def parse_project_references(request: ProjectReferenceRequest):
    """
    Parse project references from text and validate them.

    Supports #project-name syntax in text.
    Returns parsed, valid, and invalid project lists.
    """
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()

        try:
            parser = ProjectReferenceParser(neo4j_service)
            result = await parser.parse_and_validate(request.text)

            return ProjectReferenceResponse(
                parsed=result["parsed"],
                valid=result["valid"],
                invalid=result["invalid"]
            )
        finally:
            await neo4j_service.close()

    except Exception as e:
        logger.error(f"Failed to parse project references: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


@router.get("/{project_name}/stats", response_model=ProjectStatsResponse)
async def get_project_stats(project_name: str):
    """
    Get statistics for a specific project.

    Returns node count, edge count, last scanned time, and node type distribution.
    """
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()

        try:
            node_count_query = """
            MATCH (n {project: $project_name})
            RETURN count(n) as count
            """
            node_result = await neo4j_service.execute_query(node_count_query, {"project_name": project_name})
            node_count = node_result[0]["count"] if node_result else 0

            edge_count_query = """
            MATCH ()-[r]->() WHERE startNode(r).project = $project_name OR endNode(r).project = $project_name
            RETURN count(r) as count
            """
            edge_result = await neo4j_service.execute_query(edge_count_query, {"project_name": project_name})
            edge_count = edge_result[0]["count"] if edge_result else 0

            node_types_query = """
            MATCH (n {project: $project_name})
            RETURN n.type as type, count(n) as count
            ORDER BY count DESC
            """
            types_result = await neo4j_service.execute_query(node_types_query, {"project_name": project_name})
            node_types = {r["type"]: r["count"] for r in types_result if r.get("type")}

            last_scanned_query = """
            MATCH (n {project: $project_name})
            RETURN n.scanned_at as scanned_at
            ORDER BY n.scanned_at DESC
            LIMIT 1
            """
            scanned_result = await neo4j_service.execute_query(last_scanned_query, {"project_name": project_name})
            last_scanned = scanned_result[0]["scanned_at"] if scanned_result and scanned_result[0].get("scanned_at") else "Unknown"

            return ProjectStatsResponse(
                node_count=node_count,
                edge_count=edge_count,
                last_scanned=last_scanned,
                node_types=node_types
            )
        finally:
            await neo4j_service.close()

    except Exception as e:
        logger.error(f"Failed to get project stats: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e
