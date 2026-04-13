@echo off
chcp 65001 >nul 2>&1
color 0A
title YANGI BOT YUKLOVCHI
echo ====================================
echo  ESKI BOT O'LDIRILMOQDA...
echo ====================================
taskkill /F /IM python.exe /T >nul 2>&1
timeout /t 3 /nobreak >nul

echo ====================================
echo  PAPKA YARATILMOQDA...
echo ====================================
if not exist "C:\pdf_bot" mkdir "C:\pdf_bot"

echo ====================================
echo  YANGI KOD YUKLANMOQDA...
echo ====================================
powershell -Command "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://github.com/fazliddinakbarov13-netizen/pdf-ai-bot/archive/refs/heads/master.zip' -OutFile 'C:\pdf_bot\master.zip'; Expand-Archive 'C:\pdf_bot\master.zip' -DestinationPath 'C:\pdf_bot\temp' -Force; Copy-Item 'C:\pdf_bot\temp\pdf-ai-bot-master\*' -Destination 'C:\pdf_bot\' -Force -Recurse; Remove-Item 'C:\pdf_bot\master.zip' -Force; Remove-Item 'C:\pdf_bot\temp' -Recurse -Force"

echo ====================================
echo  .ENV FAYL YARATILMOQDA...
echo ====================================
(
echo BOT_TOKEN=8746734395:AAGgkW3eN6nd7fLyv_7bB0XgycH7zC_npyI
echo GEMINI_API_KEY=AIzaSyBkezDnJGM7CcT7pd6g0F6HhBcLtxr7J1U
echo ADMIN_ID=2063423669
) > "C:\pdf_bot\.env"

echo ====================================
echo  KUTUBXONALAR O'RNATILMOQDA...
echo ====================================
python -m pip install -q pdf2docx python-docx PyMuPDF openai pywin32 aiohttp pillow python-dotenv google-genai aiogram SpeechRecognition pydub >nul 2>&1

echo ====================================
echo  YANGI BOT ISHGA TUSHMOQDA!
echo ====================================
cd /d "C:\pdf_bot"
python main.py
pause
