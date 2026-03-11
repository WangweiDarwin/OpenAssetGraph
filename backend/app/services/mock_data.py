"""Mock data service for demo without Neo4j"""
from typing import Any

MOCK_NODES = [
    {"id": "db1", "label": "User Database", "type": "Database", "properties": {"engine": "PostgreSQL", "version": "14.0", "host": "db.example.com", "port": 5432}},
    {"id": "db2", "label": "Order Database", "type": "Database", "properties": {"engine": "PostgreSQL", "version": "14.0", "host": "db.example.com", "port": 5433}},
    {"id": "db3", "label": "Product Database", "type": "Database", "properties": {"engine": "MySQL", "version": "8.0", "host": "db2.example.com", "port": 3306}},
    {"id": "svc1", "label": "User Service", "type": "Service", "properties": {"language": "Java", "port": 8081, "framework": "Spring Boot", "team": "Platform"}},
    {"id": "svc2", "label": "Order Service", "type": "Service", "properties": {"language": "Java", "port": 8082, "framework": "Spring Boot", "team": "Commerce"}},
    {"id": "svc3", "label": "Product Service", "type": "Service", "properties": {"language": "Python", "port": 8083, "framework": "FastAPI", "team": "Catalog"}},
    {"id": "svc4", "label": "Payment Service", "type": "Service", "properties": {"language": "Go", "port": 8084, "framework": "Gin", "team": "Finance"}},
    {"id": "api1", "label": "User API", "type": "API", "properties": {"framework": "Spring Boot", "version": "3.0", "endpoint": "/api/v1/users"}},
    {"id": "api2", "label": "Order API", "type": "API", "properties": {"framework": "Spring Boot", "version": "3.0", "endpoint": "/api/v1/orders"}},
    {"id": "api3", "label": "Product API", "type": "API", "properties": {"framework": "FastAPI", "version": "0.100", "endpoint": "/api/v1/products"}},
    {"id": "api4", "label": "Payment API", "type": "API", "properties": {"framework": "Gin", "version": "1.9", "endpoint": "/api/v1/payments"}},
    {"id": "fe1", "label": "Admin Dashboard", "type": "FrontendApp", "properties": {"framework": "React", "version": "18.0", "url": "https://admin.example.com"}},
    {"id": "fe2", "label": "Customer Portal", "type": "FrontendApp", "properties": {"framework": "React", "version": "18.0", "url": "https://portal.example.com"}},
    {"id": "fe3", "label": "Mobile App", "type": "FrontendApp", "properties": {"framework": "React Native", "version": "0.72", "platform": "iOS/Android"}},
    {"id": "table_users", "label": "users", "type": "Table", "properties": {"schema": "public", "row_count": 1000000}},
    {"id": "table_orders", "label": "orders", "type": "Table", "properties": {"schema": "public", "row_count": 5000000}},
    {"id": "table_products", "label": "products", "type": "Table", "properties": {"schema": "catalog", "row_count": 50000}},
    {"id": "table_payments", "label": "payments", "type": "Table", "properties": {"schema": "finance", "row_count": 2000000}},
]

MOCK_EDGES = [
    {"source": "fe1", "target": "api1", "type": "REQUESTS", "properties": {"calls_per_day": 50000}},
    {"source": "fe1", "target": "api2", "type": "REQUESTS", "properties": {"calls_per_day": 30000}},
    {"source": "fe2", "target": "api2", "type": "REQUESTS", "properties": {"calls_per_day": 100000}},
    {"source": "fe2", "target": "api3", "type": "REQUESTS", "properties": {"calls_per_day": 80000}},
    {"source": "fe3", "target": "api3", "type": "REQUESTS", "properties": {"calls_per_day": 150000}},
    {"source": "fe3", "target": "api4", "type": "REQUESTS", "properties": {"calls_per_day": 50000}},
    {"source": "api1", "target": "svc1", "type": "EXPOSES", "properties": {}},
    {"source": "api2", "target": "svc2", "type": "EXPOSES", "properties": {}},
    {"source": "api3", "target": "svc3", "type": "EXPOSES", "properties": {}},
    {"source": "api4", "target": "svc4", "type": "EXPOSES", "properties": {}},
    {"source": "svc1", "target": "db1", "type": "CALLS", "properties": {"queries_per_sec": 500}},
    {"source": "svc2", "target": "db2", "type": "CALLS", "properties": {"queries_per_sec": 1200}},
    {"source": "svc3", "target": "db3", "type": "CALLS", "properties": {"queries_per_sec": 800}},
    {"source": "svc4", "target": "db2", "type": "CALLS", "properties": {"queries_per_sec": 300}},
    {"source": "svc1", "target": "svc2", "type": "CALLS", "properties": {"calls_per_sec": 50}},
    {"source": "svc2", "target": "svc3", "type": "CALLS", "properties": {"calls_per_sec": 100}},
    {"source": "svc2", "target": "svc4", "type": "CALLS", "properties": {"calls_per_sec": 80}},
    {"source": "db1", "target": "table_users", "type": "CONTAINS", "properties": {}},
    {"source": "db2", "target": "table_orders", "type": "CONTAINS", "properties": {}},
    {"source": "db2", "target": "table_payments", "type": "CONTAINS", "properties": {}},
    {"source": "db3", "target": "table_products", "type": "CONTAINS", "properties": {}},
]

