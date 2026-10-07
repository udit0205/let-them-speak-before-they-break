@echo off
setlocal
cd /d "%~dp0"

echo === LET THEM SPEAK BEFORE THEY BREAK ===
echo.
py --version
node --version
npm --version

echo.
echo [1/3] Creating backend environment...
cd backend
if not exist ".venv\Scripts\python.exe" py -3 -m venv .venv
call ".venv\Scripts\activate.bat"
python -m pip install --upgrade pip
pip install -r requirements.txt
if not exist ".env" copy .env.example .env >nul
cd ..

echo.
echo [2/3] Installing frontend packages...
cd frontend
if not exist ".env" copy .env.example .env >nul
npm install
cd ..

echo.
echo [3/3] Setup complete.
echo Start the backend with: start_backend.bat
echo Start the frontend with: start_frontend.bat
pause
