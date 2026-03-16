import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, message, Space, Divider, Result, Tabs, Tag, List, Popconfirm } from 'antd';
import { GithubOutlined, ScanOutlined, PlusOutlined, ClearOutlined, CodeOutlined, DeleteOutlined, EyeOutlined, ReloadOutlined } from '@ant-design/icons';
import { scanApi, api } from '../services/api';
import './ScanPage.css';

const { Option } = Select;
const { TextArea } = Input;

interface ScanResult {
  status: string;
  nodes_added: number;
  edges_added: number;
  message: string;
  project_id?: string;
}

const ScanPage: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [scannedProjectId, setScannedProjectId] = useState<string | null>(null);
  const [existingProjects, setExistingProjects] = useState<string[]>([]);
  const [form] = Form.useForm();
  const [manualForm] = Form.useForm();
  const [connectionError, setConnectionError] = useState<string | null>(null);

  useEffect(() => {
    fetchExistingProjects();
  }, []);

  const fetchExistingProjects = async () => {
    setConnectionError(null);
    try {
      const data = await api.getProjects();
      setExistingProjects(data.projects || []);
    } catch (error: any) {
      console.error('Failed to fetch projects:', error);
      setConnectionError(error?.message || 'Failed to connect to backend');
    }
  };

  const handleDeleteProject = async (projectName: string) => {
    try {
      const result = await scanApi.deleteProject(projectName);
      message.success(result.message || `项目 "${projectName}" 已删除`);
      fetchExistingProjects();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const handleGitHubScan = async (values: any) => {
    setLoading(true);
    setScanResult(null);
    setScannedProjectId(null);
    try {
      const data = await scanApi.scanGitHub(values.repo_url, values.branch, values.scan_type);
      setScanResult(data);
      
      if (data.project_id) {
        setScannedProjectId(data.project_id);
      } else {
        const urlLower = values.repo_url.toLowerCase();
        if (urlLower.includes('microservices-demo') || urlLower.includes('googlecloudplatform')) {
          setScannedProjectId('online-boutique');
        } else if (urlLower.includes('mall') || urlLower.includes('macrozheng')) {
          setScannedProjectId('mall');
        } else if (urlLower.includes('petclinic')) {
          setScannedProjectId('petclinic');
        }
      }
      
      message.success('Scan completed!');
      fetchExistingProjects();
    } catch (error: any) {
      message.error(error?.message || 'Scan failed');
    } finally {
      setLoading(false);
    }
  };

  const handleManualAdd = async (values: any) => {
    setLoading(true);
    try {
      const nodes = JSON.parse(values.nodes || '[]');
      const edges = values.edges ? JSON.parse(values.edges) : undefined;
      
      const data = await scanApi.addManualNodes(nodes, edges);
      setScanResult(data);
      message.success('Nodes added!');
      fetchExistingProjects();
    } catch (error: any) {
      message.error(error?.message || 'Failed to add nodes');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    try {
      await scanApi.clearTopology();
      message.success('Topology cleared');
      setScanResult(null);
      setScannedProjectId(null);
      fetchExistingProjects();
    } catch (error) {
      message.error('Failed to clear');
    }
  };

  const handleViewTopology = () => {
    if (scannedProjectId) {
      navigate(`/topology?project=${scannedProjectId}`);
    } else {
      navigate('/topology');
    }
  };

  const sampleNodes = `[
  {"id": "svc1", "label": "User Service", "type": "Service", "properties": {"language": "Java", "port": 8080}},
  {"id": "db1", "label": "User DB", "type": "Database", "properties": {"engine": "PostgreSQL"}},
  {"id": "api1", "label": "User API", "type": "API", "properties": {"endpoint": "/api/users"}}
]`;

  const sampleEdges = `[
  {"source": "api1", "target": "svc1", "type": "EXPOSES"},
  {"source": "svc1", "target": "db1", "type": "CALLS"}
]`;

  const quickTemplates = [
    { 
      name: 'Mall E-Commerce', 
      url: 'https://github.com/macrozheng/mall', 
      description: 'Spring Boot microservices',
      stars: '40k+'
    },
    { 
      name: 'Spring PetClinic', 
      url: 'https://github.com/spring-projects/spring-petclinic', 
      description: 'Spring Boot demo',
      stars: '7k+'
    },
  ];

  const nodeTypes = [
    { name: 'Database', color: '#10b981' },
    { name: 'Service', color: '#3b82f6' },
    { name: 'API', color: '#8b5cf6' },
    { name: 'FrontendApp', color: '#f59e0b' },
    { name: 'Table', color: '#6b7280' },
    { name: 'Library', color: '#ec4899' },
  ];

  return (
    <div className="scan-page">
      <div className="scan-header">
        <h2>项目扫描</h2>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>从 GitHub 导入架构或手动添加节点</p>
      </div>

      {connectionError && (
        <Card className="error-card" style={{ marginBottom: 16 }}>
          <Result
            status="error"
            title="连接错误"
            subTitle={`无法连接到后端: ${connectionError}。请检查后端服务是否在 8000 端口运行。`}
            extra={<Button type="primary" onClick={fetchExistingProjects}>重试</Button>}
          />
        </Card>
      )}

      <div className="scan-content">
        <div className="scan-main">
          <Tabs
            defaultActiveKey="github"
            items={[
              {
                key: 'github',
                label: <span><GithubOutlined /> GitHub</span>,
                children: (
                  <Card className="scan-card">
                    <Form form={form} layout="vertical" onFinish={handleGitHubScan}>
                      <Form.Item name="repo_url" label="仓库 URL" rules={[{ required: true, message: '请输入仓库 URL' }]}>
                        <Input placeholder="https://github.com/GoogleCloudPlatform/microservices-demo" size="large" />
                      </Form.Item>
                      <div className="form-row">
                        <Form.Item name="branch" label="分支" initialValue="main" className="form-item-half">
                          <Input placeholder="main" />
                        </Form.Item>
                        <Form.Item name="scan_type" label="扫描类型" initialValue="architecture" className="form-item-half">
                          <Select>
                            <Option value="architecture">架构扫描</Option>
                            <Option value="dependencies">依赖扫描</Option>
                            <Option value="full">完整扫描</Option>
                          </Select>
                        </Form.Item>
                      </div>
                      <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading} icon={<ScanOutlined />}>
                          开始扫描
                        </Button>
                      </Form.Item>
                    </Form>

                    <Divider>快速模板</Divider>
                    <div className="quick-templates">
                      {quickTemplates.map(t => (
                        <div key={t.name} className="template-card" onClick={() => form.setFieldsValue({ repo_url: t.url })}>
                          <div className="template-icon"><CodeOutlined /></div>
                          <div className="template-info">
                            <div className="template-name">{t.name} <span className="template-stars">⭐ {t.stars}</span></div>
                            <div className="template-desc">{t.description}</div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </Card>
                ),
              },
              {
                key: 'manual',
                label: <span><PlusOutlined /> 手动添加</span>,
                children: (
                  <Card className="scan-card">
                    <Form form={manualForm} layout="vertical" onFinish={handleManualAdd}>
                      <Form.Item name="nodes" label="节点 (JSON 数组)" rules={[{ required: true }]}>
                        <TextArea rows={8} placeholder={sampleNodes} className="code-input" />
                      </Form.Item>
                      <Form.Item name="edges" label="边 (JSON 数组，可选)">
                        <TextArea rows={4} placeholder={sampleEdges} className="code-input" />
                      </Form.Item>
                      <Form.Item>
                        <Space>
                          <Button type="primary" htmlType="submit" loading={loading}>添加节点</Button>
                          <Button onClick={() => manualForm.setFieldsValue({ nodes: sampleNodes, edges: sampleEdges })}>
                            加载示例
                          </Button>
                        </Space>
                      </Form.Item>
                    </Form>
                  </Card>
                ),
              },
            ]}
          />
        </div>

        <div className="scan-sidebar">
          <Card className="info-card" title="节点类型" size="small">
            <div className="node-type-list">
              {nodeTypes.map(t => (
                <div key={t.name} className="node-type-item">
                  <span className="node-type-dot" style={{ background: t.color }} />
                  <span>{t.name}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card className="info-card" title="操作" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button icon={<ClearOutlined />} danger onClick={handleClear} block>清除拓扑</Button>
              <Button type="primary" onClick={handleViewTopology} block>查看拓扑</Button>
            </Space>
          </Card>

          {existingProjects.length > 0 && (
            <Card className="info-card" title="已扫描项目" size="small" extra={<Button size="small" icon={<ReloadOutlined />} onClick={fetchExistingProjects} />}>
              <List
                size="small"
                dataSource={existingProjects}
                renderItem={(project) => (
                  <List.Item
                    actions={[
                      <Button 
                        size="small" 
                        icon={<EyeOutlined />} 
                        onClick={() => navigate(`/topology?project=${project}`)}
                      />,
                      <Popconfirm
                        title="确定删除此项目？"
                        onConfirm={() => handleDeleteProject(project)}
                        okText="删除"
                        cancelText="取消"
                      >
                        <Button size="small" danger icon={<DeleteOutlined />} />
                      </Popconfirm>
                    ]}
                  >
                    <Tag color="blue">#{project}</Tag>
                  </List.Item>
                )}
              />
            </Card>
          )}

          {scanResult && (
            <Card className="result-card" size="small">
              <Result
                status={scanResult.status === 'success' ? 'success' : 'error'}
                title={scanResult.message}
                subTitle={<span>{scanResult.nodes_added} 个节点, {scanResult.edges_added} 条边</span>}
                extra={[
                  <Button type="primary" key="view" onClick={handleViewTopology}>
                    查看拓扑
                  </Button>,
                ]}
              />
            </Card>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScanPage;
