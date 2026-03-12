"""Project reference parser service"""
import logging
import re
from typing import Any

from .graph_service import Neo4jService

logger = logging.getLogger(__name__)


class ProjectReferenceParser:
    """Parser for project references in text using #project-name syntax"""

    PROJECT_REFERENCE_PATTERN = re.compile(r'#([\w\-]+)#?')

    def __init__(self, neo4j_service: Neo4jService | None = None):
        self.neo4j_service = neo4j_service

    def parse_references(self, text: str) -> list[str]:
        """
        Parse project references from text.

        Args:
            text: Input text containing project references like "#mall#" or "#online-boutique#"
                  The trailing # is optional but recommended for clarity.

        Returns:
            List of project names found in the text (without the # prefix)

        Examples:
            >>> parser = ProjectReferenceParser()
            >>> parser.parse_references("分析 #mall# 和 #online-boutique# 的架构")
            ['mall', 'online-boutique']
            >>> parser.parse_references("请分析 #mall 的架构")
            ['mall']
        """
        if not text:
            return []

        matches = self.PROJECT_REFERENCE_PATTERN.findall(text)
        unique_projects = list(dict.fromkeys(matches))

        logger.info(f"Parsed project references from text: {unique_projects}")
        return unique_projects

    async def validate_project_references(self, project_names: list[str]) -> tuple[list[str], list[str]]:
        """
        Validate if project references exist in Neo4j database.

        Args:
            project_names: List of project names to validate

        Returns:
            Tuple of (valid_projects, invalid_projects)
        """
        if not self.neo4j_service:
            raise RuntimeError("Neo4j service not initialized")

        if not self.neo4j_service.driver:
            raise RuntimeError("Not connected to Neo4j")

        all_projects = await self.get_all_projects()

        valid_projects = []
        invalid_projects = []

        for project_name in project_names:
            if project_name in all_projects:
                valid_projects.append(project_name)
            else:
                invalid_projects.append(project_name)

        logger.info(f"Validated projects - valid: {valid_projects}, invalid: {invalid_projects}")
        return valid_projects, invalid_projects

    async def get_all_projects(self) -> list[str]:
        """
        Get all distinct project names from Neo4j database.

        Returns:
            List of unique project names
        """
        if not self.neo4j_service:
            raise RuntimeError("Neo4j service not initialized")

        if not self.neo4j_service.driver:
            raise RuntimeError("Not connected to Neo4j")

        query = """
        MATCH (n)
        WHERE n.project IS NOT NULL
        RETURN DISTINCT n.project AS project
        ORDER BY project
        """

        try:
            results = await self.neo4j_service.execute_query(query)
            projects = [record["project"] for record in results if record.get("project")]
            logger.info(f"Retrieved {len(projects)} projects from database: {projects}")
            return projects
        except Exception as e:
            logger.error(f"Failed to get projects from Neo4j: {e}")
            return []

    async def parse_and_validate(self, text: str) -> dict[str, Any]:
        """
        Parse project references from text and validate them.

        Args:
            text: Input text containing project references

        Returns:
            Dictionary with parsed, valid, and invalid project lists
        """
        parsed_projects = self.parse_references(text)

        if not parsed_projects:
            return {
                "parsed": [],
                "valid": [],
                "invalid": []
            }

        valid_projects, invalid_projects = await self.validate_project_references(parsed_projects)

        return {
            "parsed": parsed_projects,
            "valid": valid_projects,
            "invalid": invalid_projects
        }
