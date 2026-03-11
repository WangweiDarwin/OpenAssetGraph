import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Select, message, Space, Divider, Result, Tabs } from 'antd';
import { GithubOutlined, ScanOutlined, PlusOutlined, ClearOutlined, CodeOutlined } from '@ant-design/icons';
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
  const [form] = Form.useForm();
  const [manualForm] = Form.useForm();

  const handleGitHubScan = async (values: any) => {
    setLoading(true);
    setScanResult(null);
    setScannedProjectId(null);
    try {
      const response = await fetch('http://localhost:8002/api/scan/github', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      const data = await response.json();
      setScanResult(data);
      
      const urlLower = values.repo_url.toLowerCase();
      if (urlLower.includes('microservices-demo') || urlLower.includes('googlecloudplatform')) {
        setScannedProjectId('online-boutique');
      } else if (urlLower.includes('mall') || urlLower.includes('macrozheng')) {
        setScannedProjectId('mall');
      } else if (urlLower.includes('petclinic')) {
        setScannedProjectId('petclinic');
      }
      
      message.success('Scan completed!');
    } catch (error) {
      message.error('Scan failed');
    } finally {
      setLoading(false);
    }
  };

  const handleManualAdd = async (values: any) => {
    setLoading(true);
    try {
      const nodes = JSON.parse(values.nodes || '[]');
      const edges = values.edges ? JSON.parse(values.edges) : null;
      
      const response = await fetch('http://localhost:8002/api/scan/manual', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ nodes, edges }),
      });
      const data = await response.json();
      setScanResult(data);
      message.success('Nodes added!');
    } catch (error) {
      message.error('Failed to add nodes');
    } finally {
      setLoading(false);
    }
  };

  const handleClear = async () => {
    try {
      await fetch('http://localhost:8002/api/scan/clear', { method: 'POST' });
      message.success('Topology cleared');
      setScanResult(null);
      setScannedProjectId(null);
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
        <h2>Project Scanner</h2>
        <p style={{ color: 'var(--text-secondary)', margin: 0 }}>Import architecture from GitHub or add nodes manually</p>
      </div>

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
                      <Form.Item name="repo_url" label="Repository URL" rules={[{ required: true, message: 'Please enter repository URL' }]}>
                        <Input placeholder="https://github.com/GoogleCloudPlatform/microservices-demo" size="large" />
                      </Form.Item>
                      <div className="form-row">
                        <Form.Item name="branch" label="Branch" initialValue="main" className="form-item-half">
                          <Input placeholder="main" />
                        </Form.Item>
                        <Form.Item name="scan_type" label="Scan Type" initialValue="architecture" className="form-item-half">
                          <Select>
                            <Option value="architecture">Architecture</Option>
                            <Option value="dependencies">Dependencies</Option>
                            <Option value="full">Full Scan</Option>
                          </Select>
                        </Form.Item>
                      </div>
                      <Form.Item>
                        <Button type="primary" htmlType="submit" loading={loading} icon={<ScanOutlined />}>
                          Start Scan
                        </Button>
                      </Form.Item>
                    </Form>

                    <Divider>Quick Templates</Divider>
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
                label: <span><PlusOutlined /> Manual</span>,
                children: (
                  <Card className="scan-card">
                    <Form form={manualForm} layout="vertical" onFinish={handleManualAdd}>
                      <Form.Item name="nodes" label="Nodes (JSON Array)" rules={[{ required: true }]}>
                        <TextArea rows={8} placeholder={sampleNodes} className="code-input" />
                      </Form.Item>
                      <Form.Item name="edges" label="Edges (JSON Array, optional)">
                        <TextArea rows={4} placeholder={sampleEdges} className="code-input" />
                      </Form.Item>
                      <Form.Item>
                        <Space>
                          <Button type="primary" htmlType="submit" loading={loading}>Add Nodes</Button>
                          <Button onClick={() => manualForm.setFieldsValue({ nodes: sampleNodes, edges: sampleEdges })}>
                            Load Sample
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
          <Card className="info-card" title="Node Types" size="small">
            <div className="node-type-list">
              {nodeTypes.map(t => (
                <div key={t.name} className="node-type-item">
                  <span className="node-type-dot" style={{ background: t.color }} />
                  <span>{t.name}</span>
                </div>
              ))}
            </div>
          </Card>

          <Card className="info-card" title="Actions" size="small">
            <Space direction="vertical" style={{ width: '100%' }}>
              <Button icon={<ClearOutlined />} danger onClick={handleClear} block>Clear Topology</Button>
              <Button type="primary" onClick={handleViewTopology} block>View Topology</Button>
            </Space>
          </Card>

          {scanResult && (
            <Card className="result-card" size="small">
              <Result
                status={scanResult.status === 'success' ? 'success' : 'error'}
                title={scanResult.message}
                subTitle={<span>{scanResult.nodes_added} nodes, {scanResult.edges_added} edges</span>}
                extra={[
                  <Button type="primary" key="view" onClick={handleViewTopology}>
                    View Topology
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