MALL_NODES = [
    {"id": "mall-admin", "label": "mall-admin", "type": "Service", "properties": {"description": "Backend admin service", "port": 8080, "language": "Java", "framework": "Spring Boot"}},
    {"id": "mall-portal", "label": "mall-portal", "type": "Service", "properties": {"description": "Frontend portal service", "port": 8085, "language": "Java", "framework": "Spring Boot"}},
    {"id": "mall-search", "label": "mall-search", "type": "Service", "properties": {"description": "Search service with Elasticsearch", "port": 8081, "language": "Java", "framework": "Spring Boot"}},
    {"id": "mall-demo", "label": "mall-demo", "type": "Service", "properties": {"description": "Demo service", "port": 8082, "language": "Java", "framework": "Spring Boot"}},
    {"id": "mall-mbg", "label": "mall-mbg", "type": "Library", "properties": {"description": "MyBatis Generator module", "language": "Java"}},
    {"id": "mall-common", "label": "mall-common", "type": "Library", "properties": {"description": "Common utilities and configurations", "language": "Java"}},
    {"id": "mall-mysql", "label": "MySQL Database", "type": "Database", "properties": {"engine": "MySQL", "version": "5.7", "host": "localhost", "port": 3306}},
    {"id": "mall-redis", "label": "Redis Cache", "type": "Database", "properties": {"engine": "Redis", "version": "7.0", "host": "localhost", "port": 6379}},
    {"id": "mall-elasticsearch", "label": "Elasticsearch", "type": "Database", "properties": {"engine": "Elasticsearch", "version": "7.17", "host": "localhost", "port": 9200}},
    {"id": "mall-mongodb", "label": "MongoDB", "type": "Database", "properties": {"engine": "MongoDB", "version": "6.0", "host": "localhost", "port": 27017}},
    {"id": "mall-rabbitmq", "label": "RabbitMQ", "type": "Database", "properties": {"engine": "RabbitMQ", "version": "3.12", "host": "localhost", "port": 5672}},
    {"id": "admin-api", "label": "Admin API", "type": "API", "properties": {"endpoint": "/admin", "framework": "Spring MVC", "version": "1.0"}},
    {"id": "portal-api", "label": "Portal API", "type": "API", "properties": {"endpoint": "/portal", "framework": "Spring MVC", "version": "1.0"}},
    {"id": "search-api", "label": "Search API", "type": "API", "properties": {"endpoint": "/search", "framework": "Spring MVC", "version": "1.0"}},
    {"id": "mall-admin-web", "label": "Admin Dashboard", "type": "FrontendApp", "properties": {"framework": "Vue.js", "version": "3.0", "url": "https://github.com/macrozheng/mall-admin-web"}},
    {"id": "mall-app", "label": "Mobile App", "type": "FrontendApp", "properties": {"framework": "Flutter", "version": "3.0", "url": "https://github.com/macrozheng/mall-app"}},
    {"id": "pms_product", "label": "pms_product", "type": "Table", "properties": {"schema": "mall", "description": "Product table"}},
    {"id": "pms_brand", "label": "pms_brand", "type": "Table", "properties": {"schema": "mall", "description": "Brand table"}},
    {"id": "pms_category", "label": "pms_category", "type": "Table", "properties": {"schema": "mall", "description": "Category table"}},
    {"id": "oms_order", "label": "oms_order", "type": "Table", "properties": {"schema": "mall", "description": "Order table"}},
    {"id": "ums_member", "label": "ums_member", "type": "Table", "properties": {"schema": "mall", "description": "Member table"}},
]

