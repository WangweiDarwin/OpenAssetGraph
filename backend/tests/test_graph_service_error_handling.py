"""Unit tests for graph service error handling"""
import pytest
from unittest.mock import AsyncMock, Mock, patch, MagicMock

from app.services.graph_service import Neo4jService, ValidationError, with_retry
from app.models.graph import GraphNode, GraphRelationship, NodeType, RelationshipType
from neo4j.exceptions import ServiceUnavailable, AuthError, SessionExpired


class AsyncIteratorMock:
    """Mock for async iterator"""

    def __init__(self, items):
        self.items = items

    def __aiter__(self):
        return self

    async def __anext__(self):
        if not self.items:
            raise StopAsyncIteration
        return self.items.pop(0)


class TestConnectionRetry:
    """Test connection retry mechanism"""

    @pytest.mark.asyncio
    async def test_connect_success_on_first_attempt(self):
        """Test successful connection on first attempt"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        with patch("app.services.graph_service.AsyncGraphDatabase.driver") as mock_driver_func:
            mock_driver_instance = MagicMock()
            mock_driver_func.return_value = mock_driver_instance

            mock_session = MagicMock()
            mock_session.run = AsyncMock(return_value=None)
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_driver_instance.session = Mock(return_value=mock_session)

            await service.connect()

            assert service.driver is not None
            mock_driver_func.assert_called_once()

    @pytest.mark.asyncio
    async def test_connect_retry_on_service_unavailable(self):
        """Test connection retry on ServiceUnavailable error"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        with patch("app.services.graph_service.AsyncGraphDatabase.driver") as mock_driver_func:
            mock_driver_instance = MagicMock()
            mock_driver_func.return_value = mock_driver_instance

            call_count = 0

            async def mock_session_run(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise ServiceUnavailable("Service unavailable")
                return None

            mock_session = MagicMock()
            mock_session.run = mock_session_run
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_driver_instance.session = Mock(return_value=mock_session)

            await service.connect()

            assert call_count == 3

    @pytest.mark.asyncio
    async def test_connect_fails_after_max_retries(self):
        """Test connection fails after max retries"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        with patch("app.services.graph_service.AsyncGraphDatabase.driver") as mock_driver_func:
            mock_driver_instance = MagicMock()
            mock_driver_func.return_value = mock_driver_instance

            mock_session = MagicMock()
            mock_session.run = AsyncMock(side_effect=ServiceUnavailable("Service unavailable"))
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_driver_instance.session = Mock(return_value=mock_session)

            with pytest.raises(ServiceUnavailable):
                await service.connect()

    @pytest.mark.asyncio
    async def test_connect_auth_error_no_retry(self):
        """Test that AuthError is not retried"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        with patch("app.services.graph_service.AsyncGraphDatabase.driver") as mock_driver_func:
            mock_driver_instance = MagicMock()
            mock_driver_func.return_value = mock_driver_instance

            mock_session = MagicMock()
            mock_session.run = AsyncMock(side_effect=AuthError("Invalid credentials"))
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_driver_instance.session = Mock(return_value=mock_session)

            with pytest.raises(AuthError):
                await service.connect()

    @pytest.mark.asyncio
    async def test_connect_retry_on_session_expired(self):
        """Test connection retry on SessionExpired error"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        with patch("app.services.graph_service.AsyncGraphDatabase.driver") as mock_driver_func:
            mock_driver_instance = MagicMock()
            mock_driver_func.return_value = mock_driver_instance

            call_count = 0

            async def mock_session_run(*args, **kwargs):
                nonlocal call_count
                call_count += 1
                if call_count < 2:
                    raise SessionExpired("Session expired")
                return None

            mock_session = MagicMock()
            mock_session.run = mock_session_run
            mock_session.__aenter__ = AsyncMock(return_value=mock_session)
            mock_session.__aexit__ = AsyncMock(return_value=None)

            mock_driver_instance.session = Mock(return_value=mock_session)

            await service.connect()

            assert call_count == 2


class TestValidationMethods:
    """Test data validation methods"""

    def test_validate_node_success(self):
        """Test successful node validation"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        node = GraphNode(
            id="test-node",
            label="Test Node",
            type=NodeType.SERVICE,
            properties={"key": "value"}
        )

        service.validate_node(node)

    def test_validate_node_none_raises_error(self):
        """Test that None node raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        with pytest.raises(ValidationError, match="Node cannot be None"):
            service.validate_node(None)

    def test_validate_node_empty_id_raises_error(self):
        """Test that empty id raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        node = GraphNode(
            id="",
            label="Test Node",
            type=NodeType.SERVICE
        )

        with pytest.raises(ValidationError, match="Node id must be a non-empty string"):
            service.validate_node(node)

    def test_validate_node_whitespace_id_raises_error(self):
        """Test that whitespace-only id raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        node = GraphNode(
            id="   ",
            label="Test Node",
            type=NodeType.SERVICE
        )

        with pytest.raises(ValidationError, match="Node id cannot be empty or whitespace"):
            service.validate_node(node)

    def test_validate_node_empty_label_raises_error(self):
        """Test that empty label raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        node = GraphNode(
            id="test-node",
            label="",
            type=NodeType.SERVICE
        )

        with pytest.raises(ValidationError, match="Node label must be a non-empty string"):
            service.validate_node(node)

    def test_validate_node_unsupported_property_value_raises_error(self):
        """Test that unsupported property value type raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        node = GraphNode(
            id="test-node",
            label="Test Node",
            type=NodeType.SERVICE,
            properties={"key": object()}
        )

        with pytest.raises(ValidationError, match="has unsupported type"):
            service.validate_node(node)

    def test_validate_relationship_success(self):
        """Test successful relationship validation"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        rel = GraphRelationship(
            source_id="node1",
            target_id="node2",
            type=RelationshipType.CALLS,
            properties={"key": "value"}
        )

        service.validate_relationship(rel)

    def test_validate_relationship_none_raises_error(self):
        """Test that None relationship raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        with pytest.raises(ValidationError, match="Relationship cannot be None"):
            service.validate_relationship(None)

    def test_validate_relationship_empty_source_id_raises_error(self):
        """Test that empty source_id raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        rel = GraphRelationship(
            source_id="",
            target_id="node2",
            type=RelationshipType.CALLS
        )

        with pytest.raises(ValidationError, match="Relationship source_id must be a non-empty string"):
            service.validate_relationship(rel)

    def test_validate_relationship_empty_target_id_raises_error(self):
        """Test that empty target_id raises ValidationError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        rel = GraphRelationship(
            source_id="node1",
            target_id="",
            type=RelationshipType.CALLS
        )

        with pytest.raises(ValidationError, match="Relationship target_id must be a non-empty string"):
            service.validate_relationship(rel)


class TestTransactionRollback:
    """Test transaction rollback mechanism"""

    @pytest.mark.asyncio
    async def test_transaction_rollback_on_error(self):
        """Test that transaction rolls back on error"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        mock_driver = MagicMock()
        service.driver = mock_driver

        mock_tx = MagicMock()
        mock_tx.run = AsyncMock(side_effect=Exception("Query failed"))
        mock_tx.rollback = AsyncMock()
        mock_tx.__aenter__ = AsyncMock(return_value=mock_tx)
        mock_tx.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.begin_transaction = Mock(return_value=mock_tx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = Mock(return_value=mock_session)

        operations = [
            ("CREATE (n:Test {id: 1})", {}),
            ("CREATE (n:Test {id: 2})", {}),
        ]

        with pytest.raises(Exception, match="Query failed"):
            await service.execute_transaction(operations)

        mock_tx.rollback.assert_called_once()

    @pytest.mark.asyncio
    async def test_transaction_commit_on_success(self):
        """Test that transaction commits on success"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        mock_driver = MagicMock()
        service.driver = mock_driver

        mock_result = AsyncIteratorMock([])

        mock_tx = MagicMock()
        mock_tx.run = AsyncMock(return_value=mock_result)
        mock_tx.commit = AsyncMock()
        mock_tx.rollback = AsyncMock()
        mock_tx.__aenter__ = AsyncMock(return_value=mock_tx)
        mock_tx.__aexit__ = AsyncMock(return_value=None)

        mock_session = MagicMock()
        mock_session.begin_transaction = Mock(return_value=mock_tx)
        mock_session.__aenter__ = AsyncMock(return_value=mock_session)
        mock_session.__aexit__ = AsyncMock(return_value=None)

        mock_driver.session = Mock(return_value=mock_session)

        operations = [
            ("CREATE (n:Test {id: 1})", {}),
        ]

        await service.execute_transaction(operations)

        mock_tx.commit.assert_called_once()
        mock_tx.rollback.assert_not_called()

    @pytest.mark.asyncio
    async def test_transaction_without_driver_raises_error(self):
        """Test that transaction without driver raises RuntimeError"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        service.driver = None

        operations = [("CREATE (n:Test)", {})]

        with pytest.raises(RuntimeError, match="Not connected to Neo4j"):
            await service.execute_transaction(operations)

    @pytest.mark.asyncio
    async def test_batch_transaction_rollback_on_error(self):
        """Test batch transaction rollback on validation error"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        mock_driver = MagicMock()
        service.driver = mock_driver

        nodes = [
            GraphNode(id="valid", label="Valid", type=NodeType.SERVICE),
            GraphNode(id="", label="Invalid", type=NodeType.SERVICE),
        ]

        with pytest.raises(ValidationError):
            await service.execute_batch_in_transaction(nodes=nodes)


class TestRetryDecorator:
    """Test the with_retry decorator"""

    @pytest.mark.asyncio
    async def test_retry_decorator_success_no_retry(self):
        """Test decorator succeeds without retry on success"""
        call_count = 0

        class TestClass:
            @with_retry(max_retries=3)
            async def test_method(self):
                nonlocal call_count
                call_count += 1
                return "success"

        obj = TestClass()
        result = await obj.test_method()

        assert result == "success"
        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_decorator_retries_on_service_unavailable(self):
        """Test decorator retries on ServiceUnavailable"""
        call_count = 0

        class TestClass:
            @with_retry(max_retries=3, base_delay=0.01)
            async def test_method(self):
                nonlocal call_count
                call_count += 1
                if call_count < 3:
                    raise ServiceUnavailable("Service unavailable")
                return "success"

        obj = TestClass()
        result = await obj.test_method()

        assert result == "success"
        assert call_count == 3

    @pytest.mark.asyncio
    async def test_retry_decorator_fails_after_max_retries(self):
        """Test decorator fails after max retries"""
        call_count = 0

        class TestClass:
            @with_retry(max_retries=2, base_delay=0.01)
            async def test_method(self):
                nonlocal call_count
                call_count += 1
                raise ServiceUnavailable("Service unavailable")

        obj = TestClass()

        with pytest.raises(ServiceUnavailable):
            await obj.test_method()

        assert call_count == 2

    @pytest.mark.asyncio
    async def test_retry_decorator_auth_error_not_retried(self):
        """Test that AuthError is not retried"""
        call_count = 0

        class TestClass:
            @with_retry(max_retries=3)
            async def test_method(self):
                nonlocal call_count
                call_count += 1
                raise AuthError("Auth failed")

        obj = TestClass()

        with pytest.raises(AuthError):
            await obj.test_method()

        assert call_count == 1

    @pytest.mark.asyncio
    async def test_retry_decorator_generic_error_not_retried(self):
        """Test that generic exceptions are not retried"""
        call_count = 0

        class TestClass:
            @with_retry(max_retries=3)
            async def test_method(self):
                nonlocal call_count
                call_count += 1
                raise ValueError("Generic error")

        obj = TestClass()

        with pytest.raises(ValueError):
            await obj.test_method()

        assert call_count == 1


class TestCloseConnection:
    """Test connection close behavior"""

    @pytest.mark.asyncio
    async def test_close_connection_success(self):
        """Test successful connection close"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        mock_driver = MagicMock()
        mock_driver.close = AsyncMock()
        service.driver = mock_driver

        await service.close()

        mock_driver.close.assert_called_once()
        assert service.driver is None

    @pytest.mark.asyncio
    async def test_close_connection_no_driver(self):
        """Test close when no driver exists"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")
        service.driver = None

        await service.close()

        assert service.driver is None

    @pytest.mark.asyncio
    async def test_close_connection_handles_error(self):
        """Test close handles errors gracefully"""
        service = Neo4jService("bolt://localhost:7687", "neo4j", "password")

        mock_driver = MagicMock()
        mock_driver.close = AsyncMock(side_effect=Exception("Close failed"))
        service.driver = mock_driver

        await service.close()

        assert service.driver is None
