# 系统功能增强 Spec

## Why
当前系统已实现Neo4j数据持久化，但缺乏完善的错误处理和异常恢复机制。同时，用户在AI Chat中无法显性指定要分析的项目，导致AI可能分析错误的项目数据。需要增强数据存储的健壮性，并添加项目引用功能提升用户体验。

## What Changes
- 增强数据存储的错误处理和异常恢复机制
- 添加项目引用语法解析功能，支持`#项目名`格式引用项目
- 实现引用验证和错误提示机制
- 更新前端Chat页面，添加项目引用指引

## Impact
- Affected specs: `migrate-to-neo4j`, `link-chat-to-graph`
- Affected code:
  - `backend/app/services/graph_service.py` - 添加事务和重试机制
  - `backend/app/api/chat.py` - 添加项目引用解析
  - `backend/app/services/llm/graph_rag.py` - 支持项目过滤
  - `frontend/src/pages/ChatPage.tsx` - 添加引用指引UI

## ADDED Requirements

### Requirement: 数据存储错误处理
系统应提供完善的数据存储错误处理和异常恢复机制。

#### Scenario: Neo4j连接失败
- **WHEN** Neo4j数据库不可用
- **THEN** 系统记录错误日志并返回友好的错误信息
- **AND** 系统自动重试连接（最多3次）

#### Scenario: 数据写入失败
- **WHEN** 节点或关系写入失败
- **THEN** 系统回滚当前事务
- **AND** 系统返回详细的错误信息

#### Scenario: 数据验证失败
- **WHEN** 输入数据不符合模型要求
- **THEN** 系统拒绝写入并返回验证错误信息
- **AND** 系统记录验证失败的详细信息

### Requirement: 项目引用语法解析
系统应支持用户通过`#项目名`语法显性引用项目。

#### Scenario: 正确引用项目
- **WHEN** 用户输入"请分析 #online-boutique 的架构"
- **THEN** 系统识别项目引用为"online-boutique"
- **AND** AI仅基于该项目的数据进行分析

#### Scenario: 引用不存在的项目
- **WHEN** 用户输入"请分析 #nonexistent 的架构"
- **THEN** 系统返回错误提示"项目 'nonexistent' 不存在"
- **AND** 系统列出可用的项目列表

#### Scenario: 多项目引用
- **WHEN** 用户输入"比较 #mall 和 #online-boutique 的架构"
- **THEN** 系统识别两个项目引用
- **AND** AI基于两个项目的数据进行比较分析

### Requirement: 项目引用UI指引
前端应提供清晰的项目引用使用指引。

#### Scenario: 显示可用项目
- **WHEN** 用户在Chat页面输入`#`
- **THEN** 系统显示可用项目列表供选择

#### Scenario: 显示使用说明
- **WHEN** 用户首次访问Chat页面
- **THEN** 系统显示项目引用功能的使用说明

## MODIFIED Requirements

### Requirement: GraphRAG服务项目过滤
GraphRAG服务应支持按项目名称过滤数据。

#### Scenario: 按项目获取上下文
- **WHEN** AI请求指定项目的上下文
- **THEN** 系统仅返回该项目的节点和关系
- **AND** 排除其他项目的数据

## REMOVED Requirements
无移除的需求。
