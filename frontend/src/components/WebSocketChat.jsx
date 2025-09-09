import { useState, useEffect, useRef, useImperativeHandle, forwardRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import './WebSocketChat.css';

const WebSocketChat = forwardRef((_, ref) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [isConnecting, setIsConnecting] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [thoughts, setThoughts] = useState('');
  const [showThoughts, setShowThoughts] = useState(false);
  const [error, setError] = useState('');
  const [loadingElapsedTime, setLoadingElapsedTime] = useState(0); // Timer state
  const ws = useRef(null);
  const messagesEndRef = useRef(null);
  const loadingStartTimeRef = useRef(null); // Use ref instead of state for start time
  const loadingTimerRef = useRef(null); // Timer reference

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    // Clean up on unmount
    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (loadingTimerRef.current) {
        clearInterval(loadingTimerRef.current);
      }
    };
  }, []);

  // Timer effect for loading state
  useEffect(() => {
    if (isLoading) {
      // Start timer
      loadingStartTimeRef.current = Date.now();
      setLoadingElapsedTime(0);
      
      // Update elapsed time every 100ms
      loadingTimerRef.current = setInterval(() => {
        const elapsed = Math.floor((Date.now() - loadingStartTimeRef.current) / 1000);
        setLoadingElapsedTime(elapsed);
      }, 100);
    } else {
      // Stop timer
      if (loadingTimerRef.current) {
        clearInterval(loadingTimerRef.current);
        loadingTimerRef.current = null;
      }
      setLoadingElapsedTime(0);
    }
    
    // Clean up on unmount
    return () => {
      if (loadingTimerRef.current) {
        clearInterval(loadingTimerRef.current);
      }
    };
  }, [isLoading]); // Only depend on isLoading

  // Expose functions to parent component
  useImperativeHandle(ref, () => ({
    connect: connectWebSocket,
    disconnect: disconnectWebSocket,
    clear: clearConversation,
    isConnected,
    isConnecting
  }));

  const processResponseContent = (content) => {
    let text = content;
    let imageData = null;
    
    // First, try to extract JSON from markdown code blocks
    const jsonCodeBlockRegex = /```json\s*({[^`]*})\s*```/;
    const match = content.match(jsonCodeBlockRegex);
    
    if (match) {
      try {
        const jsonString = match[1];
        const parsed = JSON.parse(jsonString);
        if (parsed.text && parsed.image_path) {
          text = parsed.text;
          // Extract filename from the absolute path and construct the correct URL
          // Handle both forward slashes and backslashes for cross-platform compatibility
          const pathSeparator = parsed.image_path.includes('\\') ? '\\' : '/';
          const filename = parsed.image_path.split(pathSeparator).pop();
          imageData = {
            path: parsed.image_path,
            url: `http://localhost:8000/image/${filename}`
          };
        }
      } catch (e) {
        // If parsing fails, use the original content
      }
    } else {
      // Try to parse raw JSON content
      try {
        const parsed = JSON.parse(content);
        if (parsed.text && parsed.image_path) {
          text = parsed.text;
          // Extract filename from the absolute path and construct the correct URL
          // Handle both forward slashes and backslashes for cross-platform compatibility
          const pathSeparator = parsed.image_path.includes('\\') ? '\\' : '/';
          const filename = parsed.image_path.split(pathSeparator).pop();
          imageData = {
            path: parsed.image_path,
            url: `http://localhost:8000/image/${filename}`
          };
        }
      } catch (e) {
        // Not JSON, use as is
      }
    }
    
    return { text, imageData };
  };

  const connectWebSocket = () => {
    // Generate a new session ID for each connection
    const newSessionId = 'session_' + Math.random().toString(36).substr(2, 9);
    setSessionId(newSessionId);
    
    setIsConnecting(true);
    setError('');
    
    try {
      // Close existing connection if any
      if (ws.current) {
        ws.current.close();
      }
      
      // Create new WebSocket connection with new session ID
      ws.current = new WebSocket(`ws://localhost:8000/ws/${newSessionId}`);
      
      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setIsConnected(true);
        setIsConnecting(false);
        
        // Add system message
        const connectMessage = {
          role: 'system',
          content: 'Connected to Data Analysis Assistant',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, connectMessage]);
      };
      
      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          
          if (data.type === 'message' || data.type === 'continuation') {
            // Stop loading when we receive a message
            setIsLoading(false);
            
            // Process response content
            const { text, imageData } = processResponseContent(data.response);
            
            const aiMessage = {
              role: 'assistant',
              content: text,
              imageData: imageData,
              timestamp: new Date(data.timestamp),
              type: data.type
            };
            setMessages(prev => [...prev, aiMessage]);
            
            // Set thoughts if available
            if (data.thoughts) {
              setThoughts(data.thoughts);
            }
            
            // Set session ID from server
            if (data.session_id) {
              setSessionId(data.session_id);
            }
          } else if (data.type === 'error') {
            // Stop loading when we receive an error
            setIsLoading(false);
            
            const errorMessage = {
              role: 'error',
              content: `Error: ${data.message}`,
              timestamp: new Date(data.timestamp)
            };
            setMessages(prev => [...prev, errorMessage]);
          }
        } catch (err) {
          console.error('Error parsing WebSocket message:', err);
          // Stop loading on error
          setIsLoading(false);
        }
      };
      
      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setIsConnected(false);
        setIsConnecting(false);
        // Stop loading when disconnected
        setIsLoading(false);
        
        const disconnectMessage = {
          role: 'system',
          content: 'Disconnected from Data Analysis Assistant',
          timestamp: new Date()
        };
        setMessages(prev => [...prev, disconnectMessage]);
      };
      
      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
        setError('WebSocket connection error');
        setIsConnecting(false);
        // Stop loading on error
        setIsLoading(false);
      };
    } catch (err) {
      console.error('Error creating WebSocket connection:', err);
      setError('Failed to create WebSocket connection');
      setIsConnecting(false);
      // Stop loading on error
      setIsLoading(false);
    }
  };

  const disconnectWebSocket = () => {
    if (ws.current) {
      ws.current.close();
    }
  };

  const sendMessage = () => {
    if (!inputMessage.trim() || !isConnected || !ws.current) return;
    
    // Add user message to UI
    const userMessage = {
      role: 'user',
      content: inputMessage,
      timestamp: new Date()
    };
    setMessages(prev => [...prev, userMessage]);
    
    // Start loading
    setIsLoading(true);
    
    // Send message through WebSocket
    try {
      ws.current.send(JSON.stringify({
        message: inputMessage,
        check_continue: true
      }));
      setInputMessage('');
    } catch (err) {
      console.error('Error sending message:', err);
      const errorMessage = {
        role: 'error',
        content: `Error sending message: ${err.message}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
      // Stop loading on error
      setIsLoading(false);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setThoughts('');
    setError('');
    // Stop loading when clearing conversation
    setIsLoading(false);
    // Reset timer state
    loadingStartTimeRef.current = null;
    setLoadingElapsedTime(0);
    if (loadingTimerRef.current) {
      clearInterval(loadingTimerRef.current);
      loadingTimerRef.current = null;
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="websocket-chat">
      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <p>Welcome to the Data Analysis Assistant!</p>
              <p>This assistant can help you analyze Excel files in the data directory.</p>
              <p>{!isConnected ? 'Please connect to start chatting.' : 'You are connected. Start by sending a message.'}</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role} ${msg.type || ''}`}>
                <div className="message-content">
                  <div className="message-text">
                    <ReactMarkdown remarkPlugins={[remarkGfm]}>
                      {msg.content}
                    </ReactMarkdown>
                    {msg.imageData && (
                      <div className="image-container">
                        <img 
                          src={msg.imageData.url} 
                          alt="Analysis visualization" 
                          onError={(e) => {
                            e.target.style.display = 'none';
                            // Show error message
                            const errorDiv = document.createElement('div');
                            errorDiv.className = 'image-error';
                            errorDiv.textContent = 'Failed to load image';
                            errorDiv.style.color = 'red';
                            errorDiv.style.fontStyle = 'italic';
                            e.target.parentNode.appendChild(errorDiv);
                          }}
                          onLoad={(e) => {
                            // Image loaded successfully
                            console.log('Image loaded successfully');
                          }}
                        />
                      </div>
                    )}
                  </div>
                  {msg.role === 'assistant' && (
                    <button 
                      className="copy-button"
                      onClick={() => {
                        navigator.clipboard.writeText(msg.content)
                          .then(() => {
                            // Optional: Show a confirmation message
                            console.log('Message copied to clipboard');
                          })
                          .catch(err => {
                            console.error('Failed to copy message: ', err);
                          });
                      }}
                      title="Copy message"
                    >
                      <span className="material-symbols-outlined">content_copy</span>
                    </button>
                  )}
                  {msg.role === 'system' && (
                    <div className="message-time">
                      {msg.timestamp.toLocaleTimeString()}
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <span>Thinking... ({loadingElapsedTime}s)</span>
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {showThoughts && thoughts && (
          <div className="thoughts-panel">
            <h3>Agent Thoughts</h3>
            <div className="thoughts-content">
              <ReactMarkdown remarkPlugins={[remarkGfm]}>
                {thoughts}
              </ReactMarkdown>
            </div>
          </div>
        )}

        {error && (
          <div className="error-message">
            {error}
          </div>
        )}

        <div className="input-area">
          <textarea
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            placeholder={isConnected ? "Type your message here..." : "Connect to start chatting..."}
            disabled={!isConnected || isLoading}
            rows="3"
          />
          <button 
            onClick={sendMessage} 
            disabled={!isConnected || !inputMessage.trim() || isLoading}
            className={`send-btn ${inputMessage.trim() ? 'has-text' : ''}`}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
});

export default WebSocketChat;