import React, { useState, useRef, useEffect } from 'react';
import { Input, Button, Space, Spin, Empty, Tag, Avatar, Tooltip } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined, LoadingOutlined, ThunderboltOutlined } from '@ant-design/icons';
import './ChatPage.css';

const { TextArea } = Input;

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!inputValue.trim() || loading) return;

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
              errorDetail = `${errorData.detail.type}: ${errorData.detail.message}`;
              if (errorData.detail.suggestion) {
                errorDetail += `\n\n💡 建议: ${errorData.detail.suggestion}`;
              }
            } else {
              errorDetail = errorData.detail;
            }
          }
        } catch {
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
      };

      setMessages(prev => [...prev, assistantMessage]);
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

  const clearChat = () => setMessages([]);

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

      <div className="chat-body">
        {messages.length === 0 ? (
          <div className="chat-welcome">
            <div className="welcome-icon"><ThunderboltOutlined /></div>
            <h3>How can I help you?</h3>
            <p>Ask me anything about your architecture topology</p>
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

      <div className="chat-input">
        <TextArea
          ref={inputRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Ask about your architecture..."
          autoSize={{ minRows: 1, maxRows: 4 }}
        />
        <Button type="primary" icon={<SendOutlined />} onClick={sendMessage} loading={loading} />
      </div>
      <div className="chat-hint">Press Enter to send, Shift+Enter for new line</div>
    </div>
  );
};

export default ChatPage;
