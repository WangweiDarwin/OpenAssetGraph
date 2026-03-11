# Tasks

- [x] Task 1: 修改 Chat API 使用 GraphRAGService
  - [x] 修改 chat() 函数，使用 GraphRAGService 替代直接 LLM 调用
  - [x] 添加 Neo4j 连接错误处理（当 Neo4j 不可用时降级到直接 LLM）
  - [x] 返回上下文摘要信息

- [ ] Task 2: 优化拓扑上下文生成
  - [x] 添加项目名称过滤功能
  - [x] 生成结构化的拓扑摘要
  - [x] 限制上下文大小，避免超出 LLM token 限制

# Task Dependencies
- Task 2 依赖 Task 1