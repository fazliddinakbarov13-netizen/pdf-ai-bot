$ErrorActionPreference = 'SilentlyContinue'
Stop-Process -Name python -Force

$paths = @("C:\pdf-ai-bot", "C:\pdf_bot", "C:\Users\Administrator\Desktop\pdf-ai-bot", "C:\Users\Administrator\Desktop\pdf bot")
$d = "C:\pdf-ai-bot"
foreach ($p in $paths) {
    if (Test-Path $p) {
        $d = $p
        break
    }
}

if (-Not (Test-Path $d)) {
    New-Item -ItemType Directory -Force -Path $d
}
cd $d

$pythonCmd = "python"
$possiblePyPaths = @("python", "C:\Python312\python.exe", "C:\Python311\python.exe", "C:\Python310\python.exe")
foreach ($py in $possiblePyPaths) {
    if (Get-Command $py -ErrorAction SilentlyContinue) {
        $pythonCmd = $py
        break
    } elseif (Test-Path $py) {
        $pythonCmd = $py
        break
    }
}

& $pythonCmd -m pip install pdf2docx docx2pdf python-docx PyMuPDF aiohttp nest_asyncio pygetwindow pyautogui pyperclip proxy_requests
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
Invoke-WebRequest -Uri 'https://github.com/fazliddinakbarov13-netizen/pdf-ai-bot/archive/refs/heads/master.zip' -OutFile 'master.zip'
Expand-Archive 'master.zip' -DestinationPath 'temp' -Force
Copy-Item 'temp\pdf-ai-bot-master\*' -Destination . -Force -Recurse
Remove-Item 'master.zip' -Force
Remove-Item 'temp' -Recurse -Force

$ErrorActionPreference = 'Continue'
Write-Host "✅ Kod muvaffaqiyatli yangilandi! Bot qayta ishga tushirilmoqda..." -ForegroundColor Green
Start-Process -FilePath $pythonCmd -ArgumentList "main.py"
