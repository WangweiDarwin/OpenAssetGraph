"""Graph data models"""
from enum import Enum
from pydantic import BaseModel, Field
from typing import Optional, Any


class NodeType(str, Enum):
    """Types of nodes in the graph"""
    DATABASE = "Database"
    TABLE = "Table"
    COLUMN = "Column"
    SERVICE = "Service"
    API = "API"
    FRONTEND_APP = "FrontendApp"
    COMPONENT = "Component"


class RelationshipType(str, Enum):
    """Types of relationships in the graph"""
    CONTAINS = "CONTAINS"
    CALLS = "CALLS"
    EXPOSES = "EXPOSES"
    REQUESTS = "REQUESTS"
    DERIVES = "DERIVES"
    REFERENCES = "REFERENCES"


class GraphNode(BaseModel):
    """Graph node model"""
    id: str
    label: str
    type: NodeType
    properties: dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    class Config:
        json_encoders = {
            'created_at': lambda v: v,
            'updated_at': lambda v: v
        }


class GraphRelationship(BaseModel):
    """Graph relationship model"""
    source_id: str
    target_id: str
    type: RelationshipType
    properties: dict[str, Any] = Field(default_factory=dict)


class TableInfo(BaseModel):
    """Table information model"""
    name: str
    schema: str
    type: str
    columns: list[dict[str, Any]] = Field(default_factory=list)
    indexes: list[dict[str, Any]] = Field(default_factory=list)
    foreign_keys: list[dict[str, Any]] = Field(default_factory=list)


class ScanResult(BaseModel):
    """Scan result model"""
    scan_type: str
    status: str
    items_scanned: int = 0
    errors: list[str] = Field(default_factory=list)
    duration_seconds: float = 0.0
