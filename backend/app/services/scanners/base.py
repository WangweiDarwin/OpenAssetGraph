"""Database scanner base module"""
from abc import ABC, abstractmethod
from typing import Any


class BaseScanner(ABC):
    """Abstract base class for database scanners"""
    
    @abstractmethod
    async def connect(self) -> None:
        """Connect to the database"""
        pass
    
    @abstractmethod
    async def scan_tables(self) -> list[dict[str, Any]]:
        """Scan all tables in the database"""
        pass
    
    @abstractmethod
    async def scan_columns(self, table_name: str) -> list[dict[str, Any]]:
        """Scan columns of a specific table"""
        pass
    
    @abstractmethod
    async def scan_relationships(self) -> list[dict[str, Any]]:
        """Scan foreign key relationships between tables"""
        pass
    
    @abstractmethod
    async def scan_indexes(self) -> list[dict[str, Any]]:
        """Scan indexes in the database"""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close database connection"""
        pass
