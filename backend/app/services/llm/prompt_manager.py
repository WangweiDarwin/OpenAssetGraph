"""Prompt template management"""
from dataclasses import dataclass, field
from string import Template
from typing import Any, Optional


@dataclass
class PromptTemplate:
    """Prompt template definition"""
    name: str
    template: str
    description: str = ""
    variables: list[str] = field(default_factory=list)
    examples: list[dict[str, str]] = field(default_factory=list)
    
    def __post_init__(self):
        if not self.variables:
            self.variables = self._extract_variables()
    
    def _extract_variables(self) -> list[str]:
        """Extract template variables from the template string"""
        variables = []
        template_obj = Template(self.template)
        for match in template_obj.pattern.finditer(self.template):
            var_name = match.group('named') or match.group('braced')
            if var_name and var_name not in variables:
                variables.append(var_name)
        return variables
    
    def render(self, **kwargs: Any) -> str:
        """Render the template with provided variables"""
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        template_obj = Template(self.template)
        return template_obj.safe_substitute(**kwargs)
    
    def validate(self, values: dict[str, Any]) -> bool:
        """Validate that all required variables are provided"""
        return all(var in values for var in self.variables)


class PromptManager:
    """Manager for prompt templates"""
    
    def __init__(self):
        self._templates: dict[str, PromptTemplate] = {}
        self._load_default_templates()
    
    def register(self, template: PromptTemplate) -> None:
        """Register a new prompt template"""
        self._templates[template.name] = template
    
    def get(self, name: str) -> Optional[PromptTemplate]:
        """Get a prompt template by name"""
        return self._templates.get(name)
    
    def render(self, name: str, **kwargs: Any) -> str:
        """Render a template by name"""
        template = self.get(name)
        if not template:
            raise KeyError(f"Template not found: {name}")
        return template.render(**kwargs)
    
    def list_templates(self) -> list[str]:
        """List all available template names"""
        return list(self._templates.keys())
    
    def _load_default_templates(self) -> None:
        """Load default prompt templates"""
        
        self.register(PromptTemplate(
            name="system_base",
            description="Base system prompt for OAG assistant",
            template="""你是 OpenAssetGraph 智能助手，一个专注于企业软件架构分析的 AI 助手。

你的核心能力包括：
1. 分析企业软件架构拓扑，识别数据库、服务、API、应用之间的关系
2. 发现架构中的潜在问题：循环依赖、单点故障、性能瓶颈
3. 提供架构优化建议，支持技术决策
4. 解答关于资产关系、依赖链路的各类问题

你可以访问图数据库中的以下信息：
- 数据库及其表、字段信息
- 微服务及其 API 接口
- 前端应用及其组件
- 所有资产之间的依赖关系

回答原则：
- 基于数据给出精准、可操作的建议
- 清晰解释分析逻辑和推理过程
- 使用中文回答，保持专业和友好
- 当数据不完整时，诚实说明局限性""",
        ))
        
        self.register(PromptTemplate(
            name="topology_analysis",
            description="Analyze topology structure",
            template="""分析以下架构拓扑数据并提供洞察。

## 拓扑数据
$topology_data

## 分析请求
$user_query

请提供以下内容：
1. **架构概览**：整体拓扑结构的关键特征
2. **问题识别**：发现的潜在问题或风险点
3. **优化建议**：具体的改进建议
4. **深入洞察**：与查询相关的其他有价值信息""",
            variables=["topology_data", "user_query"],
        ))
        
        self.register(PromptTemplate(
            name="dependency_analysis",
            description="Analyze dependencies between components",
            template="""分析以下架构中的依赖关系。

## 拓扑数据
$topology_data

## 关注领域
$focus_area

请识别：
1. **循环依赖**：是否存在循环调用链路
2. **高耦合组件**：依赖关系过于复杂的组件
3. **单点故障**：关键路径上的风险节点
4. **解耦建议**：降低耦合的具体方案""",
            variables=["topology_data", "focus_area"],
        ))
        
        self.register(PromptTemplate(
            name="integration_suggestion",
            description="Generate integration suggestions",
            template="""基于现有架构，为新组件提供集成建议。

## 现有架构
$topology_data

## 新组件描述
$new_component

## 集成需求
$requirements

请提供：
1. **推荐集成点**：最佳的接入位置和方式
2. **潜在冲突**：可能与现有组件的冲突或重叠
3. **必要变更**：现有组件需要调整的部分
4. **集成步骤**：详细的集成实施计划""",
            variables=["topology_data", "new_component", "requirements"],
        ))
        
        self.register(PromptTemplate(
            name="asset_reuse",
            description="Analyze asset reuse opportunities",
            template="""分析现有资产复用机会，避免重复建设。

## 现有资产
$existing_assets

## 新需求
$requirement

请识别：
1. **可复用资产**：能够直接复用或扩展的现有资产
2. **开发缺口**：需要新建的部分
3. **节省评估**：复用带来的工作量节省估算
4. **复用风险**：每个可复用资产的潜在风险""",
            variables=["existing_assets", "requirement"],
        ))
        
        self.register(PromptTemplate(
            name="cypher_generation",
            description="Generate Cypher query from natural language",
            template="""将以下自然语言查询转换为 Neo4j Cypher 查询语句。

## 数据库模式
节点类型：Database, Table, Column, Service, API, FrontendApp, Component
关系类型：CONTAINS, CALLS, EXPOSES, REQUESTS, DERIVES, REFERENCES

## 自然语言查询
$natural_query

## 上下文
$context

只输出 Cypher 查询语句，无需解释。查询应：
1. 使用正确的 MATCH/CREATE/MERGE 语法
2. 返回相关的节点和关系数据
3. 包含适当的 WHERE 子句进行过滤
4. 对大结果集使用 LIMIT 限制""",
            variables=["natural_query", "context"],
        ))
        
        self.register(PromptTemplate(
            name="review_proposal",
            description="Review architecture proposal",
            template="""对照现有架构审查新的架构提案。

## 现有架构
$existing_topology

## 新提案
$proposal

## 审查标准
$criteria

请提供结构化审查报告：
1. **兼容性分析**：提案与现有架构的契合程度
2. **风险评估**：潜在的风险点
3. **差距分析**：缺失或不完整的部分
4. **改进建议**：具体的优化建议
5. **总体评估**：批准 / 有条件批准 / 驳回""",
            variables=["existing_topology", "proposal", "criteria"],
        ))
        
        self.register(PromptTemplate(
            name="chat_context",
            description="Build chat context with topology data",
            template="""$system_prompt

## 当前拓扑摘要
- 节点总数：$node_count
- 关系总数：$edge_count
- 节点类型：$node_types

## 相关子图
$subgraph_data

## 对话历史
$conversation_history

请基于提供的上下文回答用户问题。""",
            variables=["system_prompt", "node_count", "edge_count", "node_types", "subgraph_data", "conversation_history"],
        ))


SYSTEM_PROMPT = """你是 OpenAssetGraph 智能助手，专注于企业软件架构分析。

你的核心能力：
1. 分析企业软件架构拓扑
2. 识别架构问题和风险
3. 提供优化建议
4. 解答资产关系问题

你可以访问图数据库：
- 数据库、表、字段
- 服务、API
- 前端应用、组件
- 所有资产关系

回答原则：
- 精准、数据驱动
- 清晰解释推理过程
- 提供可操作建议
- 承认数据局限性"""


DEFAULT_PROMPTS = {
    "system": SYSTEM_PROMPT,
    "topology_analysis": """分析提供的拓扑数据并回答用户问题。

关注点：
1. 结构模式和关系
2. 潜在问题或异常
3. 可操作的建议""",
}
