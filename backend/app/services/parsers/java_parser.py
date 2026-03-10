"""Java code parser"""
import tree_sitter_java as tsjava
from tree_sitter import Language, Parser
from pathlib import Path
from typing import Any
from .base import BaseCodeParser


class JavaParser(BaseCodeParser):
    """Java code parser implementation using tree-sitter"""
    
    def __init__(self):
        self.language = Language(tsjava.language())
        self.parser = Parser(self.language)
    
    async def parse_file(self, file_path: Path) -> dict[str, Any]:
        """Parse a single Java file"""
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
            'methods': self._extract_methods(tree.root_node, source_code),
            'annotations': self._extract_annotations(tree.root_node, source_code)
        }
    
    async def parse_directory(self, directory_path: Path) -> list[dict[str, Any]]:
        """Parse all Java files in a directory"""
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory_path}")
        
        results = []
        java_files = list(directory_path.rglob('*.java'))
        
        for java_file in java_files:
            try:
                parsed = await self.parse_file(java_file)
                results.append(parsed)
            except Exception as e:
                results.append({
                    'file_path': str(java_file),
                    'error': str(e)
                })
        
        return results
    
    def extract_apis(self, parsed_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract API endpoints from parsed Java data"""
        apis = []
        
        if 'error' in parsed_data:
            return apis
        
        classes = parsed_data.get('classes', [])
        methods = parsed_data.get('methods', [])
        annotations = parsed_data.get('annotations', [])
        
        for cls in classes:
            class_annotations = cls.get('annotations', [])
            
            if self._is_rest_controller(class_annotations):
                class_path = self._get_request_mapping_path(class_annotations)
                
                for method in methods:
                    if method.get('class_name') == cls.get('name'):
                        method_annotations = method.get('annotations', [])
                        api_info = self._extract_api_info(
                            method, 
                            method_annotations, 
                            class_path
                        )
                        if api_info:
                            apis.append(api_info)
        
        return apis
    
    def extract_dependencies(self, parsed_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract dependencies from parsed Java data"""
        dependencies = []
        
        if 'error' in parsed_data:
            return dependencies
        
        source_code = parsed_data.get('source_code', '')
        
        import_lines = [
            line.strip() 
            for line in source_code.split('\n') 
            if line.strip().startswith('import ')
        ]
        
        for import_line in import_lines:
            import_line = import_line.replace('import ', '').replace(';', '').strip()
            dependencies.append({
                'type': 'import',
                'package': import_line
            })
        
        return dependencies
    
    def _extract_classes(self, node, source_code: str) -> list[dict[str, Any]]:
        """Extract class definitions"""
        classes = []
        
        for child in node.children:
            if child.type == 'class_declaration':
                class_info = {
                    'name': '',
                    'annotations': [],
                    'methods': []
                }
                
                for class_child in child.children:
                    if class_child.type == 'identifier':
                        class_info['name'] = source_code[class_child.start_byte:class_child.end_byte]
                    elif class_child.type == 'marker_annotation' or class_child.type == 'annotation':
                        annotation_text = source_code[class_child.start_byte:class_child.end_byte]
                        class_info['annotations'].append(annotation_text)
                
                classes.append(class_info)
        
        return classes
    
    def _extract_methods(self, node, source_code: str) -> list[dict[str, Any]]:
        """Extract method definitions"""
        methods = []
        
        for child in node.children:
            if child.type == 'class_declaration':
                class_name = ''
                for class_child in child.children:
                    if class_child.type == 'identifier':
                        class_name = source_code[class_child.start_byte:class_child.end_byte]
                        break
                
                for class_child in child.children:
                    if class_child.type == 'class_body':
                        for body_child in class_child.children:
                            if body_child.type == 'method_declaration':
                                method_info = {
                                    'name': '',
                                    'class_name': class_name,
                                    'annotations': [],
                                    'parameters': [],
                                    'return_type': ''
                                }
                                
                                for method_child in body_child.children:
                                    if method_child.type == 'identifier':
                                        method_info['name'] = source_code[method_child.start_byte:method_child.end_byte]
                                    elif method_child.type == 'formal_parameters':
                                        params = self._extract_parameters(method_child, source_code)
                                        method_info['parameters'] = params
                                    elif method_child.type == 'type_identifier':
                                        method_info['return_type'] = source_code[method_child.start_byte:method_child.end_byte]
                                    elif method_child.type in ['marker_annotation', 'annotation']:
                                        annotation_text = source_code[method_child.start_byte:method_child.end_byte]
                                        method_info['annotations'].append(annotation_text)
                                
                                methods.append(method_info)
        
        return methods
    
    def _extract_annotations(self, node, source_code: str) -> list[dict[str, Any]]:
        """Extract all annotations"""
        annotations = []
        
        for child in node.children:
            if child.type in ['marker_annotation', 'annotation']:
                annotation_text = source_code[child.start_byte:child.end_byte]
                annotations.append({
                    'text': annotation_text,
                    'type': child.type
                })
        
        return annotations
    
    def _extract_parameters(self, node, source_code: str) -> list[dict[str, str]]:
        """Extract method parameters"""
        parameters = []
        
        for child in node.children:
            if child.type == 'formal_parameter':
                param_info = {'type': '', 'name': ''}
                
                for param_child in child.children:
                    if param_child.type == 'type_identifier':
                        param_info['type'] = source_code[param_child.start_byte:param_child.end_byte]
                    elif param_child.type == 'identifier':
                        param_info['name'] = source_code[param_child.start_byte:param_child.end_byte]
                
                if param_info['name']:
                    parameters.append(param_info)
        
        return parameters
    
    def _is_rest_controller(self, annotations: list[str]) -> bool:
        """Check if class is a REST controller"""
        rest_annotations = [
            '@RestController',
            '@Controller',
            '@ControllerAdvice'
        ]
        
        return any(
            any(rest_ann in ann for rest_ann in rest_annotations)
            for ann in annotations
        )
    
    def _get_request_mapping_path(self, annotations: list[str]) -> str:
        """Extract base path from RequestMapping annotation"""
        for ann in annotations:
            if '@RequestMapping' in ann:
                if 'value' in ann or 'path' in ann:
                    import re
                    match = re.search(r'(?:value|path)\s*=\s*"([^"]+)"', ann)
                    if match:
                        return match.group(1)
        return ''
    
    def _extract_api_info(
        self, 
        method: dict[str, Any], 
        annotations: list[str],
        class_path: str
    ) -> dict[str, Any] | None:
        """Extract API information from method"""
        http_methods = {
            '@GetMapping': 'GET',
            '@PostMapping': 'POST',
            '@PutMapping': 'PUT',
            '@DeleteMapping': 'DELETE',
            '@PatchMapping': 'PATCH',
            '@RequestMapping': 'GET'
        }
        
        for ann in annotations:
            for mapping_ann, http_method in http_methods.items():
                if mapping_ann in ann:
                    import re
                    
                    path = ''
                    if 'value' in ann or 'path' in ann:
                        match = re.search(r'(?:value|path)\s*=\s*"([^"]+)"', ann)
                        if match:
                            path = match.group(1)
                    elif mapping_ann != '@RequestMapping':
                        match = re.search(r'\("([^"]+)"\)', ann)
                        if match:
                            path = match.group(1)
                    
                    full_path = f"{class_path}{path}".replace('//', '/')
                    
                    return {
                        'method': http_method,
                        'path': full_path,
                        'handler': f"{method.get('class_name', '')}.{method.get('name', '')}",
                        'parameters': method.get('parameters', []),
                        'return_type': method.get('return_type', ''),
                        'annotations': annotations
                    }
        
        return None
