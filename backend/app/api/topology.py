"""Topology API routes"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..services.topology_service import TopologyService
from ..services.graph_service import Neo4jService
from ..services.mock_data import mock_data_service
from ..core.config import settings


router = APIRouter(prefix="/api/topology", tags=["topology"])

USE_MOCK_DATA = True

def get_topology_service() -> TopologyService:
    """Get topology service instance"""
    neo4j_service = Neo4jService(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    return TopologyService(neo4j_service)


@router.get("")
async def get_topology(
    node_types: Optional[str] = Query(None, description="Comma-separated node types to filter"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of nodes to return")
):
    """Get full topology data"""
    if USE_MOCK_DATA:
        types_list = None
        if node_types:
            types_list = [t.strip() for t in node_types.split(",")]
        return await mock_data_service.get_topology(node_types=types_list, limit=limit)
    
    service = get_topology_service()
    
    try:
        await service.neo4j_service.connect()
        
        types_list = None
        if node_types:
            types_list = [t.strip() for t in node_types.split(",")]
        
        topology = await service.get_full_topology(node_types=types_list, limit=limit)
        
        return topology
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.neo4j_service.close()


@router.get("/search")
async def search_nodes(
    q: str = Query(..., description="Search query string"),
    node_types: Optional[str] = Query(None, description="Comma-separated node types to filter"),
    limit: int = Query(50, ge=1, le=200, description="Maximum number of results")
):
    """Search nodes by name or properties"""
    if USE_MOCK_DATA:
        types_list = None
        if node_types:
            types_list = [t.strip() for t in node_types.split(",")]
        return await mock_data_service.search_nodes(query=q, node_types=types_list, limit=limit)
    
    service = get_topology_service()
    
    try:
        await service.neo4j_service.connect()
        
        types_list = None
        if node_types:
            types_list = [t.strip() for t in node_types.split(",")]
        
        nodes = await service.search_nodes(query=q, node_types=types_list, limit=limit)
        
        return {
            "query": q,
            "results": nodes,
            "count": len(nodes)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.neo4j_service.close()


@router.get("/nodes/{node_id}")
async def get_node(node_id: str):
    """Get detailed information about a node"""
    if USE_MOCK_DATA:
        node = await mock_data_service.get_node(node_id)
        if not node:
            raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
        return node
    
    service = get_topology_service()
    
    try:
        await service.neo4j_service.connect()
        
        node = await service.get_node_details(node_id)
        
        if not node:
            raise HTTPException(status_code=404, detail=f"Node not found: {node_id}")
        
        return node
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.neo4j_service.close()


@router.get("/path")
async def find_path(
    start: str = Query(..., description="Start node ID"),
    end: str = Query(..., description="End node ID"),
    max_depth: int = Query(5, ge=1, le=10, description="Maximum search depth")
):
    """Find shortest path between two nodes"""
    if USE_MOCK_DATA:
        path = await mock_data_service.find_path(start_id=start, end_id=end, max_depth=max_depth)
        if not path:
            raise HTTPException(status_code=404, detail=f"No path found between {start} and {end}")
        return {
            "start_node_id": start,
            "end_node_id": end,
            "path": path,
            "path_length": len(path)
        }
    
    service = get_topology_service()
    
    try:
        await service.neo4j_service.connect()
        
        path = await service.find_path(
            start_node_id=start,
            end_node_id=end,
            max_depth=max_depth
        )
        
        if not path:
            raise HTTPException(
                status_code=404, 
                detail=f"No path found between {start} and {end}"
            )
        
        return {
            "start_node_id": start,
            "end_node_id": end,
            "path": path,
            "path_length": len(path)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.neo4j_service.close()


@router.get("/nodes/{node_id}/relationships")
async def get_node_relationships(
    node_id: str,
    relationship_type: Optional[str] = Query(None, description="Filter by relationship type"),
    direction: str = Query("both", regex="^(both|incoming|outgoing)$", description="Relationship direction")
):
    """Get relationships for a specific node"""
    if USE_MOCK_DATA:
        relationships = await mock_data_service.get_node_relationships(node_id)
        return {
            "node_id": node_id,
            "relationships": relationships,
            "count": len(relationships)
        }
    
    service = get_topology_service()
    
    try:
        await service.neo4j_service.connect()
        
        relationships = await service.get_node_relationships(
            node_id=node_id,
            relationship_type=relationship_type,
            direction=direction
        )
        
        return {
            "node_id": node_id,
            "relationships": relationships,
            "count": len(relationships)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.neo4j_service.close()


@router.get("/stats")
async def get_topology_stats():
    """Get topology statistics"""
    if USE_MOCK_DATA:
        return await mock_data_service.get_stats()
    
    service = get_topology_service()
    
    try:
        await service.neo4j_service.connect()
        
        topology = await service.get_full_topology(limit=10000)
        
        node_type_counts = {}
        for node in topology["nodes"]:
            node_type = node.get("type", "Unknown")
            node_type_counts[node_type] = node_type_counts.get(node_type, 0) + 1
        
        return {
            "total_nodes": topology["node_count"],
            "total_edges": topology["edge_count"],
            "node_types": node_type_counts
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await service.neo4j_service.close()
