import { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import apiService from '../services/apiService';
import './HttpChat.css';

const HttpChat = () => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [thoughts, setThoughts] = useState('');
  const [showThoughts, setShowThoughts] = useState(false);
  const [error, setError] = useState('');
  const messagesEndRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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
          const filename = parsed.image_path.split('/').pop();
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
          const filename = parsed.image_path.split('/').pop();
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

  const sendMessage = async () => {
    if (!inputMessage.trim() || isLoading) return;

    // Add user message to UI
    const userMessage = { role: 'user', content: inputMessage, timestamp: new Date() };
    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);
    setThoughts('');
    setError('');

    try {
      const data = await apiService.sendChatMessage(inputMessage, sessionId, true);
      
      // Set session ID if it's the first message
      if (!sessionId) {
        setSessionId(data.session_id);
      }

      // Process response content
      const { text, imageData } = processResponseContent(data.response);
      
      // Add AI response to UI
      const aiMessage = { 
        role: 'assistant', 
        content: text,
        imageData: imageData,
        timestamp: new Date(data.timestamp)
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // Set thoughts if available
      if (data.thoughts) {
        setThoughts(data.thoughts);
      }

      // Auto-continue if needed
      if (data.should_continue) {
        await continueConversation(data.session_id);
      }
    } catch (err) {
      console.error('Error sending message:', err);
      setError(`Error: ${err.message}`);
      const errorMessage = { 
        role: 'error', 
        content: `Error: ${err.message}`, 
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const continueConversation = async (currentSessionId) => {
    try {
      const data = await apiService.continueChat(currentSessionId, true);
      
      // Process response content
      const { text, imageData } = processResponseContent(data.response);
      
      // Add AI response to UI
      const aiMessage = { 
        role: 'assistant', 
        content: text,
        imageData: imageData,
        timestamp: new Date(data.timestamp)
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // Set thoughts if available
      if (data.thoughts) {
        setThoughts(data.thoughts);
      }

      // Continue auto-continuing if needed
      if (data.should_continue) {
        await continueConversation(data.session_id);
      }
    } catch (err) {
      console.error('Error continuing conversation:', err);
      setError(`Error: ${err.message}`);
      const errorMessage = { 
        role: 'error', 
        content: `Error: ${err.message}`, 
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }
  };

  const clearConversation = () => {
    setMessages([]);
    setSessionId(null);
    setInputMessage('');
    setThoughts('');
    setError('');
    setIsLoading(false);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="http-chat">
      <header className="chat-header">
        <h1>Data Analysis Assistant</h1>
        <div className="header-controls">
          <button onClick={clearConversation} className="clear-btn">
            New Conversation
          </button>
          {thoughts && (
            <button 
              onClick={() => setShowThoughts(!showThoughts)} 
              className="thoughts-btn"
            >
              {showThoughts ? 'Hide Thoughts' : 'Show Thoughts'}
            </button>
          )}
        </div>
      </header>

      <div className="chat-container">
        <div className="messages">
          {messages.length === 0 ? (
            <div className="welcome-message">
              <p>Welcome to the Data Analysis Assistant!</p>
              <p>I can help you analyze Excel files in the data directory. Please start by sending a message.</p>
            </div>
          ) : (
            messages.map((msg, index) => (
              <div key={index} className={`message ${msg.role}`}>
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
                  <div className="message-time">
                    {msg.timestamp.toLocaleTimeString()}
                  </div>
                </div>
              </div>
            ))
          )}
          {isLoading && (
            <div className="message assistant">
              <div className="message-content">
                <div className="loading-indicator">
                  <div className="spinner"></div>
                  <span>Thinking...</span>
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
            placeholder="Type your message here..."
            disabled={isLoading}
            rows="3"
          />
          <button 
            onClick={sendMessage} 
            disabled={isLoading || !inputMessage.trim()}
            className="send-btn"
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default HttpChat;