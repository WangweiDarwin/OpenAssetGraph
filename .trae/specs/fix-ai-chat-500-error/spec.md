# 修复 AI Chat 500 错误 Spec

## Why
AI Chat 功能始终返回 HTTP 500 错误，用户无法正常使用 AI 对话功能。需要诊断并修复 LLM 服务调用问题。

## What Changes
- 添加独立的 LLM 服务测试端点
- 增强 Chat API 错误处理和日志
- 添加 API Key 验证机制
- 优化 LLM 服务初始化流程

## Impact
- Affected code: `backend/app/api/chat.py`, `backend/app/services/llm/openai_service.py`, `backend/app/services/llm/llm_factory.py`

## ADDED Requirements

### Requirement: LLM 服务诊断端点
系统应提供 LLM 服务诊断端点，用于测试 LLM 配置是否正确。

#### Scenario: 成功诊断
- **WHEN** 用户访问 `/api/chat/test` 端点
- **THEN** 系统返回 LLM 配置状态和测试结果

### Requirement: 详细错误信息
Chat API 应返回详细的错误信息，帮助定位问题。

#### Scenario: API Key 无效
- **WHEN** GLM API Key 无效或过期
- **THEN** 系统返回明确的错误信息，提示用户检查 API Key

#### Scenario: 网络连接失败
- **WHEN** 无法连接到 LLM 服务
- **THEN** 系统返回网络错误信息

### Requirement: 前端错误展示优化
前端应展示更友好的错误信息。

#### Scenario: 显示详细错误
- **WHEN** 后端返回错误
- **THEN** 前端展示错误类型和建议解决方案
