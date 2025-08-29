from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import asyncio
import json
import uuid
from datetime import datetime
import os
import tempfile
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from fastmcp import Client
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Import your existing modules
from . import prompt
from .next_speaker_detection import ConversationController

# Load environment variables
load_dotenv()

app = FastAPI(title="AI Agent API", version="1.0.0")

# Serve static files from /tmp directory
import tempfile
import os

# Mount the temp directory for serving files
temp_dir = tempfile.gettempdir()
logger.info(f"Mounting static files from temp directory: {temp_dir}")
if os.path.exists(temp_dir):
    app.mount("/tmp", StaticFiles(directory=temp_dir), name="tmp_files")
    logger.info(f"Successfully mounted static files from: {temp_dir}")
else:
    logger.error(f"Temp directory does not exist: {temp_dir}")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for request/response
class QueryRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    check_continue: bool = True

class QueryResponse(BaseModel):
    response: str
    thoughts: Optional[str] = None
    session_id: str
    should_continue: bool
    detection_result: Optional[Dict[str, Any]] = None
    timestamp: datetime

from datetime import datetime
from pydantic import BaseModel
from typing import Optional, List, Dict, Any

class SessionInfo(BaseModel):
    session_id: str
    created_at: datetime
    message_count: int
    tools_available: bool

