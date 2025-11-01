@echo off
echo ================================
echo Frontend Chat Interface
echo ================================
echo.

echo [1/2] Installing frontend dependencies...
call npm install

if errorlevel 1 (
    echo [ERROR] Failed to install frontend dependencies
    pause
    exit /b 1
)

echo [2/2] Starting frontend development server...
echo.
echo ================================
echo Frontend running at: http://localhost:5173
echo ================================
echo.
echo Press Ctrl+C to stop the server
echo.

call npm run dev

pause
