# AI Chat 关联图数据库上下文 Spec

## Why
AI Chat 功能目前直接调用 LLM，无法获取已扫描项目的拓扑数据，导致 AI 无法回答关于项目架构的具体问题。

## What Changes
- 修改 Chat API，从 Neo4j 获取图数据作为 LLM 上下文
- 添加项目拓扑摘要生成功能
- 优化 system prompt，注入图数据上下文

## Impact
- Affected code: `backend/app/api/chat.py`, `backend/app/services/llm/graph_rag.py`

## ADDED Requirements

### Requirement: Chat API 关联图数据
Chat API 应从 Neo4j 图数据库获取项目拓扑数据，并将其作为上下文传递给 LLM。

#### Scenario: 用户询问项目架构
- **WHEN** 用户问"请总结 Online Boutique 项目的总体架构"
- **THEN** 系统从 Neo4j 获取该项目的节点和关系数据
- **AND** 将拓扑数据注入 LLM 上下文
- **AND** AI 基于实际数据回答问题

### Requirement: 拓扑摘要生成
系统应生成项目拓扑的结构化摘要，便于 LLM 理解。

#### Scenario: 生成拓扑摘要
- **WHEN** 系统获取图数据
- **THEN** 生成包含节点类型统计、关系类型统计的摘要
- **AND** 摘要格式适合 LLM 理解

## MODIFIED Requirements

### Requirement: Chat API 实现
Chat API 应使用 GraphRAGService 而非直接使用 LLM 服务，以获取图数据上下文。
