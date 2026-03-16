import json
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


ARCHITECTURE_ANALYSIS_PROMPT = """You are a software architecture analyst. Analyze the following project information and generate a comprehensive architecture diagram.

Project Information:
- Repository: {repo_name}
- Technologies detected: {technologies}
- Dependencies: {dependencies}
- Infrastructure: {infrastructure}
- Source files analyzed: {source_count}

Key Files Content:
{key_files_content}

Please analyze the project and generate a comprehensive architecture diagram.

IMPORTANT GUIDELINES:
1. **Identify ALL components** from the provided information:
   - Docker Compose services (from docker-compose.yml) - Include ALL services defined
   - Backend services (from source code and dependencies)
   - Frontend applications (from package.json and source code)
   - Databases (from docker-compose.yml and connection strings) - Include ALL databases (PostgreSQL, Neo4j, MongoDB, MySQL, etc.)
   - Caches (from docker-compose.yml and dependencies) - Redis, Memcached
   - Message queues (from docker-compose.yml and dependencies)
   - API endpoints (from source code)
   - Reverse proxies / Load balancers (nginx, traefik)

2. **Node Types** (use these exact types):
   - Service: Backend services, microservices, Docker containers
   - FrontendApp: Web frontend applications
   - Database: SQL/NoSQL databases (PostgreSQL, MySQL, MongoDB, Neo4j, etc.)
   - Cache: Redis, Memcached
   - MessageQueue: Kafka, RabbitMQ, SQS
   - API: REST/GraphQL API endpoints, Reverse proxies (nginx)
   - Library: Third-party libraries (DO NOT include as nodes unless critical)
   - Storage: Object storage (S3, OSS)

3. **Edge Types** (use these exact types):
   - CALLS: Service calls another service/database/cache
   - DEPENDS_ON: Service depends on another service
   - EXPOSES: API exposes a service, nginx routes to backend
   - CONTAINS: Service contains sub-components
   - PUBLISHES: Service publishes to message queue
   - SUBSCRIBES: Service subscribes to message queue

4. **Be specific about technologies**:
   - Instead of "Database", specify "PostgreSQL", "MongoDB", "Neo4j", etc.
   - Instead of "Cache", specify "Redis"
   - Include version numbers if available

5. **Identify architecture patterns**:
   - Microservices: Multiple independent services
   - Monolithic: Single backend service
   - Containerized: Uses Docker/Docker Compose
   - Serverless: Uses cloud functions

6. **IMPORTANT: Include ALL Docker Compose services**:
   - If docker-compose.yml defines nginx, backend, frontend, neo4j, postgres, redis
   - Then ALL of these should appear as nodes in the architecture

Return a JSON object with the following structure:
{{
  "nodes": [
    {{
      "id": "unique-id",
      "label": "Display Name",
      "type": "Service|Database|API|FrontendApp|Cache|MessageQueue|Storage",
      "properties": {{
        "technology": "specific technology name",
        "port": "port number if applicable",
        "description": "brief description of this component's role"
      }}
    }}
  ],
  "edges": [
    {{
      "source": "source-node-id",
      "target": "target-node-id", 
      "type": "CALLS|DEPENDS_ON|EXPOSES|CONTAINS|PUBLISHES|SUBSCRIBES"
    }}
  ],
  "architecture_type": "microservices|monolithic|serverless|containerized",
  "description": "A detailed description of the overall architecture",
  "technology_stack": {{
    "backend": ["list of backend technologies"],
    "frontend": ["list of frontend technologies"],
    "databases": ["list of ALL databases used"],
    "infrastructure": ["list of infrastructure tools"]
  }},
  "recommendations": ["list of architecture improvement recommendations"]
}}
"""


@dataclass
class ArchitectureAnalysis:
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    description: str
    recommendations: List[str]
    architecture_type: str = "unknown"
    technology_stack: Dict[str, List[str]] = None
    
    def __post_init__(self):
        if self.technology_stack is None:
            self.technology_stack = {}


