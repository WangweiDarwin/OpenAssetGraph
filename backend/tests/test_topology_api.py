"""Test topology API"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, Mock
from app.main import app


client = TestClient(app)


@pytest.fixture
def mock_neo4j_driver():
    """Mock Neo4j driver"""
    driver = AsyncMock()
    return driver


@pytest.fixture
def mock_topology_service():
    """Mock topology service"""
    service = Mock()
    return service


class TestTopologyAPI:
    """Test topology API endpoints"""
    
    def test_get_topology_success(self):
        """Test get topology endpoint"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_full_topology = AsyncMock(return_value={
                "nodes": [
                    {"id": "1", "label": "UserService", "type": "Service"},
                    {"id": "2", "label": "OrderService", "type": "Service"}
                ],
                "edges": [
                    {"source": "1", "target": "2", "type": "CALLS"}
                ],
                "node_count": 2,
                "edge_count": 1
            })
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology")
            
            assert response.status_code == 200
            data = response.json()
            assert "nodes" in data
            assert "edges" in data
            assert data["node_count"] == 2
            assert data["edge_count"] == 1
    
    def test_search_nodes_success(self):
        """Test search nodes endpoint"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.search_nodes = AsyncMock(return_value=[
                {"id": "1", "label": "UserService", "type": "Service"}
            ])
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology/search?q=User")
            
            assert response.status_code == 200
            data = response.json()
            assert data["query"] == "User"
            assert len(data["results"]) == 1
            assert data["count"] == 1
    
    def test_get_node_success(self):
        """Test get node details endpoint"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_node_details = AsyncMock(return_value={
                "id": "1",
                "label": "UserService",
                "type": "Service",
                "properties": {},
                "outgoing_relationships": [],
                "incoming_relationships": []
            })
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology/nodes/1")
            
            assert response.status_code == 200
            data = response.json()
            assert data["id"] == "1"
            assert data["label"] == "UserService"
    
    def test_get_node_not_found(self):
        """Test get node not found"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_node_details = AsyncMock(return_value=None)
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology/nodes/nonexistent")
            
            assert response.status_code == 404
    
    def test_find_path_success(self):
        """Test find path endpoint"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.find_path = AsyncMock(return_value=[
                {"id": "1", "label": "UserService", "type": "Service"},
                {"id": "2", "label": "OrderService", "type": "Service"}
            ])
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology/path?start=1&end=2")
            
            assert response.status_code == 200
            data = response.json()
            assert data["start_node_id"] == "1"
            assert data["end_node_id"] == "2"
            assert len(data["path"]) == 2
    
    def test_find_path_not_found(self):
        """Test find path not found"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.find_path = AsyncMock(return_value=[])
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology/path?start=1&end=999")
            
            assert response.status_code == 404
    
    def test_get_node_relationships_success(self):
        """Test get node relationships endpoint"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_node_relationships = AsyncMock(return_value=[
                {
                    "type": "CALLS",
                    "source_id": "1",
                    "target_id": "2",
                    "properties": {}
                }
            ])
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology/nodes/1/relationships")
            
            assert response.status_code == 200
            data = response.json()
            assert data["node_id"] == "1"
            assert len(data["relationships"]) == 1
            assert data["count"] == 1
    
    def test_get_topology_stats_success(self):
        """Test get topology stats endpoint"""
        with patch('app.api.topology.get_topology_service') as mock_get_service:
            mock_service = Mock()
            mock_service.get_full_topology = AsyncMock(return_value={
                "nodes": [
                    {"id": "1", "label": "UserService", "type": "Service"},
                    {"id": "2", "label": "OrderService", "type": "Service"},
                    {"id": "3", "label": "users", "type": "Table"}
                ],
                "edges": [],
                "node_count": 3,
                "edge_count": 0
            })
            mock_service.neo4j_service.connect = AsyncMock()
            mock_service.neo4j_service.close = AsyncMock()
            mock_get_service.return_value = mock_service
            
            response = client.get("/api/topology/stats")
            
            assert response.status_code == 200
            data = response.json()
            assert data["total_nodes"] == 3
            assert data["total_edges"] == 0
            assert "node_types" in data
