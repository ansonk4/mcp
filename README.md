# MCP Data Analysis Assistant

An AI-powered data analysis assistant that combines Google's Gemini API with custom tools for Excel data processing. The system consists of three main components: an AI client, an MCP server with data analysis tools, and a React frontend interface.

## Architecture

The system is composed of three main parts:

1. **MCP Server** (`src/server/`): Provides data analysis tools and file operations
2. **AI API Server** (`src/client/main_api.py`): Connects to the MCP server, interfaces with Google's Gemini API, and serves as the backend for the frontend
3. **Frontend** (`frontend/`): React web interface for interacting with the assistant

## Prerequisites

- Python 3.10 or higher
- Node.js 16 or higher
- Google Gemini API key
- [uv](https://github.com/astral-sh/uv) - Python package manager

## Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ansonk4/mcp
   cd mcp
   ```

2. Create a virtual environment and install dependencies using uv:
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file in the root directory with your Google Gemini API key:
   ```env
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install Node dependencies:
   ```bash
   npm install
   ```

3. Return to the root directory:
   ```bash
   cd ..
   ```

## Startup Instructions

You can start all services in two ways:

### Option 1: Using the Convenience Script (Recommended)

After completing the installation steps above, you can use the appropriate script for your operating system:

**On macOS/Linux:**
```bash
./start-all.sh
```

**On Windows:**
```cmd
start-all.bat
```

This will start all three services:
- MCP Server on `http://127.0.0.1:9000`
- AI API Server on `http://localhost:8000`
- Frontend on `http://localhost:5173`

### Option 2: Manual Startup (For Development)

You need to start three services for the complete system to work:

#### 1. Start the MCP Server

In one terminal, activate your virtual environment and start the MCP server:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
python -m src.server.main
```

The server will start on `http://127.0.0.1:9000`.

#### 2. Start the AI API Server

In another terminal, activate your virtual environment and start the AI API server:
```bash
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uvicorn src.client.main_api:app --host 0.0.0.0 --port 8000 --reload
```

The server will start on `http://localhost:8000`.

#### 3. Start the Frontend Server

In a third terminal, navigate to the frontend directory and start the development server:
```bash
cd frontend
npm run dev
```

The frontend will start on `http://localhost:5173` by default.

### 4. Prepare Data Files

Place any Excel files you want to analyze in the `data/` directory. The system will automatically detect and list these files when you connect.

## Usage

1. Open your browser and navigate to `http://localhost:5173`
2. Click the "Connect" button in the sidebar to establish a connection to the backend
3. Once connected, you can ask questions about the data files in your `data/` directory
4. The assistant can perform various data analysis tasks including:
   - Reading and analyzing Excel files
   - Creating visualizations
   - Generating summaries and insights
   - Answering questions about your data

## Features

- **Multi-step Task Processing**: The AI can automatically continue processing complex tasks without user intervention
- **Data Visualization**: Generate charts and graphs from your data
- **Thought Visibility**: Toggle to see the AI's reasoning process
- **Real-time Communication**: WebSocket-based communication for responsive interactions
- **File Operations**: Read, analyze, and process Excel files

## Dependencies

### Backend (Python)
- pandas>=2.0.0
- numpy>=1.24.0
- openpyxl>=3.1.0
- dotenv
- fastmcp
- fastapi
- uvicorn

### Frontend (Node.js)
- react (^19.1.1)
- react-dom (^19.1.1)
- react-markdown (^10.1.0)
- remark-gfm (^4.0.1)

## Project Structure

```
mcp/
├── src/
│   ├── client/          # AI client implementation
│   │   ├── main.py      # Main client logic (CLI version)
│   │   ├── main_api.py  # API server with WebSocket support
│   │   ├── prompt.py    # System prompts and instructions
│   │   └── next_speaker_detection.py  # Conversation flow control
│   ├── server/          # MCP server with tools
│   │   ├── main.py      # Server entry point
│   │   ├── data_analysis_tools.py  # Data analysis functions
│   │   ├── data_visualization.py   # Visualization tools
│   │   └── file_operations_tools.py  # File operation tools
│   └── streamlit/       # Streamlit interface (alternative)
├── frontend/            # React web interface
│   ├── src/
│   │   ├── components/  # React components
│   │   └── services/    # API service files
│   └── package.json     # Frontend dependencies
├── data/                # Directory for data files (git-ignored)
├── requirements.txt     # Python dependencies
├── start-all.sh         # Convenience script to start all services (macOS/Linux)
├── start-all.bat        # Convenience script to start all services (Windows)
└── README.md            # This file
```

## How It Works

The MCP Data Analysis Assistant uses a sophisticated conversation flow:

1. **MCP Server**: Exposes tools for data analysis, file operations, and visualization on port 9000
2. **AI API Server**: 
   - Connects to the MCP server
   - Interfaces with Google's Gemini API
   - Serves as the backend for the frontend on port 8000
   - Provides WebSocket endpoints for real-time communication
3. **Frontend**: Provides a user-friendly interface for interacting with the assistant
4. **Next Speaker Detection**: Intelligent system that determines when the AI should continue processing or wait for user input

The system follows these rules:
- Greets users and lists available Excel files in the data directory
- Guides users through the analysis process
- Automatically continues multi-step tasks
- Uses special formatting for image responses
- Handles conversation flow with intelligent next-speaker detection

## API Endpoints

The AI API Server provides the following endpoints:
- `POST /api/chat` - Process a chat message
- `POST /api/chat/continue` - Continue the conversation
- `GET /api/sessions/{session_id}/info` - Get session information
- `DELETE /api/sessions/{session_id}` - Delete a session
- `GET /api/sessions/{session_id}/tools` - Get available tools for a session
- `GET /api/sessions/{session_id}/history` - Get conversation history for a session
- `GET /image/{filename}` - Serve an image file from the temp directory
- `GET /health` - Health check endpoint
- `WebSocket /ws/{session_id}` - WebSocket endpoint for real-time chat

## Troubleshooting

- If you encounter connection issues, ensure all services are running on their respective ports:
  - MCP Server: `http://127.0.0.1:9000`
  - AI API Server: `http://localhost:8000`
  - Frontend: `http://localhost:5173`
- Check that your Google Gemini API key is correctly set in the `.env` file
- Make sure you've installed all dependencies with the correct Python and Node versions
- The `data/` directory is git-ignored, so your data files won't be committed to version control
- Images generated by the system are stored in the system's temporary directory and served from there

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a pull request

## License

[Add your license information here]