class AIArchitectService:
    def __init__(self, llm_service):
        self.llm_service = llm_service
    
    async def analyze_project(
        self,
        repo_name: str,
        technologies: List[str],
        dependencies: Dict[str, List[str]],
        infrastructure: Dict[str, Any],
        key_files: Dict[str, str],
        source_count: int
    ) -> Optional[ArchitectureAnalysis]:
        key_files_content = self._format_key_files(key_files)
        
        prompt = ARCHITECTURE_ANALYSIS_PROMPT.format(
            repo_name=repo_name,
            technologies=", ".join(technologies) if technologies else "Unknown",
            dependencies=json.dumps(dependencies, indent=2),
            infrastructure=json.dumps(infrastructure, indent=2),
            source_count=source_count,
            key_files_content=key_files_content
        )
        
        try:
            from .llm import Message, MessageRole
            messages = [Message(role=MessageRole.USER, content=prompt)]
            response = await self.llm_service.chat(messages)
            result = self._parse_response(response.content)
            if result:
                return result
            
            return self._generate_fallback_architecture(
                repo_name, technologies, dependencies, infrastructure
            )
            
        except Exception as e:
            logger.error(f"AI architecture analysis failed: {e}")
            return self._generate_fallback_architecture(
                repo_name, technologies, dependencies, infrastructure
            )
    
    def _format_key_files(self, key_files: Dict[str, str]) -> str:
        content_parts = []
        
        for path, content in list(key_files.items())[:10]:
            truncated = content[:2000] if len(content) > 2000 else content
            content_parts.append(f"--- {path} ---\n{truncated}\n")
        
        return "\n".join(content_parts)
    
    def _parse_response(self, response: str) -> Optional[ArchitectureAnalysis]:
        try:
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            
            if json_start != -1 and json_end > json_start:
                json_str = response[json_start:json_end]
                data = json.loads(json_str)
                
                return ArchitectureAnalysis(
                    nodes=data.get("nodes", []),
                    edges=data.get("edges", []),
                    description=data.get("description", ""),
                    recommendations=data.get("recommendations", []),
                    architecture_type=data.get("architecture_type", "unknown"),
                    technology_stack=data.get("technology_stack", {})
                )
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse AI response as JSON: {e}")
        
        return None
    
    def _generate_fallback_architecture(
        self,
        repo_name: str,
        technologies: List[str],
        dependencies: Dict[str, List[str]],
        infrastructure: Dict[str, Any]
    ) -> ArchitectureAnalysis:
        nodes = []
        edges = []
        tech_stack = {
            "backend": [],
            "frontend": [],
            "databases": [],
            "infrastructure": []
        }
        
        has_backend = any(t in technologies for t in [
            "Python", "Java", "Go", "Node.js", "FastAPI", "Flask", 
            "Spring Boot", "Express.js", "Django"
        ])
        has_frontend = any(t in technologies for t in [
            "React", "Vue.js", "Angular", "TypeScript", "JavaScript"
        ])
        
        backend_tech = None
        if has_backend:
            backend_tech = next((t for t in technologies if t in [
                "FastAPI", "Flask", "Django", "Spring Boot", "Express.js", "Gin"
            ]), "Python" if "Python" in technologies else "Backend")
            tech_stack["backend"].append(backend_tech)
            
            nodes.append({
                "id": f"{repo_name}-backend",
                "label": f"{repo_name} Backend",
                "type": "Service",
                "properties": {
                    "technology": backend_tech,
                    "description": f"Main backend service using {backend_tech}"
                }
            })
        
        frontend_tech = None
        if has_frontend:
            frontend_tech = next((t for t in technologies if t in [
                "React", "Vue.js", "Angular", "Next.js"
            ]), "JavaScript")
            tech_stack["frontend"].append(frontend_tech)
            
            nodes.append({
                "id": f"{repo_name}-frontend",
                "label": f"{repo_name} Frontend",
                "type": "FrontendApp",
                "properties": {
                    "technology": frontend_tech,
                    "description": f"Frontend application using {frontend_tech}"
                }
            })
            
            if has_backend:
                edges.append({
                    "source": f"{repo_name}-frontend",
                    "target": f"{repo_name}-backend",
                    "type": "CALLS"
                })
        
        db_technologies = ["PostgreSQL", "MySQL", "MongoDB", "Neo4j", "Redis", "SQLite"]
        for db_tech in db_technologies:
            if db_tech in technologies:
                tech_stack["databases"].append(db_tech)
                
                node_type = "Cache" if db_tech == "Redis" else "Database"
                nodes.append({
                    "id": f"{repo_name}-{db_tech.lower()}",
                    "label": f"{repo_name} {db_tech}",
                    "type": node_type,
                    "properties": {
                        "technology": db_tech,
                        "description": f"{'Cache layer' if db_tech == 'Redis' else f'Primary database ({db_tech})'}"
                    }
                })
                
                if has_backend:
                    edges.append({
                        "source": f"{repo_name}-backend",
                        "target": f"{repo_name}-{db_tech.lower()}",
                        "type": "CALLS"
                    })
        
        if infrastructure.get("services"):
            for service_name, service_info in infrastructure.get("services", {}).items():
                if service_name not in ["backend", "frontend"]:
                    service_type = self._infer_service_type(service_name, service_info)
                    tech_stack["infrastructure"].append(service_name)
                    
                    nodes.append({
                        "id": f"service-{service_name}",
                        "label": service_name.capitalize(),
                        "type": service_type,
                        "properties": {
                            "technology": service_info.get("image", service_name),
                            "description": f"Docker service: {service_name}"
                        }
                    })
        
        if has_backend:
            nodes.append({
                "id": f"{repo_name}-api",
                "label": f"{repo_name} API",
                "type": "API",
                "properties": {
                    "description": "REST API endpoints"
                }
            })
            
            edges.append({
                "source": f"{repo_name}-api",
                "target": f"{repo_name}-backend",
                "type": "EXPOSES"
            })
        
        if not nodes:
            nodes.append({
                "id": f"{repo_name}-main",
                "label": repo_name,
                "type": "Service",
                "properties": {
                    "description": "Main application component"
                }
            })
        
        architecture_type = "unknown"
        if len([n for n in nodes if n["type"] == "Service"]) > 1:
            architecture_type = "microservices"
        elif has_backend and has_frontend:
            architecture_type = "monolithic"
        if infrastructure.get("services"):
            architecture_type = "containerized"
        
        description = f"{repo_name} is a {architecture_type} software project"
        if technologies:
            description += f" built with {', '.join(technologies[:5])}"
        
        return ArchitectureAnalysis(
            nodes=nodes,
            edges=edges,
            description=description,
            recommendations=[],
            architecture_type=architecture_type,
            technology_stack=tech_stack
        )
    
    def _infer_service_type(self, service_name: str, service_info: Dict) -> str:
        name_lower = service_name.lower()
        image = service_info.get("image", "").lower()
        
        if "postgres" in name_lower or "postgres" in image or "mysql" in image:
            return "Database"
        elif "mongo" in name_lower or "mongo" in image:
            return "Database"
        elif "redis" in name_lower or "redis" in image:
            return "Cache"
        elif "kafka" in name_lower or "rabbitmq" in name_lower:
            return "MessageQueue"
        elif "nginx" in name_lower or "traefik" in name_lower:
            return "API"
        elif "frontend" in name_lower or "web" in name_lower:
            return "FrontendApp"
        else:
            return "Service"
