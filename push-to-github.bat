@echo off
echo ========================================
echo   OpenAssetGraph - Push to GitHub
echo ========================================
echo.

set GIT="C:\Program Files\Git\bin\git.exe"

cd /d d:\OAG

echo [1/4] Checking status...
%GIT% status

echo.
echo [2/4] Adding all changes...
%GIT% add .

echo.
echo [3/4] Committing changes...
set /p commit_msg="Enter commit message: "
if "%commit_msg%"=="" set commit_msg=Update: Add project scanning and CI/CD features
%GIT% commit -m "%commit_msg%"

echo.
echo [4/4] Pushing to GitHub...
%GIT% push origin main

echo.
echo ========================================
echo   Push completed!
echo ========================================
pause
