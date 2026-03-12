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
