@echo off
echo ========================================
echo TalkingLakeHouse MVP - Verification Script
echo ========================================
echo.

echo [1/5] Checking Docker...
docker --version
if %errorlevel% neq 0 (
    echo ERROR: Docker is not installed or not running
    exit /b 1
)
echo ✓ Docker is available
echo.

echo [2/5] Checking Docker Compose...
docker-compose --version
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose is not installed
    exit /b 1
)
echo ✓ Docker Compose is available
echo.

echo [3/5] Validating Docker Compose configuration...
docker-compose config > nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Docker Compose configuration is invalid
    docker-compose config
    exit /b 1
)
echo ✓ Docker Compose configuration is valid
echo.

echo [4/5] Checking Python syntax...
python -m py_compile src/main.py 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python syntax error in src/main.py
    exit /b 1
)
python -m py_compile config/settings.py 2>nul
if %errorlevel% neq 0 (
    echo ERROR: Python syntax error in config/settings.py
    exit /b 1
)
echo ✓ Python files syntax is valid
echo.

echo [5/5] Checking required files...
if not exist ".env" (
    echo Creating .env file from .env.example...
    copy .env.example .env
)
if not exist "docker\init-db.sql" (
    echo ERROR: Missing docker/init-db.sql
    exit /b 1
)
if not exist "frontend\index.html" (
    echo ERROR: Missing frontend/index.html
    exit /b 1
)
echo ✓ All required files are present
echo.

echo ========================================
echo All checks passed! Starting services...
echo ========================================
echo.
echo This will take several minutes on first run...
echo - Building Docker images
echo - Starting PostgreSQL database
echo - Starting Ollama LLM server
echo - Starting backend API
echo - Starting frontend
echo.

docker-compose up --build

echo.
echo Services stopped.
