import React, { useState, useEffect, useCallback } from 'react';
import { Layout, Spin, message, Typography, Row, Col, Card, Statistic } from 'antd';
import { NodeIndexOutlined, BranchesOutlined, DatabaseOutlined } from '@ant-design/icons';
import TopologyGraph from '../components/TopologyGraph';
import NodeDetailPanel from '../components/NodeDetailPanel';
import SearchPanel from '../components/SearchPanel';
import { topologyApi, TopologyNode, TopologyEdge, TopologyStats } from '../services/api';

const { Content, Sider } = Layout;
const { Title } = Typography;

const TopologyPage: React.FC = () => {
  const [nodes, setNodes] = useState<TopologyNode[]>([]);
  const [edges, setEdges] = useState<TopologyEdge[]>([]);
  const [selectedNode, setSelectedNode] = useState<TopologyNode | null>(null);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState<TopologyStats | null>(null);
  const [searchLoading, setSearchLoading] = useState(false);

  const loadTopology = useCallback(async () => {
    setLoading(true);
    try {
      const data = await topologyApi.getTopology(undefined, 200);
      setNodes(data.nodes);
      setEdges(data.edges);
    } catch (error) {
      console.error('Failed to load topology:', error);
      message.error('Failed to load topology data');
    } finally {
      setLoading(false);
    }
  }, []);

  const loadStats = useCallback(async () => {
    try {
      const data = await topologyApi.getStats();
      setStats(data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    }
  }, []);

  useEffect(() => {
    loadTopology();
    loadStats();
  }, [loadTopology, loadStats]);

  const handleNodeClick = (node: TopologyNode) => {
    setSelectedNode(node);
  };

  const handleNodeDoubleClick = async (node: TopologyNode) => {
    try {
      const detailedNode = await topologyApi.getNode(node.id);
      setSelectedNode(detailedNode);
    } catch (error) {
      console.error('Failed to load node details:', error);
      message.error('Failed to load node details');
    }
  };

  const handleSearch = async (query: string, filters: { type: string | null; property: string | null }) => {
    setSearchLoading(true);
    try {
      const types = filters.type ? [filters.type] : undefined;
      const response = await topologyApi.searchNodes(query, types, 50);
      if (response.results.length > 0) {
        const resultNodes = response.results.map(r => ({
          id: r.id,
          label: r.label,
          type: r.type,
          properties: r.properties,
        }));
        setNodes(resultNodes);
        setEdges([]);
        message.success(`Found ${response.count} nodes`);
      } else {
        message.info('No results found');
      }
    } catch (error) {
      console.error('Search failed:', error);
      message.error('Search failed');
    } finally {
      setSearchLoading(false);
    }
  };

  const handleNodeSelect = (node: TopologyNode) => {
    setSelectedNode(node);
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100%' }}>
        <Spin size="large" tip="Loading topology..." />
      </div>
    );
  }

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      {stats && (
        <Row gutter={16} style={{ marginBottom: 16 }}>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Total Nodes"
                value={stats.total_nodes}
                prefix={<NodeIndexOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Total Edges"
                value={stats.total_edges}
                prefix={<BranchesOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Node Types"
                value={Object.keys(stats.node_types).length}
                prefix={<DatabaseOutlined />}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card size="small">
              <Statistic
                title="Largest Type"
                value={
                  stats.node_types
                    ? Object.entries(stats.node_types).sort((a, b) => b[1] - a[1])[0]?.[0] || 'N/A'
                    : 'N/A'
                }
              />
            </Card>
          </Col>
        </Row>
      )}

      <Layout style={{ flex: 1, background: 'transparent' }}>
        <Sider width={300} theme="light" style={{ padding: 8, overflow: 'auto' }}>
          <SearchPanel
            onSearch={handleSearch}
            onNodeSelect={handleNodeSelect}
            nodes={nodes}
            loading={searchLoading}
          />
        </Sider>
        <Content style={{ padding: '0 8px' }}>
          <TopologyGraph
            nodes={nodes}
            edges={edges}
            onNodeClick={handleNodeClick}
            onNodeDoubleClick={handleNodeDoubleClick}
            width={800}
            height={500}
          />
        </Content>
        <Sider width={350} theme="light" style={{ padding: 8, overflow: 'auto' }}>
          <NodeDetailPanel node={selectedNode} />
        </Sider>
      </Layout>
    </div>
  );
};

export default TopologyPage;
