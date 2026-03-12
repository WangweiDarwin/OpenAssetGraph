# 项目启动问题修复 Spec

## Why
项目启动时存在端口占用问题和 Pydantic 模型字段命名冲突警告，导致服务无法正常启动或出现异常。需要修复这些问题并提供清晰的启动指南。

## What Changes
- 修复 `TableInfo` 模型中 `schema` 字段与 Pydantic `BaseModel` 父类属性冲突的警告
- 添加端口冲突检测和处理机制
- 提供完整的项目启动步骤文档

## Impact
- Affected specs: 无
- Affected code:
  - `backend/app/models/graph.py` - 重命名 `schema` 字段
  - `backend/app/main.py` - 添加启动前端口检测
  - `frontend/src/services/api.ts` - 确认端口配置正确

## ADDED Requirements

### Requirement: 端口冲突处理
系统应提供端口冲突检测和处理机制。

#### Scenario: 端口被占用
- **WHEN** 启动后端服务时发现 8000 端口已被占用
- **THEN** 系统显示占用进程信息
- **AND** 提供终止占用进程的命令

#### Scenario: 端口可用
- **WHEN** 启动后端服务时 8000 端口可用
- **THEN** 服务正常启动
- **AND** 显示服务运行地址

### Requirement: Pydantic 模型字段命名
模型字段名称不应与 Pydantic BaseModel 父类属性冲突。

#### Scenario: 字段重命名
- **WHEN** TableInfo 模型使用 `schema` 字段
- **THEN** 系统重命名为 `schema_name` 或其他非冲突名称
- **AND** 更新所有引用该字段的代码

### Requirement: 启动指南文档
提供完整的项目启动步骤说明。

#### Scenario: 完整启动流程
- **WHEN** 用户需要启动项目
- **THEN** 提供清晰的启动顺序
- **AND** 包含环境变量配置说明
- **AND** 包含依赖服务启动说明

## MODIFIED Requirements
无

## REMOVED Requirements
无
