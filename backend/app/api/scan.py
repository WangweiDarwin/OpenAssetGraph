"""Project scan API routes"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import re
import logging

from ..services.mock_data import mock_data_service
from ..services.graph_service import Neo4jService
from ..services.github_service import GitHubService, GitHubRepo
from ..services.analyzers import AnalyzerRegistry, AnalysisResult
from ..services.analyzers.dependency_analyzer import DependencyAnalyzer
from ..services.analyzers.infra_analyzer import InfrastructureAnalyzer
from ..services.analyzers.source_analyzer import SourceAnalyzer
from ..services.analyzers.fortran_analyzer import FortranAnalyzer
from ..services.analyzers.go_analyzer import GoAnalyzer
from ..services.ai_architect import AIArchitectService, ArchitectureAnalysis
from ..services.llm import LLMFactory
from ..models.graph import GraphNode, GraphRelationship, NodeType, RelationshipType
from ..core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/scan", tags=["scan"])


AnalyzerRegistry.register(DependencyAnalyzer())
AnalyzerRegistry.register(InfrastructureAnalyzer())
AnalyzerRegistry.register(SourceAnalyzer())
AnalyzerRegistry.register(FortranAnalyzer())
AnalyzerRegistry.register(GoAnalyzer())


class GitHubProjectRequest(BaseModel):
    """Request to scan a GitHub project"""
    repo_url: str
    branch: Optional[str] = "main"
    scan_type: str = "architecture"


class ManualNodeRequest(BaseModel):
    """Request to add nodes manually"""
    nodes: List[dict]
    edges: Optional[List[dict]] = None


class ScanResult(BaseModel):
    """Result of a project scan"""
    status: str
    nodes_added: int
    edges_added: int
    message: str
    project_id: Optional[str] = None


def get_neo4j_service() -> Neo4jService:
    """Create a Neo4jService instance with settings"""
    return Neo4jService(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )


def parse_node_type(type_str: str) -> NodeType:
    """Parse node type string to NodeType enum"""
    type_mapping = {
        "Database": NodeType.DATABASE,
        "Table": NodeType.TABLE,
        "Column": NodeType.COLUMN,
        "Service": NodeType.SERVICE,
        "API": NodeType.API,
        "FrontendApp": NodeType.FRONTEND_APP,
        "Component": NodeType.COMPONENT,
        "Library": NodeType.LIBRARY,
        "Cache": NodeType.CACHE,
        "MessageQueue": NodeType.MESSAGE_QUEUE,
        "Storage": NodeType.STORAGE,
        "Model": NodeType.MODEL,
        "Dataset": NodeType.DATASET,
        "Workflow": NodeType.WORKFLOW,
        "Configuration": NodeType.CONFIGURATION,
    }
    return type_mapping.get(type_str, NodeType.SERVICE)


def parse_relationship_type(type_str: str) -> RelationshipType:
    """Parse relationship type string to RelationshipType enum"""
    type_mapping = {
        "CONTAINS": RelationshipType.CONTAINS,
        "CALLS": RelationshipType.CALLS,
        "EXPOSES": RelationshipType.EXPOSES,
        "REQUESTS": RelationshipType.REQUESTS,
        "DERIVES": RelationshipType.DERIVES,
        "REFERENCES": RelationshipType.REFERENCES,
    }
    return type_mapping.get(type_str, RelationshipType.CALLS)


def extract_repo_info(url: str) -> dict:
    """Extract owner and repo name from GitHub URL"""
    patterns = [
        r"github\.com[/:]([^/]+)/([^/]+?)(?:\.git)?/?$",
        r"github\.com/([^/]+)/([^/]+)",
    ]
    for pattern in patterns:
        match = re.search(pattern, url, re.IGNORECASE)
        if match:
            return {"owner": match.group(1), "repo": match.group(2)}
    return {"owner": None, "repo": None}


async def store_nodes_to_neo4j(service: Neo4jService, nodes: List[dict], project_name: str = None) -> int:
    """Store nodes to Neo4j and return count of nodes created"""
    graph_nodes = []
    for node in nodes:
        node_type = parse_node_type(node.get("type", "Service"))
        properties = node.get("properties", {})
        if project_name:
            properties["project"] = project_name
        graph_node = GraphNode(
            id=node.get("id"),
            label=node.get("label", node.get("id")),
            type=node_type,
            properties=properties
        )
        graph_nodes.append(graph_node)
    
    if graph_nodes:
        return await service.batch_create_nodes(graph_nodes)
    return 0


async def store_edges_to_neo4j(service: Neo4jService, edges: List[dict]) -> int:
    """Store edges to Neo4j and return count of relationships created"""
    relationships = []
    for edge in edges:
        rel_type = parse_relationship_type(edge.get("type", "CALLS"))
        relationship = GraphRelationship(
            source_id=edge.get("source"),
            target_id=edge.get("target"),
            type=rel_type,
            properties=edge.get("properties", {})
        )
        relationships.append(relationship)
    
    if relationships:
        return await service.batch_create_relationships(relationships)
    return 0


@router.post("/github", response_model=ScanResult)
async def scan_github_project(request: GitHubProjectRequest):
    """Scan a GitHub repository and import architecture"""
    try:
        repo_info = extract_repo_info(request.repo_url)
        
        if not repo_info.get("owner") or not repo_info.get("repo"):
            raise HTTPException(status_code=400, detail="Invalid GitHub URL")
        
        project_id = repo_info.get("repo", "default").lower().replace("-", "_").replace(".", "_")
        
        logger.info(f"Starting scan for project: {project_id}")
        
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()
        
        try:
            await neo4j_service.clear_project_data(project_id)
            
            nodes, edges = await analyze_github_repo(
                repo_info.get("owner", ""),
                repo_info.get("repo", ""),
                request.branch,
                project_id
            )
            
            nodes_added = await store_nodes_to_neo4j(neo4j_service, nodes, project_id)
            edges_added = await store_edges_to_neo4j(neo4j_service, edges)
            
            return ScanResult(
                status="success",
                nodes_added=nodes_added,
                edges_added=edges_added,
                message=f"Successfully scanned {project_id}: {nodes_added} nodes, {edges_added} edges",
                project_id=project_id
            )
            
        finally:
            await neo4j_service.close()
        
    except Exception as e:
        logger.error(f"Scan failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def analyze_github_repo(
    owner: str, 
    repo: str, 
    branch: str,
    project_id: str
) -> tuple[List[dict], List[dict]]:
    """Analyze a GitHub repository using static analysis and AI"""
    
    github_service = GitHubService(token=settings.github_token)
    
    try:
        repo_info = await github_service.get_repo_info(owner, repo)
        if not repo_info:
            logger.warning(f"Could not get repo info for {owner}/{repo}")
            return generate_default_architecture(project_id), []
        
        logger.info(f"Analyzing repository: {owner}/{repo} (branch: {branch or repo_info.default_branch})")
        
        files = await github_service.get_tree(owner, repo, branch or repo_info.default_branch)
        if not files:
            logger.warning(f"No files found in {owner}/{repo}")
            return generate_default_architecture(project_id), []
        
        key_files = github_service.find_key_files(files)
        logger.info(f"Found key files - dependencies: {len(key_files['dependencies'])}, infrastructure: {len(key_files['infrastructure'])}, source: {len(key_files['source'])}, config: {len(key_files['config'])}")
        
        all_results = AnalysisResult()
        
        all_results.nodes.append({
            "id": f"project-{project_id}",
            "label": repo_info.name or project_id,
            "type": "Service",
            "properties": {
                "type": "Project",
                "description": repo_info.description or "",
                "default_branch": repo_info.default_branch,
                "owner": owner
            }
        })
        
        dep_paths = key_files.get("dependencies", [])[:10]
        if dep_paths:
            logger.info(f"Fetching {len(dep_paths)} dependency files...")
            dep_contents = await github_service.get_multiple_files(owner, repo, dep_paths, branch)
            for path, content in dep_contents.items():
                analyzers = AnalyzerRegistry.find_analyzers_for_file(path, content)
                for analyzer in analyzers:
                    try:
                        result = analyzer.analyze(path, content)
                        all_results.nodes.extend(result.nodes)
                        all_results.edges.extend(result.edges)
                        all_results.technologies.extend(result.technologies)
                        all_results.dependencies.update(result.dependencies)
                        logger.info(f"Analyzed {path} with {analyzer.name}: {len(result.nodes)} nodes")
                    except Exception as e:
                        logger.warning(f"Analyzer {analyzer.name} failed on {path}: {e}")
        
        infra_paths = key_files.get("infrastructure", [])[:10]
        if infra_paths:
            logger.info(f"Fetching {len(infra_paths)} infrastructure files...")
            infra_contents = await github_service.get_multiple_files(owner, repo, infra_paths, branch)
            for path, content in infra_contents.items():
                analyzers = AnalyzerRegistry.find_analyzers_for_file(path, content)
                for analyzer in analyzers:
                    try:
                        result = analyzer.analyze(path, content)
                        all_results.nodes.extend(result.nodes)
                        all_results.edges.extend(result.edges)
                        all_results.technologies.extend(result.technologies)
                    except Exception as e:
                        logger.warning(f"Analyzer {analyzer.name} failed on {path}: {e}")
        
        config_paths = key_files.get("config", [])[:5]
        if config_paths:
            logger.info(f"Fetching {len(config_paths)} config files...")
            config_contents = await github_service.get_multiple_files(owner, repo, config_paths, branch)
            for path, content in config_contents.items():
                analyzers = AnalyzerRegistry.find_analyzers_for_file(path, content)
                for analyzer in analyzers:
                    try:
                        result = analyzer.analyze(path, content)
                        all_results.nodes.extend(result.nodes)
                        all_results.edges.extend(result.edges)
                        all_results.technologies.extend(result.technologies)
                    except Exception as e:
                        logger.debug(f"Analyzer {analyzer.name} failed on {path}: {e}")
        
        source_paths = key_files.get("source", [])[:100]
        if source_paths:
            logger.info(f"Fetching {len(source_paths)} source files...")
            source_contents = await github_service.get_multiple_files(owner, repo, source_paths, branch, batch_size=10)
            for path, content in source_contents.items():
                analyzers = AnalyzerRegistry.find_analyzers_for_file(path, content)
                for analyzer in analyzers:
                    try:
                        result = analyzer.analyze(path, content)
                        all_results.nodes.extend(result.nodes)
                        all_results.edges.extend(result.edges)
                        all_results.technologies.extend(result.technologies)
                    except Exception as e:
                        logger.debug(f"Analyzer {analyzer.name} failed on {path}: {e}")
        
        unique_technologies = list(dict.fromkeys(all_results.technologies))
        logger.info(f"Detected technologies: {unique_technologies}")
        
        directories = set()
        for f in files:
            if f.type == "tree":
                dir_path = f.path
                parts = dir_path.split("/")
                if len(parts) <= 3:
                    directories.add("/".join(parts))
        
        for dir_path in sorted(directories):
            dir_name = dir_path.split("/")[-1]
            if dir_name not in [".git", ".github", "node_modules", "vendor", "dist", "build", "target"]:
                all_results.nodes.append({
                    "id": f"module-{dir_path.replace('/', '-')}",
                    "label": dir_name,
                    "type": "Component",
                    "properties": {
                        "path": dir_path,
                        "type": "Module"
                    }
                })
        
        infra_info = {
            "files": infra_paths,
            "technologies": unique_technologies,
            "services": {},
            "directories": list(directories)[:20]
        }
        
        for node in all_results.nodes:
            if isinstance(node, dict):
                if node.get("id", "").startswith("service-"):
                    service_name = node.get("id", "").replace("service-", "")
                    infra_info["services"][service_name] = node.get("properties", {})
            else:
                if node.id.startswith("service-"):
                    service_name = node.id.replace("service-", "")
                    infra_info["services"][service_name] = node.properties
        
        if settings.llm_provider and settings.llm_model:
            try:
                llm_service = LLMFactory.create_from_settings(settings)
                ai_architect = AIArchitectService(llm_service)
                
                key_file_contents = {}
                dep_contents = await github_service.get_multiple_files(owner, repo, dep_paths[:5], branch)
                key_file_contents.update(dep_contents)
                
                ai_analysis = await ai_architect.analyze_project(
                    repo_name=project_id,
                    technologies=unique_technologies,
                    dependencies=all_results.dependencies,
                    infrastructure=infra_info,
                    key_files=key_file_contents,
                    source_count=len(source_paths)
                )
                
                if ai_analysis:
                    for node in ai_analysis.nodes:
                        if "project" not in node.get("properties", {}):
                            node["properties"] = node.get("properties", {})
                            node["properties"]["project"] = project_id
                        all_results.nodes.append(node)
                    
                    for edge in ai_analysis.edges:
                        all_results.edges.append(edge)
                    logger.info(f"AI analysis added {len(ai_analysis.nodes)} nodes and {len(ai_analysis.edges)} edges")
            except Exception as e:
                logger.warning(f"AI analysis failed: {e}")
        
        if not all_results.nodes:
            logger.warning(f"No nodes extracted from {owner}/{repo}, using default architecture")
            return generate_default_architecture(project_id), []
        
        seen_node_ids = set()
        unique_nodes = []
        for node in all_results.nodes:
            if isinstance(node, dict):
                node_id = node.get("id", f"node-{len(unique_nodes)}")
            else:
                node_id = node.id
            
            if node_id not in seen_node_ids:
                seen_node_ids.add(node_id)
                if isinstance(node, dict):
                    unique_nodes.append({
                        "id": node_id,
                        "label": node.get("label", "Unknown"),
                        "type": node.get("type", "Service"),
                        "properties": node.get("properties", {})
                    })
                else:
                    unique_nodes.append({
                        "id": node.id,
                        "label": node.label,
                        "type": node.type.value if hasattr(node.type, 'value') else str(node.type),
                        "properties": node.properties
                    })
        
        seen_edges = set()
        unique_edges = []
        for edge in all_results.edges:
            if isinstance(edge, dict):
                edge_key = f"{edge.get('source', '')}-{edge.get('target', '')}-{edge.get('type', 'CALLS')}"
            else:
                edge_key = f"{edge.source}-{edge.target}-{edge.type}"
            
            if edge_key not in seen_edges:
                seen_edges.add(edge_key)
                if isinstance(edge, dict):
                    unique_edges.append({
                        "source": edge.get("source", ""),
                        "target": edge.get("target", ""),
                        "type": edge.get("type", "CALLS"),
                        "properties": edge.get("properties", {})
                    })
                else:
                    unique_edges.append({
                        "source": edge.source,
                        "target": edge.target,
                        "type": edge.type,
                        "properties": edge.properties
                    })
        
        logger.info(f"Analysis complete: {len(unique_nodes)} nodes, {len(unique_edges)} edges")
        return unique_nodes, unique_edges
        
    except Exception as e:
        logger.error(f"Error analyzing repository {owner}/{repo}: {e}")
        return generate_default_architecture(project_id), []
    finally:
        await github_service.close()


def generate_default_architecture(project_id: str) -> List[dict]:
    """Generate a default architecture when analysis fails"""
    return [
        {"id": f"project-{project_id}", "label": f"{project_id} Project", "type": "Service", "properties": {"type": "Project"}},
        {"id": f"{project_id}-main", "label": f"{project_id} App", "type": "Service", "properties": {}},
        {"id": f"{project_id}-db", "label": "Database", "type": "Database", "properties": {}},
        {"id": f"{project_id}-api", "label": "API", "type": "API", "properties": {}},
    ]


@router.post("/manual", response_model=ScanResult)
async def add_manual_nodes(request: ManualNodeRequest):
    """Manually add nodes and edges to the topology"""
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()
        
        try:
            nodes_added = await store_nodes_to_neo4j(neo4j_service, request.nodes)
            
            edges_added = 0
            if request.edges:
                edges_added = await store_edges_to_neo4j(neo4j_service, request.edges)
            
            return ScanResult(
                status="success",
                nodes_added=nodes_added,
                edges_added=edges_added,
                message=f"Added {nodes_added} nodes and {edges_added} edges"
            )
            
        finally:
            await neo4j_service.close()
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear")
async def clear_topology():
    """Clear all topology data"""
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()
        
        try:
            success = await neo4j_service.clear_all_data()
            if success:
                return {"status": "success", "message": "Topology cleared"}
            else:
                raise HTTPException(status_code=500, detail="Failed to clear topology")
        finally:
            await neo4j_service.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates")
async def get_scan_templates():
    """Get available scan templates"""
    return [
        {
            "id": "spring-boot",
            "name": "Spring Boot Microservices",
            "description": "Scan Spring Boot microservices architecture",
            "node_types": ["Service", "API", "Database", "Library", "FrontendApp"],
        },
        {
            "id": "react-frontend",
            "name": "React Frontend",
            "description": "Scan React frontend application",
            "node_types": ["FrontendApp", "Component", "API", "Service"],
        },
        {
            "id": "full-stack",
            "name": "Full Stack Application",
            "description": "Scan full stack application with frontend and backend",
            "node_types": ["Service", "API", "Database", "FrontendApp", "Component", "Table"],
        },
        {
            "id": "go-microservice",
            "name": "Go Microservice",
            "description": "Scan Go microservice architecture",
            "node_types": ["Service", "API", "Library", "Component"],
        },
    ]


@router.delete("/project/{project_name}")
async def delete_project(project_name: str):
    """Delete a specific project and all its nodes"""
    try:
        neo4j_service = get_neo4j_service()
        await neo4j_service.connect()
        
        try:
            query = """
            MATCH (n {project: $project_name})
            DETACH DELETE n
            RETURN count(n) as deleted_count
            """
            result = await neo4j_service.execute_query(query, {"project_name": project_name})
            deleted_count = result[0]["deleted_count"] if result else 0
            
            return {
                "status": "success",
                "message": f"项目 '{project_name}' 已删除",
                "nodes_deleted": deleted_count
            }
        finally:
            await neo4j_service.close()
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
