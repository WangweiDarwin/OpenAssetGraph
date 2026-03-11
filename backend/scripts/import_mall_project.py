"""
Scan a GitHub project and import into Neo4j for testing
Example project: https://github.com/macrozheng/mall (Spring Boot e-commerce microservices)
"""
import asyncio
import os
import re
from typing import Any
from app.services.graph_service import Neo4jService
from app.core.config import settings


async def import_mall_project():
    """
    Import mall project architecture into Neo4j
    Mall is a Spring Boot e-commerce project with microservices architecture
    """
    service = Neo4jService(settings.neo4j_uri, settings.neo4j_user, settings.neo4j_password)
    
    mall_modules = [
        {"id": "mall-admin", "label": "mall-admin", "type": "Service", "properties": {
            "description": "Backend admin service",
            "port": 8080,
            "language": "Java",
            "framework": "Spring Boot"
        }},
        {"id": "mall-portal", "label": "mall-portal", "type": "Service", "properties": {
            "description": "Frontend portal service",
            "port": 8085,
            "language": "Java",
            "framework": "Spring Boot"
        }},
        {"id": "mall-search", "label": "mall-search", "type": "Service", "properties": {
            "description": "Search service with Elasticsearch",
            "port": 8081,
            "language": "Java",
            "framework": "Spring Boot"
        }},
        {"id": "mall-demo", "label": "mall-demo", "type": "Service", "properties": {
            "description": "Demo service",
            "port": 8082,
            "language": "Java",
            "framework": "Spring Boot"
        }},
        {"id": "mall-mbg", "label": "mall-mbg", "type": "Library", "properties": {
            "description": "MyBatis Generator module",
            "language": "Java"
        }},
        {"id": "mall-common", "label": "mall-common", "type": "Library", "properties": {
            "description": "Common utilities and configurations",
            "language": "Java"
        }},
    ]
    
    databases = [
        {"id": "mall-mysql", "label": "MySQL Database", "type": "Database", "properties": {
            "engine": "MySQL",
            "version": "5.7",
            "host": "localhost",
            "port": 3306
        }},
        {"id": "mall-redis", "label": "Redis Cache", "type": "Database", "properties": {
            "engine": "Redis",
            "version": "7.0",
            "host": "localhost",
            "port": 6379
        }},
        {"id": "mall-elasticsearch", "label": "Elasticsearch", "type": "Database", "properties": {
            "engine": "Elasticsearch",
            "version": "7.17",
            "host": "localhost",
            "port": 9200
        }},
        {"id": "mall-mongodb", "label": "MongoDB", "type": "Database", "properties": {
            "engine": "MongoDB",
            "version": "6.0",
            "host": "localhost",
            "port": 27017
        }},
        {"id": "mall-rabbitmq", "label": "RabbitMQ", "type": "Database", "properties": {
            "engine": "RabbitMQ",
            "version": "3.12",
            "host": "localhost",
            "port": 5672
        }},
    ]
    
    apis = [
        {"id": "admin-api", "label": "Admin API", "type": "API", "properties": {
            "endpoint": "/admin",
            "framework": "Spring MVC",
            "version": "1.0"
        }},
        {"id": "portal-api", "label": "Portal API", "type": "API", "properties": {
            "endpoint": "/portal",
            "framework": "Spring MVC",
            "version": "1.0"
        }},
        {"id": "search-api", "label": "Search API", "type": "API", "properties": {
            "endpoint": "/search",
            "framework": "Spring MVC",
            "version": "1.0"
        }},
    ]
    
    frontends = [
        {"id": "mall-admin-web", "label": "Admin Dashboard", "type": "FrontendApp", "properties": {
            "framework": "Vue.js",
            "version": "3.0",
            "url": "https://github.com/macrozheng/mall-admin-web"
        }},
        {"id": "mall-app", "label": "Mobile App", "type": "FrontendApp", "properties": {
            "framework": "Flutter",
            "version": "3.0",
            "url": "https://github.com/macrozheng/mall-app"
        }},
    ]
    
    tables = [
        {"id": "pms_product", "label": "pms_product", "type": "Table", "properties": {"schema": "mall", "description": "Product table"}},
        {"id": "pms_brand", "label": "pms_brand", "type": "Table", "properties": {"schema": "mall", "description": "Brand table"}},
        {"id": "pms_category", "label": "pms_category", "type": "Table", "properties": {"schema": "mall", "description": "Category table"}},
        {"id": "oms_order", "label": "oms_order", "type": "Table", "properties": {"schema": "mall", "description": "Order table"}},
        {"id": "oms_order_item", "label": "oms_order_item", "type": "Table", "properties": {"schema": "mall", "description": "Order item table"}},
        {"id": "ums_member", "label": "ums_member", "type": "Table", "properties": {"schema": "mall", "description": "Member table"}},
        {"id": "sms_coupon", "label": "sms_coupon", "type": "Table", "properties": {"schema": "mall", "description": "Coupon table"}},
    ]
    
    relationships = [
        ("admin-api", "mall-admin", "EXPOSES"),
        ("portal-api", "mall-portal", "EXPOSES"),
        ("search-api", "mall-search", "EXPOSES"),
        ("mall-admin-web", "admin-api", "REQUESTS"),
        ("mall-app", "portal-api", "REQUESTS"),
        ("mall-admin", "mall-mysql", "CALLS"),
        ("mall-portal", "mall-mysql", "CALLS"),
        ("mall-search", "mall-elasticsearch", "CALLS"),
        ("mall-admin", "mall-redis", "CALLS"),
        ("mall-portal", "mall-redis", "CALLS"),
        ("mall-admin", "mall-mongodb", "CALLS"),
        ("mall-portal", "mall-rabbitmq", "CALLS"),
        ("mall-admin", "mall-mbg", "DEPENDS_ON"),
        ("mall-portal", "mall-mbg", "DEPENDS_ON"),
        ("mall-admin", "mall-common", "DEPENDS_ON"),
        ("mall-portal", "mall-common", "DEPENDS_ON"),
        ("mall-search", "mall-common", "DEPENDS_ON"),
        ("mall-mysql", "pms_product", "CONTAINS"),
        ("mall-mysql", "pms_brand", "CONTAINS"),
        ("mall-mysql", "pms_category", "CONTAINS"),
        ("mall-mysql", "oms_order", "CONTAINS"),
        ("mall-mysql", "oms_order_item", "CONTAINS"),
        ("mall-mysql", "ums_member", "CONTAINS"),
        ("mall-mysql", "sms_coupon", "CONTAINS"),
    ]
    
    try:
        await service.connect()
        
        print("Creating nodes...")
        all_nodes = mall_modules + databases + apis + frontends + tables
        for node in all_nodes:
            await service.create_node(
                node["id"],
                node["label"],
                node["type"],
                node["properties"]
            )
            print(f"  Created: {node['label']} ({node['type']})")
        
        print("\nCreating relationships...")
        for source, target, rel_type in relationships:
            await service.create_relationship(source, target, rel_type)
            print(f"  {source} --[{rel_type}]--> {target}")
        
        print("\n✅ Mall project imported successfully!")
        print(f"   Nodes: {len(all_nodes)}")
        print(f"   Relationships: {len(relationships)}")
        
    finally:
        await service.close()


async def main():
    print("=" * 60)
    print("Importing Mall Project Architecture into Neo4j")
    print("Source: https://github.com/macrozheng/mall")
    print("=" * 60)
    print()
    
    await import_mall_project()


if __name__ == "__main__":
    asyncio.run(main())
