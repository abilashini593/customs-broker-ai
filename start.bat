@echo off
echo ========================================================
echo Launching ClearBorder AI - Customs Broker Tool
echo ========================================================

set SCRIPT_DIR=%~dp0
set PATH=%SCRIPT_DIR%bin;%PATH%

start "ClearBorder Backend (FastAPI)" cmd /k "cd /d %SCRIPT_DIR%backend && python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload"

timeout /t 2 /nobreak >nul

start "ClearBorder Frontend (Next.js)" cmd /k "cd /d %SCRIPT_DIR%frontend && npm run dev"

echo.
echo Application started!
echo Frontend: http://localhost:3000
echo Backend:  http://127.0.0.1:8000/docs
echo ========================================================
