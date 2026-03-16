import React, { useState, useEffect } from 'react';
import { Input, Select, Button, Card, List, Tag, Space, Typography, Empty, Spin } from 'antd';
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons';

const { Search } = Input;
const { Option } = Select;
const { Text } = Typography;

interface TopologyNode {
  id: string;
  label: string;
  type: string;
  properties?: Record<string, any>;
}

interface SearchPanelProps {
  onSearch: (query: string, filters: SearchFilters) => void;
  onNodeSelect: (node: TopologyNode) => void;
  nodes: TopologyNode[];
  loading?: boolean;
}

interface SearchFilters {
  type: string | null;
  property: string | null;
}

interface SearchResult {
  node: TopologyNode;
  matchType: 'label' | 'id' | 'property';
  matchField?: string;
}

const typeColorMap: Record<string, string> = {
  Database: 'blue',
  Table: 'green',
  Column: 'gold',
  Service: 'purple',
  API: 'magenta',
  FrontendApp: 'cyan',
  Component: 'orange',
};

const SearchPanel: React.FC<SearchPanelProps> = ({
  onSearch,
  onNodeSelect,
  nodes,
  loading = false,
}) => {
  const [query, setQuery] = useState('');
  const [filters, setFilters] = useState<SearchFilters>({
    type: null,
    property: null,
  });
  const [results, setResults] = useState<SearchResult[]>([]);
  const [allProperties, setAllProperties] = useState<string[]>([]);

  useEffect(() => {
    const properties = new Set<string>();
    nodes.forEach(node => {
      if (node.properties) {
        Object.keys(node.properties).forEach(prop => properties.add(prop));
      }
    });
    setAllProperties(Array.from(properties).sort());
  }, [nodes]);

  const handleSearch = () => {
    const searchResults: SearchResult[] = [];
    const lowerQuery = query.toLowerCase();

    nodes.forEach(node => {
      if (filters.type && node.type !== filters.type) {
        return;
      }

      if (node.label.toLowerCase().includes(lowerQuery)) {
        searchResults.push({ node, matchType: 'label' });
        return;
      }

      if (node.id.toLowerCase().includes(lowerQuery)) {
        searchResults.push({ node, matchType: 'id' });
        return;
      }

      if (node.properties) {
        for (const [key, value] of Object.entries(node.properties)) {
          if (filters.property && key !== filters.property) {
            continue;
          }
          if (String(value).toLowerCase().includes(lowerQuery)) {
            searchResults.push({ node, matchType: 'property', matchField: key });
            return;
          }
        }
      }
    });

    setResults(searchResults);
    onSearch(query, filters);
  };

  const handleReset = () => {
    setQuery('');
    setFilters({ type: null, property: null });
    setResults([]);
  };

  const uniqueTypes = [...new Set(nodes.map(n => n.type))];

  return (
    <Card 
      className="search-panel" 
      title={
        <Space>
          <SearchOutlined />
          <span>Search Nodes</span>
        </Space>
      }
      style={{ height: '100%' }}
      extra={
        <Button 
          icon={<ReloadOutlined />} 
          size="small" 
          onClick={handleReset}
        >
          Reset
        </Button>
      }
    >
      <Space direction="vertical" style={{ width: '100%' }} size="middle">
        <Search
          placeholder="Search by label, ID, or property..."
          value={query}
          onChange={e => setQuery(e.target.value)}
          onSearch={handleSearch}
          enterButton={<SearchOutlined />}
          loading={loading}
        />

        <Space style={{ width: '100%' }} wrap>
          <Select
            placeholder="Filter by type"
            style={{ width: 140 }}
            value={filters.type}
            onChange={type => setFilters({ ...filters, type })}
            allowClear
          >
            {uniqueTypes.map(type => (
              <Option key={type} value={type}>
                <Tag color={typeColorMap[type]} style={{ margin: 0 }}>
                  {type}
                </Tag>
              </Option>
            ))}
          </Select>

          <Select
            placeholder="Filter by property"
            style={{ width: 160 }}
            value={filters.property}
            onChange={property => setFilters({ ...filters, property })}
            allowClear
            showSearch
          >
            {allProperties.map(prop => (
              <Option key={prop} value={prop}>
                {prop}
              </Option>
            ))}
          </Select>
        </Space>

        <div style={{ marginTop: 8 }}>
          <Text type="secondary">
            Found {results.length} result{results.length !== 1 ? 's' : ''}
          </Text>
        </div>

        {loading ? (
          <Spin tip="Searching..." />
        ) : results.length > 0 ? (
          <List
            className="search-results"
            dataSource={results}
            style={{ maxHeight: 400, overflow: 'auto' }}
            renderItem={(result) => (
              <List.Item
                style={{ cursor: 'pointer', padding: '8px 12px' }}
                onClick={() => onNodeSelect(result.node)}
              >
                <List.Item.Meta
                  title={
                    <Space>
                      <Text strong>{result.node.label}</Text>
                      <Tag color={typeColorMap[result.node.type]}>
                        {result.node.type}
                      </Tag>
                    </Space>
                  }
                  description={
                    <Space direction="vertical" size={0}>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        ID: {result.node.id}
                      </Text>
                      <Text type="secondary" style={{ fontSize: 12 }}>
                        Match: {result.matchType}
                        {result.matchField && ` (${result.matchField})`}
                      </Text>
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        ) : query && !loading ? (
          <Empty 
            description="No results found"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        ) : (
          <Empty 
            description="Enter a search query"
            image={Empty.PRESENTED_IMAGE_SIMPLE}
          />
        )}
      </Space>
    </Card>
  );
};

export default SearchPanel;
