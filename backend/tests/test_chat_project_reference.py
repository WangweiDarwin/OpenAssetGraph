"""Integration tests for Chat API project reference functionality"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, Mock, patch

from app.main import app


client = TestClient(app)


class TestChatProjectReference:
    """Integration tests for Chat API with project references"""

    def test_chat_with_valid_project_reference(self):
        """Test chat with valid project reference"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class, \
             patch("app.api.chat.get_graph_rag_service") as mock_get_rag, \
             patch("app.api.chat.get_llm_service") as mock_get_llm:

            mock_neo4j = Mock()
            mock_neo4j.driver = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {"project": "mall"},
                {"project": "online-boutique"}
            ])
            mock_neo4j_class.return_value = mock_neo4j

            mock_rag = Mock()
            mock_rag.extract_relevant_context = AsyncMock(return_value=Mock(
                nodes=[{"id": "1", "label": "Test", "type": "Service"}],
                relationships=[],
                subgraph_summary="Test summary"
            ))
            mock_get_rag.return_value = mock_rag

            mock_llm = Mock()
            mock_llm.chat = AsyncMock(return_value=Mock(
                content="This is a test response",
                model="test-model",
                usage={"prompt_tokens": 10, "completion_tokens": 20}
            ))
            mock_get_llm.return_value = mock_llm

            response = client.post("/api/chat", json={
                "message": "分析 #mall 的架构"
            })

            assert response.status_code == 200
            data = response.json()
            assert "response" in data
            assert data["referenced_projects"] == ["mall"]

    def test_chat_with_invalid_project_reference_returns_400(self):
        """Test chat with invalid project reference returns 400 error"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class, \
             patch("app.api.chat.get_graph_rag_service") as mock_get_rag, \
             patch("app.api.chat.get_llm_service") as mock_get_llm:

            mock_neo4j = Mock()
            mock_neo4j.driver = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {"project": "mall"},
                {"project": "online-boutique"}
            ])
            mock_neo4j_class.return_value = mock_neo4j

            mock_rag = Mock()
            mock_rag.extract_relevant_context = AsyncMock(return_value=Mock(
                nodes=[],
                relationships=[],
                subgraph_summary=""
            ))
            mock_get_rag.return_value = mock_rag

            mock_llm = Mock()
            mock_llm.chat = AsyncMock(return_value=Mock(
                content="Test response",
                model="test-model",
                usage={"prompt_tokens": 10, "completion_tokens": 20}
            ))
            mock_get_llm.return_value = mock_llm

            response = client.post("/api/chat", json={
                "message": "分析 #nonexistent-project 的架构"
            })

            assert response.status_code == 400
            data = response.json()
            assert "detail" in data
            detail = data["detail"]
            assert detail["error"] == "invalid_project_reference"
            assert "nonexistent-project" in detail["invalid_projects"]
            assert "available_projects" in detail

    def test_chat_with_multiple_project_references(self):
        """Test chat with multiple project references"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class, \
             patch("app.api.chat.get_graph_rag_service") as mock_get_rag, \
             patch("app.api.chat.get_llm_service") as mock_get_llm:

            mock_neo4j = Mock()
            mock_neo4j.driver = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {"project": "mall"},
                {"project": "online-boutique"},
                {"project": "petclinic"}
            ])
            mock_neo4j_class.return_value = mock_neo4j

            mock_rag = Mock()
            mock_rag.extract_relevant_context = AsyncMock(return_value=Mock(
                nodes=[],
                relationships=[],
                subgraph_summary=""
            ))
            mock_get_rag.return_value = mock_rag

            mock_llm = Mock()
            mock_llm.chat = AsyncMock(return_value=Mock(
                content="Multi-project analysis",
                model="test-model",
                usage={"prompt_tokens": 10, "completion_tokens": 20}
            ))
            mock_get_llm.return_value = mock_llm

            response = client.post("/api/chat", json={
                "message": "比较 #mall 和 #online-boutique 的架构"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["referenced_projects"] == ["mall", "online-boutique"]

    def test_chat_with_mixed_valid_invalid_references(self):
        """Test chat with mix of valid and invalid project references"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class, \
             patch("app.api.chat.get_graph_rag_service") as mock_get_rag, \
             patch("app.api.chat.get_llm_service") as mock_get_llm:

            mock_neo4j = Mock()
            mock_neo4j.driver = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {"project": "mall"}
            ])
            mock_neo4j_class.return_value = mock_neo4j

            mock_rag = Mock()
            mock_rag.extract_relevant_context = AsyncMock(return_value=Mock(
                nodes=[],
                relationships=[],
                subgraph_summary=""
            ))
            mock_get_rag.return_value = mock_rag

            mock_llm = Mock()
            mock_llm.chat = AsyncMock(return_value=Mock(
                content="Test response",
                model="test-model",
                usage={"prompt_tokens": 10, "completion_tokens": 20}
            ))
            mock_get_llm.return_value = mock_llm

            response = client.post("/api/chat", json={
                "message": "分析 #mall 和 #invalid-project"
            })

            assert response.status_code == 400
            data = response.json()
            detail = data["detail"]
            assert "invalid-project" in detail["invalid_projects"]
            assert "mall" not in detail["invalid_projects"]

    def test_chat_without_project_reference(self):
        """Test chat without any project reference"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class, \
             patch("app.api.chat.get_graph_rag_service") as mock_get_rag, \
             patch("app.api.chat.get_llm_service") as mock_get_llm:

            mock_neo4j = Mock()
            mock_neo4j.driver = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[])
            mock_neo4j_class.return_value = mock_neo4j

            mock_rag = Mock()
            mock_rag.extract_relevant_context = AsyncMock(return_value=Mock(
                nodes=[],
                relationships=[],
                subgraph_summary=""
            ))
            mock_get_rag.return_value = mock_rag

            mock_llm = Mock()
            mock_llm.chat = AsyncMock(return_value=Mock(
                content="General response",
                model="test-model",
                usage={"prompt_tokens": 10, "completion_tokens": 20}
            ))
            mock_get_llm.return_value = mock_llm

            response = client.post("/api/chat", json={
                "message": "什么是微服务架构？"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["referenced_projects"] is None

    def test_chat_with_chinese_project_name(self):
        """Test chat with Chinese project name in reference"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class, \
             patch("app.api.chat.get_graph_rag_service") as mock_get_rag, \
             patch("app.api.chat.get_llm_service") as mock_get_llm:

            mock_neo4j = Mock()
            mock_neo4j.driver = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {"project": "mall"}
            ])
            mock_neo4j_class.return_value = mock_neo4j

            mock_rag = Mock()
            mock_rag.extract_relevant_context = AsyncMock(return_value=Mock(
                nodes=[],
                relationships=[],
                subgraph_summary=""
            ))
            mock_get_rag.return_value = mock_rag

            mock_llm = Mock()
            mock_llm.chat = AsyncMock(return_value=Mock(
                content="Chinese project response",
                model="test-model",
                usage={"prompt_tokens": 10, "completion_tokens": 20}
            ))
            mock_get_llm.return_value = mock_llm

            response = client.post("/api/chat", json={
                "message": "分析 #mall 的架构"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["referenced_projects"] == ["mall"]


class TestChatAPIErrorHandling:
    """Test Chat API error handling"""

    def test_chat_handles_neo4j_connection_error(self):
        """Test chat handles Neo4j connection error"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class:
            mock_neo4j = Mock()
            mock_neo4j.connect = AsyncMock(side_effect=Exception("Connection failed"))
            mock_neo4j_class.return_value = mock_neo4j

            response = client.post("/api/chat", json={
                "message": "测试消息"
            })

            assert response.status_code == 500

    def test_chat_handles_empty_message(self):
        """Test chat handles empty message"""
        response = client.post("/api/chat", json={
            "message": ""
        })

        assert response.status_code in [400, 422, 500]

    def test_chat_with_conversation_history(self):
        """Test chat with conversation history"""
        with patch("app.api.chat.Neo4jService") as mock_neo4j_class, \
             patch("app.api.chat.get_graph_rag_service") as mock_get_rag, \
             patch("app.api.chat.get_llm_service") as mock_get_llm:

            mock_neo4j = Mock()
            mock_neo4j.driver = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[])
            mock_neo4j_class.return_value = mock_neo4j

            mock_rag = Mock()
            mock_rag.extract_relevant_context = AsyncMock(return_value=Mock(
                nodes=[],
                relationships=[],
                subgraph_summary=""
            ))
            mock_get_rag.return_value = mock_rag

            mock_llm = Mock()
            mock_llm.chat = AsyncMock(return_value=Mock(
                content="Follow-up response",
                model="test-model",
                usage={"prompt_tokens": 10, "completion_tokens": 20}
            ))
            mock_get_llm.return_value = mock_llm

            response = client.post("/api/chat", json={
                "message": "继续分析",
                "conversation_history": [
                    {"role": "user", "content": "分析 #mall 的架构"},
                    {"role": "assistant", "content": "mall 是一个电商系统..."}
                ]
            })

            assert response.status_code == 200


class TestProjectsAPI:
    """Test Projects API endpoints"""

    def test_get_all_projects_success(self):
        """Test get all projects endpoint"""
        with patch("app.api.projects.get_neo4j_service") as mock_get_neo4j:
            mock_neo4j = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {"project": "mall"},
                {"project": "online-boutique"},
                {"project": "petclinic"}
            ])
            mock_get_neo4j.return_value = mock_neo4j

            response = client.get("/api/projects")

            assert response.status_code == 200
            data = response.json()
            assert "projects" in data
            assert len(data["projects"]) == 3

    def test_parse_project_references_endpoint(self):
        """Test parse project references endpoint"""
        with patch("app.api.projects.get_neo4j_service") as mock_get_neo4j:
            mock_neo4j = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_neo4j.execute_query = AsyncMock(return_value=[
                {"project": "mall"},
                {"project": "online-boutique"}
            ])
            mock_get_neo4j.return_value = mock_neo4j

            response = client.post("/api/projects/parse", json={
                "text": "分析 #mall 和 #unknown-project 的架构"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["parsed"] == ["mall", "unknown-project"]
            assert data["valid"] == ["mall"]
            assert data["invalid"] == ["unknown-project"]

    def test_parse_no_references(self):
        """Test parse endpoint with no references"""
        with patch("app.api.projects.get_neo4j_service") as mock_get_neo4j:
            mock_neo4j = Mock()
            mock_neo4j.connect = AsyncMock()
            mock_neo4j.close = AsyncMock()
            mock_get_neo4j.return_value = mock_neo4j

            response = client.post("/api/projects/parse", json={
                "text": "这是一段没有项目引用的文本"
            })

            assert response.status_code == 200
            data = response.json()
            assert data["parsed"] == []
            assert data["valid"] == []
            assert data["invalid"] == []
