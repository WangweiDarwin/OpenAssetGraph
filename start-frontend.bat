@echo off
title OpenAssetGraph Frontend
echo ========================================
echo   OpenAssetGraph Frontend Launcher
echo ========================================
echo.

REM Set Node.js path
set PATH=d:\OAG\node-v20.11.0-win-x64;%PATH%

REM Navigate to frontend directory
cd /d d:\OAG\frontend

echo Starting Vite development server...
echo Frontend will be available at: http://localhost:3000/
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

node node_modules/vite/bin/vite.js

pause
