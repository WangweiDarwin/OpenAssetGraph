"""Graph RAG service for context-aware LLM responses"""
import json
from dataclasses import dataclass, field
from typing import Any, Optional

from ..graph_service import Neo4jService
from .base import ChatContext, LLMConfig, LLMResponse, LLMService, Message, MessageRole
from .llm_factory import LLMFactory, LLMProvider
from .prompt_manager import PromptManager


@dataclass
class GraphContext:
    """Context extracted from the graph database"""
    nodes: list[dict[str, Any]] = field(default_factory=list)
    relationships: list[dict[str, Any]] = field(default_factory=list)
    subgraph_summary: str = ""
    relevant_paths: list[list[str]] = field(default_factory=list)


class GraphRAGService:
    """Graph RAG service combining graph queries with LLM"""
    
    def __init__(
        self,
        neo4j_service: Neo4jService,
        llm_service: Optional[LLMService] = None,
        prompt_manager: Optional[PromptManager] = None,
    ):
        self.neo4j_service = neo4j_service
        self.llm_service = llm_service or self._create_default_llm()
        self.prompt_manager = prompt_manager or PromptManager()
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service using factory"""
        from ...core.config import settings
        return LLMFactory.create_from_settings(settings)
    
    async def extract_relevant_context(
        self,
        query: str,
        max_nodes: int = 50,
        max_depth: int = 2
    ) -> GraphContext:
        """Extract relevant context from the graph based on query"""
        context = GraphContext()
        
        try:
            await self.neo4j_service.connect()
            
            keywords = self._extract_keywords(query)
            
            nodes = []
            if keywords:
                nodes = await self._search_nodes_by_keywords(keywords, max_nodes)
            
            if len(nodes) < 5:
                nodes = await self._get_all_nodes(max_nodes)
            
            context.nodes = nodes
            
            if nodes:
                node_ids = [n["id"] for n in nodes]
                relationships = await self._get_relationships_for_nodes(node_ids)
                context.relationships = relationships
            
            context.subgraph_summary = self._generate_summary(context)
            
        finally:
            await self.neo4j_service.close()
        
        return context
    
    async def _get_all_nodes(self, limit: int = 200) -> list[dict[str, Any]]:
        """Get all nodes from the graph"""
        query = """
        MATCH (n)
        RETURN n.id as id, n.label as label, n.type as type, n.properties as properties
        LIMIT $limit
        """
        result = await self.neo4j_service.execute_query(query, {"limit": limit})
        return [dict(record) for record in result]
    
    def _extract_keywords(self, query: str) -> list[str]:
        """Extract keywords from query for graph search"""
        stop_words = {"the", "a", "an", "is", "are", "was", "were", "be", "been",
                      "being", "have", "has", "had", "do", "does", "did", "will",
                      "would", "could", "should", "may", "might", "must", "shall",
                      "can", "need", "dare", "ought", "used", "to", "of", "in",
                      "for", "on", "with", "at", "by", "from", "as", "into",
                      "through", "during", "before", "after", "above", "below",
                      "between", "under", "again", "further", "then", "once",
                      "here", "there", "when", "where", "why", "how", "all",
                      "each", "few", "more", "most", "other", "some", "such",
                      "no", "nor", "not", "only", "own", "same", "so", "than",
                      "too", "very", "just", "and", "but", "if", "or", "because",
                      "until", "while", "about", "against", "between", "into",
                      "through", "during", "before", "after", "above", "below",
                      "show", "list", "find", "get", "give", "tell", "what", "which",
                      "who", "whom", "this", "that", "these", "those", "请", "你",
                      "我", "的", "是", "在", "有", "和", "了", "不", "这", "那",
                      "就", "也", "都", "会", "说", "对", "要", "能", "着", "把",
                      "总结", "分析", "介绍", "描述", "说明", "解释", "总体", "架构",
                      "项目", "系统", "应用", "服务", "数据库", "组件", "模块"}
        
        import re
        words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', query.lower())
        keywords = [w for w in words if w and w not in stop_words and len(w) > 1]
        
        return list(set(keywords))
    
    async def _search_nodes_by_keywords(
        self,
        keywords: list[str],
        limit: int
    ) -> list[dict[str, Any]]:
        """Search nodes matching keywords"""
        if not keywords:
            return []
        
        query = """
        CALL db.index.fulltext.queryNodes('node_search', $search_term)
        YIELD node, score
        RETURN node.id as id, node.label as label, node.type as type, 
               node.properties as properties, score
        ORDER BY score DESC
        LIMIT $limit
        """
        
        search_term = " OR ".join(keywords)
        
        try:
            result = await self.neo4j_service.execute_query(
                query,
                {"search_term": search_term, "limit": limit}
            )
            return [dict(record) for record in result]
        except Exception:
            query = """
            MATCH (n)
            WHERE any(keyword IN $keywords WHERE 
                toLower(n.label) CONTAINS toLower(keyword) OR
                toLower(n.id) CONTAINS toLower(keyword))
            RETURN n.id as id, n.label as label, n.type as type, n.properties as properties
            LIMIT $limit
            """
            result = await self.neo4j_service.execute_query(
                query,
                {"keywords": keywords, "limit": limit}
            )
            return [dict(record) for record in result]
    
    async def _get_relationships_for_nodes(
        self,
        node_ids: list[str]
    ) -> list[dict[str, Any]]:
        """Get relationships between specified nodes"""
        query = """
        MATCH (source)-[r]->(target)
        WHERE source.id IN $node_ids AND target.id IN $node_ids
        RETURN source.id as source, target.id as target,
               type(r) as type, properties(r) as properties
        """
        
        result = await self.neo4j_service.execute_query(
            query,
            {"node_ids": node_ids}
        )
        return [dict(record) for record in result]
    
    def _generate_summary(self, context: GraphContext) -> str:
        """Generate a summary of the graph context"""
        if not context.nodes:
            return "No relevant nodes found in the graph."
        
        type_counts: dict[str, int] = {}
        type_examples: dict[str, list[str]] = {}
        
        for node in context.nodes:
            node_type = node.get("type", "Unknown")
            type_counts[node_type] = type_counts.get(node_type, 0) + 1
            
            if node_type not in type_examples:
                type_examples[node_type] = []
            if len(type_examples[node_type]) < 5:
                label = node.get("label", node.get("id", "unknown"))
                type_examples[node_type].append(label)
        
        summary_parts = [f"拓扑数据摘要：共 {len(context.nodes)} 个节点，{len(context.relationships)} 条关系\n"]
        
        summary_parts.append("节点类型分布：")
        for node_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
            examples = type_examples.get(node_type, [])[:3]
            examples_str = ", ".join(examples) if examples else ""
            summary_parts.append(f"  - {node_type}: {count} 个 ({examples_str})")
        
        if context.relationships:
            rel_types: dict[str, int] = {}
            for rel in context.relationships:
                rel_type = rel.get("type", "UNKNOWN")
                rel_types[rel_type] = rel_types.get(rel_type, 0) + 1
            
            summary_parts.append("\n关系类型分布：")
            for rel_type, count in sorted(rel_types.items(), key=lambda x: -x[1]):
                summary_parts.append(f"  - {rel_type}: {count} 条")
        
        return "\n".join(summary_parts)
    
    async def chat(
        self,
        user_query: str,
        conversation_history: Optional[list[dict[str, str]]] = None,
        context_data: Optional[dict[str, Any]] = None
    ) -> LLMResponse:
        """Process a chat query with graph context"""
        
        graph_context = await self.extract_relevant_context(user_query)
        
        messages = []
        
        system_prompt = self.prompt_manager.render(
            "chat_context",
            system_prompt=self.prompt_manager.render("system_base"),
            node_count=len(graph_context.nodes),
            edge_count=len(graph_context.relationships),
            node_types=", ".join(set(n.get("type", "Unknown") for n in graph_context.nodes)),
            subgraph_data=json.dumps({
                "nodes": graph_context.nodes[:20],
                "relationships": graph_context.relationships[:20],
                "summary": graph_context.subgraph_summary
            }, indent=2, default=str),
            conversation_history=self._format_history(conversation_history or [])
        )
        messages.append(Message(role=MessageRole.SYSTEM, content=system_prompt))
        
        if conversation_history:
            for msg in conversation_history[-10:]:
                role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
                messages.append(Message(role=role, content=msg["content"]))
        
        messages.append(Message(role=MessageRole.USER, content=user_query))
        
        response = await self.llm_service.chat(messages)
        
        return response
    
    async def chat_stream(
        self,
        user_query: str,
        conversation_history: Optional[list[dict[str, str]]] = None,
        context_data: Optional[dict[str, Any]] = None
    ):
        """Process a chat query with streaming response"""
        
        graph_context = await self.extract_relevant_context(user_query)
        
        messages = []
        
        system_prompt = self.prompt_manager.render(
            "chat_context",
            system_prompt=self.prompt_manager.render("system_base"),
            node_count=len(graph_context.nodes),
            edge_count=len(graph_context.relationships),
            node_types=", ".join(set(n.get("type", "Unknown") for n in graph_context.nodes)),
            subgraph_data=json.dumps({
                "nodes": graph_context.nodes[:20],
                "relationships": graph_context.relationships[:20],
                "summary": graph_context.subgraph_summary
            }, indent=2, default=str),
            conversation_history=self._format_history(conversation_history or [])
        )
        messages.append(Message(role=MessageRole.SYSTEM, content=system_prompt))
        
        if conversation_history:
            for msg in conversation_history[-10:]:
                role = MessageRole.USER if msg["role"] == "user" else MessageRole.ASSISTANT
                messages.append(Message(role=role, content=msg["content"]))
        
        messages.append(Message(role=MessageRole.USER, content=user_query))
        
        async for chunk in self.llm_service.chat_stream(messages):
            yield chunk
    
    def _format_history(self, history: list[dict[str, str]]) -> str:
        """Format conversation history for context"""
        if not history:
            return "No previous conversation."
        
        formatted = []
        for msg in history[-6:]:
            role = msg.get("role", "user").capitalize()
            content = msg.get("content", "")
            formatted.append(f"{role}: {content}")
        
        return "\n".join(formatted)
    
    async def analyze_topology(
        self,
        analysis_type: str = "general",
        focus_nodes: Optional[list[str]] = None
    ) -> LLMResponse:
        """Perform topology analysis"""
        
        await self.neo4j_service.connect()
        try:
            topology = await self._get_full_topology()
        finally:
            await self.neo4j_service.close()
        
        topology_str = json.dumps(topology, indent=2, default=str)[:8000]
        
        template_name = {
            "general": "topology_analysis",
            "dependency": "dependency_analysis",
        }.get(analysis_type, "topology_analysis")
        
        if focus_nodes:
            focus_str = ", ".join(focus_nodes)
        else:
            focus_str = "entire topology"
        
        prompt = self.prompt_manager.render(
            template_name,
            topology_data=topology_str,
            user_query=f"Analyze the {focus_str}",
            focus_area=focus_str
        )
        
        messages = [
            Message(role=MessageRole.SYSTEM, content=self.prompt_manager.render("system_base")),
            Message(role=MessageRole.USER, content=prompt)
        ]
        
        return await self.llm_service.chat(messages)
    
    async def suggest_integration(
        self,
        new_component: str,
        requirements: str
    ) -> LLMResponse:
        """Suggest integration approach for new component"""
        
        await self.neo4j_service.connect()
        try:
            topology = await self._get_full_topology()
        finally:
            await self.neo4j_service.close()
        
        topology_str = json.dumps(topology, indent=2, default=str)[:8000]
        
        prompt = self.prompt_manager.render(
            "integration_suggestion",
            topology_data=topology_str,
            new_component=new_component,
            requirements=requirements
        )
        
        messages = [
            Message(role=MessageRole.SYSTEM, content=self.prompt_manager.render("system_base")),
            Message(role=MessageRole.USER, content=prompt)
        ]
        
        return await self.llm_service.chat(messages)
    
    async def analyze_asset_reuse(
        self,
        requirement: str
    ) -> LLMResponse:
        """Analyze asset reuse opportunities"""
        
        await self.neo4j_service.connect()
        try:
            nodes = await self._get_all_nodes()
        finally:
            await self.neo4j_service.close()
        
        assets_str = json.dumps(nodes[:50], indent=2, default=str)[:6000]
        
        prompt = self.prompt_manager.render(
            "asset_reuse",
            existing_assets=assets_str,
            requirement=requirement
        )
        
        messages = [
            Message(role=MessageRole.SYSTEM, content=self.prompt_manager.render("system_base")),
            Message(role=MessageRole.USER, content=prompt)
        ]
        
        return await self.llm_service.chat(messages)
    
    async def _get_full_topology(self) -> dict[str, Any]:
        """Get full topology from Neo4j"""
        nodes_query = "MATCH (n) RETURN n.id as id, n.label as label, n.type as type, n.properties as properties LIMIT 200"
        edges_query = """
        MATCH (source)-[r]->(target)
        RETURN source.id as source, target.id as target, type(r) as type, properties(r) as properties
        LIMIT 500
        """
        
        nodes = await self.neo4j_service.execute_query(nodes_query, {})
        edges = await self.neo4j_service.execute_query(edges_query, {})
        
        return {
            "nodes": [dict(n) for n in nodes],
            "edges": [dict(e) for e in edges]
        }
