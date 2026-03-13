# 系统性修复前端 API 连接问题 Spec

## Why
前端页面可以打开，但拓扑、扫描、Chat 页面都无法正常工作。问题反复出现，需要系统性地解决前端与后端 API 连接问题，确保所有页面都能正常工作。

## What Changes
- 统一前端所有页面的 API 调用方式，全部使用相对路径通过 Vite 代理
- 创建统一的 API 配置管理模块
- 添加 API 连接状态检测和错误提示
- 确保后端服务启动时 Neo4j 已就绪

## Impact
- Affected specs: fix-startup-issues
- Affected code:
  - `frontend/src/services/api.ts` - 统一 API 配置
  - `frontend/src/pages/TopologyPage.tsx` - 使用统一 API
  - `frontend/src/pages/ScanPage.tsx` - 使用统一 API
  - `frontend/src/pages/ChatPage.tsx` - 使用统一 API
  - `frontend/vite.config.ts` - 代理配置
  - `backend/app/main.py` - 启动时 Neo4j 连接检测

## ADDED Requirements

### Requirement: 统一 API 配置管理
系统应提供统一的 API 配置管理，避免各页面各自管理 API 地址。

#### Scenario: API 配置统一
- **WHEN** 前端应用启动
- **THEN** 所有 API 调用使用统一的配置
- **AND** 通过 Vite 代理转发到后端

### Requirement: API 连接状态检测
系统应在前端显示 API 连接状态，帮助用户快速定位问题。

#### Scenario: 后端不可用
- **WHEN** 后端服务不可用
- **THEN** 前端显示明确的连接错误提示
- **AND** 提供重试或检查后端的建议

### Requirement: 服务启动顺序保证
后端启动时应确保 Neo4j 已就绪，避免启动失败。

#### Scenario: Neo4j 未就绪
- **WHEN** 后端启动时 Neo4j 未就绪
- **THEN** 后端应等待 Neo4j 就绪后再完成启动
- **AND** 显示连接状态日志

## MODIFIED Requirements

### Requirement: 前端 API 调用方式
所有前端页面必须使用相对路径调用 API，通过 Vite 代理转发。

**修改前**: 各页面独立定义 `API_BASE`，可能使用硬编码地址
**修改后**: 所有页面使用统一的 `api.ts` 服务模块

## REMOVED Requirements
无
