# OpenAssetGraph (OAG)

**AI-Native Digital Twin for Enterprise Software Architecture**

OpenAssetGraph 是一个智能平台，结合图数据库技术与 AI，为企业软件资产及其关系提供全面的可视化和分析能力。

## ✨ 核心功能

- **🔍 GitHub 项目扫描** - 自动分析 GitHub 仓库，提取架构信息（支持 Go、Java、Python、JavaScript 等）
- **📊 拓扑可视化** - 交互式图形展示数据库、服务、API、应用之间的关系
- **🤖 AI 智能分析** - 使用自然语言查询架构信息，支持项目上下文引用
- **📁 项目管理** - 持久化存储和管理扫描的项目架构资产
- **🔗 依赖追踪** - 理解组件连接方式，识别潜在风险
- **📝 架构评审** - AI 辅助评估架构提案

## 🛠 技术栈

| 层级 | 技术 |
|------|------|
| 前端 | React 18, TypeScript, Ant Design, @antv/g6 |
| 后端 | Python 3.11+, FastAPI, Neo4j |
| LLM | GLM-4-Plus, Kimi, DeepSeek, OpenAI (多提供商支持) |
| 部署 | Docker, Docker Compose |

## 📦 安装与运行

### 前置要求

- Python 3.11+
- Node.js 18+
- Docker Desktop（用于 Neo4j）
- Git

### 方式一：本地开发（推荐）

#### 1. 克隆项目

```bash
git clone https://github.com/your-username/OAG.git
cd OAG
```

#### 2. 启动 Neo4j 数据库

```bash
docker-compose up -d neo4j
```

等待 Neo4j 启动完成（约 30 秒），访问 http://localhost:7474 验证。
- 用户名: `neo4j`
- 密码: `password123`

#### 3. 配置后端

```bash
cd backend

# 创建虚拟环境
python -m venv venv
.\venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 创建 .env 文件
cp .env.example .env
```

编辑 `.env` 文件，配置 API Key：

```env
# LLM 配置 (必填)
LLM_PROVIDER=glm
LLM_MODEL=glm-4-plus
GLM_API_KEY=your-glm-api-key  # 从 https://open.bigmodel.cn/ 获取

# GitHub Token (可选，用于提高 API 限制)
GITHUB_TOKEN=your-github-token

# Neo4j 配置
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password123
```

#### 4. 启动后端服务

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

访问 http://localhost:8000/docs 查看 API 文档。

#### 5. 启动前端服务（新终端）

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

访问 http://localhost:3000 开始使用！

### 方式二：Docker 一键部署

```bash
docker-compose up -d
```

访问 http://localhost:3000

## 🚀 快速开始

### 1. 扫描 GitHub 项目

1. 点击左侧菜单 **"扫描"**
2. 输入 GitHub 仓库 URL，例如：
   - `https://github.com/zeromicro/go-zero` (Go 微服务框架)
   - `https://github.com/macrozheng/mall` (Java 电商系统)
   - `https://github.com/GoogleCloudPlatform/microservices-demo` (Google 微服务示例)
3. 点击 **"开始扫描"**
4. 等待扫描完成，系统将自动提取：
   - 项目模块结构
   - 技术栈信息
   - 服务依赖关系
   - 数据库和缓存配置

### 2. 查看拓扑图

1. 点击左侧菜单 **"拓扑"**
2. 在下拉菜单中选择已扫描的项目
3. 拖拽、缩放查看架构图
4. 点击节点查看详细信息

### 3. AI 智能分析

1. 点击左侧菜单 **"AI 对话"**
2. 使用自然语言提问，例如：
   - `分析 #go-zero# 的架构`
   - `#mall# 项目有哪些微服务？`
   - `比较 #mall# 和 #online-boutique# 的区别`
   - `#go-zero# 项目存在哪些潜在问题？`

**项目引用语法**: 使用 `#项目名#` 引用特定项目，AI 将基于该项目的拓扑数据回答。

## 🔧 配置说明

### 支持的 LLM 提供商

| 提供商 | 模型 | API Key 获取 |
|--------|------|--------------|
| **GLM (智谱AI)** | glm-4, glm-4-flash, glm-4-plus | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| **Kimi (月之暗面)** | moonshot-v1-8k, moonshot-v1-32k | [platform.moonshot.cn](https://platform.moonshot.cn/) |
| **DeepSeek** | deepseek-chat, deepseek-coder | [platform.deepseek.com](https://platform.deepseek.com/) |
| **OpenAI** | gpt-4, gpt-4-turbo, gpt-4o | [platform.openai.com](https://platform.openai.com/) |

**推荐**: 使用 `glm-4-plus` 获得最佳分析效果。

### 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `LLM_PROVIDER` | LLM 提供商 | `glm` |
| `LLM_MODEL` | 模型名称 | `glm-4-plus` |
| `LLM_TEMPERATURE` | 生成温度 | `0.7` |
| `LLM_MAX_TOKENS` | 最大 Token 数 | `4096` |
| `GITHUB_TOKEN` | GitHub API Token | - |

## 📁 项目结构

```
OAG/
├── backend/
│   ├── app/
│   │   ├── api/              # API 路由
│   │   │   ├── chat.py       # AI 对话 API
│   │   │   ├── scan.py       # 项目扫描 API
│   │   │   └── topology.py   # 拓扑数据 API
│   │   ├── services/
│   │   │   ├── analyzers/    # 代码分析器
│   │   │   ├── llm/          # LLM 服务
│   │   │   ├── github_service.py    # GitHub API
│   │   │   └── graph_service.py     # Neo4j 服务
│   │   ├── models/           # 数据模型
│   │   └── main.py           # 应用入口
│   ├── requirements.txt
│   └── .env                  # 环境配置
├── frontend/
│   ├── src/
│   │   ├── components/       # React 组件
│   │   ├── pages/            # 页面组件
│   │   ├── services/         # API 服务
│   │   └── App.tsx
│   └── package.json
├── docker-compose.yml
└── README.md
```

## 🔌 API 端点

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/topology` | GET | 获取完整拓扑 |
| `/api/topology/search` | GET | 搜索节点 |
| `/api/topology/stats` | GET | 获取统计信息 |
| `/api/projects` | GET | 列出所有项目 |
| `/api/scan/github` | POST | 扫描 GitHub 仓库 |
| `/api/scan/project/{name}` | DELETE | 删除项目 |
| `/api/chat` | POST | AI 对话 |

完整 API 文档: http://localhost:8000/docs

## 💡 使用场景

- 📊 **架构文档化** - 自动生成架构图，替代手工维护
- 🔍 **依赖分析** - 识别循环依赖和潜在风险
- 📈 **变更影响评估** - 分析修改对整体架构的影响
- 🎓 **知识传承** - 帮助新成员快速理解系统架构
- 🤝 **决策支持** - AI 辅助架构决策
- 📋 **多项目管理** - 统一管理多个项目的架构资产

## 🐛 故障排除

### Neo4j 连接失败

```bash
# 检查 Neo4j 容器状态
docker ps

# 重启 Neo4j
docker-compose restart neo4j

# 查看日志
docker logs oag-neo4j
```

### 后端启动失败

```bash
# 检查 Python 版本
python --version  # 需要 3.11+

# 重新安装依赖
pip install -r requirements.txt --upgrade
```

### 前端无法连接后端

1. 确认后端在 8000 端口运行
2. 检查 CORS 配置
3. 清除浏览器缓存

### AI 分析结果不准确

1. 确保使用 `glm-4-plus` 模型
2. 检查 `.env` 中的 API Key 是否有效
3. 确认项目已正确扫描

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

Apache License 2.0
