@echo off
title Smart-Sheet AI Setup Utility
echo ===================================================
echo           Smart-Sheet AI (Flask + React)
echo ===================================================
echo.

:: 1. Setup Backend Environment File
if not exist "backend\.env" (
    echo [INFO] Creating backend\.env from template...
    copy "backend\.env.example" "backend\.env" > nul
)

:: 2. Prompt for Gemini API Key
set /p GEMINI_KEY="Enter your Google Gemini API Key (or press Enter to skip and edit backend\.env manually): "
if not "%GEMINI_KEY%"=="" (
    powershell -Command "(gc backend\.env) -replace 'GEMINI_API_KEY=your_google_gemini_api_key_here', 'GEMINI_API_KEY=%GEMINI_KEY%' | Out-File -encoding ASCII backend\.env"
    echo [SUCCESS] Gemini API Key configured in backend\.env!
)
echo.

:: 3. Run Selection
echo How would you like to run the application?
echo [1] Docker Compose (Pre-configured PostgreSQL database, backend API, Nginx frontend)
echo [2] Local Development (Flask SQLite fallback, Node React Dev Server)
echo.
set /p CHOICE="Enter choice [1 or 2]: "

if "%CHOICE%"=="1" (
    echo.
    echo [INFO] Launching Docker Compose...
    docker-compose up --build
    goto end
)

if "%CHOICE%"=="2" (
    echo.
    echo [INFO] Setting up Local Development Environment...
    
    :: Install Backend Requirements
    echo.
    echo [INFO] Initializing virtual environment and installing backend packages...
    if not exist "backend\.venv" (
        python -m venv backend\.venv
    )
    call backend\.venv\Scripts\pip install -r backend\requirements.txt
    
    :: Install Frontend Requirements
    echo.
    echo [INFO] Installing frontend node packages...
    cd frontend
    call npm install
    cd ..

    echo.
    echo [SUCCESS] Setup complete!
    echo.
    echo To run the application locally:
    echo 1. Start backend: Open terminal and run:
    echo    cd backend
    echo    .venv\Scripts\python run.py
    echo.
    echo 2. Start frontend: Open another terminal and run:
    echo    cd frontend
    echo    npm run dev
    echo.
    pause
    goto end
)

:end
echo Setup exiting.
pause
