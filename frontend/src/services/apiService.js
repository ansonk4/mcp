// apiService.js
const API_BASE_URL = 'http://localhost:8000';

export const apiService = {
  // Send a chat message
  async sendChatMessage(message, sessionId = null, checkContinue = true) {
    const response = await fetch(`${API_BASE_URL}/api/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        session_id: sessionId,
        check_continue: checkContinue
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  // Continue the conversation
  async continueChat(sessionId, checkContinue = true) {
    const response = await fetch(`${API_BASE_URL}/api/chat/continue`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        session_id: sessionId,
        check_continue: checkContinue
      }),
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  // Get session information
  async getSessionInfo(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/info`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  // Get session tools
  async getSessionTools(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/tools`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  // Get session history
  async getSessionHistory(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}/history`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  // Delete session
  async deleteSession(sessionId) {
    const response = await fetch(`${API_BASE_URL}/api/sessions/${sessionId}`, {
      method: 'DELETE',
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  },

  // Health check
  async healthCheck() {
    const response = await fetch(`${API_BASE_URL}/health`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  }
};

export default apiService;