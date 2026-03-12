"""Neo4j graph database service"""
import logging
import asyncio
import functools
from typing import Optional, Any, Callable, TypeVar
from neo4j import AsyncGraphDatabase, AsyncDriver, AsyncSession
from neo4j.exceptions import ServiceUnavailable, AuthError, SessionExpired
from ..models.graph import GraphNode, GraphRelationship, NodeType, RelationshipType

T = TypeVar('T')

logger = logging.getLogger(__name__)


def setup_logging(level: int = logging.INFO) -> None:
    """Setup structured logging for Neo4j service"""
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(level)


def with_retry(max_retries: int = 3, base_delay: float = 1.0, max_delay: float = 10.0):
    """
    Retry decorator with exponential backoff
    
    Args:
        max_retries: Maximum number of retry attempts
        base_delay: Initial delay in seconds
        max_delay: Maximum delay cap in seconds
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs) -> T:
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return await func(self, *args, **kwargs)
                except (ServiceUnavailable, SessionExpired, ConnectionError, OSError) as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        delay = min(base_delay * (2 ** attempt), max_delay)
                        logger.warning(
                            f"Retry attempt {attempt + 1}/{max_retries} for {func.__name__}. "
                            f"Error: {str(e)}. Retrying in {delay:.1f}s..."
                        )
                        await asyncio.sleep(delay)
                    else:
                        logger.error(
                            f"All {max_retries} retry attempts failed for {func.__name__}. "
                            f"Last error: {str(e)}"
                        )
                except AuthError as e:
                    logger.error(f"Authentication error in {func.__name__}: {str(e)}")
                    raise
                except Exception as e:
                    logger.error(f"Unexpected error in {func.__name__}: {str(e)}")
                    raise
            raise last_exception
        return wrapper
    return decorator


class ValidationError(Exception):
    """Exception raised for validation errors"""
    pass


class Neo4jService:
    """Service for interacting with Neo4j graph database"""
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver: Optional[AsyncDriver] = None
        self._connection_retries = 3
        self._retry_base_delay = 1.0
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def connect(self) -> None:
        """Connect to Neo4j database with retry mechanism"""
        logger.info(f"Attempting to connect to Neo4j at {self.uri}")
        try:
            self.driver = AsyncGraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            async with self.driver.session() as session:
                await session.run("RETURN 1")
            logger.info("Successfully connected to Neo4j")
        except AuthError as e:
            logger.error(f"Authentication failed for Neo4j: {str(e)}")
            raise
        except ServiceUnavailable as e:
            logger.error(f"Neo4j service unavailable at {self.uri}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {str(e)}")
            raise
    
    async def close(self) -> None:
        """Close Neo4j connection"""
        if self.driver:
            try:
                await self.driver.close()
                logger.info("Neo4j connection closed successfully")
            except Exception as e:
                logger.error(f"Error closing Neo4j connection: {str(e)}")
            finally:
                self.driver = None
    
    def validate_node(self, node: GraphNode) -> None:
        """
        Validate node data before database operations
        
        Args:
            node: GraphNode to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not node:
            raise ValidationError("Node cannot be None")
        
        if not node.id or not isinstance(node.id, str):
            raise ValidationError(f"Node id must be a non-empty string, got: {type(node.id)}")
        
        if not node.id.strip():
            raise ValidationError("Node id cannot be empty or whitespace")
        
        if not node.label or not isinstance(node.label, str):
            raise ValidationError(f"Node label must be a non-empty string, got: {type(node.label)}")
        
        if not isinstance(node.type, NodeType):
            raise ValidationError(f"Node type must be a NodeType enum, got: {type(node.type)}")
        
        if node.properties is not None and not isinstance(node.properties, dict):
            raise ValidationError(f"Node properties must be a dict, got: {type(node.properties)}")
        
        for key, value in node.properties.items():
            if not isinstance(key, str):
                raise ValidationError(f"Property key must be string, got: {type(key)}")
            if not isinstance(value, (str, int, float, bool, list, type(None))):
                raise ValidationError(
                    f"Property value for key '{key}' has unsupported type: {type(value)}"
                )
        
        logger.debug(f"Node validation passed for id: {node.id}")
    
    def validate_relationship(self, rel: GraphRelationship) -> None:
        """
        Validate relationship data before database operations
        
        Args:
            rel: GraphRelationship to validate
            
        Raises:
            ValidationError: If validation fails
        """
        if not rel:
            raise ValidationError("Relationship cannot be None")
        
        if not rel.source_id or not isinstance(rel.source_id, str):
            raise ValidationError(
                f"Relationship source_id must be a non-empty string, got: {type(rel.source_id)}"
            )
        
        if not rel.source_id.strip():
            raise ValidationError("Relationship source_id cannot be empty or whitespace")
        
        if not rel.target_id or not isinstance(rel.target_id, str):
            raise ValidationError(
                f"Relationship target_id must be a non-empty string, got: {type(rel.target_id)}"
            )
        
        if not rel.target_id.strip():
            raise ValidationError("Relationship target_id cannot be empty or whitespace")
        
        if not isinstance(rel.type, RelationshipType):
            raise ValidationError(
                f"Relationship type must be a RelationshipType enum, got: {type(rel.type)}"
            )
        
        if rel.properties is not None and not isinstance(rel.properties, dict):
            raise ValidationError(
                f"Relationship properties must be a dict, got: {type(rel.properties)}"
            )
        
        for key, value in rel.properties.items():
            if not isinstance(key, str):
                raise ValidationError(f"Property key must be string, got: {type(key)}")
            if not isinstance(value, (str, int, float, bool, list, type(None))):
                raise ValidationError(
                    f"Property value for key '{key}' has unsupported type: {type(value)}"
                )
        
        logger.debug(
            f"Relationship validation passed for {rel.source_id} -> {rel.target_id}"
        )
    
    async def execute_transaction(
        self,
        operations: list[tuple[str, dict]],
        rollback_on_error: bool = True
    ) -> list[dict[str, Any]]:
        """
        Execute multiple operations in a single transaction
        
        Args:
            operations: List of (query, parameters) tuples to execute
            rollback_on_error: Whether to rollback on error (always True for Neo4j)
            
        Returns:
            List of results from each operation
            
        Raises:
            RuntimeError: If not connected to Neo4j
            Exception: If transaction fails
        """
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        logger.info(f"Starting transaction with {len(operations)} operations")
        results = []
        
        async with self.driver.session() as session:
            async with session.begin_transaction() as tx:
                try:
                    for i, (query, params) in enumerate(operations):
                        logger.debug(f"Executing transaction operation {i + 1}/{len(operations)}")
                        result = await tx.run(query, **params)
                        records = []
                        async for record in result:
                            records.append(dict(record))
                        results.append(records)
                    
                    await tx.commit()
                    logger.info(f"Transaction completed successfully with {len(operations)} operations")
                    return results
                    
                except Exception as e:
                    logger.error(
                        f"Transaction failed after {len(results)} operations. "
                        f"Rolling back. Error: {str(e)}"
                    )
                    await tx.rollback()
                    raise
    
    async def execute_batch_in_transaction(
        self,
        nodes: Optional[list[GraphNode]] = None,
        relationships: Optional[list[GraphRelationship]] = None
    ) -> dict[str, int]:
        """
        Execute batch creation of nodes and relationships in a single transaction
        
        Args:
            nodes: List of nodes to create
            relationships: List of relationships to create
            
        Returns:
            Dictionary with 'nodes_created' and 'relationships_created' counts
        """
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        operations = []
        result = {"nodes_created": 0, "relationships_created": 0}
        
        if nodes:
            for node in nodes:
                self.validate_node(node)
                query = f"""
                MERGE (n:{node.type.value} {{id: $id}})
                SET n += $props
                RETURN n
                """
                operations.append((query, {"id": node.id, "props": node.model_dump()}))
        
        if relationships:
            for rel in relationships:
                self.validate_relationship(rel)
                query = f"""
                MATCH (source {{id: $source_id}})
                MATCH (target {{id: $target_id}})
                MERGE (source)-[r:{rel.type.value}]->(target)
                SET r += $props
                RETURN source, target
                """
                operations.append((
                    query,
                    {"source_id": rel.source_id, "target_id": rel.target_id, "props": rel.properties}
                ))
        
        if not operations:
            return result
        
        try:
            results = await self.execute_transaction(operations)
            result["nodes_created"] = len(nodes) if nodes else 0
            result["relationships_created"] = len(relationships) if relationships else 0
            return result
        except Exception as e:
            logger.error(f"Batch transaction failed: {str(e)}")
            raise
    
    def _log_operation(self, operation: str, params: dict[str, Any]) -> None:
        """Log operation details for debugging"""
        safe_params = {k: v for k, v in params.items() if k not in ('password', 'auth')}
        logger.debug(f"Operation: {operation}, Params: {safe_params}")
    
    def _log_error(self, operation: str, error: Exception, params: Optional[dict] = None) -> None:
        """Log error details with context"""
        safe_params = None
        if params:
            safe_params = {k: v for k, v in params.items() if k not in ('password', 'auth')}
        logger.error(
            f"Operation failed: {operation}",
            extra={
                "operation": operation,
                "error_type": type(error).__name__,
                "error_message": str(error),
                "params": safe_params
            }
        )
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def create_node(self, node: GraphNode) -> bool:
        """Create or update a node in the graph"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        self.validate_node(node)
        self._log_operation("create_node", {"node_id": node.id, "type": node.type.value})
        
        query = f"""
        MERGE (n:{node.type.value} {{id: $id}})
        SET n += $props
        RETURN n
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    id=node.id,
                    props=node.model_dump()
                )
                record = await result.single()
                success = record is not None
                if success:
                    logger.info(f"Node created/updated successfully: {node.id}")
                return success
        except Exception as e:
            self._log_error("create_node", e, {"node_id": node.id})
            raise
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def create_relationship(self, rel: GraphRelationship) -> bool:
        """Create a relationship between two nodes"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        self.validate_relationship(rel)
        self._log_operation(
            "create_relationship",
            {"source": rel.source_id, "target": rel.target_id, "type": rel.type.value}
        )
        
        query = f"""
        MATCH (source {{id: $source_id}})
        MATCH (target {{id: $target_id}})
        MERGE (source)-[r:{rel.type.value}]->(target)
        SET r += $props
        RETURN source, target
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(
                    query,
                    source_id=rel.source_id,
                    target_id=rel.target_id,
                    props=rel.properties
                )
                record = await result.single()
                success = record is not None
                if success:
                    logger.info(
                        f"Relationship created: {rel.source_id} -[{rel.type.value}]-> {rel.target_id}"
                    )
                return success
        except Exception as e:
            self._log_error(
                "create_relationship",
                e,
                {"source": rel.source_id, "target": rel.target_id}
            )
            raise
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def get_node(self, node_id: str) -> Optional[GraphNode]:
        """Get a node by ID"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        self._log_operation("get_node", {"node_id": node_id})
        
        query = """
        MATCH (n {id: $id})
        RETURN n
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, id=node_id)
                record = await result.single()
                if record:
                    node_data = dict(record["n"])
                    logger.debug(f"Node retrieved: {node_id}")
                    return GraphNode(**node_data)
                logger.debug(f"Node not found: {node_id}")
                return None
        except Exception as e:
            self._log_error("get_node", e, {"node_id": node_id})
            raise
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def get_all_nodes(self, limit: int = 100) -> list[GraphNode]:
        """Get all nodes with optional limit"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        self._log_operation("get_all_nodes", {"limit": limit})
        
        query = """
        MATCH (n)
        RETURN n
        LIMIT $limit
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, limit=limit)
                nodes = []
                async for record in result:
                    node_data = dict(record["n"])
                    nodes.append(GraphNode(**node_data))
                logger.info(f"Retrieved {len(nodes)} nodes")
                return nodes
        except Exception as e:
            self._log_error("get_all_nodes", e, {"limit": limit})
            raise
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def delete_node(self, node_id: str) -> bool:
        """Delete a node by ID"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        self._log_operation("delete_node", {"node_id": node_id})
        
        query = """
        MATCH (n {id: $id})
        DETACH DELETE n
        RETURN count(n) as deleted
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, id=node_id)
                record = await result.single()
                deleted = record and record["deleted"] > 0
                if deleted:
                    logger.info(f"Node deleted: {node_id}")
                else:
                    logger.warning(f"Node not found for deletion: {node_id}")
                return deleted
        except Exception as e:
            self._log_error("delete_node", e, {"node_id": node_id})
            raise
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def execute_query(self, query: str, parameters: Optional[dict] = None) -> list[dict[str, Any]]:
        """Execute a custom Cypher query and return results"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        if parameters is None:
            parameters = {}
        
        self._log_operation("execute_query", {"query": query[:100] + "..." if len(query) > 100 else query})
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query, **parameters)
                records = []
                async for record in result:
                    records.append(dict(record))
                logger.debug(f"Query executed, returned {len(records)} records")
                return records
        except Exception as e:
            self._log_error("execute_query", e, {"query": query[:100]})
            raise
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def batch_create_nodes(self, nodes: list[GraphNode]) -> int:
        """Batch create nodes using UNWIND"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        if not nodes:
            return 0
        
        for node in nodes:
            self.validate_node(node)
        
        self._log_operation("batch_create_nodes", {"count": len(nodes)})
        
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
                created = record["created"] if record else 0
                logger.info(f"Batch created {created} nodes")
                return created
        except Exception as e:
            logger.warning(f"APOC batch create failed, trying alternative method: {str(e)}")
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
                    created = record["created"] if record else 0
                    logger.info(f"Batch created {created} nodes (alternative method)")
                    return created
            except Exception as e2:
                logger.warning(f"Alternative batch method also failed: {str(e2)}")
                created = 0
                for node in nodes:
                    try:
                        success = await self.create_node(node)
                        if success:
                            created += 1
                    except Exception as e3:
                        logger.error(f"Failed to create node {node.id}: {str(e3)}")
                logger.info(f"Individual creation completed: {created}/{len(nodes)} nodes created")
                return created
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def batch_create_relationships(self, relationships: list[GraphRelationship]) -> int:
        """Batch create relationships using UNWIND"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        if not relationships:
            return 0
        
        for rel in relationships:
            self.validate_relationship(rel)
        
        self._log_operation("batch_create_relationships", {"count": len(relationships)})
        
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
                created = record["created"] if record else 0
                logger.info(f"Batch created {created} relationships")
                return created
        except Exception as e:
            logger.warning(f"Batch relationship creation failed, falling back to individual: {str(e)}")
            created = 0
            for rel in relationships:
                try:
                    success = await self.create_relationship(rel)
                    if success:
                        created += 1
                except Exception as e2:
                    logger.error(
                        f"Failed to create relationship {rel.source_id} -> {rel.target_id}: {str(e2)}"
                    )
            logger.info(f"Individual creation completed: {created}/{len(relationships)} relationships created")
            return created
    
    async def clear_all_data(self) -> bool:
        """Clear all data from the database"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        self._log_operation("clear_all_data", {})
        
        query = """
        MATCH (n)
        DETACH DELETE n
        """
        
        try:
            async with self.driver.session() as session:
                await session.run(query)
            logger.warning("All data cleared from database")
            return True
        except Exception as e:
            self._log_error("clear_all_data", e)
            return False
    
    @with_retry(max_retries=3, base_delay=1.0)
    async def get_node_count(self) -> int:
        """Get total count of nodes in the database"""
        if not self.driver:
            raise RuntimeError("Not connected to Neo4j")
        
        query = """
        MATCH (n)
        RETURN count(n) as count
        """
        
        try:
            async with self.driver.session() as session:
                result = await session.run(query)
                record = await result.single()
                count = record["count"] if record else 0
                logger.debug(f"Node count: {count}")
                return count
        except Exception as e:
            self._log_error("get_node_count", e)
            raise
