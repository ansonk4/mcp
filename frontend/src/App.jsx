import { useState, useRef, useEffect } from 'react';
import WebSocketChat from './components/WebSocketChat';
import './App.css';

function App() {
  const webSocketChatRef = useRef();
  const [selectedModel, setSelectedModel] = useState('gemini-2.5-flash');
  const [customModel, setCustomModel] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [lastSentModel, setLastSentModel] = useState('gemini-2.5-flash');

  // WebSocket connection functions
  const connectWebSocket = () => {
    // Update the last sent model
    setLastSentModel(getSelectedModel());
    
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

  const handleCustomModelChange = (e) => {
    setCustomModel(e.target.value);
  };

  // Function to handle model update when user explicitly selects or confirms a custom model
  const handleCustomModelUpdate = () => {
    if (selectedModel === 'others' && isValidModelName(customModel) && isConnected) {
      // Only reconnect if the model has actually changed
      if (customModel !== lastSentModel) {
        // If already connected, disconnect and reconnect with new model
        disconnectWebSocket();
        // Reconnect after a short delay to ensure disconnection
        setTimeout(() => {
          connectWebSocket();
        }, 500);
      }
    }
  };

  const isValidModelName = (model) => {
    // Check if it's one of the predefined models
    const predefinedModels = ['gemini-2.5-pro', 'gemini-2.5-flash', 'gemini-2.5-flash-lite'];
    if (predefinedModels.includes(model)) {
      return true;
    }
    
    // For custom models, check if it's not empty
    return model && model.trim() !== '';
  };

  const handleModelChange = (e) => {
    const newModel = e.target.value;
    setSelectedModel(newModel);
    
    // Only reconnect if we're connected and the new model selection is valid
    if (isConnected) {
      // For predefined models, always reconnect
      if (newModel !== 'others') {
        disconnectWebSocket();
        // Reconnect after a short delay to ensure disconnection
        setTimeout(() => {
          connectWebSocket();
        }, 500);
      }
      // For 'others', we'll reconnect when the user explicitly confirms the model
      // (e.g., by pressing Enter or clicking away)
    }
  };

  const getSelectedModel = () => {
    if (selectedModel === 'others') {
      return isValidModelName(customModel) ? customModel : 'gemini-2.5-flash';
    }
    return selectedModel;
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
            <option value="gemini-2.5-pro">gemini-2.5-pro</option>
            <option value="gemini-2.5-flash">gemini-2.5-flash</option>
            <option value="gemini-2.5-flash-lite">gemini-2.5-flash-lite</option>
            <option value="others">Others</option>
          </select>
          {selectedModel === 'others' && (
            <input
              type="text"
              className="custom-model-input"
              placeholder="Enter model name"
              value={customModel}
              onChange={handleCustomModelChange}
              onKeyPress={(e) => {
                if (e.key === 'Enter') {
                  handleCustomModelUpdate();
                }
              }}
              onBlur={handleCustomModelUpdate}
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
        <WebSocketChat 
          ref={webSocketChatRef} 
          model={getSelectedModel()}
          onConnectionChange={setIsConnected}
        />
      </div>
    </div>
  );
}

export default App;
