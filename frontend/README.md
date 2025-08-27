# Data Analysis Assistant Frontend

This is a React frontend for the Data Analysis Assistant API.

## Features

- Real-time chat interface using WebSockets
- Traditional HTTP-based chat as an alternative
- Session management
- Thought visibility toggle
- Responsive design

## Getting Started

1. Install dependencies:
   ```bash
   npm install
   ```

2. Start the development server:
   ```bash
   npm run dev
   ```

3. Open your browser to http://localhost:5173

## Architecture

- `components/WebSocketChat.jsx` - WebSocket-based chat component
- `components/HttpChat.jsx` - HTTP-based chat component
- `services/apiService.js` - HTTP API service for communicating with the backend

## API Endpoints Used

- `POST /api/chat` - Send a message
- `POST /api/chat/continue` - Continue conversation
- `GET /api/sessions/{session_id}/info` - Get session info
- `GET /api/sessions/{session_id}/tools` - Get session tools
- `GET /api/sessions/{session_id}/history` - Get session history
- `DELETE /api/sessions/{session_id}` - Delete session
- `GET /health` - Health check
- `WebSocket /ws/{session_id}` - Real-time communication

## Development

This project was bootstrapped with Vite.js and uses React for the frontend framework.