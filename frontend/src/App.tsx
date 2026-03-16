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
    { key: '1', icon: <HomeOutlined />, label: '首页' },
    { key: '2', icon: <ApartmentOutlined />, label: '拓扑图' },
    { key: '3', icon: <MessageOutlined />, label: 'AI 对话' },
    { key: '4', icon: <ScanOutlined />, label: '项目扫描' },
    { key: '5', icon: <FolderOutlined />, label: '项目管理' },
    { key: '6', icon: <FileSearchOutlined />, label: '架构评审' },
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
      <p className="home-subtitle">AI 驱动的企业软件架构数字孪生平台</p>
    </div>
    
    <div className="home-features">
      <div className="feature-card" onClick={() => window.location.href = '/topology'}>
        <div className="feature-icon topology-icon"></div>
        <h3>拓扑可视化</h3>
        <p>交互式企业架构图可视化</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/chat'}>
        <div className="feature-icon chat-icon"></div>
        <h3>AI 对话</h3>
        <p>用自然语言询问架构问题</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/scan'}>
        <div className="feature-icon scan-icon"></div>
        <h3>项目扫描</h3>
        <p>从 GitHub 仓库导入架构</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/projects'}>
        <div className="feature-icon projects-icon"></div>
        <h3>项目管理</h3>
        <p>管理扫描的项目架构资产</p>
      </div>
      
      <div className="feature-card" onClick={() => window.location.href = '/review'}>
        <div className="feature-icon review-icon"></div>
        <h3>架构评审</h3>
        <p>AI 辅助架构方案评审</p>
      </div>
    </div>

    <div className="home-steps">
      <h2>快速开始</h2>
      <div className="steps-list">
        <div className="step-item">
          <div className="step-number">1</div>
          <div className="step-content">
            <h4>扫描项目</h4>
            <p>从 GitHub 导入架构或手动添加节点</p>
          </div>
        </div>
        <div className="step-item">
          <div className="step-number">2</div>
          <div className="step-content">
            <h4>探索拓扑</h4>
            <p>查看和交互架构图</p>
          </div>
        </div>
        <div className="step-item">
          <div className="step-number">3</div>
          <div className="step-content">
            <h4>询问 AI</h4>
            <p>用自然语言获取架构洞察</p>
          </div>
        </div>
      </div>
    </div>
  </div>
);

const ReviewPage: React.FC = () => (
  <div className="review-page">
    <div className="review-header">
      <h2>架构评审</h2>
      <p>AI 辅助的架构方案评审与分析</p>
    </div>
    
    <div className="review-content">
      <div className="review-card">
        <h3>评审类型</h3>
        <div className="review-types">
          <div className="review-type">
            <div className="review-type-icon security"></div>
            <h4>安全评审</h4>
            <p>分析安全风险和漏洞</p>
          </div>
          <div className="review-type">
            <div className="review-type-icon performance"></div>
            <h4>性能评审</h4>
            <p>识别性能瓶颈</p>
          </div>
          <div className="review-type">
            <div className="review-type-icon cost"></div>
            <h4>成本优化</h4>
            <p>发现成本节约机会</p>
          </div>
          <div className="review-type">
            <div className="review-type-icon compliance"></div>
            <h4>合规检查</h4>
            <p>验证合规要求</p>
          </div>
        </div>
      </div>
      
      <div className="review-card">
        <h3>开始使用</h3>
        <p>在后端设置中配置 OpenAI API Key 以启用 AI 驱动的架构评审功能。</p>
        <div className="review-steps">
          <p>1. 在环境中设置 <code>OPENAI_API_KEY</code></p>
          <p>2. 使用扫描页面导入架构</p>
          <p>3. 选择评审类型并开始分析</p>
        </div>
      </div>
    </div>
  </div>
);

export default App;
