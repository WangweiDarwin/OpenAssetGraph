"""Test PostgreSQL scanner"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from app.services.scanners.postgres_scanner import PostgreSQLScanner


@pytest.fixture
def mock_connection():
    """Mock database connection"""
    connection = AsyncMock()
    return connection


@pytest.fixture
def scanner(mock_connection):
    """Create PostgreSQL scanner instance"""
    scanner = PostgreSQLScanner("postgresql://test:test@localhost:5432/test")
    scanner.connection = mock_connection
    return scanner


@pytest.mark.asyncio
async def test_connect(scanner):
    """Test database connection"""
    with patch('asyncpg.connect', new_callable=AsyncMock) as mock_connect:
        await scanner.connect()
        mock_connect.assert_called_once()


@pytest.mark.asyncio
async def test_scan_tables(scanner, mock_connection):
    """Test table scanning"""
    mock_data = [
        {
            "table_name": "users",
            "table_schema": "public",
            "table_type": "BASE TABLE"
        },
        {
            "table_name": "orders",
            "table_schema": "public",
            "table_type": "BASE TABLE"
        }
    ]
    
    mock_connection.fetch.return_value = mock_data
    
    result = await scanner.scan_tables()
    
    assert len(result) == 2
    assert result[0]["name"] == "users"
    assert result[1]["name"] == "orders"


@pytest.mark.asyncio
async def test_scan_columns(scanner, mock_connection):
    """Test column scanning"""
    mock_data = [
        {
            "column_name": "id",
            "data_type": "integer",
            "is_nullable": "NO",
            "column_default": None,
            "character_maximum_length": None,
            "numeric_precision": 32,
            "numeric_scale": 0,
            "ordinal_position": 1
        },
        {
            "column_name": "name",
            "data_type": "character varying",
            "is_nullable": "YES",
            "column_default": None,
            "character_maximum_length": 255,
            "numeric_precision": None,
            "numeric_scale": None,
            "ordinal_position": 2
        }
    ]
    
    mock_connection.fetch.return_value = mock_data
    
    result = await scanner.scan_columns("users")
    
    assert len(result) == 2
    assert result[0]["name"] == "id"
    assert result[1]["name"] == "name"
    assert result[0]["is_nullable"] is False
    assert result[1]["is_nullable"] is True


@pytest.mark.asyncio
async def test_scan_relationships(scanner, mock_connection):
    """Test relationship scanning"""
    mock_data = [
        {
            "from_table": "orders",
            "from_column": "user_id",
            "to_table": "users",
            "to_column": "id",
            "constraint_name": "fk_orders_user_id"
        }
    ]
    
    mock_connection.fetch.return_value = mock_data
    
    result = await scanner.scan_relationships()
    
    assert len(result) == 1
    assert result[0]["from_table"] == "orders"
    assert result[0]["to_table"] == "users"


@pytest.mark.asyncio
async def test_scan_indexes(scanner, mock_connection):
    """Test index scanning"""
    mock_data = [
        {
            "table_name": "users",
            "index_name": "users_pkey",
            "index_definition": "CREATE UNIQUE INDEX users_pkey ON users(id)"
        },
        {
            "table_name": "users",
            "index_name": "idx_users_email",
            "index_definition": "CREATE INDEX idx_users_email ON users(email)"
        }
    ]
    
    mock_connection.fetch.return_value = mock_data
    
    result = await scanner.scan_indexes()
    
    assert len(result) == 2
    assert result[0]["table_name"] == "users"
    assert result[0]["index_name"] == "users_pkey"


@pytest.mark.asyncio
async def test_close(scanner, mock_connection):
    """Test connection close"""
    await scanner.close()
    mock_connection.close.assert_called_once()
    assert scanner.connection is None


@pytest.mark.asyncio
async def test_not_connected_error(scanner):
    """Test error when not connected"""
    scanner.connection = None
    
    with pytest.raises(RuntimeError, match="Not connected to database"):
        await scanner.scan_tables()
