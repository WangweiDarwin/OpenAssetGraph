import re
import logging
from typing import Dict, List, Any, Optional
from . import (
    BaseAnalyzer, AnalysisResult, AnalyzedNode, AnalyzedEdge, NodeType,
    AnalyzerRegistry
)

logger = logging.getLogger(__name__)


class FortranAnalyzer(BaseAnalyzer):
    name = "fortran"
    priority = 25
    supported_files = ["*.f90", "*.F90", "*.f95", "*.F95", "*.f03", "*.F03", "*.f08", "*.F08"]
    
    def can_analyze(self, file_path: str, content: str) -> bool:
        return self.matches_pattern(file_path, self.supported_files)
    
    def analyze(self, file_path: str, content: str) -> AnalysisResult:
        result = AnalysisResult()
        result.technologies.append("Fortran")
        
        modules = self._extract_modules(content)
        subroutines = self._extract_subroutines(content)
        functions = self._extract_functions(content)
        use_statements = self._extract_use_statements(content)
        include_statements = self._extract_include_statements(content)
        
        for module in modules:
            result.nodes.append(AnalyzedNode(
                id=f"module-{module['name']}",
                label=module['name'],
                type=NodeType.MODEL,
                properties={
                    "type": "Fortran Module",
                    "file": file_path,
                    "line": module.get('line', 0)
                },
                source_file=file_path
            ))
        
        for subroutine in subroutines:
            result.nodes.append(AnalyzedNode(
                id=f"subroutine-{subroutine['name']}",
                label=subroutine['name'],
                type=NodeType.COMPONENT,
                properties={
                    "type": "Fortran Subroutine",
                    "file": file_path,
                    "line": subroutine.get('line', 0),
                    "arguments": subroutine.get('arguments', [])
                },
                source_file=file_path
            ))
        
        for func in functions:
            result.nodes.append(AnalyzedNode(
                id=f"function-{func['name']}",
                label=func['name'],
                type=NodeType.COMPONENT,
                properties={
                    "type": "Fortran Function",
                    "file": file_path,
                    "line": func.get('line', 0),
                    "arguments": func.get('arguments', []),
                    "return_type": func.get('return_type', 'unknown')
                },
                source_file=file_path
            ))
        
        for use in use_statements:
            result.dependencies.setdefault("fortran", []).append(use)
            
            result.edges.append(AnalyzedEdge(
                source=file_path.split("/")[-1].replace(".f90", "").replace(".F90", ""),
                target=f"module-{use}",
                type="USES"
            ))
        
        for include in include_statements:
            result.dependencies.setdefault("fortran_include", []).append(include)
        
        return result
    
    def _extract_modules(self, content: str) -> List[Dict[str, Any]]:
        modules = []
        pattern = r'module\s+(\w+)(?:\s*\n|\s*!)'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            modules.append({
                "name": match.group(1),
                "line": content[:match.start()].count('\n') + 1
            })
        return modules
    
    def _extract_subroutines(self, content: str) -> List[Dict[str, Any]]:
        subroutines = []
        pattern = r'subroutine\s+(\w+)\s*\(([^)]*)\)'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            args = [a.strip() for a in match.group(2).split(',') if a.strip()]
            subroutines.append({
                "name": match.group(1),
                "arguments": args,
                "line": content[:match.start()].count('\n') + 1
            })
        return subroutines
    
    def _extract_functions(self, content: str) -> List[Dict[str, Any]]:
        functions = []
        patterns = [
            (r'function\s+(\w+)\s*\(([^)]*)\)\s*(?:result\s*\((\w+)\))?', 'unknown'),
            (r'(?:real|integer|logical|character|complex|double\s*precision)\s*(?:\([^)]*\))?\s*(?:,\s*(?:intent|parameter|save)\s*(?:\([^)]*\))?\s*)*\s*function\s+(\w+)\s*\(([^)]*)\)', None),
        ]
        
        for pattern, _ in patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                func_name = match.group(1)
                args = [a.strip() for a in match.group(2).split(',') if a.strip()] if match.group(2) else []
                functions.append({
                    "name": func_name,
                    "arguments": args,
                    "line": content[:match.start()].count('\n') + 1,
                    "return_type": "inferred"
                })
        
        seen = set()
        unique_functions = []
        for f in functions:
            if f['name'] not in seen:
                seen.add(f['name'])
                unique_functions.append(f)
        
        return unique_functions
    
    def _extract_use_statements(self, content: str) -> List[str]:
        modules = []
        pattern = r'use\s+(\w+)(?:\s*,\s*(?:only\s*:)?)?'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            module_name = match.group(1)
            if module_name.lower() not in ['iso_fortran_env', 'iso_c_binding', 'ieee_arithmetic']:
                modules.append(module_name)
        return list(set(modules))
    
    def _extract_include_statements(self, content: str) -> List[str]:
        includes = []
        pattern = r'include\s+["\']([^"\']+)["\']'
        for match in re.finditer(pattern, content, re.IGNORECASE):
            includes.append(match.group(1))
        return includes


AnalyzerRegistry.register(FortranAnalyzer())
