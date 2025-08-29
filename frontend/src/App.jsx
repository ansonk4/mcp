import { useState, useRef } from 'react';
import WebSocketChat from './components/WebSocketChat';
import HttpChat from './components/HttpChat';
import './App.css';

function App() {
  const [chatMode, setChatMode] = useState('websocket'); // 'websocket' or 'http'
  const webSocketChatRef = useRef();

  // WebSocket connection functions
  const connectWebSocket = () => {
    if (webSocketChatRef.current) {
      webSocketChatRef.current.connect();
    }
  };

  const disconnectWebSocket = () => {
    if (webSocketChatRef.current) {
      webSocketChatRef.current.disconnect();
    }
  };

  const clearConversation = () => {
    if (webSocketChatRef.current) {
      webSocketChatRef.current.clear();
    }
  };

  return (
    <div className="App">
      <div className="sidebar">
        <div className="sidebar-header">
          <h2>Data Analysis Assistant</h2>
        </div>
        <div className="mode-selector">
          <label className={chatMode === 'websocket' ? 'active' : ''}>
            <input
              type="radio"
              value="websocket"
              checked={chatMode === 'websocket'}
              onChange={(e) => setChatMode(e.target.value)}
            />
            <span>WebSocket Mode</span>
          </label>
          <label className={chatMode === 'http' ? 'active' : ''}>
            <input
              type="radio"
              value="http"
              checked={chatMode === 'http'}
              onChange={(e) => setChatMode(e.target.value)}
            />
            <span>HTTP Mode</span>
          </label>
        </div>
        <div className="sidebar-controls">
          {chatMode === 'websocket' ? (
            <>
              <button 
                className="control-button" 
                onClick={connectWebSocket}
              >
                <span>Connect</span>
              </button>
              <button 
                className="control-button disconnect" 
                onClick={disconnectWebSocket}
              >
                <span>Disconnect</span>
              </button>
              <button className="control-button" onClick={clearConversation}>
                <span>Clear Chat</span>
              </button>
            </>
          ) : (
            <button className="control-button" onClick={clearConversation}>
              <span>New Conversation</span>
            </button>
          )}
        </div>
      </div>
      <div className="main-content">
        {chatMode === 'websocket' ? (
          <WebSocketChat ref={webSocketChatRef} />
        ) : (
          <HttpChat />
        )}
      </div>
    </div>
  );
}

export default App;