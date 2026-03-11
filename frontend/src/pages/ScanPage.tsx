import React, { useState } from 'react';
import { Card, Form, Input, Button, Select, message, Space, Typography, Divider, Table, Tag, Steps, Result } from 'antd';
import { GithubOutlined, ScanOutlined, PlusOutlined, ClearOutlined } from '@ant-design/icons';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;

interface ScanResult {
  status: string;
  nodes_added: number;
  edges_added: number;
  message: string;
}

const ScanPage: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [scanResult, setScanResult] = useState<ScanResult | null>(null);
  const [activeTab, setActiveTab] = useState('github');
  const [form] = Form.useForm();
  const [manualForm] = Form.useForm();

  const handleGitHubScan = async (values: any) => {
    setLoading(true);
    setScanResult(null);
    try {
      const response = await fetch('http://localhost:8002/api/scan/github', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(values),
      });
      const data = await response.json();
      setScanResult(data);
      message.success('Scan completed successfully!');
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
      message.success('Nodes added successfully!');
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
    } catch (error) {
      message.error('Failed to clear');
    }
  };

  const sampleNodes = `[
  {"id": "svc1", "label": "User Service", "type": "Service", "properties": {"language": "Java"}},
  {"id": "db1", "label": "User DB", "type": "Database", "properties": {"engine": "PostgreSQL"}}
]`;

  const sampleEdges = `[
  {"source": "svc1", "target": "db1", "type": "CALLS", "properties": {}}
]`;

  return (
    <div style={{ padding: 24, maxWidth: 1200, margin: '0 auto' }}>
      <Title level={2}>Project Scanner</Title>
      <Paragraph type="secondary">
        Import project architecture from GitHub or add nodes manually
      </Paragraph>

      <Divider />

      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        <Card
          title={
            <Space>
              <GithubOutlined />
              <span>Scan GitHub Repository</span>
            </Space>
          }
          extra={
            <Button icon={<ClearOutlined />} onClick={handleClear} danger>
              Clear All
            </Button>
          }
        >
          <Form form={form} layout="vertical" onFinish={handleGitHubScan}>
            <Form.Item
              name="repo_url"
              label="GitHub Repository URL"
              rules={[{ required: true, message: 'Please enter repository URL' }]}
            >
              <Input placeholder="https://github.com/macrozheng/mall" size="large" />
            </Form.Item>
            <Form.Item name="branch" label="Branch" initialValue="main">
              <Input placeholder="main" />
            </Form.Item>
            <Form.Item name="scan_type" label="Scan Type" initialValue="architecture">
              <Select>
                <Option value="architecture">Architecture Analysis</Option>
                <Option value="dependencies">Dependencies Only</Option>
                <Option value="full">Full Scan</Option>
              </Select>
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading} icon={<ScanOutlined />}>
                Start Scan
              </Button>
            </Form.Item>
          </Form>
        </Card>

        <Card
          title={
            <Space>
              <PlusOutlined />
              <span>Add Nodes Manually</span>
            </Space>
          }
        >
          <Form form={manualForm} layout="vertical" onFinish={handleManualAdd}>
            <Form.Item
              name="nodes"
              label="Nodes (JSON Array)"
              rules={[{ required: true, message: 'Please enter nodes' }]}
            >
              <TextArea
                rows={8}
                placeholder={sampleNodes}
                style={{ fontFamily: 'monospace' }}
              />
            </Form.Item>
            <Form.Item name="edges" label="Edges (JSON Array, optional)">
              <TextArea
                rows={4}
                placeholder={sampleEdges}
                style={{ fontFamily: 'monospace' }}
              />
            </Form.Item>
            <Form.Item>
              <Button type="primary" htmlType="submit" loading={loading}>
                Add Nodes
              </Button>
            </Form.Item>
          </Form>
        </Card>

        {scanResult && (
          <Card title="Scan Result">
            <Result
              status={scanResult.status === 'success' ? 'success' : 'error'}
              title={scanResult.message}
              subTitle={
                <Space size="large">
                  <Tag color="blue">{scanResult.nodes_added} Nodes</Tag>
                  <Tag color="green">{scanResult.edges_added} Edges</Tag>
                </Space>
              }
              extra={[
                <Button type="primary" key="view" onClick={() => window.location.href = '/topology'}>
                  View Topology
                </Button>,
              ]}
            />
          </Card>
        )}

        <Card title="Quick Start Templates">
          <Space wrap>
            <Button onClick={() => form.setFieldsValue({ repo_url: 'https://github.com/macrozheng/mall' })}>
              Mall E-Commerce (Spring Boot)
            </Button>
            <Button onClick={() => manualForm.setFieldsValue({ nodes: sampleNodes, edges: sampleEdges })}>
              Sample Microservices
            </Button>
          </Space>
        </Card>
      </Space>
    </div>
  );
};

export default ScanPage;
