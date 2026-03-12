"""Unit tests for project reference parser"""
import pytest
from unittest.mock import AsyncMock, Mock, patch

from app.services.project_reference import ProjectReferenceParser
from app.services.graph_service import Neo4jService


class TestParseReferences:
    """Test parse_references method"""

    def test_single_project_reference(self):
        """Test parsing a single project reference"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("分析 #mall 的架构")
        assert result == ["mall"]

    def test_multiple_project_references(self):
        """Test parsing multiple project references"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("分析 #mall 和 #online-boutique 的架构")
        assert result == ["mall", "online-boutique"]

    def test_no_project_reference(self):
        """Test parsing text with no project references"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("分析整体架构")
        assert result == []

    def test_empty_text(self):
        """Test parsing empty text"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("")
        assert result == []

    def test_none_text(self):
        """Test parsing None text"""
        parser = ProjectReferenceParser()
        result = parser.parse_references(None)
        assert result == []

    def test_duplicate_project_references(self):
        """Test that duplicate references are deduplicated"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("#mall 和 #mall 是同一个项目")
        assert result == ["mall"]

    def test_special_characters_in_project_name(self):
        """Test project names with hyphens"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("分析 #online-boutique 项目")
        assert result == ["online-boutique"]

    def test_project_name_with_underscore(self):
        """Test project names with underscores"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("分析 #my_project_name 项目")
        assert result == ["my_project_name"]

    def test_project_name_with_numbers(self):
        """Test project names with numbers"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("分析 #project123 项目")
        assert result == ["project123"]

    def test_chinese_text_with_references(self):
        """Test Chinese text with project references"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("请帮我分析 #mall 和 #online-boutique 的架构设计")
        assert result == ["mall", "online-boutique"]

    def test_hash_without_project_name(self):
        """Test hash symbol at end of text"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("这是一个测试#")
        assert result == []

    def test_multiple_hashes(self):
        """Test multiple consecutive hashes"""
        parser = ProjectReferenceParser()
        result = parser.parse_references("##mall 和 ###online-boutique")
        assert result == ["mall", "online-boutique"]


