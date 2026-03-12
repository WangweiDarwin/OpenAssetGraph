# Tasks

- [ ] Task 1: 修复 Pydantic 模型字段命名冲突
  - [ ] 将 `TableInfo.schema` 字段重命名为 `schema_name`
  - [ ] 搜索并更新所有引用 `schema` 字段的代码
  - [ ] 验证修复后无警告信息

- [ ] Task 2: 检查并修复前端端口配置
  - [ ] 确认 `api.ts` 中 API_BASE_URL 端口为 8000
  - [ ] 确认 `TopologyPage.tsx` 中 API_BASE 端口为 8000
  - [ ] 确认 `ScanPage.tsx` 中 API_BASE 端口为 8000
  - [ ] 确认 `vite.config.ts` 中代理目标端口为 8000

- [ ] Task 3: 创建端口检测脚本
  - [ ] 创建 PowerShell 脚本检测端口占用
  - [ ] 提供终止占用进程的命令

- [ ] Task 4: 创建启动指南文档
  - [ ] 编写完整的启动步骤说明
  - [ ] 包含环境变量配置
  - [ ] 包含依赖服务启动顺序
  - [ ] 包含常见问题排查

- [ ] Task 5: 验证修复效果
  - [ ] 终止所有相关进程
  - [ ] 按启动指南重新启动服务
  - [ ] 验证拓扑页面正常加载
  - [ ] 验证扫描页面正常工作
  - [ ] 验证 AI Chat 正常工作

# Task Dependencies
- Task 5 依赖 Task 1, Task 2, Task 3, Task 4
