@echo off
setlocal
cd /d "%~dp0frontend"
if not exist "node_modules" (
  echo Installing frontend dependencies...
  npm install
)
if not exist ".env" copy .env.example .env >nul
npm run dev
