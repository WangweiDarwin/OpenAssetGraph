"""Chat API routes"""
import logging
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional, List
import json
import traceback

from ..services.graph_service import Neo4jService
from ..services.llm.graph_rag import GraphRAGService
from ..services.llm import LLMFactory, Message, MessageRole
from ..services.project_reference import ProjectReferenceParser
from ..core.config import settings

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/chat", tags=["chat"])


def get_graph_rag_service() -> GraphRAGService:
    """Get Graph RAG service instance"""
    neo4j_service = Neo4jService(
        uri=settings.neo4j_uri,
        user=settings.neo4j_user,
        password=settings.neo4j_password
    )
    return GraphRAGService(neo4j_service)


def get_llm_service():
    """Get LLM service instance"""
    return LLMFactory.create_from_settings(settings)


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str
    content: str


class ChatRequest(BaseModel):
    """Chat request model"""
    message: str
    conversation_history: Optional[List[ChatMessage]] = None
    context: Optional[dict] = None
    project_refs: Optional[List[str]] = None
    resolved_projects: Optional[List[str]] = None


class ChatResponse(BaseModel):
    """Chat response model"""
    response: str
    model: str
    usage: dict
    context_summary: Optional[str] = None
    referenced_projects: Optional[List[str]] = None


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


@router.get("/test")
async def test_llm_service():
    """Test LLM service configuration and connectivity"""
    from ..services.llm.llm_factory import LLMModelConfig, LLMProvider
    
    provider = LLMProvider(settings.llm_provider.lower())
    model_config = LLMModelConfig.get_model_config(provider, settings.llm_model)
    actual_base_url = getattr(settings, 'llm_base_url', None) or (model_config.get("base_url") if model_config else None)
    
    result = {
        "status": "unknown",
        "config": {
            "provider": settings.llm_provider,
            "model": settings.llm_model,
            "api_key_set": bool(settings.glm_api_key if settings.llm_provider == "glm" else settings.openai_api_key),
            "api_key_preview": (settings.glm_api_key[:10] + "..." if settings.llm_provider == "glm" and settings.glm_api_key else 
                               (settings.openai_api_key[:10] + "..." if settings.openai_api_key else "NOT SET")),
            "base_url": actual_base_url or "default",
        },
        "test_result": None,
        "error": None
    }
    
    try:
        llm = get_llm_service()
        result["status"] = "service_created"
        
        test_message = [Message(role=MessageRole.USER, content="Hi")]
        response = await llm.chat(test_message)
        
        result["status"] = "success"
        result["test_result"] = {
            "model": response.model,
            "response_preview": response.content[:100] if response.content else "",
            "tokens": response.usage
        }
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = {
            "type": type(e).__name__,
            "message": str(e)
        }
        logger.error(f"LLM test error: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
    
    return result


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a chat message and get AI response with graph context"""
    try:
        logger.info(f"Chat request received: {request.message[:50]}...")
        logger.info(f"LLM Provider: {settings.llm_provider}, Model: {settings.llm_model}")
        
        neo4j_service = Neo4jService(
            uri=settings.neo4j_uri,
            user=settings.neo4j_user,
            password=settings.neo4j_password
        )
        await neo4j_service.connect()
        parser = ProjectReferenceParser(neo4j_service)
        
        project_validation = await parser.parse_and_validate(request.message)
        valid_projects = project_validation["valid"]
        invalid_projects = project_validation["invalid"]
        
        if invalid_projects:
            available_projects = await parser.get_all_projects()
            logger.warning(f"Invalid project references: {invalid_projects}")
            raise HTTPException(
                status_code=400,
                detail={
                    "error": "invalid_project_reference",
                    "invalid_projects": invalid_projects,
                    "available_projects": available_projects,
                    "message": f"以下项目引用无效: {', '.join(invalid_projects)}。可用项目: {', '.join(available_projects)}"
                }
            )
        
        referenced_projects = valid_projects if valid_projects else None
        logger.info(f"Referenced projects: {referenced_projects}")
        
        context_summary = None
        graph_context_data = None
        
        try:
            graph_rag_service = get_graph_rag_service()
            graph_context = await graph_rag_service.extract_relevant_context(
                request.message,
                projects=referenced_projects
            )
            
            if graph_context.nodes:
                context_summary = graph_context.subgraph_summary
                graph_context_data = {
                    "nodes": graph_context.nodes[:30],
                    "relationships": graph_context.relationships[:30],
                    "summary": graph_context.subgraph_summary
                }
                logger.info(f"Graph context extracted: {len(graph_context.nodes)} nodes, {len(graph_context.relationships)} relationships")
            else:
                logger.info("No relevant graph context found")
        except Exception as graph_error:
            logger.warning(f"Failed to get graph context: {graph_error}. Falling back to direct LLM.")
        
        llm = get_llm_service()
        logger.info("LLM service created successfully")
        
        if graph_context_data:
            context_str = json.dumps(graph_context_data, indent=2, ensure_ascii=False, default=str)[:6000]
            system_prompt = f"""你是 OpenAssetGraph 智能助手，一个专注于企业软件架构分析的 AI 助手。

当前项目的拓扑数据如下：
{context_str}

你的核心能力包括：
1. 分析企业软件架构拓扑，识别数据库、服务、API、应用之间的关系
2. 发现架构中的潜在问题：循环依赖、单点故障、性能瓶颈
3. 提供架构优化建议，支持技术决策
4. 解答关于资产关系、依赖链路的各类问题

回答原则：
- 必须基于上述拓扑数据回答问题，不要编造不存在的信息
- 如果拓扑数据中包含具体的服务名称、数据库类型等，请准确引用
- 清晰解释分析逻辑和推理过程
- 使用中文回答，保持专业和友好
- 当数据不完整时，诚实说明局限性"""
        else:
            system_prompt = """你是 OpenAssetGraph 智能助手，一个专注于企业软件架构分析的 AI 助手。

你的核心能力包括：
1. 分析企业软件架构拓扑，识别数据库、服务、API、应用之间的关系
2. 发现架构中的潜在问题：循环依赖、单点故障、性能瓶颈
3. 提供架构优化建议，支持技术决策
4. 解答关于资产关系、依赖链路的各类问题

回答原则：
- 基于数据给出精准、可操作的建议
- 清晰解释分析逻辑和推理过程
- 使用中文回答，保持专业和友好
- 当数据不完整时，诚实说明局限性"""
        
        messages = [
            Message(role=MessageRole.SYSTEM, content=system_prompt),
        ]
        
        if request.conversation_history:
            for msg in request.conversation_history[-10:]:
                role = MessageRole.USER if msg.role == "user" else MessageRole.ASSISTANT
                messages.append(Message(role=role, content=msg.content))
        
        messages.append(Message(role=MessageRole.USER, content=request.message))
        logger.info(f"Sending {len(messages)} messages to LLM...")
        
        response = await llm.chat(messages)
        logger.info(f"LLM response received: {response.content[:100]}...")
        
        return ChatResponse(
            response=response.content,
            model=response.model,
            usage=response.usage,
            context_summary=context_summary,
            referenced_projects=referenced_projects
        )
        
    except Exception as e:
        logger.error(f"Chat API error: {type(e).__name__}: {e}")
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        error_info = {
            "type": type(e).__name__,
            "message": str(e),
            "suggestion": None
        }
        
        error_type = type(e).__name__.lower()
        error_str = str(e).lower()
        
        if "timeout" in error_type or "timeout" in error_str:
            error_info["suggestion"] = "API 请求超时，可能是网络问题或服务响应慢。已增加超时时间到 120 秒，请重试。"
        elif "api key" in error_str or "authentication" in error_str or "unauthorized" in error_str:
            error_info["suggestion"] = "API Key 无效或已过期，请检查 .env 文件中的 GLM_API_KEY 配置"
        elif "rate limit" in error_str or "quota" in error_str:
            error_info["suggestion"] = "API 调用频率超限，请稍后重试或检查账户配额"
        elif "connection" in error_str or "network" in error_str:
            error_info["suggestion"] = "网络连接失败，请检查网络连接或代理设置"
        elif "model" in error_str:
            error_info["suggestion"] = f"模型 {settings.llm_model} 不可用，请检查模型名称"
        else:
            error_info["suggestion"] = "请检查后端日志获取详细错误信息"
        
        raise HTTPException(
            status_code=500, 
            detail=error_info
        )


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
