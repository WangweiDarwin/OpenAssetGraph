"""PostgreSQL database scanner"""
from typing import Any
import asyncpg
from .base import BaseScanner


class PostgreSQLScanner(BaseScanner):
    """PostgreSQL database scanner implementation"""
    
    def __init__(self, connection_string: str):
        self.connection_string = connection_string
        self.connection = None
    
    async def connect(self) -> None:
        """Connect to PostgreSQL database"""
        self.connection = await asyncpg.connect(self.connection_string)
    
    async def scan_tables(self) -> list[dict[str, Any]]:
        """Scan all tables in the database"""
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        query = """
        SELECT 
            table_name,
            table_schema,
            table_type
        FROM information_schema.tables 
        WHERE table_schema NOT IN ('pg_catalog', 'information_schema')
        ORDER BY table_name
        """
        
        rows = await self.connection.fetch(query)
        return [
            {
                "name": row["table_name"],
                "schema": row["table_schema"],
                "type": row["table_type"]
            }
            for row in rows
        ]
    
    async def scan_columns(self, table_name: str) -> list[dict[str, Any]]:
        """Scan columns of a specific table"""
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        query = """
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length,
            numeric_precision,
            numeric_scale,
            ordinal_position
        FROM information_schema.columns 
        WHERE table_name = $1
        ORDER BY ordinal_position
        """
        
        rows = await self.connection.fetch(query, table_name)
        return [
            {
                "name": row["column_name"],
                "data_type": row["data_type"],
                "is_nullable": row["is_nullable"] == "YES",
                "default": row["column_default"],
                "max_length": row["character_maximum_length"],
                "precision": row["numeric_precision"],
                "scale": row["numeric_scale"],
                "position": row["ordinal_position"]
            }
            for row in rows
        ]
    
    async def scan_relationships(self) -> list[dict[str, Any]]:
        """Scan foreign key relationships"""
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        query = """
        SELECT 
            tc.table_name AS from_table,
            kcu.column_name AS from_column,
            ccu.table_name AS to_table,
            ccu.column_name AS to_column,
            tc.constraint_name
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu 
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu 
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
        ORDER BY tc.table_name
        """
        
        rows = await self.connection.fetch(query)
        return [
            {
                "from_table": row["from_table"],
                "from_column": row["from_column"],
                "to_table": row["to_table"],
                "to_column": row["to_column"],
                "constraint_name": row["constraint_name"]
            }
            for row in rows
        ]
    
    async def scan_indexes(self) -> list[dict[str, Any]]:
        """Scan indexes in the database"""
        if not self.connection:
            raise RuntimeError("Not connected to database")
        
        query = """
        SELECT 
            tablename AS table_name,
            indexname AS index_name,
            indexdef AS index_definition
        FROM pg_indexes
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY tablename, indexname
        """
        
        rows = await self.connection.fetch(query)
        return [
            {
                "table_name": row["table_name"],
                "index_name": row["index_name"],
                "definition": row["index_definition"]
            }
            for row in rows
        ]
    
    async def close(self) -> None:
        """Close database connection"""
        if self.connection:
            await self.connection.close()
            self.connection = None
