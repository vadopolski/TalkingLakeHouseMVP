@echo off
echo ================================
echo Sales Analytics Chat Assistant
echo Docker Setup with Local LLM
echo ================================
echo.

echo Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Docker is not installed or not running
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [1/4] Starting Docker services (PostgreSQL, Ollama, Backend, Frontend)...
docker-compose up -d

echo.
echo [2/4] Waiting for services to be healthy...
timeout /t 10 /nobreak >nul

echo.
echo [3/4] Checking if Ollama model is available...
docker exec ollama ollama list | findstr llama3.2 >nul 2>&1
if errorlevel 1 (
    echo [INFO] Pulling llama3.2 model (this may take a few minutes)...
    docker exec ollama ollama pull llama3.2
) else (
    echo [INFO] llama3.2 model already available
)

echo.
echo [4/4] Services are starting up...
echo.
echo ================================
echo Services Status:
echo ================================
echo PostgreSQL Database: http://localhost:5432
echo   - Database: analytics_db
echo   - User: readonly_user
echo   - Password: readonly123
echo.
echo Ollama (Local LLM): http://localhost:11434
echo   - Model: llama3.2
echo.
echo Backend API: http://localhost:8000
echo   - API Docs: http://localhost:8000/docs
echo.
echo Frontend UI: http://localhost:5173
echo ================================
echo.
echo To view logs:
echo   - All services:    docker-compose logs -f
echo   - Backend only:    docker-compose logs -f backend
echo   - Frontend only:   docker-compose logs -f frontend
echo.
echo To stop all services:
echo   - docker-compose down
echo.
echo Press any key to view live logs (Ctrl+C to exit)...
pause >nul

docker-compose logs -f
