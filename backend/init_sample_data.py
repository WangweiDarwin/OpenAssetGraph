"""Sample data initialization script"""
import asyncio
from app.services.graph_service import Neo4jService
from app.core.config import settings

SAMPLE_NODES = [
    {"id": "db1", "label": "User Database", "type": "Database", "properties": {"engine": "PostgreSQL", "version": "14.0"}},
    {"id": "db2", "label": "Order Database", "type": "Database", "properties": {"engine": "PostgreSQL", "version": "14.0"}},
    {"id": "db3", "label": "Product Database", "type": "Database", "properties": {"engine": "PostgreSQL", "version": "14.0"}},
    {"id": "svc1", "label": "User Service", "type": "Service", "properties": {"language": "Java", "port": 8081}},
    {"id": "svc2", "label": "Order Service", "type": "Service", "properties": {"language": "Java", "port": 8082}},
    {"id": "svc3", "label": "Product Service", "type": "Service", "properties": {"language": "Java", "port": 8083}},
    {"id": "api1", "label": "User API", "type": "API", "properties": {"framework": "Spring Boot", "version": "3.0"}},
    {"id": "api2", "label": "Order API", "type": "API", "properties": {"framework": "Spring Boot", "version": "3.0"}},
    {"id": "api3", "label": "Product API", "type": "API", "properties": {"framework": "Spring Boot", "version": "3.0"}},
    {"id": "fe1", "label": "Admin Dashboard", "type": "FrontendApp", "properties": {"framework": "React", "version": "18.0"}},
    {"id": "fe2", "label": "Customer Portal", "type": "FrontendApp", "properties": {"framework": "React", "version": "18.0"}},
]

SAMPLE_EDGES = [
    {"source": "fe1", "target": "api1", "type": "REQUESTS"},
    {"source": "fe2", "target": "api2", "type": "REQUESTS"},
    {"source": "api1", "target": "svc1", "type": "EXPOSES"},
    {"source": "api2", "target": "svc2", "type": "EXPOSES"},
    {"source": "api3", "target": "svc3", "type": "EXPOSES"},
    {"source": "svc1", "target": "db1", "type": "CALLS"},
    {"source": "svc2", "target": "db2", "type": "CALLS"},
    {"source": "svc3", "target": "db3", "type": "CALLS"},
    {"source": "svc1", "target": "svc2", "type": "CALLS"},
    {"source": "svc2", "target": "svc3", "type": "CALLS"},
]

SAMPLE_TABLES = [
    {"name": "users", "schema": "public", "type": "table", "database_id": "db1"},
    {"name": "orders", "schema": "public", "type": "table", "database_id": "db2"},
    {"name": "products", "schema": "public", "type": "table", "database_id": "db3"},
]

SAMPLE_COLUMNS = [
    {"name": "id", "type": "integer", "table": "users", "database_id": "db1"},
    {"name": "username", "type": "varchar", "table": "users", "database_id": "db1"},
    {"name": "email", "type": "varchar", "table": "users", "database_id": "db1"},
    {"name": "id", "type": "integer", "table": "orders", "database_id": "db2"},
    {"name": "user_id", "type": "integer", "table": "orders", "database_id": "db2"},
    {"name": "product_id", "type": "integer", "table": "orders", "database_id": "db2"},
]

async def init_sample_data():
    service = Neo4jService(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    
    try:
        await service.connect()
        
        for node in SAMPLE_NODES:
            await service.create_node(
                node["id"],
                node["label"],
                node["type"],
                node["properties"]
            )
            print(f"Created node: {node['label']}")
        
        for edge in SAMPLE_EDGES:
            await service.create_relationship(
                edge["source"],
                edge["target"],
                edge["type"],
                edge.get("properties", {})
            )
            print(f"Created relationship: {edge['source']} -> {edge['target']}")
        
        for table in SAMPLE_TABLES:
            await service.create_node(
                f"table_{table['name']}_{table['database_id']}",
                table['name'],
                'Table',
                {'schema': table['schema'], 'database_id': table['database_id']}
            )
            await service.create_relationship(
                table['database_id'],
                f"table_{table['name']}_{table['database_id']}",
                'CONTAINS'
            )
            print(f"Created table: {table['name']}")
        
        for column in SAMPLE_COLUMNS:
            await service.create_node(
                f"col_{column['name']}_{column['table']}_{column['database_id']}",
                column['name'],
                'Column',
                {'type': column['type'], 'table': column['table']}
            )
            table_id = f"table_{column['table']}_{column['database_id']}"
            await service.create_relationship(
                table_id,
                f"col_{column['name']}_{column['table']}_{column['database_id']}",
                'CONTAINS'
            )
            print(f"Created column: {column['name']}")
        
        print("\nSample data initialized successfully!")
        
    finally:
        await service.close()

if __name__ == "__main__":
    asyncio.run(init_sample_data())
