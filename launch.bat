@echo off
title Caberg Valuation Screener
color 0A

echo.
echo  ============================================
echo   Caberg Asset Management
echo   Valuation Screener
echo  ============================================
echo.

python --version >nul 2>&1
if errorlevel 1 (
    echo  [ERROR] Python not found. Install from https://python.org
    echo  Tick "Add Python to PATH" during install.
    pause & exit /b 1
)

echo  Installing / verifying dependencies...
pip install -r requirements.txt --quiet

echo  Launching Caberg Valuation Screener...
echo  Opening at http://localhost:8501
echo  Press Ctrl+C to stop.
echo.

streamlit run screener.py --server.headless true --browser.gatherUsageStats false
pause
