"""Neo4j graph database service"""
from typing import Optional
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
            return result.single() is not None
    
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
            return result.single() is not None
    
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
