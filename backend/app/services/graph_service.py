"""Neo4j graph database service"""
from typing import Optional, Any
from neo4j import AsyncGraphDatabase, AsyncDriver
from ..models.graph import GraphNode, GraphRelationship, NodeType, RelationshipType


class Neo4jService:
    """Service for interacting with Neo4j graph database"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncDriver] = None
    
    async def connect(self) -> None:
        """Connect to Neo4j database"""
        self.driver = AsyncGraphDatabase.driver(
            self.uri,
            auth=(self.user, self.password)
        )
    
    async def close(self) -> None:
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()
            self.driver = None
    
    async def create_node(self, node: GraphNode) -> bool:
        """Create or update a node in the graph"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = f"""
        MERGE (n:{node.type.value} {{id: $id}})
        SET n += $props
        RETURN n
        """
        
        async with self.driver.session() as session:
            result = await session.run(
                query,
                id=node.id,
                props=node.model_dump()
            )
            record = await result.single()
            return record is not None
    
    async def create_relationship(self, rel: GraphRelationship) -> bool:
        """Create a relationship between two nodes"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{rel.type.value}]->(target)
        SET r += $props
        RETURN source, target
        """
        
        async with self.driver.session() as session:
            result = await session.run(
                query,
                source_id=rel.source_id,
                target_id=rel.target_id,
                props=rel.properties
            )
            record = await result.single()
            return record is not None
    
    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = """
        MATCH (n {id: $id})
        RETURN n
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, id=node_id)
            record = await result.single()
            if record:
                node_data = dict(record["n"])
                return GraphNode(**node_data)
            return None
    
    async def get_all_nodes(self, limit: int = 100) -> list[GraphNode]:
        """Get all nodes with optional limit"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = """
        MATCH (n)
        RETURN n
        LIMIT $limit
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, limit=limit)
            nodes = []
            async for record in result:
                node_data = dict(record["n"])
                nodes.append(GraphNode(**node_data))
            return nodes
    
    async def delete_node(self, node_id: str) -> bool:
        """Delete a node by ID"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = """
        MATCH (n {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        
        async with self.driver.session() as session:
            result = await session.run(query, id=node_id)
            record = await result.single()
            return record and record["deleted"] > 0
    
    async def execute_query(self, query: str, parameters: Optional[dict] = None) -> list[dict[str, Any]]:
        """Execute a custom Cypher query and return results"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        if parameters is None:
            parameters = {}
        
        async with self.driver.session() as session:
            result = await session.run(query, **parameters)
            records = []
            async for record in result:
                records.append(dict(record))
            return records
    
    async def batch_create_nodes(self, nodes: list[GraphNode]) -> int:
        """Batch create nodes using UNWIND"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        if not nodes:
            return 0
        
        node_data_list = []
        for node in nodes:
            props = {
                "id": node.id,
                "label": node.label,
                "type": node.type.value,
            }
            if node.properties:
                for k, v in node.properties.items():
                    if isinstance(v, (str, int, float, bool, list)) or v is None:
                        props[k] = v
            node_data_list.append({
                "id": node.id,
                "type": node.type.value,
                "props": props
            })
        
        query = """
        UNWIND $nodes AS node_data
        CALL apoc.cypher.run(
            'MERGE (n:' + node_data.type + ' {id: $id}) SET n += $props RETURN n',
            {id: node_data.id, props: node_data.props}
        ) YIELD value
        RETURN count(value.n) as created
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, nodes=node_data_list)
                record = await result.single()
                return record["created"] if record else 0
        except Exception:
            query = """
            UNWIND $nodes AS node_data
            MERGE (n {id: node_data.id})
            SET n += node_data.props
            WITH n, node_data
            CALL apoc.create.addLabels(n, [node_data.type]) YIELD node
            RETURN count(node) as created
            """
            try:
                async with self.driver.session() as session:
                    result = await session.run(query, nodes=node_data_list)
                    record = await result.single()
                    return record["created"] if record else 0
            except Exception:
                created = 0
                for node in nodes:
                    success = await self.create_node(node)
                    if success:
                        created += 1
                return created
    
    async def batch_create_relationships(self, relationships: list[GraphRelationship]) -> int:
        """Batch create relationships using UNWIND"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        if not relationships:
            return 0
        
        rel_data_list = []
        for rel in relationships:
            rel_data_list.append({
                "source_id": rel.source_id,
                "target_id": rel.target_id,
                "type": rel.type.value,
                "props": rel.properties or {}
            })
        
        query = """
        UNWIND $rels AS rel_data
        MATCH (source {id: rel_data.source_id})
        MATCH (target {id: rel_data.target_id})
        CALL apoc.create.relationship(source, rel_data.type, rel_data.props, target) YIELD rel
        RETURN count(rel) as created
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, rels=rel_data_list)
                record = await result.single()
                return record["created"] if record else 0
        except Exception:
            created = 0
            for rel in relationships:
                success = await self.create_relationship(rel)
                if success:
                    created += 1
            return created
    
    async def clear_all_data(self) -> bool:
        """Clear all data from the database"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        
        try:
            async with self.driver.session() as session:
                await session.run(query)
            return True
        except Exception:
            return False
    
    async def get_node_count(self) -> int:
        """Get total count of nodes in the database"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = """
        MATCH (n)
        RETURN count(n) as count
        """
        
        async with self.driver.session() as session:
            result = await session.run(query)
            record = await result.single()
            return record["count"] if record else 0
