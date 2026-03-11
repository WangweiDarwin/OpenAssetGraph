# Checklist

- [x] `/api/chat/test` 端点已添加到 chat.py
- [x] Chat API 返回结构化错误信息（包含 type, message, suggestion）
- [x] 前端展示友好的错误信息（包含解决建议）
- [ ] LLM 服务可正常调用并返回响应（需用户手动测试）

## 测试步骤

### 1. 启动后端
```powershell
cd d:\OAG\backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8005
```

### 2. 测试 LLM 诊断端点
访问: http://localhost:8005/api/chat/test

### 3. 启动前端
```powershell
cd d:\OAG\frontend
npm run dev
```

### 4. 测试 AI Chat
访问: http://localhost:3000/chat

## 已完成的修改

### 后端修改
1. **chat.py** - 添加 `/api/chat/test` 诊断端点
2. **chat.py** - 增强 Chat API 错误处理，返回结构化错误信息

### 前端修改
1. **ChatPage.tsx** - 解析后端错误响应，展示友好的错误信息

### 配置修改
1. **vite.config.ts** - proxy 端口更新为 8005
