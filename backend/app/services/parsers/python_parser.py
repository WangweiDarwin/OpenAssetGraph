"""Python code parser"""
import tree_sitter_python as tspython
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Any
from .base import BaseCodeParser


class PythonParser(BaseCodeParser):
    """Python code parser implementation using tree-sitter"""
    
    def __init__(self):
        self.language = Language(tspython.language())
        self.parser = Parser(self.language)
    
    async def parse_file(self, file_path: Path) -> dict[str, Any]:
        """Parse a single Python file"""
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()
        
        tree = self.parser.parse(bytes(source_code, 'utf8'))
        
        return {
            'file_path': str(file_path),
            'source_code': source_code,
            'tree': tree,
            'classes': self._extract_classes(tree.root_node, source_code),
            'functions': self._extract_functions(tree.root_node, source_code),
            'imports': self._extract_imports(tree.root_node, source_code)
        }
    
    async def parse_directory(self, directory_path: Path) -> list[dict[str, Any]]:
        """Parse all Python files in a directory"""
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        results = []
        python_files = list(directory_path.rglob('*.py'))
        
        for python_file in python_files:
            try:
                parsed = await self.parse_file(python_file)
                results.append(parsed)
            except Exception as e:
                results.append({
                    'file_path': str(python_file),
                    'error': str(e)
                })
        
        return results
    
    def extract_apis(self, parsed_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract API endpoints from parsed Python data"""
        apis = []
        
        if 'error' in parsed_data:
            return apis
        
        functions = parsed_data.get('functions', [])
        source_code = parsed_data.get('source_code', '')
        
        for func in functions:
            decorators = func.get('decorators', [])
            
            for decorator in decorators:
                api_info = self._extract_fastapi_route(func, decorator, source_code)
                if api_info:
                    apis.append(api_info)
        
        return apis
    
    def extract_dependencies(self, parsed_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract dependencies from parsed Python data"""
        dependencies = []
        
        if 'error' in parsed_data:
            return dependencies
        
        imports = parsed_data.get('imports', [])
        
        for imp in imports:
            dependencies.append({
                'type': imp.get('type', 'import'),
                'module': imp.get('module', ''),
                'names': imp.get('names', [])
            })
        
        return dependencies
    
    def _extract_classes(self, node, source_code: str) -> list[dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        for child in node.children:
            if child.type == 'class_definition':
                class_info = {
                    'name': '',
                    'decorators': [],
                    'methods': []
                }
                
                for class_child in child.children:
                    if class_child.type == 'identifier':
                        class_info['name'] = source_code[class_child.start_byte:class_child.end_byte]
                    elif class_child.type == 'decorator':
                        decorator_text = source_code[class_child.start_byte:class_child.end_byte]
                        class_info['decorators'].append(decorator_text)
                
                classes.append(class_info)
        
        return classes
    
    def _extract_functions(self, node, source_code: str) -> list[dict[str, Any]]:
        """Extract function definitions"""
        functions = []
        
        for child in node.children:
            if child.type == 'function_definition':
                func_info = {
                    'name': '',
                    'decorators': [],
                    'parameters': [],
                    'return_type': ''
                }
                
                for func_child in child.children:
                    if func_child.type == 'identifier':
                        func_info['name'] = source_code[func_child.start_byte:func_child.end_byte]
                    elif func_child.type == 'parameters':
                        params = self._extract_parameters(func_child, source_code)
                        func_info['parameters'] = params
                    elif func_child.type == 'type':
                        func_info['return_type'] = source_code[func_child.start_byte:func_child.end_byte]
                    elif func_child.type == 'decorator':
                        decorator_text = source_code[func_child.start_byte:func_child.end_byte]
                        func_info['decorators'].append(decorator_text)
                
                functions.append(func_info)
        
        return functions
    
    def _extract_imports(self, node, source_code: str) -> list[dict[str, Any]]:
        """Extract import statements"""
        imports = []
        
        for child in node.children:
            if child.type == 'import_statement':
                import_text = source_code[child.start_byte:child.end_byte]
                imports.append({
                    'type': 'import',
                    'text': import_text,
                    'module': self._parse_import_module(import_text),
                    'names': []
                })
            elif child.type == 'import_from_statement':
                import_text = source_code[child.start_byte:child.end_byte]
                imports.append({
                    'type': 'from_import',
                    'text': import_text,
                    'module': self._parse_from_import_module(import_text),
                    'names': self._parse_from_import_names(import_text)
                })
        
        return imports
    
    def _extract_parameters(self, node, source_code: str) -> list[dict[str, str]]:
        """Extract function parameters"""
        parameters = []
        
        for child in node.children:
            if child.type == 'identifier':
                param_name = source_code[child.start_byte:child.end_byte]
                parameters.append({
                    'name': param_name,
                    'type': '',
                    'default': None
                })
            elif child.type == 'typed_parameter':
                param_info = {'name': '', 'type': '', 'default': None}
                
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_info['name'] = source_code[param_child.start_byte:param_child.end_byte]
                    elif param_child.type == 'type':
                        param_info['type'] = source_code[param_child.start_byte:param_child.end_byte]
                
                if param_info['name']:
                    parameters.append(param_info)
            elif child.type == 'default_parameter':
                param_info = {'name': '', 'type': '', 'default': None}
                
                for param_child in child.children:
                    if param_child.type == 'identifier':
                        param_info['name'] = source_code[param_child.start_byte:param_child.end_byte]
                    elif param_child.type == 'type':
                        param_info['type'] = source_code[param_child.start_byte:param_child.end_byte]
                
                if param_info['name']:
                    parameters.append(param_info)
        
        return parameters
    
    def _parse_import_module(self, import_text: str) -> str:
        """Parse module name from import statement"""
        import re
        match = re.search(r'import\s+([^\s,]+)', import_text)
        return match.group(1) if match else ''
    
    def _parse_from_import_module(self, import_text: str) -> str:
        """Parse module name from from-import statement"""
        import re
        match = re.search(r'from\s+([^\s]+)\s+import', import_text)
        return match.group(1) if match else ''
    
    def _parse_from_import_names(self, import_text: str) -> list[str]:
        """Parse imported names from from-import statement"""
        import re
        match = re.search(r'import\s+(.+)$', import_text)
        if match:
            names_str = match.group(1)
            return [name.strip() for name in names_str.split(',')]
        return []
    
    def _extract_fastapi_route(
        self, 
        func: dict[str, Any], 
        decorator: str,
        source_code: str
    ) -> dict[str, Any] | None:
        """Extract FastAPI route information"""
        http_methods = {
            '@app.get': 'GET',
            '@app.post': 'POST',
            '@app.put': 'PUT',
            '@app.delete': 'DELETE',
            '@app.patch': 'PATCH',
            '@router.get': 'GET',
            '@router.post': 'POST',
            '@router.put': 'PUT',
            '@router.delete': 'DELETE',
            '@router.patch': 'PATCH'
        }
        
        decorator_lower = decorator.lower()
        
        for route_decorator, http_method in http_methods.items():
            if route_decorator in decorator_lower:
                import re
                match = re.search(r'\(["\']([^"\']+)["\']', decorator)
                
                path = match.group(1) if match else ''
                
                return {
                    'method': http_method,
                    'path': path,
                    'handler': func.get('name', ''),
                    'parameters': func.get('parameters', []),
                    'return_type': func.get('return_type', ''),
                    'decorators': func.get('decorators', [])
                }
        
        return None
