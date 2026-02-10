@echo off
REM Quick Setup Script for NovaOCR
REM This installs all required dependencies

echo ======================================
echo NovaOCR - Installing Dependencies
echo ======================================
echo.

pip install -r requirements.txt

echo.
echo ======================================
echo Installation Complete!
echo ======================================
echo.
echo Next steps:
echo 1. Get your Mistral API key from: https://console.mistral.ai/
echo 2. Copy .env.example to .env and add your API key
echo 3. Run: run.bat
echo.
pause
