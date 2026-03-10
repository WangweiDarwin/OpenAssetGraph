"""Scan task scheduler service"""
import asyncio
from typing import Optional
from datetime import datetime
from pathlib import Path
from .scanners.postgres_scanner import PostgreSQLScanner
from .parsers.java_parser import JavaParser
from .parsers.python_parser import PythonParser
from .graph_service import Neo4jService
from ..models.graph import GraphNode, GraphRelationship, NodeType, RelationshipType
from ..core.config import settings


class ScanService:
    """Service for managing scan tasks"""
    
    def __init__(self):
        self.neo4j_service = Neo4jService(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password
        )
        self.java_parser = JavaParser()
        self.python_parser = PythonParser()
    
    async def scan_database(
        self, 
        connection_string: str,
        database_name: str
    ) -> dict:
        """Scan a database and write to Neo4j"""
        start_time = datetime.now()
        
        try:
            scanner = PostgreSQLScanner(connection_string)
            await scanner.connect()
            
            tables = await scanner.scan_tables()
            relationships = await scanner.scan_relationships()
            indexes = await scanner.scan_indexes()
            
            await self.neo4j_service.connect()
            
            db_node = GraphNode(
                id=f"db_{database_name}",
                label=database_name,
                type=NodeType.DATABASE,
                properties={
                    'name': database_name,
                    'type': 'PostgreSQL',
                    'scanned_at': datetime.now().isoformat()
                }
            )
            await self.neo4j_service.create_node(db_node)
            
            for table in tables:
                table_node = GraphNode(
                    id=f"table_{database_name}_{table['name']}",
                    label=table['name'],
                    type=NodeType.TABLE,
                    properties={
                        'name': table['name'],
                        'schema': table['schema'],
                        'type': table['type']
                    }
                )
                await self.neo4j_service.create_node(table_node)
                
                rel = GraphRelationship(
                    source_id=db_node.id,
                    target_id=table_node.id,
                    type=RelationshipType.CONTAINS
                )
                await self.neo4j_service.create_relationship(rel)
                
                columns = await scanner.scan_columns(table['name'])
                for column in columns:
                    column_node = GraphNode(
                        id=f"column_{database_name}_{table['name']}_{column['name']}",
                        label=column['name'],
                        type=NodeType.COLUMN,
                        properties={
                            'name': column['name'],
                            'data_type': column['data_type'],
                            'is_nullable': column['is_nullable'],
                            'default': column.get('default'),
                            'position': column.get('position')
                        }
                    )
                    await self.neo4j_service.create_node(column_node)
                    
                    col_rel = GraphRelationship(
                        source_id=table_node.id,
                        target_id=column_node.id,
                        type=RelationshipType.CONTAINS
                    )
                    await self.neo4j_service.create_relationship(col_rel)
            
            for fk in relationships:
                from_table_id = f"table_{database_name}_{fk['from_table']}"
                to_table_id = f"table_{database_name}_{fk['to_table']}"
                
                fk_rel = GraphRelationship(
                    source_id=from_table_id,
                    target_id=to_table_id,
                    type=RelationshipType.REFERENCES,
                    properties={
                        'from_column': fk['from_column'],
                        'to_column': fk['to_column'],
                        'constraint_name': fk['constraint_name']
                    }
                )
                await self.neo4j_service.create_relationship(fk_rel)
            
            await scanner.close()
            await self.neo4j_service.close()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'status': 'success',
                'database_name': database_name,
                'tables_scanned': len(tables),
                'relationships_found': len(relationships),
                'indexes_found': len(indexes),
                'duration_seconds': duration
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'database_name': database_name
            }
    
    async def scan_code(
        self, 
        directory_path: str,
        language: str = 'auto'
    ) -> dict:
        """Scan code directory and extract APIs"""
        start_time = datetime.now()
        
        try:
            directory = Path(directory_path)
            if not directory.exists():
                raise FileNotFoundError(f"Directory not found: {directory}")
            
            all_apis = []
            all_dependencies = []
            parsed_files = []
            
            if language == 'java' or language == 'auto':
                java_files = await self.java_parser.parse_directory(directory)
                for parsed in java_files:
                    if 'error' not in parsed:
                        apis = self.java_parser.extract_apis(parsed)
                        deps = self.java_parser.extract_dependencies(parsed)
                        all_apis.extend(apis)
                        all_dependencies.extend(deps)
                        parsed_files.append(parsed['file_path'])
            
            if language == 'python' or language == 'auto':
                python_files = await self.python_parser.parse_directory(directory)
                for parsed in python_files:
                    if 'error' not in parsed:
                        apis = self.python_parser.extract_apis(parsed)
                        deps = self.python_parser.extract_dependencies(parsed)
                        all_apis.extend(apis)
                        all_dependencies.extend(deps)
                        parsed_files.append(parsed['file_path'])
            
            await self.neo4j_service.connect()
            
            for api in all_apis:
                api_node = GraphNode(
                    id=f"api_{api['path']}_{api['method']}",
                    label=f"{api['method']} {api['path']}",
                    type=NodeType.API,
                    properties={
                        'method': api['method'],
                        'path': api['path'],
                        'handler': api.get('handler', ''),
                        'return_type': api.get('return_type', '')
                    }
                )
                await self.neo4j_service.create_node(api_node)
            
            await self.neo4j_service.close()
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'status': 'success',
                'directory': directory_path,
                'language': language,
                'files_parsed': len(parsed_files),
                'apis_found': len(all_apis),
                'dependencies_found': len(all_dependencies),
                'duration_seconds': duration,
                'parsed_files': parsed_files[:10]
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'error': str(e),
                'directory': directory_path
            }
    
    async def full_scan(
        self,
        db_connection_string: Optional[str] = None,
        code_directory: Optional[str] = None,
        database_name: Optional[str] = None
    ) -> dict:
        """Perform full scan of database and code"""
        results = {}
        
        if db_connection_string and database_name:
            results['database'] = await self.scan_database(
                db_connection_string,
                database_name
            )
        
        if code_directory:
            results['code'] = await self.scan_code(code_directory)
        
        return results
