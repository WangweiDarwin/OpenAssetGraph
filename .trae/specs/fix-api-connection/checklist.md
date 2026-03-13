# Checklist

## API 配置统一

- [x] `services/api.ts` 提供统一的 API 请求方法
- [x] 所有页面不再独立定义 API_BASE
- [x] 所有 API 调用使用相对路径

## 页面功能验证

- [x] TopologyPage 正常加载拓扑数据
- [ ] ScanPage 正常显示已扫描项目列表
- [ ] ScanPage 正常扫描新项目
- [ ] ChatPage 正常发送消息并收到响应
- [ ] 项目引用功能 (#项目名#) 正常工作

## 服务状态

- [x] Neo4j 容器运行正常 (healthy)
- [x] 后端服务运行在 8000 端口
- [x] 前端服务运行在 3001 端口
- [x] Vite 代理正常转发 API 请求
