#!/bin/bash

# Script to start all services for the MCP Data Analysis Assistant

echo "Starting MCP Data Analysis Assistant services..."

# Function to clean up background processes on exit
cleanup() {
    echo "Stopping all services..."
    kill $MCP_SERVER_PID $API_SERVER_PID $FRONTEND_SERVER_PID 2>/dev/null
    wait $MCP_SERVER_PID $API_SERVER_PID $FRONTEND_SERVER_PID 2>/dev/null
    exit 0
}

# Trap SIGINT and SIGTERM to clean up properly
trap cleanup SIGINT SIGTERM

# Start MCP Server
echo "Starting MCP Server on http://127.0.0.1:9000..."
cd /Users/anson/quality_people/mcp
source .venv/bin/activate
python -m src.server.main &
MCP_SERVER_PID=$!

# Start AI API Server
echo "Starting AI API Server on http://localhost:8000..."
cd /Users/anson/quality_people/mcp
source .venv/bin/activate
uvicorn src.client.main_api:app --host 0.0.0.0 --port 8000 --reload &
API_SERVER_PID=$!

# Start Frontend Server
echo "Starting Frontend Server on http://localhost:5173..."
cd /Users/anson/quality_people/mcp/frontend
npm run dev &
FRONTEND_SERVER_PID=$!

echo "All services started!"
echo "MCP Server PID: $MCP_SERVER_PID"
echo "AI API Server PID: $API_SERVER_PID"
echo "Frontend Server PID: $FRONTEND_SERVER_PID"
echo ""
echo "Access the application at: http://localhost:5173"
echo "Press Ctrl+C to stop all services"

# Wait for all background processes
wait $MCP_SERVER_PID $API_SERVER_PID $FRONTEND_SERVER_PID