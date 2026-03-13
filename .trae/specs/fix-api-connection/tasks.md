# Tasks

- [x] Task 1: 创建统一 API 配置模块
  - [x] 在 `services/api.ts` 中创建统一的 API 请求函数
  - [x] 添加连接状态检测功能
  - [x] 导出统一的 API 调用方法

- [x] Task 2: 重构 TopologyPage 使用统一 API
  - [x] 移除页面内的 API_BASE 定义
  - [x] 使用 api.ts 中的统一方法
  - [x] 添加错误处理和用户提示

- [x] Task 3: 重构 ScanPage 使用统一 API
  - [x] 移除页面内的 API_BASE 定义
  - [x] 使用 api.ts 中的统一方法
  - [x] 添加错误处理和用户提示

- [x] Task 4: 重构 ChatPage 使用统一 API
  - [x] 确认已使用相对路径
  - [x] 添加错误处理和用户提示

- [x] Task 5: 验证 Vite 代理配置
  - [x] 确认 vite.config.ts 代理配置正确
  - [x] 测试代理转发功能

- [x] Task 6: 启动所有服务并验证
  - [x] 启动 Neo4j 容器
  - [x] 启动后端服务
  - [x] 启动前端服务
  - [x] 验证所有页面功能正常

# Task Dependencies
- Task 2, Task 3, Task 4 依赖 Task 1
- Task 6 依赖 Task 1-5
