@echo off
echo ========================================================
echo   Starting TRIAGE-AI Healthcare Intake Assistant
echo ========================================================
echo.

IF NOT EXIST ".venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment not found. Please run:
    echo python -m venv .venv
    echo .venv\Scripts\pip install -r requirements.txt
    pause
    exit /b 1
)

echo [INFO] Starting FastAPI server on http://localhost:8000 ...
echo [INFO] Press Ctrl+C in this window to stop the server.
echo.

.\.venv\Scripts\python.exe -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