class TestValidateProjectReferences:
    """Test validate_project_references method"""

    @pytest.mark.asyncio
    async def test_validate_valid_projects(self):
        """Test validating valid project references"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[
            {"project": "mall"},
            {"project": "online-boutique"},
            {"project": "petclinic"}
        ])

        parser = ProjectReferenceParser(mock_neo4j)
        valid, invalid = await parser.validate_project_references(["mall", "online-boutique"])

        assert valid == ["mall", "online-boutique"]
        assert invalid == []

    @pytest.mark.asyncio
    async def test_validate_invalid_projects(self):
        """Test validating invalid project references"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[
            {"project": "mall"},
            {"project": "online-boutique"}
        ])

        parser = ProjectReferenceParser(mock_neo4j)
        valid, invalid = await parser.validate_project_references(["mall", "nonexistent"])

        assert valid == ["mall"]
        assert invalid == ["nonexistent"]

    @pytest.mark.asyncio
    async def test_validate_all_invalid_projects(self):
        """Test validating all invalid project references"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[
            {"project": "mall"}
        ])

        parser = ProjectReferenceParser(mock_neo4j)
        valid, invalid = await parser.validate_project_references(["unknown1", "unknown2"])

        assert valid == []
        assert invalid == ["unknown1", "unknown2"]

    @pytest.mark.asyncio
    async def test_validate_empty_list(self):
        """Test validating empty project list"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[])

        parser = ProjectReferenceParser(mock_neo4j)
        valid, invalid = await parser.validate_project_references([])

        assert valid == []
        assert invalid == []

    @pytest.mark.asyncio
    async def test_validate_without_neo4j_service(self):
        """Test validating without Neo4j service raises error"""
        parser = ProjectReferenceParser(None)

        with pytest.raises(RuntimeError, match="Neo4j service not initialized"):
            await parser.validate_project_references(["mall"])

    @pytest.mark.asyncio
    async def test_validate_without_driver(self):
        """Test validating without Neo4j driver raises error"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = None

        parser = ProjectReferenceParser(mock_neo4j)

        with pytest.raises(RuntimeError, match="Not connected to Neo4j"):
            await parser.validate_project_references(["mall"])


class TestGetAllProjects:
    """Test get_all_projects method"""

    @pytest.mark.asyncio
    async def test_get_all_projects_success(self):
        """Test getting all projects successfully"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[
            {"project": "mall"},
            {"project": "online-boutique"},
            {"project": "petclinic"}
        ])

        parser = ProjectReferenceParser(mock_neo4j)
        projects = await parser.get_all_projects()

        assert projects == ["mall", "online-boutique", "petclinic"]

    @pytest.mark.asyncio
    async def test_get_all_projects_empty(self):
        """Test getting all projects when none exist"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[])

        parser = ProjectReferenceParser(mock_neo4j)
        projects = await parser.get_all_projects()

        assert projects == []

    @pytest.mark.asyncio
    async def test_get_all_projects_filters_none(self):
        """Test that None project values are filtered out"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[
            {"project": "mall"},
            {"project": None},
            {"project": "online-boutique"}
        ])

        parser = ProjectReferenceParser(mock_neo4j)
        projects = await parser.get_all_projects()

        assert projects == ["mall", "online-boutique"]

    @pytest.mark.asyncio
    async def test_get_all_projects_without_neo4j_service(self):
        """Test getting projects without Neo4j service raises error"""
        parser = ProjectReferenceParser(None)

        with pytest.raises(RuntimeError, match="Neo4j service not initialized"):
            await parser.get_all_projects()

    @pytest.mark.asyncio
    async def test_get_all_projects_without_driver(self):
        """Test getting projects without Neo4j driver raises error"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = None

        parser = ProjectReferenceParser(mock_neo4j)

        with pytest.raises(RuntimeError, match="Not connected to Neo4j"):
            await parser.get_all_projects()

    @pytest.mark.asyncio
    async def test_get_all_projects_handles_exception(self):
        """Test that exceptions are handled and empty list returned"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(side_effect=Exception("Connection error"))

        parser = ProjectReferenceParser(mock_neo4j)
        projects = await parser.get_all_projects()

        assert projects == []


class TestParseAndValidate:
    """Test parse_and_validate method"""

    @pytest.mark.asyncio
    async def test_parse_and_validate_with_valid_references(self):
        """Test parse and validate with valid references"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[
            {"project": "mall"},
            {"project": "online-boutique"}
        ])

        parser = ProjectReferenceParser(mock_neo4j)
        result = await parser.parse_and_validate("分析 #mall 和 #online-boutique")

        assert result["parsed"] == ["mall", "online-boutique"]
        assert result["valid"] == ["mall", "online-boutique"]
        assert result["invalid"] == []

    @pytest.mark.asyncio
    async def test_parse_and_validate_with_invalid_references(self):
        """Test parse and validate with invalid references"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()
        mock_neo4j.execute_query = AsyncMock(return_value=[
            {"project": "mall"}
        ])

        parser = ProjectReferenceParser(mock_neo4j)
        result = await parser.parse_and_validate("分析 #mall 和 #unknown")

        assert result["parsed"] == ["mall", "unknown"]
        assert result["valid"] == ["mall"]
        assert result["invalid"] == ["unknown"]

    @pytest.mark.asyncio
    async def test_parse_and_validate_no_references(self):
        """Test parse and validate with no references"""
        mock_neo4j = Mock(spec=Neo4jService)
        mock_neo4j.driver = Mock()

        parser = ProjectReferenceParser(mock_neo4j)
        result = await parser.parse_and_validate("分析整体架构")

        assert result["parsed"] == []
        assert result["valid"] == []
        assert result["invalid"] == []
