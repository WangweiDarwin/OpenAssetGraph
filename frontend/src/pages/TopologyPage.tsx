import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Spin, message, Select, Button, Space, Input, Tag, Empty, Drawer } from 'antd';
import { ReloadOutlined, SearchOutlined, CloseOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import TopologyGraph from '../components/TopologyGraph';
import { topologyApi, TopologyNode, TopologyEdge, TopologyStats } from '../services/api';
import './TopologyPage.css';

const { Option } = Select;

const RECENT_PROJECTS_KEY = 'oag_recent_projects';
const MAX_RECENT_PROJECTS = 5;

interface Project {
  id: string;
  name: string;
  description: string;
}

interface RecentProject {
  id: string;
  name: string;
  timestamp: number;
}

const getRecentProjects = (): RecentProject[] => {
  try {
    const stored = localStorage.getItem(RECENT_PROJECTS_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
};

const saveRecentProject = (projectId: string, projectName: string) => {
  const recent = getRecentProjects();
  const filtered = recent.filter(p => p.id !== projectId);
  const updated = [{ id: projectId, name: projectName, timestamp: Date.now() }, ...filtered].slice(0, MAX_RECENT_PROJECTS);
  localStorage.setItem(RECENT_PROJECTS_KEY, JSON.stringify(updated));
};

const TopologyPage: React.FC = () => {
  const [searchParams] = useSearchParams();
  const projectFromUrl = searchParams.get('project');
  
  const [nodes, setNodes] = useState<TopologyNode[]>([]);
  const [edges, setEdges] = useState<TopologyEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<TopologyStats | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState('');
  const [projects, setProjects] = useState<Project[]>([]);
  const [currentProject, setCurrentProject] = useState<string>(projectFromUrl || 'default');
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [connectionError, setConnectionError] = useState<string | null>(null);
  const [recentProjects, setRecentProjects] = useState<RecentProject[]>([]);
      
const loadProjects = useCallback(async () => {
    try {
      const data = await topologyApi.getProjects();
      setProjects(data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  }, []);

  const loadTopology = useCallback(async (projectId?: string) => {
    setLoading(true);
    setConnectionError(null);
    try {
      const projectToLoad = projectId || currentProject;
      if (projectToLoad && projectToLoad !== 'default') {
        await topologyApi.switchProject(projectToLoad);
      }
      const data = await topologyApi.getTopology(undefined, 1000);
      setNodes(data.nodes);
      setEdges(data.edges);
    } catch (error: any) {
      console.error('Failed to load topology:', error);
      setConnectionError(error?.message || 'Failed to load topology data');
      message.error('Failed to load topology data');
    } finally {
      setLoading(false);
    }
  }, [currentProject]);

  const loadStats = useCallback(async () => {
    try {
      const data = await topologyApi.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }, []);

  useEffect(() => {
    loadProjects();
    setRecentProjects(getRecentProjects());
  }, [loadProjects]);

  useEffect(() => {
    if (projectFromUrl) {
      setCurrentProject(projectFromUrl);
      loadTopology(projectFromUrl);
      loadStats();
      const project = projects.find(p => p.id === projectFromUrl);
      if (project) {
        saveRecentProject(projectFromUrl, project.name);
        setRecentProjects(getRecentProjects());
      }
    } else {
      loadTopology();
      loadStats();
    }
  }, [projectFromUrl]);

  const handleProjectChange = async (projectId: string) => {
    setLoading(true);
    try {
      await topologyApi.switchProject(projectId);
      setCurrentProject(projectId);
      const data = await topologyApi.getTopology(undefined, 1000);
      setNodes(data.nodes);
      setEdges(data.edges);
      const statsData = await topologyApi.getStats();
      setStats(statsData);
      
      const project = projects.find(p => p.id === projectId);
      if (project) {
        saveRecentProject(projectId, project.name);
        setRecentProjects(getRecentProjects());
      }
      
      message.success(`Switched to: ${projectId}`);
    } catch (error) {
      console.error('Failed to switch project:', error);
      message.error('Failed to switch project');
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    await loadTopology();
    await loadStats();
    message.success('Refreshed');
  };

  const handleNodeClick = (node: TopologyNode) => {
    setSelectedNode(node);
    setDrawerVisible(true);
  };

  const handleNodeDoubleClick = async (node: TopologyNode) => {
    try {
      const detailedNode = await topologyApi.getNode(node.id);
      setSelectedNode(detailedNode);
      setDrawerVisible(true);
    } catch (error) {
      console.error('Failed to load node details:', error);
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setSearchLoading(true);
    try {
      const response = await topologyApi.searchNodes(searchQuery, undefined, 50);
      if (response.results.length > 0) {
        setNodes(response.results);
        setEdges([]);
        message.success(`Found ${response.count} nodes`);
      } else {
        message.info('No results found');
      }
    } catch (error) {
      console.error('Search failed:', error);
    } finally {
      setSearchLoading(false);
    }
  };

  const nodeTypeColors: Record<string, string> = {
    Database: '#10b981',
    Service: '#3b82f6',
    API: '#8b5cf6',
    FrontendApp: '#f59e0b',
    Table: '#6b7280',
    Library: '#ec4899',
  };

  const nodeTypeCount = useMemo(() => {
    const counts: Record<string, number> = {};
    nodes.forEach(n => {
      counts[n.type] = (counts[n.type] || 0) + 1;
    });
    return counts;
  }, [nodes]);

  if (loading && nodes.length === 0) {
    return (
      <div className="loading-container">
        <Spin size="large" />
        <p>加载拓扑数据...</p>
      </div>
    );
  }

  return (
    <div className="topology-page">
      <div className="topology-toolbar">
        <div className="toolbar-left">
          <Space.Compact className="search-box">
            <Input
              placeholder="搜索节点..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onPressEnter={handleSearch}
              prefix={<SearchOutlined />}
              allowClear
            />
            <Button type="primary" onClick={handleSearch} loading={searchLoading}>
              搜索
            </Button>
          </Space.Compact>
        </div>
        
        <div className="toolbar-center">
          <div className="stats-mini">
            <span className="stat-item">
              <span className="stat-label">节点</span>
              <span className="stat-value">{stats?.total_nodes || 0}</span>
            </span>
            <span className="stat-divider">|</span>
            <span className="stat-item">
              <span className="stat-label">边</span>
              <span className="stat-value">{stats?.total_edges || 0}</span>
            </span>
            <span className="stat-divider">|</span>
            <span className="stat-item">
              <span className="stat-label">类型</span>
              <span className="stat-value">{Object.keys(nodeTypeCount).length}</span>
            </span>
          </div>
          
          <div className="type-tags">
            {Object.entries(nodeTypeCount).map(([type, count]) => (
              <Tag key={type} color={nodeTypeColors[type] || '#666'} className="type-tag">
                {type} ({count})
              </Tag>
            ))}
          </div>
        </div>
        
        <div className="toolbar-right">
          <Select
            value={currentProject}
            onChange={handleProjectChange}
            style={{ width: 180 }}
            size="small"
            placeholder="选择项目"
          >
            {recentProjects.length > 0 && (
              <Select.OptGroup label={<span><ClockCircleOutlined /> 最近访问</span>}>
                {recentProjects.map(p => (
                  <Option key={p.id} value={p.id}>{p.name}</Option>
                ))}
              </Select.OptGroup>
            )}
            <Select.OptGroup label="所有项目">
              {projects.filter(p => !recentProjects.find(r => r.id === p.id)).map(p => (
                <Option key={p.id} value={p.id}>{p.name}</Option>
              ))}
            </Select.OptGroup>
          </Select>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} size="small">
            刷新
          </Button>
        </div>
      </div>

      <div className="topology-content">
        {connectionError ? (
          <div className="error-container">
            <Empty 
              description={
                <div>
                  <p>连接错误: {connectionError}</p>
                  <p>请检查后端服务是否在 8000 端口运行</p>
                  <Button type="primary" onClick={handleRefresh}>重试</Button>
                </div>
              } 
            />
          </div>
        ) : nodes.length === 0 ? (
          <div className="empty-topology">
            <Empty description="暂无拓扑数据。扫描项目以开始。" />
          </div>
        ) : (
          <TopologyGraph
            nodes={nodes}
            edges={edges}
            onNodeClick={handleNodeClick}
            onNodeDoubleClick={handleNodeDoubleClick}
          />
        )}
      </div>

      <Drawer
        title={
          selectedNode ? (
            <Space>
              <Tag color={nodeTypeColors[selectedNode.type] || '#666'}>
                {selectedNode.type}
              </Tag>
              <span>{selectedNode.label}</span>
            </Space>
          ) : null
        }
        placement="right"
        width={360}
        onClose={() => setDrawerVisible(false)}
        open={drawerVisible}
        className="node-drawer"
        closeIcon={<CloseOutlined />}
      >
        {selectedNode && (
          <div className="node-details">
            <div className="node-id">ID: {selectedNode.id}</div>
            <div className="properties-section">
              <h4>属性</h4>
              {selectedNode.properties && Object.keys(selectedNode.properties).length > 0 ? (
                <div className="property-list">
                  {Object.entries(selectedNode.properties).map(([key, value]) => (
                    <div key={key} className="property-item">
                      <span className="property-key">{key}</span>
                      <span className="property-value">{String(value)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <Empty description="暂无属性" image={Empty.PRESENTED_IMAGE_SIMPLE} />
              )}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default TopologyPage;
