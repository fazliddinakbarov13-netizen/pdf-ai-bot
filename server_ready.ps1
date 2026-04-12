Write-Output "Asosiy o'rnatish boshlandi..."
Set-ExecutionPolicy Bypass -Scope Process -Force
[System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
Write-Output "Chocolatey o'rnatilmoqda..."
iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
$env:Path += ';C:\ProgramData\chocolatey\bin'

Write-Output "Python 3.11 va Git o'rnatilmoqda..."
choco install python311 git -y --force
$env:Path += ';C:\Python311;C:\Python311\Scripts;C:\Program Files\Git\bin'

Write-Output "Loyihani klonlash..."
cd C:\
git clone https://github.com/fazliddinakbarov13-netizen/pdf-ai-bot.git C:\pdf-ai-bot
cd C:\pdf-ai-bot

Write-Output ".env yaratilmoqda..."
Set-Content -Path C:\pdf-ai-bot\.env -Value "BOT_TOKEN=7772622058:AAGLaqfbq1Snd0e3MJXKmiGVOuXJBaaGxjU`nGEMINI_API_KEY=AIzaSyAFMFpMZpFRMzxhBfDdMbrSO2v77P_jhYc`nADMIN_ID=6023720930"

Write-Output "Kutubxonalar yuklanmoqda..."
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Output "BOT ISHGA TUSHDI!!!"
python main.py
