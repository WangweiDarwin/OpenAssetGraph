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
            template="""You are OpenAssetGraph Assistant, an AI-powered enterprise architecture analysis tool.

Your role is to help users understand and optimize their enterprise software architecture by:
1. Analyzing the topology of databases, services, APIs, and applications
2. Identifying potential issues like circular dependencies, isolated components, and bottlenecks
3. Providing recommendations for architecture improvements
4. Answering questions about the existing asset landscape

You have access to a graph database containing information about:
- Databases and their tables/columns
- Services and their APIs
- Applications and their components
- Relationships between all assets

Always provide clear, actionable insights backed by the data in the graph.
When making recommendations, explain the reasoning and potential impact.""",
        ))
        
        self.register(PromptTemplate(
            name="topology_analysis",
            description="Analyze topology structure",
            template="""Analyze the following topology data and provide insights.

## Topology Data
$topology_data

## Analysis Request
$user_query

Please provide:
1. Key observations about the topology
2. Potential issues or risks identified
3. Recommendations for improvement
4. Any additional insights relevant to the query""",
            variables=["topology_data", "user_query"],
        ))
        
        self.register(PromptTemplate(
            name="dependency_analysis",
            description="Analyze dependencies between components",
            template="""Analyze the dependencies in the following topology.

## Topology Data
$topology_data

## Focus Area
$focus_area

Please identify:
1. Circular dependencies (if any)
2. Highly coupled components
3. Potential single points of failure
4. Recommendations for reducing coupling""",
            variables=["topology_data", "focus_area"],
        ))
        
        self.register(PromptTemplate(
            name="integration_suggestion",
            description="Generate integration suggestions",
            template="""Based on the existing topology, suggest how to integrate a new component.

## Existing Topology
$topology_data

## New Component Description
$new_component

## Integration Requirements
$requirements

Please provide:
1. Recommended integration points
2. Potential conflicts or overlaps
3. Required changes to existing components
4. Step-by-step integration plan""",
            variables=["topology_data", "new_component", "requirements"],
        ))
        
        self.register(PromptTemplate(
            name="asset_reuse",
            description="Analyze asset reuse opportunities",
            template="""Analyze opportunities for reusing existing assets instead of building new ones.

## Existing Assets
$existing_assets

## New Requirement
$requirement

Please identify:
1. Existing assets that could be reused or extended
2. Gaps that would need new development
3. Estimated effort savings from reuse
4. Risks of reusing each identified asset""",
            variables=["existing_assets", "requirement"],
        ))
        
        self.register(PromptTemplate(
            name="cypher_generation",
            description="Generate Cypher query from natural language",
            template="""Convert the following natural language query to a Cypher query for Neo4j.

## Database Schema
Node types: Database, Table, Column, Service, API, FrontendApp, Component
Relationship types: CONTAINS, CALLS, EXPOSES, REQUESTS, DERIVES, REFERENCES

## Natural Language Query
$natural_query

## Context
$context

Provide only the Cypher query without explanation. The query should:
1. Use proper MATCH/CREATE/MERGE syntax
2. Return relevant node and relationship data
3. Include appropriate WHERE clauses for filtering
4. Use LIMIT for large result sets""",
            variables=["natural_query", "context"],
        ))
        
        self.register(PromptTemplate(
            name="review_proposal",
            description="Review architecture proposal",
            template="""Review the following architecture proposal against the existing topology.

## Existing Topology
$existing_topology

## New Proposal
$proposal

## Review Criteria
$criteria

Please provide a structured review:
1. **Compatibility Analysis**: How well does the proposal fit with existing architecture?
2. **Risk Assessment**: What are the potential risks?
3. **Gap Analysis**: What's missing or incomplete?
4. **Recommendations**: Specific suggestions for improvement
5. **Overall Assessment**: Approve / Approve with Changes / Reject""",
            variables=["existing_topology", "proposal", "criteria"],
        ))
        
        self.register(PromptTemplate(
            name="chat_context",
            description="Build chat context with topology data",
            template="""$system_prompt

## Current Topology Summary
- Total Nodes: $node_count
- Total Relationships: $edge_count
- Node Types: $node_types

## Relevant Subgraph
$subgraph_data

## Conversation History
$conversation_history

Please respond to the user's query using the provided context.""",
            variables=["system_prompt", "node_count", "edge_count", "node_types", "subgraph_data", "conversation_history"],
        ))


SYSTEM_PROMPT = """You are OpenAssetGraph Assistant, an AI-powered enterprise architecture analysis tool.

Your capabilities include:
1. Analyzing enterprise software topology
2. Identifying architectural issues and risks
3. Providing optimization recommendations
4. Answering questions about assets and their relationships

You have access to a graph database containing:
- Databases, Tables, Columns
- Services, APIs
- Frontend Applications, Components
- All relationships between these assets

Guidelines:
- Be precise and data-driven in your responses
- Explain your reasoning clearly
- Provide actionable recommendations
- Acknowledge limitations when data is incomplete"""


DEFAULT_PROMPTS = {
    "system": SYSTEM_PROMPT,
    "topology_analysis": """Analyze the provided topology data and answer the user's question.

Focus on:
1. Structural patterns and relationships
2. Potential issues or anomalies
3. Actionable recommendations""",
}
