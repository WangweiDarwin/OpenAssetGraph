import React, { useState } from 'react';
import { Layout, Menu, Button } from 'antd';
import { Routes, Route, useNavigate, useLocation } from 'react-router-dom';
import { HomeOutlined, ApartmentOutlined, MessageOutlined, FileSearchOutlined, ScanOutlined, MenuFoldOutlined, MenuUnfoldOutlined, FolderOutlined } from '@ant-design/icons';
import TopologyPage from './pages/TopologyPage';
import ChatPage from './pages/ChatPage';
import ScanPage from './pages/ScanPage';
import ProjectPage from './pages/ProjectPage';
import './App.css';

const { Header, Sider, Content } = Layout;

const App: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = useState(false);

  const getSelectedKey = () => {
    switch (location.pathname) {
      case '/': return '1';
      case '/topology': return '2';
      case '/chat': return '3';
      case '/scan': return '4';
      case '/projects': return '5';
      case '/review': return '6';
      default: return '1';
    }
  };

  const menuItems = [
    { key: '1', icon: <HomeOutlined />, label: 'Home' },
    { key: '2', icon: <ApartmentOutlined />, label: 'Topology' },
    { key: '3', icon: <MessageOutlined />, label: 'AI Chat' },
    { key: '4', icon: <ScanOutlined />, label: 'Scan' },
    { key: '5', icon: <FolderOutlined />, label: 'Projects' },
    { key: '6', icon: <FileSearchOutlined />, label: 'Review' },
  ];

  const handleMenuClick = (key: string) => {
    switch (key) {
      case '1': navigate('/'); break;
      case '2': navigate('/topology'); break;
      case '3': navigate('/chat'); break;
      case '4': navigate('/scan'); break;
      case '5': navigate('/projects'); break;
      case '6': navigate('/review'); break;
    }
  };

  return (
    <Layout className="app">
      <Sider
        collapsible
        collapsed={collapsed}
        onCollapse={setCollapsed}
        width={180}
        collapsedWidth={56}
        className="sider"
        trigger={null}
      >
        <div className="logo">
          {collapsed ? <span className="logo-icon">O</span> : <span>OpenAssetGraph</span>}
        </div>
        <Menu
          mode="inline"
          selectedKeys={[getSelectedKey()]}
          items={menuItems}
          onClick={({ key }) => handleMenuClick(key)}
        />
      </Sider>
      <Layout>
        <Header className="header">
          <Button
            type="text"
            icon={collapsed ? <MenuUnfoldOutlined /> : <MenuFoldOutlined />}
            onClick={() => setCollapsed(!collapsed)}
            className="collapse-btn"
          />
          <div className="header-title">
            {menuItems.find(item => item.key === getSelectedKey())?.label || 'Home'}
          </div>
        </Header>
        <Content className="content">
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/topology" element={<TopologyPage />} />
            <Route path="/chat" element={<ChatPage />} />
            <Route path="/scan" element={<ScanPage />} />
            <Route path="/projects" element={<ProjectPage />} />
            <Route path="/review" element={<ReviewPage />} />
          </Routes>
        </Content>
      </Layout>
    </Layout>
  );
};

const HomePage: React.FC = () => (
  <div className="home-page">
    <div className="home-hero">
      <h1>OpenAssetGraph</h1>
      <p className="home-subtitle">AI-Native Digital Twin for Enterprise Software Architecture</p>
    </div>
    
    <div className="home-features">
      <div className="feature-card" onClick={() => window.location.href = '/topology'}>
        <div className="feature-icon topology-icon"></div>
        <h3>Topology Visualization</h3>
        <p>Interactive graph visualization of your enterprise architecture</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/chat'}>
        <div className="feature-icon chat-icon"></div>
        <h3>AI Chat</h3>
        <p>Ask questions about your architecture in natural language</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/scan'}>
        <div className="feature-icon scan-icon"></div>
        <h3>Project Scanner</h3>
        <p>Import architecture from GitHub repositories</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/projects'}>
        <div className="feature-icon projects-icon"></div>
        <h3>Projects</h3>
        <p>Manage your scanned project architecture assets</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/review'}>
        <div className="feature-icon review-icon"></div>
        <h3>Architecture Review</h3>
        <p>AI-assisted review of architectural proposals</p>
      </div>
    </div>

    <div className="home-steps">
      <h2>Quick Start</h2>
      <div className="steps-list">
        <div className="step-item">
          <div className="step-number">1</div>
          <div className="step-content">
            <h4>Scan a Project</h4>
            <p>Import architecture from GitHub or add nodes manually</p>
          </div>
        </div>
        <div className="step-item">
          <div className="step-number">2</div>
          <div className="step-content">
            <h4>Explore Topology</h4>
            <p>View and interact with your architecture graph</p>
          </div>
        </div>
        <div className="step-item">
          <div className="step-number">3</div>
          <div className="step-content">
            <h4>Ask AI</h4>
            <p>Get insights about your architecture using natural language</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const ReviewPage: React.FC = () => (
  <div className="review-page">
    <div className="review-header">
      <h2>Architecture Review</h2>
      <p>AI-assisted review and analysis of architectural proposals</p>
    </div>
    
    <div className="review-content">
      <div className="review-card">
        <h3>Review Types</h3>
        <div className="review-types">
          <div className="review-type">
            <div className="review-type-icon security"></div>
            <h4>Security Review</h4>
            <p>Analyze security risks and vulnerabilities</p>
          </div>
          <div className="review-type">
            <div className="review-type-icon performance"></div>
            <h4>Performance Review</h4>
            <p>Identify performance bottlenecks</p>
          </div>
          <div className="review-type">
            <div className="review-type-icon cost"></div>
            <h4>Cost Optimization</h4>
            <p>Find cost-saving opportunities</p>
          </div>
          <div className="review-type">
            <div className="review-type-icon compliance"></div>
            <h4>Compliance Check</h4>
            <p>Verify compliance requirements</p>
          </div>
        </div>
      </div>
      
      <div className="review-card">
        <h3>Getting Started</h3>
        <p>Configure your OpenAI API key in the backend settings to enable AI-powered architecture reviews.</p>
        <div className="review-steps">
          <p>1. Set <code>OPENAI_API_KEY</code> in your environment</p>
          <p>2. Import your architecture using the Scan page</p>
          <p>3. Select a review type and start the analysis</p>
        </div>
      </div>
    </div>
  </div>
);

export default App;
