# OpenAssetGraph Frontend Launcher
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  OpenAssetGraph Frontend Launcher" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Set Node.js path
$env:Path = "d:\OAG\node-v20.11.0-win-x64;" + $env:Path

# Navigate to frontend directory
Set-Location d:\OAG\frontend

Write-Host "Starting Vite development server..." -ForegroundColor Green
Write-Host "Frontend will be available at: " -NoNewline
Write-Host "http://localhost:3000/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Start Vite
node node_modules/vite/bin/vite.js
