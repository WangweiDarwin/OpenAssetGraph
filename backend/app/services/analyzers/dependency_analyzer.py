import re
import logging
from typing import Dict, List, Any, Optional
from . import (
    BaseAnalyzer, AnalysisResult, AnalyzedNode, AnalyzedEdge, NodeType,
    AnalyzerRegistry, parse_json, parse_yaml, parse_toml, parse_xml
)

logger = logging.getLogger(__name__)


class DependencyAnalyzer(BaseAnalyzer):
    name = "dependency"
    priority = 10
    supported_files = [
        "package.json", "requirements.txt", "pyproject.toml", "setup.py",
        "pom.xml", "build.gradle", "build.gradle.kts", "go.mod",
        "Cargo.toml", "composer.json", "Gemfile", "*.csproj"
    ]
    
    def can_analyze(self, file_path: str, content: str) -> bool:
        return self.matches_pattern(file_path, self.supported_files)
    
    def analyze(self, file_path: str, content: str) -> AnalysisResult:
        result = AnalysisResult()
        
        if file_path.endswith("package.json"):
            self._analyze_package_json(content, result)
        elif file_path.endswith("requirements.txt"):
            self._analyze_requirements(content, result)
        elif file_path.endswith("pyproject.toml"):
            self._analyze_pyproject(content, result)
        elif file_path.endswith("pom.xml"):
            self._analyze_pom_xml(content, result)
        elif file_path.endswith(".gradle") or file_path.endswith(".gradle.kts"):
            self._analyze_gradle(content, result)
        elif file_path.endswith("go.mod"):
            self._analyze_go_mod(content, result)
        elif file_path.endswith("Cargo.toml"):
            self._analyze_cargo(content, result)
        elif file_path.endswith("composer.json"):
            self._analyze_composer(content, result)
        elif file_path.endswith(".csproj"):
            self._analyze_csproj(content, result)
        
        return result
    
    def _analyze_package_json(self, content: str, result: AnalysisResult):
        data = parse_json(content)
        if not data:
            return
        
        result.technologies.append("Node.js")
        
        deps = data.get("dependencies", {})
        dev_deps = data.get("devDependencies", {})
        
        all_deps = {**deps, **dev_deps}
        result.dependencies["npm"] = list(all_deps.keys())
        
        frameworks = {
            "react": "React",
            "vue": "Vue.js",
            "angular": "Angular",
            "express": "Express.js",
            "nestjs": "NestJS",
            "next": "Next.js",
            "nuxt": "Nuxt.js",
            "svelte": "Svelte",
            "fastify": "Fastify",
            "koa": "Koa",
            "@ant-design/pro-components": "Ant Design Pro",
            "antd": "Ant Design",
            "@antv/g6": "AntV G6",
        }
        
        for dep, version in all_deps.items():
            dep_lower = dep.lower()
            is_framework = False
            
            for key, tech in frameworks.items():
                if key in dep_lower:
                    if tech not in result.technologies:
                        result.technologies.append(tech)
                    is_framework = True
                    break
            
            node = AnalyzedNode(
                id=f"lib-{dep}",
                label=dep,
                type=NodeType.LIBRARY,
                properties={
                    "version": version, 
                    "manager": "npm",
                    "is_framework": is_framework
                }
            )
            result.nodes.append(node)
        
        if "scripts" in data:
            result.metadata["scripts"] = data["scripts"]
        
        if "engines" in data:
            result.metadata["engines"] = data["engines"]
    
    def _analyze_requirements(self, content: str, result: AnalysisResult):
        result.technologies.append("Python")
        
        deps = []
        for line in content.split("\n"):
            line = line.strip()
            if line and not line.startswith("#"):
                match = re.match(r"^([a-zA-Z0-9_-]+)", line)
                if match:
                    deps.append(match.group(1))
        
        result.dependencies["pip"] = deps
        
        frameworks = {
            "fastapi": "FastAPI",
            "flask": "Flask",
            "django": "Django",
            "tornado": "Tornado",
            "aiohttp": "AIOHTTP",
            "sanic": "Sanic",
            "starlette": "Starlette",
            "uvicorn": "Uvicorn",
            "gunicorn": "Gunicorn",
            "celery": "Celery",
            "sqlalchemy": "SQLAlchemy",
            "pymongo": "MongoDB",
            "redis": "Redis",
            "neo4j": "Neo4j",
        }
        
        scientific_libs = {
            "netcdf4": "NetCDF",
            "h5py": "HDF5",
            "h5netcdf": "HDF5-NetCDF",
            "gdal": "GDAL",
            "rasterio": "Rasterio",
            "xarray": "xarray",
            "dask": "Dask",
            "numpy": "NumPy",
            "scipy": "SciPy",
            "pandas": "Pandas",
            "matplotlib": "Matplotlib",
            "cartopy": "Cartopy",
            "geopandas": "GeoPandas",
            "shapely": "Shapely",
            "fiona": "Fiona",
            "pyproj": "PyProj",
            "iris": "Iris",
            "cdo": "CDO",
            "wrf-python": "WRF-Python",
        }
        
        for dep in deps:
            dep_lower = dep.lower()
            for key, tech in frameworks.items():
                if key in dep_lower:
                    if tech not in result.technologies:
                        result.technologies.append(tech)
            
            for key, tech in scientific_libs.items():
                if key in dep_lower:
                    if tech not in result.technologies:
                        result.technologies.append(tech)
                    
                    result.nodes.append(AnalyzedNode(
                        id=f"lib-{dep}",
                        label=dep,
                        type=NodeType.LIBRARY,
                        properties={
                            "category": "scientific",
                            "technology": tech
                        }
                    ))
    
    def _analyze_pyproject(self, content: str, result: AnalysisResult):
        data = parse_toml(content)
        if not data:
            return
        
        result.technologies.append("Python")
        
        project = data.get("project", {})
        deps = project.get("dependencies", [])
        
        result.dependencies["pip"] = deps
        
        if "name" in project:
            result.metadata["project_name"] = project["name"]
    
    def _analyze_pom_xml(self, content: str, result: AnalysisResult):
        result.technologies.append("Java")
        result.technologies.append("Maven")
        
        try:
            import xml.etree.ElementTree as ET
            root = ET.fromstring(content)
            
            ns = {"m": "http://maven.apache.org/POM/4.0.0"}
            
            deps = root.findall(".//m:dependency", ns)
            dep_list = []
            
            for dep in deps:
                group_id = dep.find("m:groupId", ns)
                artifact_id = dep.find("m:artifactId", ns)
                if group_id is not None and artifact_id is not None:
                    dep_list.append(f"{group_id.text}:{artifact_id.text}")
            
            result.dependencies["maven"] = dep_list
            
            spring_patterns = ["spring-boot", "spring-cloud", "springframework"]
            for dep in dep_list:
                for pattern in spring_patterns:
                    if pattern in dep.lower():
                        if "Spring Boot" not in result.technologies:
                            result.technologies.append("Spring Boot")
                        break
        except Exception as e:
            logger.error(f"Failed to parse pom.xml: {e}")
    
    def _analyze_gradle(self, content: str, result: AnalysisResult):
        result.technologies.append("Java")
        result.technologies.append("Gradle")
        
        if "spring-boot" in content.lower() or "org.springframework" in content.lower():
            result.technologies.append("Spring Boot")
        
        if "kotlin" in content.lower():
            result.technologies.append("Kotlin")
        
        deps = re.findall(r'["\']([^"\']+:[^"\']+)["\']', content)
        result.dependencies["gradle"] = deps
    
    def _analyze_go_mod(self, content: str, result: AnalysisResult):
        result.technologies.append("Go")
        
        deps = []
        for line in content.split("\n"):
            if line.strip().startswith("require"):
                match = re.search(r"require\s+(.+)", line)
                if match:
                    deps.append(match.group(1).strip())
            elif "\t" in line and not line.strip().startswith("//"):
                parts = line.strip().split()
                if len(parts) >= 2:
                    deps.append(parts[0])
        
        result.dependencies["go"] = deps
        
        frameworks = {
            "gin-gonic": "Gin",
            "echo": "Echo",
            "fiber": "Fiber",
            "beego": "Beego",
            "revel": "Revel",
        }
        
        for dep in deps:
            for key, tech in frameworks.items():
                if key in dep.lower():
                    if tech not in result.technologies:
                        result.technologies.append(tech)
    
    def _analyze_cargo(self, content: str, result: AnalysisResult):
        data = parse_toml(content)
        if not data:
            return
        
        result.technologies.append("Rust")
        
        deps = data.get("dependencies", {})
        dep_list = list(deps.keys()) if isinstance(deps, dict) else []
        result.dependencies["cargo"] = dep_list
        
        frameworks = {
            "actix-web": "Actix Web",
            "rocket": "Rocket",
            "warp": "Warp",
            "axum": "Axum",
        }
        
        for dep in dep_list:
            for key, tech in frameworks.items():
                if key == dep.lower():
                    if tech not in result.technologies:
                        result.technologies.append(tech)
    
    def _analyze_composer(self, content: str, result: AnalysisResult):
        data = parse_json(content)
        if not data:
            return
        
        result.technologies.append("PHP")
        
        deps = data.get("require", {})
        result.dependencies["composer"] = list(deps.keys())
        
        frameworks = {
            "laravel": "Laravel",
            "symfony": "Symfony",
            "yii": "Yii",
            "cakephp": "CakePHP",
            "slim": "Slim",
        }
        
        for dep in deps.keys():
            dep_lower = dep.lower()
            for key, tech in frameworks.items():
                if key in dep_lower:
                    if tech not in result.technologies:
                        result.technologies.append(tech)
    
    def _analyze_csproj(self, content: str, result: AnalysisResult):
        result.technologies.append(".NET")
        
        if "Microsoft.NET.Sdk.Web" in content:
            result.technologies.append("ASP.NET Core")
        
        deps = re.findall(r'<PackageReference\s+Include="([^"]+)"', content)
        result.dependencies["nuget"] = deps


AnalyzerRegistry.register(DependencyAnalyzer())
