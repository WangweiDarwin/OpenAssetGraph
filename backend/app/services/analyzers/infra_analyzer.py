import re
import logging
from typing import Dict, List, Any, Optional
from . import (
    BaseAnalyzer, AnalysisResult, AnalyzedNode, AnalyzedEdge, NodeType,
    AnalyzerRegistry, parse_yaml
)

logger = logging.getLogger(__name__)


class InfrastructureAnalyzer(BaseAnalyzer):
    name = "infrastructure"
    priority = 20
    supported_files = [
        "docker-compose.yml", "docker-compose.yaml",
        "Dockerfile", "*.tf", "Chart.yaml", "values.yaml",
        ".gitlab-ci.yml", "Jenkinsfile"
    ]
    
    def can_analyze(self, file_path: str, content: str) -> bool:
        return self.matches_pattern(file_path, self.supported_files)
    
    def analyze(self, file_path: str, content: str) -> AnalysisResult:
        result = AnalysisResult()
        
        if "docker-compose" in file_path:
            self._analyze_docker_compose(content, result)
        elif file_path.endswith("Dockerfile"):
            self._analyze_dockerfile(content, result)
        elif file_path.endswith(".tf"):
            self._analyze_terraform(content, result)
        elif "gitlab-ci" in file_path:
            self._analyze_gitlab_ci(content, result)
        
        return result
    
    def _analyze_docker_compose(self, content: str, result: AnalysisResult):
        data = parse_yaml(content)
        if not data:
            return
        
        result.technologies.append("Docker")
        result.technologies.append("Docker Compose")
        
        services = data.get("services", {})
        
        for service_name, service_config in services.items():
            node = AnalyzedNode(
                id=f"service-{service_name}",
                label=service_name,
                type=NodeType.SERVICE,
                properties={
                    "docker_service": True,
                },
                source_file="docker-compose.yml"
            )
            
            image = service_config.get("image", "")
            if image:
                node.properties["image"] = image
                
                if "postgres" in image.lower() or "mysql" in image.lower() or "mariadb" in image.lower():
                    node.type = NodeType.DATABASE
                elif "mongo" in image.lower():
                    node.type = NodeType.DATABASE
                    node.properties["database_type"] = "MongoDB"
                elif "redis" in image.lower():
                    node.type = NodeType.CACHE
                elif "kafka" in image.lower() or "rabbitmq" in image.lower():
                    node.type = NodeType.MESSAGE_QUEUE
                elif "nginx" in image.lower() or "traefik" in image.lower():
                    node.type = NodeType.API
                    node.properties["role"] = "Load Balancer"
                elif "node" in image.lower() or "python" in image.lower() or "java" in image.lower():
                    node.type = NodeType.SERVICE
            
            build = service_config.get("build", {})
            if build:
                node.properties["build_context"] = build.get("context", ".")
            
            ports = service_config.get("ports", [])
            if ports:
                node.properties["ports"] = ports
            
            environment = service_config.get("environment", {})
            if environment:
                for key, value in environment.items() if isinstance(environment, dict) else []:
                    if "DATABASE" in key.upper() or "DB" in key.upper():
                        node.type = NodeType.SERVICE
            
            result.nodes.append(node)
        
        depends_on = service_config.get("depends_on", [])
        if isinstance(depends_on, list):
            for dep in depends_on:
                result.edges.append(AnalyzedEdge(
                    source=f"service-{service_name}",
                    target=f"service-{dep}",
                    type="DEPENDS_ON"
                ))
        elif isinstance(depends_on, dict):
            for dep in depends_on.keys():
                result.edges.append(AnalyzedEdge(
                    source=f"service-{service_name}",
                    target=f"service-{dep}",
                    type="DEPENDS_ON"
                ))
        
        networks = data.get("networks", {})
        if networks:
            result.metadata["networks"] = list(networks.keys())
        
        volumes = data.get("volumes", {})
        if volumes:
            result.metadata["volumes"] = list(volumes.keys())
    
    def _analyze_dockerfile(self, content: str, result: AnalysisResult):
        result.technologies.append("Docker")
        
        from_match = re.search(r"FROM\s+([^\s]+)", content)
        if from_match:
            base_image = from_match.group(1)
            result.metadata["base_image"] = base_image
            
            if "node" in base_image.lower():
                result.technologies.append("Node.js")
            elif "python" in base_image.lower():
                result.technologies.append("Python")
            elif "java" in base_image.lower() or "openjdk" in base_image.lower():
                result.technologies.append("Java")
            elif "golang" in base_image.lower() or "go" in base_image.lower():
                result.technologies.append("Go")
        
        expose_matches = re.findall(r"EXPOSE\s+(\d+)", content)
        if expose_matches:
            result.metadata["exposed_ports"] = expose_matches
        
        env_matches = re.findall(r"ENV\s+(\w+)=([^\s]+)", content)
        if env_matches:
            result.metadata["environment_vars"] = dict(env_matches)
    
    def _analyze_terraform(self, content: str, result: AnalysisResult):
        result.technologies.append("Terraform")
        
        resource_matches = re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', content)
        
        for resource_type, resource_name in resource_matches:
            node_type = NodeType.SERVICE
            
            if "db" in resource_type.lower() or "database" in resource_type.lower():
                node_type = NodeType.DATABASE
            elif "cache" in resource_type.lower() or "redis" in resource_type.lower():
                node_type = NodeType.CACHE
            elif "queue" in resource_type.lower() or "sqs" in resource_type.lower():
                node_type = NodeType.MESSAGE_QUEUE
            elif "storage" in resource_type.lower() or "s3" in resource_type.lower() or "bucket" in resource_type.lower():
                node_type = NodeType.STORAGE
            
            result.nodes.append(AnalyzedNode(
                id=f"tf-{resource_name}",
                label=resource_name,
                type=node_type,
                properties={
                    "resource_type": resource_type,
                    "managed_by": "Terraform"
                }
            ))
        
        provider_match = re.search(r'provider\s+"([^"]+)"', content)
        if provider_match:
            result.metadata["provider"] = provider_match.group(1)
    
    def _analyze_gitlab_ci(self, content: str, result: AnalysisResult):
        data = parse_yaml(content)
        if not data:
            return
        
        result.technologies.append("GitLab CI/CD")
        
        stages = data.get("stages", [])
        result.metadata["stages"] = stages
        
        for stage in stages:
            result.nodes.append(AnalyzedNode(
                id=f"stage-{stage}",
                label=stage,
                type=NodeType.SERVICE,
                properties={
                    "type": "CI Stage"
                }
            ))


AnalyzerRegistry.register(InfrastructureAnalyzer())