MALL_EDGES = [
    {"source": "admin-api", "target": "mall-admin", "type": "EXPOSES", "properties": {}},
    {"source": "portal-api", "target": "mall-portal", "type": "EXPOSES", "properties": {}},
    {"source": "search-api", "target": "mall-search", "type": "EXPOSES", "properties": {}},
    {"source": "mall-admin-web", "target": "admin-api", "type": "REQUESTS", "properties": {}},
    {"source": "mall-app", "target": "portal-api", "type": "REQUESTS", "properties": {}},
    {"source": "mall-admin", "target": "mall-mysql", "type": "CALLS", "properties": {}},
    {"source": "mall-portal", "target": "mall-mysql", "type": "CALLS", "properties": {}},
    {"source": "mall-search", "target": "mall-elasticsearch", "type": "CALLS", "properties": {}},
    {"source": "mall-admin", "target": "mall-redis", "type": "CALLS", "properties": {}},
    {"source": "mall-portal", "target": "mall-redis", "type": "CALLS", "properties": {}},
    {"source": "mall-admin", "target": "mall-mongodb", "type": "CALLS", "properties": {}},
    {"source": "mall-portal", "target": "mall-rabbitmq", "type": "CALLS", "properties": {}},
    {"source": "mall-admin", "target": "mall-mbg", "type": "DEPENDS_ON", "properties": {}},
    {"source": "mall-portal", "target": "mall-mbg", "type": "DEPENDS_ON", "properties": {}},
    {"source": "mall-admin", "target": "mall-common", "type": "DEPENDS_ON", "properties": {}},
    {"source": "mall-portal", "target": "mall-common", "type": "DEPENDS_ON", "properties": {}},
    {"source": "mall-search", "target": "mall-common", "type": "DEPENDS_ON", "properties": {}},
    {"source": "mall-mysql", "target": "pms_product", "type": "CONTAINS", "properties": {}},
    {"source": "mall-mysql", "target": "pms_brand", "type": "CONTAINS", "properties": {}},
    {"source": "mall-mysql", "target": "pms_category", "type": "CONTAINS", "properties": {}},
    {"source": "mall-mysql", "target": "oms_order", "type": "CONTAINS", "properties": {}},
    {"source": "mall-mysql", "target": "ums_member", "type": "CONTAINS", "properties": {}},
]

ONLINE_BOUTIQUE_NODES = [
    {"id": "frontend", "label": "frontend", "type": "Service", "properties": {"language": "Go", "port": 8080, "description": "Web frontend"}},
    {"id": "cartservice", "label": "cartservice", "type": "Service", "properties": {"language": "C#", "port": 7070, "description": "Shopping cart service"}},
    {"id": "productcatalogservice", "label": "productcatalogservice", "type": "Service", "properties": {"language": "Go", "port": 3550, "description": "Product catalog"}},
    {"id": "currencyservice", "label": "currencyservice", "type": "Service", "properties": {"language": "Node.js", "port": 7000, "description": "Currency conversion"}},
    {"id": "paymentservice", "label": "paymentservice", "type": "Service", "properties": {"language": "Node.js", "port": 50051, "description": "Payment processing"}},
    {"id": "shippingservice", "label": "shippingservice", "type": "Service", "properties": {"language": "Go", "port": 50051, "description": "Shipping quotes"}},
    {"id": "emailservice", "label": "emailservice", "type": "Service", "properties": {"language": "Python", "port": 8080, "description": "Email notifications"}},
    {"id": "checkoutservice", "label": "checkoutservice", "type": "Service", "properties": {"language": "Go", "port": 5050, "description": "Checkout orchestration"}},
    {"id": "recommendationservice", "label": "recommendationservice", "type": "Service", "properties": {"language": "Python", "port": 8080, "description": "Product recommendations"}},
    {"id": "adservice", "label": "adservice", "type": "Service", "properties": {"language": "Java", "port": 9555, "description": "Ad targeting"}},
    {"id": "loadgenerator", "label": "loadgenerator", "type": "Service", "properties": {"language": "Python", "port": 8089, "description": "Load testing"}},
    {"id": "redis-cart", "label": "Redis Cache", "type": "Database", "properties": {"engine": "Redis", "port": 6379, "description": "Cart data store"}},
    {"id": "web-app", "label": "Online Boutique", "type": "FrontendApp", "properties": {"framework": "Go Templates", "url": "https://onlineboutique.dev"}},
]

ONLINE_BOUTIQUE_EDGES = [
    {"source": "web-app", "target": "frontend", "type": "REQUESTS", "properties": {}},
    {"source": "frontend", "target": "productcatalogservice", "type": "CALLS", "properties": {}},
    {"source": "frontend", "target": "currencyservice", "type": "CALLS", "properties": {}},
    {"source": "frontend", "target": "cartservice", "type": "CALLS", "properties": {}},
    {"source": "frontend", "target": "recommendationservice", "type": "CALLS", "properties": {}},
    {"source": "frontend", "target": "shippingservice", "type": "CALLS", "properties": {}},
    {"source": "frontend", "target": "checkoutservice", "type": "CALLS", "properties": {}},
    {"source": "cartservice", "target": "redis-cart", "type": "CALLS", "properties": {}},
    {"source": "checkoutservice", "target": "productcatalogservice", "type": "CALLS", "properties": {}},
    {"source": "checkoutservice", "target": "cartservice", "type": "CALLS", "properties": {}},
    {"source": "checkoutservice", "target": "paymentservice", "type": "CALLS", "properties": {}},
    {"source": "checkoutservice", "target": "emailservice", "type": "CALLS", "properties": {}},
    {"source": "checkoutservice", "target": "shippingservice", "type": "CALLS", "properties": {}},
    {"source": "checkoutservice", "target": "currencyservice", "type": "CALLS", "properties": {}},
    {"source": "recommendationservice", "target": "productcatalogservice", "type": "CALLS", "properties": {}},
    {"source": "adservice", "target": "productcatalogservice", "type": "CALLS", "properties": {}},
    {"source": "loadgenerator", "target": "frontend", "type": "CALLS", "properties": {}},
]

