"""Chat API routes"""
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json

from ..services.graph_service import Neo4jService
from ..services.llm.graph_rag import GraphRAGService
from ..core.config import settings

router = APIRouter(prefix="/api/chat", tags=["chat"])


def get_graph_rag_service() -> GraphRAGService:
    """Get Graph RAG service instance"""
    neo4j_service = Neo4jService(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    return GraphRAGService(neo4j_service)


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    model: str
    usage: dict
    context_summary: Optional[str] = None


class AnalysisRequest(BaseModel):
    """Analysis request model"""
    analysis_type: str = "general"
    focus_nodes: Optional[List[str]] = None


class IntegrationRequest(BaseModel):
    """Integration suggestion request"""
    new_component: str
    requirements: str


class ReuseRequest(BaseModel):
    """Asset reuse analysis request"""
    requirement: str


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message and get AI response"""
    service = get_graph_rag_service()
    
    try:
        history = None
        if request.conversation_history:
            history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
        
        response = await service.chat(
            user_query=request.message,
            conversation_history=history,
            context_data=request.context
        )
        
        return ChatResponse(
            response=response.content,
            model=response.model,
            usage=response.usage,
            context_summary=f"Analyzed topology context with {response.usage.get('prompt_tokens', 0)} tokens"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def chat_stream(request: ChatRequest):
    """Send a chat message and get streaming response"""
    service = get_graph_rag_service()
    
    async def generate():
        try:
            history = None
            if request.conversation_history:
                history = [{"role": msg.role, "content": msg.content} for msg in request.conversation_history]
            
            async for chunk in service.chat_stream(
                user_query=request.message,
                conversation_history=history,
                context_data=request.context
            ):
                yield f"data: {json.dumps({'content': chunk})}\n\n"
            
            yield "data: [DONE]\n\n"
            
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
    
    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        }
    )


@router.post("/analyze")
async def analyze_topology(request: AnalysisRequest):
    """Analyze topology structure"""
    service = get_graph_rag_service()
    
    try:
        response = await service.analyze_topology(
            analysis_type=request.analysis_type,
            focus_nodes=request.focus_nodes
        )
        
        return {
            "analysis": response.content,
            "model": response.model,
            "usage": response.usage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/suggest-integration")
async def suggest_integration(request: IntegrationRequest):
    """Get integration suggestions for a new component"""
    service = get_graph_rag_service()
    
    try:
        response = await service.suggest_integration(
            new_component=request.new_component,
            requirements=request.requirements
        )
        
        return {
            "suggestions": response.content,
            "model": response.model,
            "usage": response.usage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/analyze-reuse")
async def analyze_reuse(request: ReuseRequest):
    """Analyze asset reuse opportunities"""
    service = get_graph_rag_service()
    
    try:
        response = await service.analyze_asset_reuse(
            requirement=request.requirement
        )
        
        return {
            "analysis": response.content,
            "model": response.model,
            "usage": response.usage
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