class MCPClientManager:
    def __init__(self):
        self.sessions: Dict[str, 'MCPClient'] = {}
        self.gemini_client = genai.Client()

    async def get_or_create_session(self, session_id: Optional[str] = None) -> tuple[str, 'MCPClient']:
        """Get existing session or create new one"""
        if session_id and session_id in self.sessions:
            return session_id, self.sessions[session_id]
        
        # Create new session
        new_session_id = session_id or str(uuid.uuid4())
        client = MCPClient(self.gemini_client)
        
        # Connect to MCP server
        connected = await client.connect_to_server()
        if not connected:
            raise HTTPException(status_code=500, detail="Failed to connect to MCP server")
        
        self.sessions[new_session_id] = client
        return new_session_id, client

    async def remove_session(self, session_id: str):
        """Remove and cleanup session"""
        if session_id in self.sessions:
            await self.sessions[session_id].cleanup()
            del self.sessions[session_id]

    def get_session_info(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        if session_id not in self.sessions:
            return None
        
        client = self.sessions[session_id]
        return SessionInfo(
            session_id=session_id,
            created_at=client.created_at,
            message_count=len(client.messages),
            tools_available=client.tools is not None
        )

class MCPClient:
    def __init__(self, gemini_client):
        self.gemini_client = gemini_client
        self.mcp_client = None
        self.tools = None
        self.messages = []
        self.created_at = datetime.now()
        self.conversation_controller = ConversationController(self.gemini_client)

    async def connect_to_server(self, server_url: str = "http://127.0.0.1:9000/mcp"):
        """Connect to the MCP server"""
        try:
            self.mcp_client = Client(server_url)
            async with self.mcp_client:
                self.tools = await self.mcp_client.list_tools()
            return True
        except Exception as e:
            print(f"Failed to connect to MCP server: {str(e)}")
            return False

    async def call_gemini(self):
        """Call Gemini API with current messages"""
        if not self.mcp_client:
            raise Exception("MCP client is not connected")
            
        async with self.mcp_client:
            response = await self.gemini_client.aio.models.generate_content(
                model="gemini-2.5-flash",
                contents=self.messages,
                config=genai.types.GenerateContentConfig(
                    temperature=0.1,
                    tools=[self.mcp_client.session],
                    system_instruction=prompt.system_prompt,
                    thinking_config=types.ThinkingConfig(
                        include_thoughts=True
                    )
                )
            )
        return response
    
    async def process_query(self, query: str, check_continue: bool = True):
        """Process a user query and return the response"""
        if not self.mcp_client:
            raise Exception("MCP client is not connected")
            
        self.messages.append({"role": "user", "parts": [{"text": query}]})
        response = await self.call_gemini()
        self.messages.append({"role": "model", "parts": response.candidates[0].content.parts})

        if check_continue:
            should_continue, detection_result = await self.conversation_controller.process_turn(self.messages)
        else:
            should_continue, detection_result = False, None

        return response, should_continue, detection_result

    def extract_response_parts(self, response):
        """Extract text and thoughts from response"""
        response_text = ""
        thoughts_text = ""
        
        for part in response.candidates[0].content.parts:
            if not part.text:
                continue
            if part.thought:
                thoughts_text += part.text + "\n"
            else:
                response_text += part.text + "\n"
        
        return response_text.strip(), thoughts_text.strip() if thoughts_text else None

    async def get_initial_message(self):
        """Get the initial greeting message"""
        intro_message = prompt.intro_message
        intro_message += "\n\nAvailable data files:"

        data_dir = Path("data")
        if data_dir.exists() and data_dir.is_dir():
            files = [f"{f.name}" for f in data_dir.iterdir() if f.is_file()]
        else:
            files = []

        for file in files:
            intro_message += f"\n  - {file}"
        
        intro_message += "\n\nHow would you like to analyze the data?"
         
        self.messages.append({"role": "model", "parts": [{"text": intro_message}]})
    
        return intro_message

    def get_tools_info(self):
        """Get information about available tools"""
        if not self.tools:
            return None
        return self.tools

    async def cleanup(self):
        """Cleanup resources"""
        if self.mcp_client:
            try:
                await self.mcp_client.close()
            except Exception as e:
                print(f"Error during cleanup: {str(e)}")

# Global client manager
client_manager = MCPClientManager()

# API Routes
@app.get("/")
async def root():
    return {"message": "AI Agent API is running"}

@app.post("/api/chat", response_model=QueryResponse)
async def chat(request: QueryRequest):
    """Process a chat message"""
    try:
        session_id, client = await client_manager.get_or_create_session(request.session_id)
        
        response, should_continue, detection_result = await client.process_query(
            request.message, request.check_continue
        )
        
        response_text, thoughts = client.extract_response_parts(response)
        
        return QueryResponse(
            response=response_text,
            thoughts=thoughts,
            session_id=session_id,
            should_continue=should_continue,
            detection_result=serialize_detection_result(detection_result),
            timestamp=datetime.now()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/continue", response_model=QueryResponse)
async def continue_chat(request: QueryRequest):
    """Continue the conversation"""
    if not request.session_id:
        raise HTTPException(status_code=400, detail="Session ID required for continue")
    
    # Use "Please continue" as the default message
    continue_request = QueryRequest(
        message="Please continue",
        session_id=request.session_id,
        check_continue=request.check_continue
    )
    
    return await chat(continue_request)

@app.get("/api/sessions/{session_id}/info", response_model=SessionInfo)
async def get_session_info(session_id: str):
    """Get session information"""
    session_info = client_manager.get_session_info(session_id)
    if not session_info:
        raise HTTPException(status_code=404, detail="Session not found")
    return session_info

@app.delete("/api/sessions/{session_id}")
async def delete_session(session_id: str):
    """Delete a session"""
    if session_id not in client_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await client_manager.remove_session(session_id)
    return {"message": "Session deleted successfully"}

@app.get("/api/sessions/{session_id}/tools")
async def get_session_tools(session_id: str):
    """Get available tools for a session"""
    if session_id not in client_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    client = client_manager.sessions[session_id]
    tools = client.get_tools_info()
    return {"tools": tools}

@app.get("/api/sessions/{session_id}/history")
async def get_session_history(session_id: str):
    """Get conversation history for a session"""
    if session_id not in client_manager.sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    client = client_manager.sessions[session_id]
    return {"messages": client.messages}

# WebSocket endpoint for real-time communication
def serialize_detection_result(result):
    """Convert NextSpeakerResult to a serializable dictionary"""
    if result is None:
        return None
    if hasattr(result, '__dict__'):
        return result.__dict__
    return result

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket endpoint for real-time chat"""
    await websocket.accept()
    
    try:
        # Get or create session
        session_id, client = await client_manager.get_or_create_session(session_id)
        
        # Send initial message if this is a new session
        if len(client.messages) == 0:
            initial_message = await client.get_initial_message()
            await websocket.send_json({
                "type": "message",
                "response": initial_message,
                "session_id": session_id,
                "timestamp": datetime.now().isoformat()
            })
        
        while True:
            # Receive message from client
            data = await websocket.receive_json()
            message = data.get("message", "")
            check_continue = data.get("check_continue", True)
            
            if message:
                try:
                    response, should_continue, detection_result = await client.process_query(
                        message, check_continue
                    )
                    
                    response_text, thoughts = client.extract_response_parts(response)
                    
                    # Send response
                    await websocket.send_json({
                        "type": "message",
                        "response": response_text,
                        "thoughts": thoughts,
                        "session_id": session_id,
                        "should_continue": should_continue,
                        "detection_result": serialize_detection_result(detection_result),
                        "timestamp": datetime.now().isoformat()
                    })
                    
                    # If should continue, automatically send continue message
                    # while should_continue:
                    #     response, should_continue, detection_result = await client.process_query(
                    #         "Please continue", check_continue
                    #     )
                        
                    #     response_text, thoughts = client.extract_response_parts(response)
                        
                    #     await websocket.send_json({
                    #         "type": "continuation",
                    #         "response": response_text,
                    #         "thoughts": thoughts,
                    #         "session_id": session_id,
                    #         "should_continue": should_continue,
                    #         "detection_result": serialize_detection_result(detection_result),
                    #         "timestamp": datetime.now().isoformat()
                    #     })
                
                except Exception as e:
                    await websocket.send_json({
                        "type": "error",
                        "message": str(e),
                        "timestamp": datetime.now().isoformat()
                    })
    
    except WebSocketDisconnect:
        print(f"WebSocket disconnected for session: {session_id}")
    except Exception as e:
        print(f"WebSocket error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e),
                "timestamp": datetime.now().isoformat()
            })
        except:
            pass

@app.get("/image/{filename}")
async def get_image(filename: str):
    """Serve an image file from the temp directory"""
    temp_dir = tempfile.gettempdir()
    file_path = os.path.join(temp_dir, filename)
    
    logger.info(f"Requested image: {file_path}")
    logger.info(f"Temp directory: {temp_dir}")
    logger.info(f"Filename: {filename}")
    
    # Check if file exists
    if os.path.exists(file_path):
        logger.info(f"Found image: {file_path}")
        return FileResponse(file_path)
    else:
        # List files in temp directory for debugging
        try:
            files = os.listdir(temp_dir)
            logger.info(f"Files in temp directory: {files[:10]}")  # Show first 10 files
        except Exception as e:
            logger.error(f"Error listing temp directory: {e}")
        
        logger.error(f"Image not found: {file_path}")
        raise HTTPException(status_code=404, detail=f"Image not found: {file_path}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}

# Cleanup on shutdown
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup all sessions on shutdown"""
    for session_id in list(client_manager.sessions.keys()):
        await client_manager.remove_session(session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)