import { useState, useRef } from 'react';
import WebSocketChat from './components/WebSocketChat';
import './App.css';

function App() {
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
          <h1>Data Analysis Assistant</h1>
        </div>
        <div className="sidebar-controls">
          <button 
            className="control-button" 
            onClick={connectWebSocket}
          >
            <span className="material-symbols-outlined">conversion_path</span>
            <span>Connect</span>
          </button>
          <button 
            className="control-button disconnect" 
            onClick={disconnectWebSocket}
          >
            <span className="material-symbols-outlined">cloud_off</span>
            <span>Disconnect</span>
          </button>
          <button className="control-button" onClick={clearConversation}>
            <span className="material-symbols-outlined">delete</span>
            <span>Clear Chat</span>
          </button>
        </div>
      </div>
      <div className="main-content">
        <WebSocketChat ref={webSocketChatRef} />
      </div>
    </div>
  );
}

export default App;