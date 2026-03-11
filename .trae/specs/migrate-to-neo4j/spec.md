# 从模拟数据迁移到Neo4j数据库 Spec

## Why
项目当前使用模拟(mock)数据而非真实的Neo4j图数据库，导致数据无法持久化、AI分析无法基于真实扫描数据、系统功能受限。开发环境已完成Neo4j和Node.js的安装配置，需要将系统从模拟数据迁移到真实数据库。

## What Changes
- **BREAKING**: 禁用模拟数据模式，启用Neo4j数据库连接
- 创建数据迁移脚本，将模拟数据导入Neo4j
- 重构Scan API，使用Neo4j存储扫描结果
- 添加应用启动时的Neo4j连接初始化
- 更新前端配置以支持Node.js环境

## Impact
- Affected specs: `link-chat-to-graph`
- Affected code:
  - `backend/app/api/topology.py` - 禁用USE_MOCK_DATA
  - `backend/app/api/scan.py` - 使用Neo4j存储
  - `backend/app/services/graph_service.py` - 添加批量操作方法
  - `backend/app/main.py` - 添加启动初始化
  - `backend/app/services/mock_data.py` - 添加迁移方法

## ADDED Requirements

### Requirement: Neo4j数据持久化
系统应将所有拓扑数据持久化到Neo4j数据库，而非使用内存中的模拟数据。

#### Scenario: 扫描项目后数据持久化
- **WHEN** 用户扫描GitHub项目
- **THEN** 系统将节点和关系数据写入Neo4j
- **AND** 数据在服务重启后仍然可用

#### Scenario: 查询拓扑数据
- **WHEN** 用户请求拓扑数据
- **THEN** 系统从Neo4j数据库读取数据
- **AND** 返回真实的持久化数据

### Requirement: 模拟数据迁移
系统应提供将现有模拟数据迁移到Neo4j的功能。

#### Scenario: 初始数据迁移
- **WHEN** Neo4j数据库为空
- **THEN** 系统自动将预设的模拟数据导入Neo4j
- **AND** 数据包含Online Boutique、Mall等示例项目

### Requirement: 应用启动初始化
应用启动时应自动初始化Neo4j连接并验证数据库状态。

#### Scenario: 启动时连接Neo4j
- **WHEN** 应用启动
- **THEN** 系统自动连接Neo4j数据库
- **AND** 验证连接状态
- **AND** 在日志中记录连接状态

### Requirement: Scan API使用Neo4j
Scan API应将扫描结果存储到Neo4j而非模拟数据服务。

#### Scenario: GitHub项目扫描
- **WHEN** 用户扫描GitHub项目
- **THEN** 系统解析项目结构
- **AND** 创建节点和关系到Neo4j
- **AND** 返回创建的数据统计

## MODIFIED Requirements

### Requirement: Topology API数据源
Topology API应从Neo4j数据库获取数据，而非模拟数据服务。

#### Scenario: 获取拓扑统计
- **WHEN** 用户请求拓扑统计
- **THEN** 系统查询Neo4j数据库
- **AND** 返回真实的节点和关系统计

## REMOVED Requirements

### Requirement: 模拟数据模式
**Reason**: 系统已具备Neo4j环境，不再需要模拟数据模式
**Migration**: 将模拟数据迁移到Neo4j作为初始数据
