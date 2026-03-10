"""Topology query service"""
from typing import Optional
from ..services.graph_service import Neo4jService
from ..models.graph import GraphNode, GraphRelationship


class TopologyService:
    """Service for querying topology data"""
    
    def __init__(self, neo4j_service: Neo4jService):
        self.neo4j_service = neo4j_service
    
    async def get_full_topology(
        self,
        node_types: Optional[list[str]] = None,
        limit: int = 100
    ) -> dict:
        """Get full topology data"""
        if not self.neo4j_service.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        nodes = []
        relationships = []
        
        async with self.neo4j_service.driver.session() as session:
            node_query = "MATCH (n) RETURN n"
            if node_types:
                node_query = f"MATCH (n) WHERE n.type IN $types RETURN n"
                result = await session.run(node_query, types=node_types)
            else:
                result = await session.run(node_query)
            
            async for record in result:
                node_data = dict(record["n"])
                nodes.append({
                    "id": node_data.get("id", ""),
                    "label": node_data.get("label", ""),
                    "type": node_data.get("type", ""),
                    "properties": node_data
                })
            
            rel_query = """
            MATCH (source)-[r]->(target)
            RETURN source.id as source_id, type(r) as rel_type, target.id as target_id, properties(r) as props
            """
            result = await session.run(rel_query)
            
            async for record in result:
                relationships.append({
                    "source": record["source_id"],
                    "target": record["target_id"],
                    "type": record["rel_type"],
                    "properties": dict(record["props"]) if record["props"] else {}
                })
        
        return {
            "nodes": nodes[:limit],
            "edges": relationships[:limit],
            "node_count": len(nodes),
            "edge_count": len(relationships)
        }
    
    async def search_nodes(
        self,
        query: str,
        node_types: Optional[list[str]] = None,
        limit: int = 50
    ) -> list[dict]:
        """Search nodes by name or properties"""
        if not self.neo4j_service.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        async with self.neo4j_service.driver.session() as session:
            search_query = """
            MATCH (n)
            WHERE n.label CONTAINS $query OR n.name CONTAINS $query
            """
            
            if node_types:
                search_query += " AND n.type IN $types"
            
            search_query += " RETURN n LIMIT $limit"
            
            params = {"query": query, "limit": limit}
            if node_types:
                params["types"] = node_types
            
            result = await session.run(search_query, **params)
            
            nodes = []
            async for record in result:
                node_data = dict(record["n"])
                nodes.append({
                    "id": node_data.get("id", ""),
                    "label": node_data.get("label", ""),
                    "type": node_data.get("type", ""),
                    "properties": node_data
                })
            
            return nodes
    
    async def get_node_details(self, node_id: str) -> Optional[dict]:
        """Get detailed information about a node"""
        if not self.neo4j_service.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        async with self.neo4j_service.driver.session() as session:
            query = """
            MATCH (n {id: $id})
            OPTIONAL MATCH (n)-[outgoing]->(out)
            OPTIONAL MATCH (in)-[incoming]->(n)
            RETURN n, 
                   collect(DISTINCT {node: out, relationship: type(outgoing)}) as outgoing,
                   collect(DISTINCT {node: in, relationship: type(incoming)}) as incoming
            """
            
            result = await session.run(query, id=node_id)
            record = await result.single()
            
            if not record:
                return None
            
            node_data = dict(record["n"])
            
            return {
                "id": node_data.get("id", ""),
                "label": node_data.get("label", ""),
                "type": node_data.get("type", ""),
                "properties": node_data,
                "outgoing_relationships": [
                    {
                        "target_id": rel["node"]["id"] if rel["node"] else None,
                        "target_label": rel["node"]["label"] if rel["node"] else None,
                        "relationship_type": rel["relationship"]
                    }
                    for rel in record["outgoing"]
                    if rel["node"]
                ],
                "incoming_relationships": [
                    {
                        "source_id": rel["node"]["id"] if rel["node"] else None,
                        "source_label": rel["node"]["label"] if rel["node"] else None,
                        "relationship_type": rel["relationship"]
                    }
                    for rel in record["incoming"]
                    if rel["node"]
                ]
            }
    
    async def find_path(
        self,
        start_node_id: str,
        end_node_id: str,
        max_depth: int = 5
    ) -> list[dict]:
        """Find shortest path between two nodes"""
        if not self.neo4j_service.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        async with self.neo4j_service.driver.session() as session:
            query = """
            MATCH path = shortestPath(
                (start {id: $start_id})-[*..{max_depth}]-(end {id: $end_id})
            )
            RETURN path
            """
            
            result = await session.run(
                query,
                start_id=start_node_id,
                end_id=end_node_id,
                max_depth=max_depth
            )
            
            record = await result.single()
            
            if not record:
                return []
            
            path = record["path"]
            nodes = []
            
            for node in path.nodes:
                node_data = dict(node)
                nodes.append({
                    "id": node_data.get("id", ""),
                    "label": node_data.get("label", ""),
                    "type": node_data.get("type", ""),
                    "properties": node_data
                })
            
            return nodes
    
    async def get_node_relationships(
        self,
        node_id: str,
        relationship_type: Optional[str] = None,
        direction: str = "both"
    ) -> list[dict]:
        """Get relationships for a specific node"""
        if not self.neo4j_service.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        async with self.neo4j_service.driver.session() as session:
            if direction == "outgoing":
                query = "MATCH (n {id: $id})-[r]->(target)"
            elif direction == "incoming":
                query = "MATCH (source)-[r]->(n {id: $id})"
            else:
                query = "MATCH (n {id: $id})-[r]-(other)"
            
            if relationship_type:
                query += f" WHERE type(r) = $rel_type"
            
            query += " RETURN r, startNode(r) as start, endNode(r) as end"
            
            params = {"id": node_id}
            if relationship_type:
                params["rel_type"] = relationship_type
            
            result = await session.run(query, **params)
            
            relationships = []
            async for record in result:
                rel_data = dict(record["r"])
                start_data = dict(record["start"])
                end_data = dict(record["end"])
                
                relationships.append({
                    "type": rel_data.get("type", ""),
                    "source_id": start_data.get("id", ""),
                    "target_id": end_data.get("id", ""),
                    "properties": rel_data
                })
            
            return relationships
