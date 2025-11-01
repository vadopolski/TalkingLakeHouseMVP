import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  chartData?: any;
  citation?: string;
}

interface ChatInterfaceProps {
  apiUrl?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({
  apiUrl = 'http://localhost:8000/api/query'
}) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);
    setError(null);

    try {
      const response = await axios.post(apiUrl, {
        query: input,
        user_id: 'default_user' // In production, get from auth
      });

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: response.data.text_response || 'No response',
        timestamp: new Date(),
        chartData: response.data.chart_data,
        citation: response.data.citation
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (err: any) {
      const errorMessage = err.response?.data?.error ||
                          err.message ||
                          'An error occurred while processing your query.';
      setError(errorMessage);

      const errorAssistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: `Error: ${errorMessage}`,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorAssistantMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const exampleQuestions = [
    'What were sales last week?',
    'Show me top selling products',
    'How many visitors yesterday?',
    "What's our conversion rate this week?"
  ];

  return (
    <div className="chat-interface" style={styles.container}>
      {/* Header */}
      <div style={styles.header}>
        <h1 style={styles.title}>Sales & Website Analytics Assistant</h1>
        <p style={styles.subtitle}>Ask questions about your sales and website traffic in plain English</p>
      </div>

      {/* Messages */}
      <div style={styles.messagesContainer}>
        {messages.length === 0 ? (
          <div style={styles.welcomeMessage}>
            <h2>Welcome! 👋</h2>
            <p>Try asking questions like:</p>
            <div style={styles.exampleQuestions}>
              {exampleQuestions.map((question, index) => (
                <button
                  key={index}
                  style={styles.exampleButton}
                  onClick={() => setInput(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        ) : (
          messages.map(message => (
            <div
              key={message.id}
              style={{
                ...styles.messageWrapper,
                ...(message.role === 'user' ? styles.userMessageWrapper : styles.assistantMessageWrapper)
              }}
            >
              <div
                style={{
                  ...styles.message,
                  ...(message.role === 'user' ? styles.userMessage : styles.assistantMessage)
                }}
              >
                <div style={styles.messageContent}>
                  {message.content}
                </div>
                {message.citation && (
                  <div style={styles.citation}>
                    {message.citation}
                  </div>
                )}
                {message.chartData && (
                  <div style={styles.chartPlaceholder}>
                    📊 Chart: {message.chartData.type || 'Chart'}
                    <br />
                    <small>(Chart rendering will be implemented in Phase 3)</small>
                  </div>
                )}
              </div>
              <div style={styles.timestamp}>
                {message.timestamp.toLocaleTimeString()}
              </div>
            </div>
          ))
        )}
        {isLoading && (
          <div style={styles.loadingMessage}>
            <div style={styles.loadingDots}>
              <span>●</span><span>●</span><span>●</span>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div style={styles.inputContainer}>
        {error && (
          <div style={styles.errorBanner}>
            ⚠️ {error}
          </div>
        )}
        <div style={styles.inputWrapper}>
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder="Ask a question about sales or website traffic..."
            style={styles.input}
            rows={2}
            disabled={isLoading}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || !input.trim()}
            style={{
              ...styles.sendButton,
              ...(isLoading || !input.trim() ? styles.sendButtonDisabled : {})
            }}
          >
            {isLoading ? '⏳' : '📨'} Send
          </button>
        </div>
      </div>
    </div>
  );
};

// Styles
const styles = {
  container: {
    display: 'flex',
    flexDirection: 'column' as const,
    height: '100vh',
    maxWidth: '1200px',
    margin: '0 auto',
    backgroundColor: '#f5f5f5',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif'
  },
  header: {
    backgroundColor: '#2c3e50',
    color: 'white',
    padding: '20px',
    textAlign: 'center' as const
  },
  title: {
    margin: '0 0 10px 0',
    fontSize: '24px',
    fontWeight: 600
  },
  subtitle: {
    margin: 0,
    fontSize: '14px',
    opacity: 0.9
  },
  messagesContainer: {
    flex: 1,
    overflowY: 'auto' as const,
    padding: '20px',
    backgroundColor: 'white'
  },
  welcomeMessage: {
    textAlign: 'center' as const,
    padding: '40px 20px',
    color: '#666'
  },
  exampleQuestions: {
    display: 'flex',
    flexDirection: 'column' as const,
    gap: '10px',
    marginTop: '20px',
    maxWidth: '400px',
    margin: '20px auto 0'
  },
  exampleButton: {
    padding: '12px 20px',
    backgroundColor: '#ecf0f1',
    border: '1px solid #bdc3c7',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    transition: 'all 0.2s',
    ':hover': {
      backgroundColor: '#d5dbdb'
    }
  },
  messageWrapper: {
    marginBottom: '16px',
    display: 'flex',
    flexDirection: 'column' as const
  },
  userMessageWrapper: {
    alignItems: 'flex-end'
  },
  assistantMessageWrapper: {
    alignItems: 'flex-start'
  },
  message: {
    maxWidth: '70%',
    padding: '12px 16px',
    borderRadius: '12px',
    wordWrap: 'break-word' as const
  },
  userMessage: {
    backgroundColor: '#3498db',
    color: 'white'
  },
  assistantMessage: {
    backgroundColor: '#ecf0f1',
    color: '#2c3e50'
  },
  messageContent: {
    whiteSpace: 'pre-wrap' as const
  },
  citation: {
    marginTop: '8px',
    fontSize: '12px',
    opacity: 0.8,
    borderTop: '1px solid rgba(0,0,0,0.1)',
    paddingTop: '8px'
  },
  chartPlaceholder: {
    marginTop: '12px',
    padding: '20px',
    backgroundColor: 'rgba(0,0,0,0.05)',
    borderRadius: '8px',
    textAlign: 'center' as const
  },
  timestamp: {
    fontSize: '11px',
    color: '#95a5a6',
    marginTop: '4px'
  },
  loadingMessage: {
    display: 'flex',
    justifyContent: 'center',
    padding: '20px'
  },
  loadingDots: {
    display: 'flex',
    gap: '4px',
    fontSize: '20px',
    color: '#3498db',
    animation: 'pulse 1.5s infinite'
  },
  inputContainer: {
    padding: '20px',
    backgroundColor: 'white',
    borderTop: '1px solid #e0e0e0'
  },
  errorBanner: {
    backgroundColor: '#e74c3c',
    color: 'white',
    padding: '10px',
    borderRadius: '8px',
    marginBottom: '10px',
    fontSize: '14px'
  },
  inputWrapper: {
    display: 'flex',
    gap: '10px',
    alignItems: 'flex-end'
  },
  input: {
    flex: 1,
    padding: '12px',
    border: '1px solid #bdc3c7',
    borderRadius: '8px',
    fontSize: '14px',
    fontFamily: 'inherit',
    resize: 'none' as const
  },
  sendButton: {
    padding: '12px 24px',
    backgroundColor: '#3498db',
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    cursor: 'pointer',
    fontSize: '14px',
    fontWeight: 600,
    transition: 'background-color 0.2s'
  },
  sendButtonDisabled: {
    backgroundColor: '#95a5a6',
    cursor: 'not-allowed'
  }
};

export default ChatInterface;
