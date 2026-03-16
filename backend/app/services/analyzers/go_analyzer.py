import re
import logging
from typing import Dict, List, Any, Optional
from . import (
    BaseAnalyzer, AnalysisResult, AnalyzedNode, AnalyzedEdge, NodeType,
    AnalyzerRegistry
)

logger = logging.getLogger(__name__)


class GoAnalyzer(BaseAnalyzer):
    name = "go"
    priority = 25
    supported_files = ["*.go", "go.mod", "go.sum"]
    
    def can_analyze(self, file_path: str, content: str) -> bool:
        return file_path.endswith(".go") or file_path.endswith("go.mod") or file_path.endswith("go.sum")
    
    def analyze(self, file_path: str, content: str) -> AnalysisResult:
        result = AnalysisResult()
        result.technologies.append("Go")
        
        if file_path.endswith("go.mod"):
            self._analyze_go_mod(content, result)
        elif file_path.endswith(".go"):
            self._analyze_go_file(content, file_path, result)
        
        return result
    
    def _analyze_go_mod(self, content: str, result: AnalysisResult):
        module_match = re.search(r"module\s+([^\s\n]+)", content)
        if module_match:
            module_name = module_match.group(1)
            result.nodes.append(AnalyzedNode(
                id=f"module-{module_name}",
                label=module_name,
                type=NodeType.LIBRARY,
                properties={
                    "type": "Go Module",
                    "name": module_name
                },
                source_file="go.mod"
            ))
        
        go_version_match = re.search(r"go\s+(\d+\.\d+(?:\.\d+)?)", content)
        if go_version_match:
            result.technologies.append(f"Go {go_version_match.group(1)}")
        
        require_pattern = r"require\s*\(([^)]+)\)"
        require_match = re.search(require_pattern, content, re.DOTALL)
        if require_match:
            requires = require_match.group(1)
            for line in requires.strip().split("\n"):
                line = line.strip()
                if line and not line.startswith("//"):
                    parts = line.split()
                    if parts:
                        dep_name = parts[0]
                        dep_version = parts[1] if len(parts) > 1 else "unknown"
                        
                        result.dependencies.setdefault("go", []).append(f"{dep_name}@{dep_version}")
                        
                        if any(kw in dep_name.lower() for kw in ["gin", "echo", "fiber", "chi", "mux"]):
                            result.technologies.append("Web Framework")
                        elif any(kw in dep_name.lower() for kw in ["grpc", "proto"]):
                            result.technologies.append("gRPC")
                        elif any(kw in dep_name.lower() for kw in ["redis", "mongo", "postgres", "mysql", "sql"]):
                            result.technologies.append("Database")
                        elif any(kw in dep_name.lower() for kw in ["kafka", "rabbitmq", "nats", "mq"]):
                            result.technologies.append("Message Queue")
                        elif any(kw in dep_name.lower() for kw in ["k8s", "kubernetes", "docker"]):
                            result.technologies.append("Container")
                        
                        result.nodes.append(AnalyzedNode(
                            id=f"dep-{dep_name}",
                            label=dep_name,
                            type=NodeType.LIBRARY,
                            properties={
                                "type": "Go Dependency",
                                "version": dep_version
                            },
                            source_file="go.mod"
                        ))
        
        single_require_pattern = r"require\s+([^\s]+)\s+([^\s\n]+)"
        for match in re.finditer(single_require_pattern, content):
            dep_name = match.group(1)
            dep_version = match.group(2)
            result.dependencies.setdefault("go", []).append(f"{dep_name}@{dep_version}")
    
    def _analyze_go_file(self, content: str, file_path: str, result: AnalysisResult):
        package_match = re.search(r"package\s+(\w+)", content)
        if package_match:
            package_name = package_match.group(1)
            
            if package_name == "main":
                result.nodes.append(AnalyzedNode(
                    id=f"service-{file_path.replace('/', '-').replace('.go', '')}",
                    label=file_path.split("/")[-1].replace(".go", ""),
                    type=NodeType.SERVICE,
                    properties={
                        "type": "Go Main Package",
                        "file": file_path
                    },
                    source_file=file_path
                ))
            elif package_name not in ["main", "test"]:
                if not any(n.label == package_name for n in result.nodes):
                    result.nodes.append(AnalyzedNode(
                        id=f"package-{package_name}",
                        label=package_name,
                        type=NodeType.COMPONENT,
                        properties={
                            "type": "Go Package",
                            "file": file_path
                        },
                        source_file=file_path
                    ))
        
        struct_pattern = r"type\s+(\w+)\s+struct\s*\{"
        for match in re.finditer(struct_pattern, content):
            struct_name = match.group(1)
            result.nodes.append(AnalyzedNode(
                id=f"struct-{struct_name}",
                label=struct_name,
                type=NodeType.MODEL,
                properties={
                    "type": "Go Struct",
                    "file": file_path
                },
                source_file=file_path
            ))
        
        interface_pattern = r"type\s+(\w+)\s+interface\s*\{"
        for match in re.finditer(interface_pattern, content):
            interface_name = match.group(1)
            result.nodes.append(AnalyzedNode(
                id=f"interface-{interface_name}",
                label=interface_name,
                type=NodeType.API,
                properties={
                    "type": "Go Interface",
                    "file": file_path
                },
                source_file=file_path
            ))
        
        func_pattern = r"func\s+(?:\([^)]+\)\s+)?(\w+)\s*\("
        for match in re.finditer(func_pattern, content):
            func_name = match.group(1)
            if not func_name.startswith("test") and not func_name.startswith("Test"):
                if func_name[0].isupper():
                    result.nodes.append(AnalyzedNode(
                        id=f"func-{func_name}",
                        label=func_name,
                        type=NodeType.COMPONENT,
                        properties={
                            "type": "Go Function",
                            "exported": True,
                            "file": file_path
                        },
                        source_file=file_path
                    ))
        
        import_pattern = r"import\s+(?:\"([^\"]+)\"|\(([^)]+)\))"
        for match in re.finditer(import_pattern, content, re.DOTALL):
            if match.group(1):
                imports = [match.group(1)]
            else:
                import_block = match.group(2)
                imports = re.findall(r"\"([^\"]+)\"", import_block)
            
            for imp in imports:
                result.dependencies.setdefault("go_import", []).append(imp)
        
        http_pattern = r"(?:http\.|gin\.|echo\.|fiber\.|chi\.|mux\.)"
        if re.search(http_pattern, content):
            result.technologies.append("HTTP Server")
        
        grpc_pattern = r"(?:grpc\.|proto\.)"
        if re.search(grpc_pattern, content):
            result.technologies.append("gRPC")


AnalyzerRegistry.register(GoAnalyzer())
