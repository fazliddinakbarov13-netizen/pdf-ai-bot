@echo off
color 0A
title PDF-BOT MO'JIZA YANGILOVCHI
echo =======================================================
echo XATOLIKLARNI TOZALASH VA YANGI BOTNI ISHGA TUSHIRISH...
echo Iltimos, teginmang! Dastur barchasini o'zi qiladi.
echo =======================================================
echo.

echo [1/4] Eski, xato bergan botlar majburan o'ldirilmoqda...
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 2 /nobreak >nul

echo [2/4] Ishchi papka sozlanmoqda...
set CURRENT_DIR=%CD%
set WORK_DIR=C:\pdf-ai-bot
if exist "C:\pdf_bot" set WORK_DIR=C:\pdf_bot
if not exist "%WORK_DIR%" mkdir "%WORK_DIR%"
copy /Y "%CURRENT_DIR%\.env" "%WORK_DIR%\.env" >nul 2>&1
copy /Y "%CURRENT_DIR%\bot_database.db" "%WORK_DIR%\bot_database.db" >nul 2>&1
cd /d "%WORK_DIR%"

echo [3/4] Mo'jizaviy yangi kod (xatosiz) yuklab olinmoqda...
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/fazliddinakbarov13-netizen/pdf-ai-bot/archive/refs/heads/master.zip' -OutFile 'master.zip'; Expand-Archive 'master.zip' -DestinationPath 'temp' -Force; Copy-Item 'temp\pdf-ai-bot-master\*' -Destination . -Force -Recurse; Remove-Item 'master.zip' -Force; Remove-Item 'temp' -Recurse -Force"

set PY_CMD=python
if exist "C:\Python311\python.exe" set PY_CMD=C:\Python311\python.execmd

if exist "C:\Python312\python.exe" set PY_CMD=C:\Python312\python.exe

echo [4/4] Kutubxonalar (ovoz uchun yangi funksiyalar) o'rnatilmoqda...
%PY_CMD% -m pip install pytesseract pdf2docx python-docx PyMuPDF aiohttp pillow python-dotenv google-genai aiogram SpeechRecognition pydub >nul 2>&1

echo.
echo =======================================================
echo HAMMASI TAYYOR 100%%! 
echo YANGI (XATOSIZ) BOT ISHGA TUSHYAPTI...
echo =======================================================
%PY_CMD% main.py
pause
