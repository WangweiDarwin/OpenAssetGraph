"""Scan API routes"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional
from ..services.scan_service import ScanService


router = APIRouter(prefix="/api/scan", tags=["scan"])


class DatabaseScanRequest(BaseModel):
    """Database scan request model"""
    connection_string: str
    database_name: str


class CodeScanRequest(BaseModel):
    """Code scan request model"""
    directory_path: str
    language: str = 'auto'


class FullScanRequest(BaseModel):
    """Full scan request model"""
    db_connection_string: Optional[str] = None
    database_name: Optional[str] = None
    code_directory: Optional[str] = None


@router.post("/database")
async def scan_database(request: DatabaseScanRequest):
    """Scan a database and store results in Neo4j"""
    service = ScanService()
    
    result = await service.scan_database(
        request.connection_string,
        request.database_name
    )
    
    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.post("/code")
async def scan_code(request: CodeScanRequest):
    """Scan code directory and extract APIs"""
    service = ScanService()
    
    result = await service.scan_code(
        request.directory_path,
        request.language
    )
    
    if result['status'] == 'error':
        raise HTTPException(status_code=500, detail=result['error'])
    
    return result


@router.post("/full")
async def full_scan(request: FullScanRequest):
    """Perform full scan of database and code"""
    service = ScanService()
    
    result = await service.full_scan(
        db_connection_string=request.db_connection_string,
        code_directory=request.code_directory,
        database_name=request.database_name
    )
    
    return result


@router.get("/status/{task_id}")
async def get_scan_status(task_id: str):
    """Get scan task status (placeholder for future async task support)"""
    return {
        "task_id": task_id,
        "status": "completed",
        "message": "Task tracking not yet implemented"
    }


@router.get("/history")
async def get_scan_history():
    """Get scan history (placeholder for future implementation)"""
    return {
        "scans": [],
        "message": "Scan history tracking not yet implemented"
    }