PROJECT_TEMPLATES = {
    "default": {"nodes": MOCK_NODES, "edges": MOCK_EDGES},
    "mall": {"nodes": MALL_NODES, "edges": MALL_EDGES},
    "online-boutique": {"nodes": ONLINE_BOUTIQUE_NODES, "edges": ONLINE_BOUTIQUE_EDGES},
}


class MockDataService:
    """Service for mock/demo data"""
    
    def __init__(self, project: str = "default"):
        self.project = project
        self._load_project(project)
    
    def _load_project(self, project: str):
        template = PROJECT_TEMPLATES.get(project, PROJECT_TEMPLATES["default"])
        self.nodes = {n["id"]: n for n in template["nodes"]}
        self.edges = template["edges"]
    
    def set_project(self, project: str):
        self.project = project
        self._load_project(project)
    
    async def get_topology(
        self,
        node_types: list[str] | None = None,
        limit: int = 100
    ) -> dict[str, Any]:
        nodes = list(self.nodes.values())
        if node_types:
            nodes = [n for n in nodes if n["type"] in node_types]
        nodes = nodes[:limit]
        node_ids = {n["id"] for n in nodes}
        edges = [e for e in self.edges if e["source"] in node_ids and e["target"] in node_ids]
        return {
            "nodes": nodes,
            "edges": edges,
            "node_count": len(nodes),
            "edge_count": len(edges),
            "project": self.project
        }
    
    async def get_node(self, node_id: str) -> dict[str, Any] | None:
        return self.nodes.get(node_id)
    
    async def search_nodes(
        self,
        query: str,
        node_types: list[str] | None = None,
        limit: int = 50
    ) -> dict[str, Any]:
        query_lower = query.lower()
        results = []
        for node in self.nodes.values():
            if node_types and node["type"] not in node_types:
                continue
            if query_lower in node["label"].lower() or query_lower in node["id"].lower():
                results.append(node)
            elif node.get("properties"):
                for v in node["properties"].values():
                    if query_lower in str(v).lower():
                        results.append(node)
                        break
        return {
            "query": query,
            "results": results[:limit],
            "count": len(results)
        }
    
    async def get_stats(self) -> dict[str, Any]:
        type_counts = {}
        for node in self.nodes.values():
            t = node["type"]
            type_counts[t] = type_counts.get(t, 0) + 1
        return {
            "total_nodes": len(self.nodes),
            "total_edges": len(self.edges),
            "node_types": type_counts,
            "project": self.project
        }
    
    async def get_node_relationships(self, node_id: str) -> list[dict[str, Any]]:
        return [e for e in self.edges if e["source"] == node_id or e["target"] == node_id]
    
    async def find_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 5
    ) -> list[dict[str, Any]]:
        if start_id not in self.nodes or end_id not in self.nodes:
            return []
        
        visited = set()
        queue = [(start_id, [start_id])]
        
        while queue:
            current, path = queue.pop(0)
            if current == end_id:
                return [{"id": n, **self.nodes[n]} for n in path]
            if len(path) > max_depth:
                continue
            for edge in self.edges:
                next_node = None
                if edge["source"] == current and edge["target"] not in visited:
                    next_node = edge["target"]
                elif edge["target"] == current and edge["source"] not in visited:
                    next_node = edge["source"]
                if next_node:
                    visited.add(next_node)
                    queue.append((next_node, path + [next_node]))
        return []
    
    async def list_projects(self) -> list[dict[str, Any]]:
        return [
            {"id": "default", "name": "Demo Project", "description": "Sample enterprise architecture"},
            {"id": "mall", "name": "Mall E-Commerce", "description": "Spring Boot microservices (40k+ stars)"},
            {"id": "online-boutique", "name": "Online Boutique", "description": "Google Cloud 11 microservices demo"},
        ]
    
    async def add_nodes(self, nodes: list[dict[str, Any]]) -> int:
        for node in nodes:
            self.nodes[node["id"]] = node
        return len(nodes)
    
    async def add_edges(self, edges: list[dict[str, Any]]) -> int:
        self.edges.extend(edges)
        return len(edges)
    
    async def clear_project(self) -> None:
        self.nodes.clear()
        self.edges.clear()


mock_data_service = MockDataService()
