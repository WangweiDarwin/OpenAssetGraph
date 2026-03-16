import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Table, Button, Space, Tag, Modal, Descriptions, Spin, Empty, message, Popconfirm, Typography, Tooltip } from 'antd';
import { FolderOutlined, EyeOutlined, DeleteOutlined, ReloadOutlined, ApartmentOutlined, DatabaseOutlined, ApiOutlined, ClockCircleOutlined } from '@ant-design/icons';
import { api, scanApi } from '../services/api';
import './ProjectPage.css';

const { Title, Text } = Typography;

interface ProjectInfo {
  name: string;
  nodeCount: number;
  edgeCount: number;
  lastScanned: string;
  nodeTypes: Record<string, number>;
}

const ProjectPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [projects, setProjects] = useState<ProjectInfo[]>([]);
  const [selectedProject, setSelectedProject] = useState<ProjectInfo | null>(null);
  const [detailVisible, setDetailVisible] = useState(false);

  useEffect(() => {
    loadProjects();
  }, []);

  const loadProjects = async () => {
    setLoading(true);
    try {
      const data = await api.getProjects();
      const projectList = data.projects || [];
      
      const projectInfos: ProjectInfo[] = await Promise.all(
        projectList.map(async (name) => {
          try {
            const stats = await api.getProjectStats(name);
            return {
              name,
              nodeCount: stats.node_count || 0,
              edgeCount: stats.edge_count || 0,
              lastScanned: stats.last_scanned || 'Unknown',
              nodeTypes: stats.node_types || {},
            };
          } catch {
            return {
              name,
              nodeCount: 0,
              edgeCount: 0,
              lastScanned: 'Unknown',
              nodeTypes: {},
            };
          }
        })
      );
      
      setProjects(projectInfos);
    } catch (error: any) {
      message.error(error?.message || 'Failed to load projects');
    } finally {
      setLoading(false);
    }
  };

  const handleViewTopology = (projectName: string) => {
    navigate(`/topology?project=${projectName}`);
  };

  const handleDeleteProject = async (projectName: string) => {
    try {
      await scanApi.deleteProject(projectName);
      message.success(`Project "${projectName}" deleted successfully`);
      loadProjects();
    } catch (error: any) {
      message.error(error?.message || 'Failed to delete project');
    }
  };

  const handleViewDetails = async (project: ProjectInfo) => {
    setSelectedProject(project);
    setDetailVisible(true);
  };

  const columns = [
    {
      title: 'Project Name',
      dataIndex: 'name',
      key: 'name',
      render: (name: string) => (
        <Space>
          <FolderOutlined style={{ color: '#1890ff' }} />
          <Text strong>{name}</Text>
        </Space>
      ),
    },
    {
      title: 'Nodes',
      dataIndex: 'nodeCount',
      key: 'nodeCount',
      render: (count: number) => (
        <Tag color="blue">
          <ApartmentOutlined /> {count}
        </Tag>
      ),
    },
    {
      title: 'Edges',
      dataIndex: 'edgeCount',
      key: 'edgeCount',
      render: (count: number) => (
        <Tag color="green">
          <ApiOutlined /> {count}
        </Tag>
      ),
    },
    {
      title: 'Node Types',
      dataIndex: 'nodeTypes',
      key: 'nodeTypes',
      render: (types: Record<string, number>) => (
        <Space size="small">
          {Object.entries(types).slice(0, 3).map(([type, count]) => (
            <Tag key={type} color="purple">{type}: {count}</Tag>
          ))}
          {Object.keys(types).length > 3 && (
            <Tag>+{Object.keys(types).length - 3} more</Tag>
          )}
        </Space>
      ),
    },
    {
      title: 'Last Scanned',
      dataIndex: 'lastScanned',
      key: 'lastScanned',
      render: (time: string) => (
        <Space>
          <ClockCircleOutlined />
          <Text type="secondary">{time}</Text>
        </Space>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_: any, record: ProjectInfo) => (
        <Space>
          <Tooltip title="View Topology">
            <Button 
              type="primary" 
              icon={<EyeOutlined />} 
              size="small"
              onClick={() => handleViewTopology(record.name)}
            />
          </Tooltip>
          <Tooltip title="View Details">
            <Button 
              icon={<DatabaseOutlined />} 
              size="small"
              onClick={() => handleViewDetails(record)}
            />
          </Tooltip>
          <Popconfirm
            title="Delete this project?"
            description="This will remove all nodes and edges for this project."
            onConfirm={() => handleDeleteProject(record.name)}
            okText="Delete"
            cancelText="Cancel"
            okButtonProps={{ danger: true }}
          >
            <Tooltip title="Delete">
              <Button 
                danger 
                icon={<DeleteOutlined />} 
                size="small"
              />
            </Tooltip>
          </Popconfirm>
        </Space>
      ),
    },
  ];

  if (loading) {
    return (
      <div className="project-page loading-container">
        <Spin size="large" />
        <p>Loading projects...</p>
      </div>
    );
  }

  return (
    <div className="project-page">
      <div className="project-header">
        <Title level={2}>
          <FolderOutlined /> Projects
        </Title>
        <Text type="secondary">
          Manage your scanned project architecture assets
        </Text>
        <Button 
          icon={<ReloadOutlined />} 
          onClick={loadProjects}
          style={{ marginLeft: 16 }}
        >
          Refresh
        </Button>
      </div>

      <Card className="project-card">
        {projects.length === 0 ? (
          <Empty
            description="No projects found. Scan a project to get started."
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          >
            <Button type="primary" onClick={() => navigate('/scan')}>
              Go to Scan
            </Button>
          </Empty>
        ) : (
          <Table
            dataSource={projects}
            columns={columns}
            rowKey="name"
            pagination={{ pageSize: 10 }}
          />
        )}
      </Card>

      <Modal
        title={
          selectedProject ? (
            <Space>
              <FolderOutlined style={{ color: '#1890ff' }} />
              <span>{selectedProject.name}</span>
            </Space>
          ) : null
        }
        open={detailVisible}
        onCancel={() => setDetailVisible(false)}
        footer={[
          <Button key="close" onClick={() => setDetailVisible(false)}>
            Close
          </Button>,
          <Button 
            key="topology" 
            type="primary" 
            icon={<EyeOutlined />}
            onClick={() => {
              setDetailVisible(false);
              handleViewTopology(selectedProject?.name || '');
            }}
          >
            View Topology
          </Button>,
        ]}
        width={600}
      >
        {selectedProject && (
          <Descriptions column={2} bordered size="small">
            <Descriptions.Item label="Project Name" span={2}>
              {selectedProject.name}
            </Descriptions.Item>
            <Descriptions.Item label="Total Nodes">
              <Tag color="blue">{selectedProject.nodeCount}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Total Edges">
              <Tag color="green">{selectedProject.edgeCount}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="Last Scanned" span={2}>
              {selectedProject.lastScanned}
            </Descriptions.Item>
            <Descriptions.Item label="Node Types" span={2}>
              <Space wrap>
                {Object.entries(selectedProject.nodeTypes).map(([type, count]) => (
                  <Tag key={type} color="purple">{type}: {count}</Tag>
                ))}
              </Space>
            </Descriptions.Item>
          </Descriptions>
        )}
      </Modal>
    </div>
  );
};

export default ProjectPage;
