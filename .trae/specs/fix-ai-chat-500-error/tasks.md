# Tasks

- [x] Task 1: 添加 LLM 服务诊断端点
  - [x] 创建 `/api/chat/test` GET 端点
  - [x] 返回 LLM 配置信息（Provider, Model, API Key 状态）
  - [x] 测试 LLM API 连接

- [x] Task 2: 增强 Chat API 错误处理
  - [x] 捕获并分类 LLM API 错误（API Key 错误、网络错误、配额错误）
  - [x] 返回结构化错误响应
  - [x] 添加详细日志记录

- [x] Task 3: 优化前端错误展示
  - [x] 解析后端错误响应
  - [x] 展示友好的错误信息
  - [x] 提供解决建议

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 2
