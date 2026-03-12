# Checklist

## Pydantic 模型修复

- [ ] `TableInfo.schema` 字段已重命名为 `schema_name`
- [ ] 所有引用该字段的代码已更新
- [ ] 启动后端无 UserWarning 警告

## 端口配置检查

- [ ] `api.ts` 中 API_BASE_URL 端口正确 (8000)
- [ ] `TopologyPage.tsx` 中 API_BASE 端口正确 (8000)
- [ ] `ScanPage.tsx` 中 API_BASE 端口正确 (8000)
- [ ] `vite.config.ts` 中代理目标端口正确 (8000)

## 启动验证

- [ ] 所有相关进程已终止
- [ ] Neo4j 服务正常启动
- [ ] 后端服务正常启动 (端口 8000)
- [ ] 前端服务正常启动 (端口 3000)
- [ ] 拓扑页面正常加载数据
- [ ] 扫描页面正常工作
- [ ] AI Chat 正常工作
