import React, { useState, useRef, useEffect } from 'react';
import { Card, Input, Button, List, Typography, Space, Spin, Empty, Tag, Avatar, Tooltip } from 'antd';
import { SendOutlined, RobotOutlined, UserOutlined, ClearOutlined, LoadingOutlined } from '@ant-design/icons';

const { TextArea } = Input;
const { Text, Paragraph } = Typography;

interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatPageProps {
  apiBaseUrl?: string;
}

const ChatPage: React.FC<ChatPageProps> = ({ apiBaseUrl = 'http://localhost:8001' }) => {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [loading, setLoading] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<any>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingContent]);

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
    setStreamingContent('');

    try {
      const conversationHistory = messages.map(msg => ({
        role: msg.role,
        content: msg.content,
      }));

      const response = await fetch(`${apiBaseUrl}/api/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: userMessage.content,
          conversation_history: conversationHistory,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
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
        content: `Error: ${error instanceof Error ? error.message : 'Failed to send message'}`,
        timestamp: new Date(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setLoading(false);
      setStreamingContent('');
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
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const quickQuestions = [
    'Show me all databases in the topology',
    'Find circular dependencies',
    'What services call the User API?',
    'Analyze the architecture for risks',
  ];

  return (
    <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
      <Card
        title={
          <Space>
            <RobotOutlined />
            <span>AI Architecture Assistant</span>
          </Space>
        }
        extra={
          <Button icon={<ClearOutlined />} onClick={clearChat} size="small">
            Clear Chat
          </Button>
        }
        style={{ height: '100%', display: 'flex', flexDirection: 'column' }}
        bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}
      >
        <div style={{ flex: 1, overflow: 'auto', padding: '16px' }}>
          {messages.length === 0 ? (
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center' }}>
              <Empty
                description={
                  <Space direction="vertical" size="large">
                    <Text>Start a conversation with the AI Architecture Assistant</Text>
                    <div>
                      <Text type="secondary">Try asking:</Text>
                      <div style={{ marginTop: 8 }}>
                        {quickQuestions.map((q, i) => (
                          <Tag
                            key={i}
                            style={{ cursor: 'pointer', margin: '4px' }}
                            color="blue"
                            onClick={() => {
                              setInputValue(q);
                              inputRef.current?.focus();
                            }}
                          >
                            {q}
                          </Tag>
                        ))}
                      </div>
                    </div>
                  </Space>
                }
              />
            </div>
          ) : (
            <List
              dataSource={messages}
              renderItem={(item) => (
                <List.Item style={{ border: 'none', padding: '8px 0' }}>
                  <div
                    style={{
                      display: 'flex',
                      width: '100%',
                      flexDirection: item.role === 'user' ? 'row-reverse' : 'row',
                      gap: '12px',
                    }}
                  >
                    <Avatar
                      icon={item.role === 'user' ? <UserOutlined /> : <RobotOutlined />}
                      style={{
                        backgroundColor: item.role === 'user' ? '#1890ff' : '#52c41a',
                        flexShrink: 0,
                      }}
                    />
                    <div
                      style={{
                        maxWidth: '80%',
                        padding: '12px 16px',
                        borderRadius: '12px',
                        backgroundColor: item.role === 'user' ? '#1890ff' : '#f5f5f5',
                        color: item.role === 'user' ? '#fff' : 'inherit',
                      }}
                    >
                      <Paragraph
                        style={{
                          margin: 0,
                          color: item.role === 'user' ? '#fff' : 'inherit',
                          whiteSpace: 'pre-wrap',
                        }}
                      >
                        {item.content}
                      </Paragraph>
                      <Text
                        type="secondary"
                        style={{
                          fontSize: '11px',
                          display: 'block',
                          marginTop: '4px',
                          color: item.role === 'user' ? 'rgba(255,255,255,0.7)' : undefined,
                        }}
                      >
                        {formatTime(item.timestamp)}
                      </Text>
                    </div>
                  </div>
                </List.Item>
              )}
            />
          )}
          
          {loading && (
            <div style={{ display: 'flex', alignItems: 'center', gap: '12px', padding: '8px 0' }}>
              <Avatar
                icon={<RobotOutlined />}
                style={{ backgroundColor: '#52c41a', flexShrink: 0 }}
              />
              <div
                style={{
                  padding: '12px 16px',
                  borderRadius: '12px',
                  backgroundColor: '#f5f5f5',
                }}
              >
                {streamingContent ? (
                  <Paragraph style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                    {streamingContent}
                  </Paragraph>
                ) : (
                  <Spin indicator={<LoadingOutlined style={{ fontSize: 16 }} spin />} />
                )}
              </div>
            </div>
          )}
          
          <div ref={messagesEndRef} />
        </div>

        <div style={{ padding: '16px', borderTop: '1px solid #f0f0f0' }}>
          <Space.Compact style={{ width: '100%' }}>
            <TextArea
              ref={inputRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about your architecture..."
              autoSize={{ minRows: 1, maxRows: 4 }}
              style={{ borderRadius: '8px 0 0 8px' }}
              disabled={loading}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={sendMessage}
              loading={loading}
              style={{ borderRadius: '0 8px 8px 0', height: 'auto' }}
            >
              Send
            </Button>
          </Space.Compact>
          <Text type="secondary" style={{ fontSize: '11px', marginTop: '4px', display: 'block' }}>
            Press Enter to send, Shift+Enter for new line
          </Text>
        </div>
      </Card>
    </div>
  );
};

export default ChatPage;
