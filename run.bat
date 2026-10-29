@echo off
setlocal enabledelayedexpansion

echo ======================================================================
echo   REST API Design and Documentation Kit - Capstone 48
echo ======================================================================

:: 1. Verify Python availability
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not found in your PATH.
    echo Please install Python 3.11+ and ensure 'Add Python to PATH' is checked.
    pause
    exit /b 1
)

:: 2. Create virtual environment if absent
if not exist ".venv" (
    echo [*] Creating virtual environment in .venv...
    python -m venv .venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: 3. Activate virtual environment
call .venv\Scripts\activate.bat

:: 4. Install / Verify dependencies
echo [*] Checking dependencies...
python -m pip install -r requirements.txt --quiet
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Failed to install dependencies from requirements.txt.
    pause
    exit /b 1
)

:: 5. Initialize & Seed database idempotently
echo [*] Initializing and seeding database...
python scripts\seed_database.py
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Database seeding failed.
    pause
    exit /b 1
)

:: 6. Launch FastAPI server
echo ======================================================================
echo [*] Starting FastAPI application with Uvicorn...
echo [*] Local Server URL:    http://127.0.0.1:8000
echo [*] Swagger UI (Docs):   http://127.0.0.1:8000/docs
echo [*] ReDoc UI:            http://127.0.0.1:8000/redoc
echo [*] OpenAPI JSON:        http://127.0.0.1:8000/openapi.json
echo [*] Press Ctrl+C to stop the server anytime.
echo ======================================================================

uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
