$ErrorActionPreference = 'SilentlyContinue'
Stop-Process -Name python -Force
Start-Sleep 3

$d = "C:\pdf-ai-bot"
if (Test-Path "C:\pdf_bot") { $d = "C:\pdf_bot" }
if (-Not (Test-Path $d)) { New-Item -ItemType Directory -Force -Path $d }
cd $d

$pythonCmd = "C:\Python311\python.exe"
if (-Not (Test-Path $pythonCmd)) {
    $pythonCmd = "C:\Python312\python.exe"
}
if (-Not (Test-Path $pythonCmd)) {
    $pythonCmd = "python"
}

& $pythonCmd -m pip install pdf2docx python-docx PyMuPDF pytesseract aiohttp pillow python-dotenv google-genai aiogram SpeechRecognition pydub 2>$null

# ffmpeg o'rnatish (SpeechRecognition uchun kerak)
if (-Not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    if (Get-Command choco -ErrorAction SilentlyContinue) {
        choco install ffmpeg -y 2>$null
    }
}

[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri 'https://github.com/fazliddinakbarov13-netizen/pdf-ai-bot/archive/refs/heads/master.zip' -OutFile 'master.zip'
Expand-Archive 'master.zip' -DestinationPath 'temp' -Force
Copy-Item 'temp\pdf-ai-bot-master\*' -Destination . -Force -Recurse
Remove-Item 'master.zip' -Force
Remove-Item 'temp' -Recurse -Force

$ErrorActionPreference = 'Continue'
Write-Host "KOD YANGILANDI! Bot ishga tushmoqda..." -ForegroundColor Green
Start-Process -FilePath $pythonCmd -ArgumentList "main.py" -WorkingDirectory $d
