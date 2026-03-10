@echo off
echo Starting OpenAssetGraph Backend...
echo.

REM Navigate to backend directory
cd /d d:\OAG\backend

REM Start backend server
echo Starting FastAPI server on http://localhost:8001/
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001

pause
