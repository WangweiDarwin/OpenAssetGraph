import React from 'react';
import { Layout, Menu } from 'antd';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { HomeOutlined, ApartmentOutlined, MessageOutlined, FileSearchOutlined, ScanOutlined } from '@ant-design/icons';
import TopologyPage from './pages/TopologyPage';
import ChatPage from './pages/ChatPage';
import ScanPage from './pages/ScanPage';
import './App.css';

const { Header, Content, Sider } = Layout;

const App: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  
  const getSelectedKey = () => {
    switch (location.pathname) {
      case '/': return '1';
      case '/topology': return '2';
      case '/chat': return '3';
      case '/scan': return '4';
      case '/review': return '5';
      default: return '1';
    }
  };

  return (
    <Layout className="app">
      <Header className="header">
        <div className="logo">
          <h1>OpenAssetGraph</h1>
        </div>
      </Header>
      <Layout>
        <Sider width={200} className="sider">
          <Menu
            mode="inline"
            selectedKeys={[getSelectedKey()]}
            style={{ height: '100%', borderRight: 0 }}
            onClick={({ key }) => {
              switch (key) {
                case '1': navigate('/'); break;
                case '2': navigate('/topology'); break;
                case '3': navigate('/chat'); break;
                case '4': navigate('/scan'); break;
                case '5': navigate('/review'); break;
              }
            }}
          >
            <Menu.Item key="1" icon={<HomeOutlined />}>
              Home
            </Menu.Item>
            <Menu.Item key="2" icon={<ApartmentOutlined />}>
              Topology
            </Menu.Item>
            <Menu.Item key="3" icon={<MessageOutlined />}>
              AI Chat
            </Menu.Item>
            <Menu.Item key="4" icon={<ScanOutlined />}>
              Scan Project
            </Menu.Item>
            <Menu.Item key="5" icon={<FileSearchOutlined />}>
              Review
            </Menu.Item>
          </Menu>
        </Sider>
        <Layout className="content-layout">
          <Content className="content">
            <Routes>
              <Route path="/" element={<HomePage />} />
              <Route path="/topology" element={<TopologyPage />} />
              <Route path="/chat" element={<ChatPage />} />
              <Route path="/scan" element={<ScanPage />} />
              <Route path="/review" element={<ReviewPage />} />
            </Routes>
          </Content>
        </Layout>
      </Layout>
    </Layout>
  );
};

const HomePage: React.FC = () => (
  <div style={{ padding: 24 }}>
    <h2>Welcome to OpenAssetGraph</h2>
    <p>AI-Native Digital Twin for Enterprise Software</p>
    <div style={{ marginTop: 24 }}>
      <h3>Features</h3>
      <ul>
        <li><strong>Topology Visualization</strong> - View and interact with your enterprise asset topology</li>
        <li><strong>AI Chat</strong> - Interact with your assets using natural language</li>
        <li><strong>Project Scanner</strong> - Import architecture from GitHub repositories</li>
        <li><strong>Architecture Review</strong> - Review and analyze architectural proposals</li>
      </ul>
    </div>
    <div style={{ marginTop: 24 }}>
      <h3>Quick Start</h3>
      <ol>
        <li>Go to <strong>Scan Project</strong> to import a GitHub repository</li>
        <li>View the topology in <strong>Topology</strong> page</li>
        <li>Ask questions using <strong>AI Chat</strong></li>
      </ol>
    </div>
  </div>
);

const ReviewPage: React.FC = () => (
  <div style={{ padding: 24 }}>
    <h2>Architecture Review</h2>
    <p>Review and analyze architectural proposals</p>
  </div>
);

export default App;
