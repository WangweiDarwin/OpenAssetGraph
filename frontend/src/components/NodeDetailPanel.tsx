import React from 'react';
import { Card, Descriptions, Tag, Table, Empty, Typography, Divider } from 'antd';
import { DatabaseOutlined, TableOutlined, ColumnHeightOutlined, ApiOutlined, DesktopOutlined, AppstoreOutlined, SettingOutlined } from '@ant-design/icons';

const { Text } = Typography;

interface TopologyNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
}

interface NodeDetailPanelProps {
  node: TopologyNode | null;
}

const typeIconMap: Record<string, React.ReactNode> = {
  Database: <DatabaseOutlined />,
  Table: <TableOutlined />,
  Column: <ColumnHeightOutlined />,
  Service: <SettingOutlined />,
  API: <ApiOutlined />,
  FrontendApp: <DesktopOutlined />,
  Component: <AppstoreOutlined />,
};

const typeColorMap: Record<string, string> = {
  Database: 'blue',
  Table: 'green',
  Column: 'gold',
  Service: 'purple',
  API: 'magenta',
  FrontendApp: 'cyan',
  Component: 'orange',
};

const NodeDetailPanel: React.FC<NodeDetailPanelProps> = ({ node }) => {
  if (!node) {
    return (
      <Card 
        className="node-detail-panel" 
        title="Node Details"
        style={{ height: '100%' }}
      >
        <Empty 
          description="Select a node to view details"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      </Card>
    );
  }

  const properties = node.properties || {};
  const propertyEntries = Object.entries(properties);

  const columns = [
    {
      title: 'Property',
      dataIndex: 'key',
      key: 'key',
      width: '40%',
      render: (text: string) => <Text strong>{text}</Text>,
    },
    {
      title: 'Value',
      dataIndex: 'value',
      key: 'value',
      width: '60%',
      render: (value: any) => {
        if (typeof value === 'object') {
          return <Text code>{JSON.stringify(value, null, 2)}</Text>;
        }
        if (typeof value === 'boolean') {
          return <Tag color={value ? 'green' : 'red'}>{value.toString()}</Tag>;
        }
        if (typeof value === 'number') {
          return <Text code>{value}</Text>;
        }
        return <Text>{String(value)}</Text>;
      },
    },
  ];

  const dataSource = propertyEntries.map(([key, value], index) => ({
    key,
    value,
    id: index,
  }));

  return (
    <Card 
      className="node-detail-panel" 
      title={
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          {typeIconMap[node.type] || <AppstoreOutlined />}
          <span>Node Details</span>
        </div>
      }
      style={{ height: '100%', overflow: 'auto' }}
    >
      <Descriptions column={1} size="small" bordered>
        <Descriptions.Item label="ID">
          <Text copyable code>{node.id}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="Label">
          <Text strong>{node.label}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="Type">
          <Tag color={typeColorMap[node.type] || 'default'} icon={typeIconMap[node.type]}>
            {node.type}
          </Tag>
        </Descriptions.Item>
      </Descriptions>

      <Divider orientation="left" style={{ margin: '16px 0 8px' }}>
        Properties ({propertyEntries.length})
      </Divider>

      {propertyEntries.length > 0 ? (
        <Table 
          dataSource={dataSource}
          columns={columns}
          size="small"
          pagination={false}
          showHeader={false}
          rowKey="id"
          scroll={{ y: 300 }}
        />
      ) : (
        <Empty 
          description="No properties available"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        />
      )}
    </Card>
  );
};

export default NodeDetailPanel;
