# Tasks

- [x] Task 1: 扩展Neo4jService添加批量操作方法
  - [x] 添加 `execute_query` 方法用于执行自定义Cypher查询
  - [x] 添加 `batch_create_nodes` 方法用于批量创建节点
  - [x] 添加 `batch_create_relationships` 方法用于批量创建关系
  - [x] 添加 `clear_all_data` 方法用于清空数据库
  - [x] 添加 `get_node_count` 方法用于获取节点数量

- [x] Task 2: 创建数据迁移脚本
  - [x] 在mock_data.py中添加 `migrate_to_neo4j` 方法
  - [x] 实现将MOCK_NODES、MALL_NODES、ONLINE_BOUTIQUE_NODES导入Neo4j
  - [x] 实现将对应的EDGES导入Neo4j
  - [x] 添加迁移状态检查和日志

- [x] Task 3: 修改应用启动初始化
  - [x] 在main.py中添加Neo4j连接初始化
  - [x] 添加启动时自动迁移逻辑（当Neo4j为空时）
  - [x] 添加健康检查端点验证Neo4j连接

- [x] Task 4: 重构Topology API使用Neo4j
  - [x] 修改topology.py，设置USE_MOCK_DATA = False
  - [x] 确保所有端点正确使用TopologyService
  - [x] 添加错误处理和降级逻辑

- [x] Task 5: 重构Scan API使用Neo4j
  - [x] 修改scan.py，使用Neo4jService存储数据
  - [x] 实现项目扫描结果的持久化
  - [x] 更新扫描模板和响应格式

- [x] Task 6: 验证和测试
  - [x] 验证数据迁移完整性
  - [x] 测试Topology API端点
  - [x] 测试Scan API端点
  - [x] 测试AI Chat关联图数据功能

# Task Dependencies
- Task 2 依赖 Task 1
- Task 3 依赖 Task 2
- Task 4 依赖 Task 3
- Task 5 依赖 Task 3
- Task 6 依赖 Task 4, Task 5
