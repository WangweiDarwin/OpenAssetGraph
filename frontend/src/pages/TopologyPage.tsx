import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Spin, message, Select, Button, Space, Input, Tag, Empty, Tooltip, Drawer } from 'antd';
import { ReloadOutlined, SearchOutlined, ZoomInOutlined, ZoomOutOutlined, FullscreenOutlined, CloseOutlined } from '@ant-design/icons';
import { useSearchParams } from 'react-router-dom';
import TopologyGraph from '../components/TopologyGraph';
import { topologyApi, TopologyNode, TopologyEdge, TopologyStats } from '../services/api';
import './TopologyPage.css';

const { Option } = Select;

interface Project {
  id: string;
  name: string;
  description: string;
}

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

  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8005';
      
const loadProjects = useCallback(async () => {
    try {
      const response = await fetch(`${API_BASE}/api/topology/projects`);
      const data = await response.json();
      setProjects(data);
    } catch (error) {
      console.error('Failed to load projects:', error);
    }
  }, []);

  const loadTopology = useCallback(async (projectId?: string) => {
    setLoading(true);
    try {
      const projectToLoad = projectId || currentProject;
      if (projectToLoad && projectToLoad !== 'default') {
        await fetch(`${API_BASE}/api/topology/projects/${projectToLoad}/switch`, {
          method: 'POST',
        });
      }
      const data = await topologyApi.getTopology(undefined, 200);
      setNodes(data.nodes);
      setEdges(data.edges);
    } catch (error) {
      console.error('Failed to load topology:', error);
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
  }, [loadProjects]);

  useEffect(() => {
    if (projectFromUrl) {
      setCurrentProject(projectFromUrl);
      loadTopology(projectFromUrl);
      loadStats();
    } else {
      loadTopology();
      loadStats();
    }
  }, [projectFromUrl]);

  const handleProjectChange = async (projectId: string) => {
    setLoading(true);
    try {
      await fetch(`${API_BASE}/api/topology/projects/${projectId}/switch`, {
        method: 'POST',
      });
      setCurrentProject(projectId);
      const data = await topologyApi.getTopology(undefined, 200);
      setNodes(data.nodes);
      setEdges(data.edges);
      const statsData = await topologyApi.getStats();
      setStats(statsData);
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
        <p>Loading topology...</p>
      </div>
    );
  }

  return (
    <div className="topology-page">
      <div className="topology-toolbar">
        <div className="toolbar-left">
          <Space.Compact className="search-box">
            <Input
              placeholder="Search nodes..."
              value={searchQuery}
              onChange={e => setSearchQuery(e.target.value)}
              onPressEnter={handleSearch}
              prefix={<SearchOutlined />}
              allowClear
            />
            <Button type="primary" onClick={handleSearch} loading={searchLoading}>
              Search
            </Button>
          </Space.Compact>
        </div>
        
        <div className="toolbar-center">
          <div className="stats-mini">
            <span className="stat-item">
              <span className="stat-label">Nodes</span>
              <span className="stat-value">{stats?.total_nodes || 0}</span>
            </span>
            <span className="stat-divider">|</span>
            <span className="stat-item">
              <span className="stat-label">Edges</span>
              <span className="stat-value">{stats?.total_edges || 0}</span>
            </span>
            <span className="stat-divider">|</span>
            <span className="stat-item">
              <span className="stat-label">Types</span>
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
            style={{ width: 160 }}
            size="small"
          >
            {projects.map(p => (
              <Option key={p.id} value={p.id}>{p.name}</Option>
            ))}
          </Select>
          <Button icon={<ReloadOutlined />} onClick={handleRefresh} size="small">
            Refresh
          </Button>
        </div>
      </div>

      <div className="topology-content">
        {nodes.length === 0 ? (
          <div className="empty-topology">
            <Empty description="No topology data. Scan a project to get started." />
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
              <h4>Properties</h4>
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
                <Empty description="No properties" image={Empty.PRESENTED_IMAGE_SIMPLE} />
              )}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default TopologyPage;
