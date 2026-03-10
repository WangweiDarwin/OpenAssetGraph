"""Code parser base module"""
from abc import ABC, abstractmethod
from typing import Any
from pathlib import Path


class BaseCodeParser(ABC):
    """Abstract base class for code parsers"""
    
    @abstractmethod
    async def parse_file(self, file_path: Path) -> dict[str, Any]:
        """Parse a single code file"""
        pass
    
    @abstractmethod
    async def parse_directory(self, directory_path: Path) -> list[dict[str, Any]]:
        """Parse all code files in a directory"""
        pass
    
    @abstractmethod
    def extract_apis(self, parsed_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract API endpoints from parsed data"""
        pass
    
    @abstractmethod
    def extract_dependencies(self, parsed_data: dict[str, Any]) -> list[dict[str, Any]]:
        """Extract dependencies from parsed data"""
        pass
