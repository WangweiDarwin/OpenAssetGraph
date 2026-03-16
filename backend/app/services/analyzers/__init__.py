import os
import re
import json
import yaml
import toml
import logging
import xml.etree.ElementTree as ET
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class NodeType(Enum):
    SERVICE = "Service"
    DATABASE = "Database"
    API = "API"
    FRONTEND_APP = "FrontendApp"
    LIBRARY = "Library"
    TABLE = "Table"
    CACHE = "Cache"
    MESSAGE_QUEUE = "MessageQueue"
    STORAGE = "Storage"
    MODEL = "Model"
    DATASET = "Dataset"
    WORKFLOW = "Workflow"
    CONFIGURATION = "Configuration"
    UNKNOWN = "Unknown"


@dataclass
class AnalyzedNode:
    id: str
    label: str
    type: NodeType
    properties: Dict[str, Any] = field(default_factory=dict)
    source_file: Optional[str] = None


@dataclass
class AnalyzedEdge:
    source: str
    target: str
    type: str
    properties: Dict[str, Any] = field(default_factory=dict)


@dataclass
class AnalysisResult:
    nodes: List[AnalyzedNode] = field(default_factory=list)
    edges: List[AnalyzedEdge] = field(default_factory=list)
    technologies: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAnalyzer(ABC):
    name: str = "base"
    priority: int = 100
    supported_files: List[str] = []
    
    @abstractmethod
    def can_analyze(self, file_path: str, content: str) -> bool:
        pass
    
    @abstractmethod
    def analyze(self, file_path: str, content: str) -> AnalysisResult:
        pass
    
    def matches_pattern(self, file_path: str, patterns: List[str]) -> bool:
        for pattern in patterns:
            if pattern.startswith("*"):
                if file_path.endswith(pattern[1:]):
                    return True
            elif file_path.endswith(pattern):
                return True
        return False


class AnalyzerRegistry:
    _analyzers: Dict[str, BaseAnalyzer] = {}
    
    @classmethod
    def register(cls, analyzer: BaseAnalyzer):
        cls._analyzers[analyzer.name] = analyzer
        logger.info(f"Registered analyzer: {analyzer.name}")
    
    @classmethod
    def get_analyzer(cls, name: str) -> Optional[BaseAnalyzer]:
        return cls._analyzers.get(name)
    
    @classmethod
    def get_all_analyzers(cls) -> List[BaseAnalyzer]:
        return sorted(cls._analyzers.values(), key=lambda a: a.priority)
    
    @classmethod
    def find_analyzers_for_file(cls, file_path: str, content: str) -> List[BaseAnalyzer]:
        matching = []
        for analyzer in cls.get_all_analyzers():
            if analyzer.can_analyze(file_path, content):
                matching.append(analyzer)
        return matching


def parse_json(content: str) -> Optional[Dict]:
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        return None


def parse_yaml(content: str) -> Optional[Dict]:
    try:
        return yaml.safe_load(content)
    except yaml.YAMLError:
        return None


def parse_toml(content: str) -> Optional[Dict]:
    try:
        return toml.loads(content)
    except toml.TomlDecodeError:
        return None


def parse_xml(content: str) -> Optional[ET.Element]:
    try:
        return ET.fromstring(content)
    except ET.ParseError:
        return None


def extract_connection_strings(content: str) -> List[Dict[str, str]]:
    patterns = [
        (r"postgresql://[^\s\"']+", "PostgreSQL"),
        (r"mysql://[^\s\"']+", "MySQL"),
        (r"mongodb(\+srv)?://[^\s\"']+", "MongoDB"),
        (r"redis://[^\s\"']+", "Redis"),
        (r"amqp://[^\s\"']+", "RabbitMQ"),
        (r"kafka://[^\s\"']+", "Kafka"),
        (r"jdbc:[^\s\"']+", "JDBC"),
        (r"bolt://[^\s\"']+", "Neo4j"),
    ]
    
    connections = []
    for pattern, db_type in patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            connections.append({"type": db_type, "connection_string": match})
    
    return connections


def extract_api_endpoints(content: str, language: str) -> List[Dict[str, str]]:
    endpoints = []
    
    if language == "python":
        fastapi_pattern = r'@(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(fastapi_pattern, content, re.IGNORECASE):
            endpoints.append({"path": match.group(1), "framework": "FastAPI"})
        
        flask_pattern = r'@app\.route\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(flask_pattern, content):
            endpoints.append({"path": match.group(1), "framework": "Flask"})
    
    elif language == "javascript" or language == "typescript":
        express_pattern = r'(?:app|router)\.(?:get|post|put|delete|patch)\s*\(\s*["\']([^"\']+)["\']'
        for match in re.finditer(express_pattern, content):
            endpoints.append({"path": match.group(1), "framework": "Express"})
    
    elif language == "java":
        spring_pattern = r'@(?:GetMapping|PostMapping|PutMapping|DeleteMapping|PatchMapping|RequestMapping)\s*\(\s*(?:value\s*=\s*)?["\']([^"\']+)["\']'
        for match in re.finditer(spring_pattern, content):
            endpoints.append({"path": match.group(1), "framework": "Spring Boot"})
    
    return endpoints


from .dependency_analyzer import DependencyAnalyzer
from .infra_analyzer import InfrastructureAnalyzer
from .source_analyzer import SourceAnalyzer
from .fortran_analyzer import FortranAnalyzer
from .go_analyzer import GoAnalyzer
