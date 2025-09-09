import { useState, useRef } from 'react';
import WebSocketChat from './components/WebSocketChat';
import './App.css';

function App() {
  const webSocketChatRef = useRef();
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [customModel, setCustomModel] = useState('');

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

  const handleModelChange = (e) => {
    setSelectedModel(e.target.value);
  };

  const handleCustomModelChange = (e) => {
    setCustomModel(e.target.value);
  };

  return (
    <div className="App">
      <div className="sidebar">
        <div className="sidebar-header">
          <h1>Data Analysis Assistant</h1>
        </div>
        <div className="model-selection">
          <label htmlFor="model-select">Select Model:</label>
          <select 
            id="model-select" 
            className="model-select"
            value={selectedModel} 
            onChange={handleModelChange}
          >
            <option value="gemini-2.5-pro">Gemini 2.5 Pro</option>
            <option value="gemini-2.5-flash">Gemini 2.5 Flash</option>
            <option value="gemini-2.5-flash-lite">Gemini 2.5 Flash Lite</option>
            <option value="others">Others</option>
          </select>
          {selectedModel === 'others' && (
            <input
              type="text"
              className="custom-model-input"
              placeholder="Enter model name"
              value={customModel}
              onChange={handleCustomModelChange}
            />
          )}
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
        <WebSocketChat ref={webSocketChatRef} model={selectedModel === 'others' ? customModel : selectedModel} />
      </div>
    </div>
  );
}

export default App;
