import { useState } from 'react';
import WebSocketChat from './components/WebSocketChat';
import HttpChat from './components/HttpChat';
import './App.css';

function App() {
  const [chatMode, setChatMode] = useState('websocket'); // 'websocket' or 'http'

  return (
    <div className="App">
      <div className="mode-selector">
        <label>
          <input
            type="radio"
            value="websocket"
            checked={chatMode === 'websocket'}
            onChange={(e) => setChatMode(e.target.value)}
          />
          WebSocket Mode
        </label>
        <label>
          <input
            type="radio"
            value="http"
            checked={chatMode === 'http'}
            onChange={(e) => setChatMode(e.target.value)}
          />
          HTTP Mode
        </label>
      </div>
      {chatMode === 'websocket' ? <WebSocketChat /> : <HttpChat />}
    </div>
  );
}

export default App;