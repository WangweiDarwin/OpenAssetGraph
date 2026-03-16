import re
import logging
from typing import Dict, List, Any, Optional
from . import (
    BaseAnalyzer, AnalysisResult, AnalyzedNode, AnalyzedEdge, NodeType,
    AnalyzerRegistry, extract_connection_strings, extract_api_endpoints
)

logger = logging.getLogger(__name__)


class SourceAnalyzer(BaseAnalyzer):
    name = "source"
    priority = 30
    supported_files = [
        "*.py", "*.js", "*.ts", "*.java", "*.go", "*.rs", "*.php", "*.rb", "*.cs"
    ]
    
    def can_analyze(self, file_path: str, content: str) -> bool:
        return self.matches_pattern(file_path, self.supported_files)
    
    def analyze(self, file_path: str, content: str) -> AnalysisResult:
        result = AnalysisResult()
        
        if file_path.endswith(".py"):
            self._analyze_python(file_path, content, result)
        elif file_path.endswith(".js") or file_path.endswith(".ts"):
            self._analyze_javascript(file_path, content, result)
        elif file_path.endswith(".java"):
            self._analyze_java(file_path, content, result)
        elif file_path.endswith(".go"):
            self._analyze_go(file_path, content, result)
        
        return result
    
    def _analyze_python(self, file_path: str, content: str, result: AnalysisResult):
        result.technologies.append("Python")
        
        endpoints = extract_api_endpoints(content, "python")
        for endpoint in endpoints:
            result.nodes.append(AnalyzedNode(
                id=f"api-{endpoint['path'].replace('/', '_')}",
                label=endpoint['path'],
                type=NodeType.API,
                properties={
                    "framework": endpoint.get("framework", "Unknown"),
                    "file": file_path
                },
                source_file=file_path
            ))
        
        connections = extract_connection_strings(content)
        for conn in connections:
            result.nodes.append(AnalyzedNode(
                id=f"db-{conn['type'].lower()}",
                label=conn['type'],
                type=NodeType.DATABASE,
                properties={
                    "connection_type": conn['type'],
                    "file": file_path
                },
                source_file=file_path
            ))
        
        fastapi_imports = re.findall(r"from\s+fastapi\s+import|import\s+fastapi", content)
        if fastapi_imports:
            result.technologies.append("FastAPI")
        
        flask_imports = re.findall(r"from\s+flask\s+import|import\s+flask", content)
        if flask_imports:
            result.technologies.append("Flask")
        
        django_imports = re.findall(r"from\s+django\s+import|import\s+django", content)
        if django_imports:
            result.technologies.append("Django")
        
        sqlalchemy_imports = re.findall(r"from\s+sqlalchemy\s+import|import\s+sqlalchemy", content)
        if sqlalchemy_imports:
            result.technologies.append("SQLAlchemy")
        
        neo4j_imports = re.findall(r"from\s+neo4j\s+import|import\s+neo4j", content)
        if neo4j_imports:
            result.technologies.append("Neo4j Driver")
        
        redis_imports = re.findall(r"import\s+redis|from\s+redis\s+import", content)
        if redis_imports:
            result.technologies.append("Redis")
        
        mongo_imports = re.findall(r"from\s+pymongo\s+import|import\s+pymongo", content)
        if mongo_imports:
            result.technologies.append("MongoDB")
    
    def _analyze_javascript(self, file_path: str, content: str, result: AnalysisResult):
        if file_path.endswith(".ts"):
            result.technologies.append("TypeScript")
        else:
            result.technologies.append("JavaScript")
        
        endpoints = extract_api_endpoints(content, "javascript")
        for endpoint in endpoints:
            result.nodes.append(AnalyzedNode(
                id=f"api-{endpoint['path'].replace('/', '_')}",
                label=endpoint['path'],
                type=NodeType.API,
                properties={
                    "framework": endpoint.get("framework", "Unknown"),
                    "file": file_path
                },
                source_file=file_path
            ))
        
        connections = extract_connection_strings(content)
        for conn in connections:
            result.nodes.append(AnalyzedNode(
                id=f"db-{conn['type'].lower()}",
                label=conn['type'],
                type=NodeType.DATABASE,
                properties={
                    "connection_type": conn['type'],
                    "file": file_path
                },
                source_file=file_path
            ))
        
        react_patterns = [
            r"import\s+.*from\s+['\"]react['\"]",
            r"import\s+React",
            r"@jsx",
        ]
        for pattern in react_patterns:
            if re.search(pattern, content):
                result.technologies.append("React")
                break
        
        vue_patterns = [
            r"import\s+.*from\s+['\"]vue['\"]",
            r"createApp\s*\(",
            r"defineComponent",
        ]
        for pattern in vue_patterns:
            if re.search(pattern, content):
                result.technologies.append("Vue.js")
                break
        
        express_patterns = [
            r"require\s*\(\s*['\"]express['\"]\s*\)",
            r"import\s+.*from\s+['\"]express['\"]",
            r"express\(\)",
        ]
        for pattern in express_patterns:
            if re.search(pattern, content):
                result.technologies.append("Express.js")
                break
        
        nextjs_patterns = [
            r"from\s+['\"]next/",
            r"getServerSideProps",
            r"getStaticProps",
        ]
        for pattern in nextjs_patterns:
            if re.search(pattern, content):
                result.technologies.append("Next.js")
                break
    
    def _analyze_java(self, file_path: str, content: str, result: AnalysisResult):
        result.technologies.append("Java")
        
        endpoints = extract_api_endpoints(content, "java")
        for endpoint in endpoints:
            result.nodes.append(AnalyzedNode(
                id=f"api-{endpoint['path'].replace('/', '_')}",
                label=endpoint['path'],
                type=NodeType.API,
                properties={
                    "framework": endpoint.get("framework", "Unknown"),
                    "file": file_path
                },
                source_file=file_path
            ))
        
        spring_patterns = [
            r"@SpringBootApplication",
            r"@RestController",
            r"@Controller",
            r"@Service",
            r"@Repository",
            r"@Component",
        ]
        for pattern in spring_patterns:
            if re.search(pattern, content):
                if "Spring Boot" not in result.technologies:
                    result.technologies.append("Spring Boot")
                break
        
        package_match = re.search(r"package\s+([\w.]+);", content)
        if package_match:
            result.metadata["package"] = package_match.group(1)
        
        class_match = re.search(r"class\s+(\w+)", content)
        if class_match:
            result.metadata["class"] = class_match.group(1)
    
    def _analyze_go(self, file_path: str, content: str, result: AnalysisResult):
        result.technologies.append("Go")
        
        package_match = re.search(r"package\s+(\w+)", content)
        if package_match:
            result.metadata["package"] = package_match.group(1)
        
        gin_patterns = [
            r"gin\.",
            r"github.com/gin-gonic/gin",
        ]
        for pattern in gin_patterns:
            if re.search(pattern, content):
                result.technologies.append("Gin")
                break
        
        echo_patterns = [
            r"echo\.",
            r"github.com/labstack/echo",
        ]
        for pattern in echo_patterns:
            if re.search(pattern, content):
                result.technologies.append("Echo")
                break
        
        http_patterns = [
            r"http\.ListenAndServe",
            r"http\.HandleFunc",
        ]
        for pattern in http_patterns:
            if re.search(pattern, content):
                result.technologies.append("net/http")
                break


AnalyzerRegistry.register(SourceAnalyzer())
