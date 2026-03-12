import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Space, Spin, Empty, Tag, Avatar, Tooltip, Alert, message } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined, LoadingOutlined, ThunderboltOutlined, ProjectOutlined } from '@ant-design/icons';
import './ChatPage.css';

const { TextArea } = Input;

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  referencedProjects?: string[];
}

interface Project {
  name: string;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [projects, setProjects] = useState<Project[]>([]);
  const [showProjectDropdown, setShowProjectDropdown] = useState(false);
  const [projectDropdownPosition, setProjectDropdownPosition] = useState({ top: 0, left: 0 });
  const [cursorPosition, setCursorPosition] = useState(0);
  const [errorAlert, setErrorAlert] = useState<{ visible: boolean; message: string; invalidProjects: string[]; availableProjects: string[] }>({
    visible: false,
    message: '',
    invalidProjects: [],
    availableProjects: [],
  });
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<any>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    const fetchProjects = async () => {
      try {
        const response = await fetch('/api/projects');
        if (response.ok) {
          const data = await response.json();
          setProjects(data.projects || []);
        }
      } catch (error) {
        console.error('Failed to fetch projects:', error);
      }
    };
    fetchProjects();
  }, []);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowProjectDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const findHashPosition = (text: string, cursorPos: number): number => {
    let hashPos = -1;
    for (let i = cursorPos - 1; i >= 0; i--) {
      if (text[i] === '#') {
        if (i === 0 || text[i - 1] === ' ' || text[i - 1] === '\n') {
          hashPos = i;
          break;
        }
      } else if (text[i] === ' ' || text[i] === '\n') {
        break;
      }
    }
    return hashPos;
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const value = e.target.value;
    const cursorPos = e.target.selectionStart || 0;
    setInputValue(value);
    setCursorPosition(cursorPos);

    const hashPos = findHashPosition(value, cursorPos);
    
    if (hashPos !== -1 && projects.length > 0) {
      const textAfterHash = value.substring(hashPos + 1, cursorPos);
      if (!textAfterHash.includes(' ') && !textAfterHash.includes('\n')) {
        const inputElement = inputRef.current?.resizableTextArea?.textArea;
        if (inputElement) {
          const rect = inputElement.getBoundingClientRect();
          setProjectDropdownPosition({
            top: rect.bottom + window.scrollY,
            left: rect.left,
          });
        }
        setShowProjectDropdown(true);
      } else {
        setShowProjectDropdown(false);
      }
    } else {
      setShowProjectDropdown(false);
    }
  };

  const getFilteredProjects = () => {
    const hashPos = findHashPosition(inputValue, cursorPosition);
    if (hashPos === -1) return projects;
    
    const searchText = inputValue.substring(hashPos + 1, cursorPosition).toLowerCase();
    return projects.filter(p => p.name.toLowerCase().includes(searchText));
  };

  const insertProject = (projectName: string) => {
    const hashPos = findHashPosition(inputValue, cursorPosition);
    if (hashPos === -1) return;

    const beforeHash = inputValue.substring(0, hashPos);
    const afterCursor = inputValue.substring(cursorPosition);
    const newValue = beforeHash + '#' + projectName + ' ' + afterCursor;
    
    setInputValue(newValue);
    setShowProjectDropdown(false);
    
    setTimeout(() => {
      const newCursorPos = hashPos + projectName.length + 2;
      inputRef.current?.focus();
      inputRef.current?.resizableTextArea?.textArea?.setSelectionRange(newCursorPos, newCursorPos);
    }, 0);
  };

  const sendMessage = async () => {
    if (!inputValue.trim() || loading) return;

    setErrorAlert(prev => ({ ...prev, visible: false }));

    const userMessage: ChatMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setLoading(true);

    try {
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_history: conversationHistory,
        }),
      });

      if (!response.ok) {
        let errorDetail = `HTTP error: ${response.status}`;
        try {
          const errorData = await response.json();
          if (errorData.detail) {
            if (typeof errorData.detail === 'object') {
              if (errorData.detail.type === 'invalid_project_reference') {
                setErrorAlert({
                  visible: true,
                  message: errorData.detail.message,
                  invalidProjects: errorData.detail.invalid_projects || [],
                  availableProjects: errorData.detail.available_projects || [],
                });
                throw new Error(errorData.detail.message);
              }
              errorDetail = `${errorData.detail.type}: ${errorData.detail.message}`;
              if (errorData.detail.suggestion) {
                errorDetail += `\n\n💡 建议: ${errorData.detail.suggestion}`;
              }
            } else {
              errorDetail = errorData.detail;
            }
          }
        } catch (e) {
          if (e instanceof Error && e.message !== errorDetail) {
            throw e;
          }
          errorDetail = await response.text();
        }
        throw new Error(errorDetail);
      }

      const data = await response.json();

      const assistantMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response,
        timestamp: new Date(),
        referencedProjects: data.referenced_projects || [],
      };

      const updatedUserMessage: ChatMessage = {
        ...userMessage,
        referencedProjects: data.referenced_projects || [],
      };

      setMessages(prev => {
        const newMessages = [...prev];
        const userMsgIndex = newMessages.findIndex(m => m.id === userMessage.id);
        if (userMsgIndex !== -1) {
          newMessages[userMsgIndex] = updatedUserMessage;
        }
        return [...newMessages, assistantMessage];
      });
    } catch (error) {
      console.error('Chat error:', error);
      const errorMessage: ChatMessage = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `❌ 错误: ${error instanceof Error ? error.message : '发送消息失败'}\n\n请检查:\n1. 后端服务是否正常运行\n2. API Key 是否正确配置\n3. 访问 /api/chat/test 测试 LLM 服务`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const clearChat = () => {
    setMessages([]);
    setErrorAlert(prev => ({ ...prev, visible: false }));
  };

  const formatTime = (date: Date) => date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });

  const quickQuestions = [
    { icon: '🔍', text: 'Show all databases' },
    { icon: '🔗', text: 'Find circular dependencies' },
    { icon: '📊', text: 'Analyze architecture risks' },
    { icon: '⚡', text: 'What services call User API?' },
  ];

  return (
    <div className="chat-page">
      <div className="chat-header">
        <div className="chat-title">
          <RobotOutlined className="chat-icon" />
          <div>
            <h2>AI Architecture Assistant</h2>
            <p>Ask questions about your topology</p>
          </div>
        </div>
        <Button icon={<ClearOutlined />} onClick={clearChat}>Clear</Button>
      </div>

      {errorAlert.visible && (
        <Alert
          className="error-alert"
          type="error"
          showIcon
          closable
          onClose={() => setErrorAlert(prev => ({ ...prev, visible: false }))}
          message="项目引用错误"
          description={
            <div>
              <p>{errorAlert.message}</p>
              {errorAlert.invalidProjects.length > 0 && (
                <p><strong>无效项目:</strong> {errorAlert.invalidProjects.join(', ')}</p>
              )}
              {errorAlert.availableProjects.length > 0 && (
                <p><strong>可用项目:</strong> {errorAlert.availableProjects.join(', ')}</p>
              )}
            </div>
          }
        />
      )}

      <div className="chat-body">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="welcome-icon"><ThunderboltOutlined /></div>
            <h3>How can I help you?</h3>
            <p>Ask me anything about your architecture topology</p>
            
            <div className="project-reference-hint">
              <ProjectOutlined className="hint-icon" />
              <div className="hint-content">
                <strong>项目引用功能</strong>
                <p>使用 <code>#项目名#</code> 引用特定项目，如：<code>分析 #mall# 的架构</code></p>
                <p className="hint-note">结尾的 # 可选，但建议添加以明确断句</p>
              </div>
            </div>
            
            <div className="quick-actions">
              {quickQuestions.map((q, i) => (
                <div key={i} className="quick-action" onClick={() => { setInputValue(q.text); inputRef.current?.focus(); }}>
                  <span>{q.icon}</span>
                  <span>{q.text}</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="messages-container">
            {messages.map((msg) => (
              <div key={msg.id} className={`message ${msg.role}`}>
                <Avatar
                  icon={msg.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                  className={`message-avatar ${msg.role}`}
                  size={32}
                />
                <div className="message-content">
                  <div className="message-header">
                    <span className="message-role">{msg.role === 'user' ? 'You' : 'AI Assistant'}</span>
                    <span className="message-time">{formatTime(msg.timestamp)}</span>
                  </div>
                  {msg.referencedProjects && msg.referencedProjects.length > 0 && (
                    <div className="referenced-projects">
                      <ProjectOutlined /> 引用项目: 
                      {msg.referencedProjects.map((project, idx) => (
                        <Tag key={idx} color="blue" className="project-tag">{project}</Tag>
                      ))}
                    </div>
                  )}
                  <div className="message-text">{msg.content}</div>
                </div>
              </div>
            ))}
            {loading && (
              <div className="message assistant">
                <Avatar icon={<RobotOutlined />} className="message-avatar assistant" size={32} />
                <div className="message-content">
                  <div className="message-loading">
                    <LoadingOutlined spin />
                    <span>Thinking...</span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      <div className="chat-input-wrapper">
        <div className="chat-input">
          <TextArea
            ref={inputRef}
            value={inputValue}
            onChange={handleInputChange}
            onKeyPress={handleKeyPress}
            placeholder="Ask about your architecture... 使用 #项目名 引用特定项目"
            autoSize={{ minRows: 1, maxRows: 4 }}
          />
          <Button type="primary" icon={<SendOutlined />} onClick={sendMessage} loading={loading} />
        </div>
        <div className="chat-hint">Press Enter to send, Shift+Enter for new line</div>
      </div>

      {showProjectDropdown && (
        <div 
          ref={dropdownRef}
          className="project-dropdown"
          style={{ 
            top: projectDropdownPosition.top,
            left: projectDropdownPosition.left,
          }}
        >
          <div className="dropdown-header">选择项目</div>
          <div className="dropdown-list">
            {getFilteredProjects().map((project, index) => (
              <div 
                key={index} 
                className="dropdown-item"
                onClick={() => insertProject(project.name)}
              >
                <ProjectOutlined className="dropdown-item-icon" />
                <span>{project.name}</span>
              </div>
            ))}
            {getFilteredProjects().length === 0 && (
              <div className="dropdown-empty">没有匹配的项目</div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default ChatPage;
