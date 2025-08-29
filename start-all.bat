@echo off
setlocal

echo Starting MCP Data Analysis Assistant services...

:: Set the base directory
set BASE_DIR=%~dp0
set FRONTEND_DIR=%BASE_DIR%frontend

:: Change to the base directory
cd /d "%BASE_DIR%"

:: Start MCP Server
echo Starting MCP Server on http://127.0.0.1:9000...
start "MCP Server" /d "%BASE_DIR%" cmd /c ".venv\Scripts\activate.bat && python -m src/server/main"

:: Start AI API Server
echo Starting AI API Server on http://localhost:8000...
start "AI API Server" /d "%BASE_DIR%" cmd /c ".venv\Scripts\activate.bat && uvicorn src.client.main_api:app --host 0.0.0.0 --port 8000 --reload"

:: Start Frontend Server
echo Starting Frontend Server on http://localhost:5173...
start "Frontend Server" /d "%FRONTEND_DIR%" cmd /c "npm run dev"

echo All services started!
echo.
echo Access the application at: http://localhost:5173
echo Press Ctrl+C and close the terminal windows to stop all services

:: Keep the main window open
pause