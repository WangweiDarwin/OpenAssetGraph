# 新增 Project 管理页面和最近浏览功能 Spec

## Why
当前系统缺乏持久化存储已扫描项目信息资产的功能，用户无法方便地管理和查看历史扫描的项目。同时，Topology 页面的项目切换不够便捷，需要增加最近浏览记录功能。

## What Changes
- 在一级导航中新增 "Project" 栏目，用于持久化存储和管理已扫描项目
- 在 Topology 页面的项目下拉菜单中，保留最近浏览的 5 个项目
- 使用 localStorage 存储最近浏览记录

## Impact
- Affected specs: 无
- Affected code:
  - `frontend/src/App.tsx` - 新增 Project 路由和菜单项
  - `frontend/src/pages/ProjectPage.tsx` - 新建项目管理页面
  - `frontend/src/pages/TopologyPage.tsx` - 添加最近浏览功能
  - `frontend/src/services/api.ts` - 新增项目相关 API
  - `backend/app/api/projects.py` - 扩展项目 API

## ADDED Requirements

### Requirement: Project 管理页面
系统应提供 Project 管理页面，用于持久化存储和管理已扫描项目的信息资产架构数据。

#### Scenario: 查看项目列表
- **WHEN** 用户访问 Project 页面
- **THEN** 显示所有已扫描项目的列表
- **AND** 每个项目显示名称、节点数、边数、扫描时间等信息

#### Scenario: 查看项目详情
- **WHEN** 用户点击某个项目
- **THEN** 显示该项目的详细架构信息
- **AND** 可以查看拓扑图、节点列表、关系列表

#### Scenario: 删除项目
- **WHEN** 用户删除某个项目
- **THEN** 从数据库中删除该项目的所有数据
- **AND** 从项目列表中移除

### Requirement: 最近浏览项目记录
Topology 页面应保留最近浏览的 5 个项目供用户快速选择。

#### Scenario: 记录浏览历史
- **WHEN** 用户在 Topology 页面切换项目
- **THEN** 系统记录该项目的浏览时间
- **AND** 更新最近浏览列表

#### Scenario: 显示最近浏览
- **WHEN** 用户打开 Topology 页面的项目下拉菜单
- **THEN** 在顶部显示最近浏览的 5 个项目
- **AND** 按浏览时间倒序排列

#### Scenario: 持久化浏览记录
- **WHEN** 用户刷新页面或重新打开应用
- **THEN** 最近浏览记录从 localStorage 恢复
- **AND** 保持之前的浏览顺序

## MODIFIED Requirements
无

## REMOVED Requirements
无
