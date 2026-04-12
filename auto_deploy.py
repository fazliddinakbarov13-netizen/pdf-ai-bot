import pyautogui
import time
import subprocess
import os

def main():
    print("Avtomatik O'rnatuvchi Ishga Tushdi!")
    print("Iltimos, hech narsa klaviaturada yoki sichqonchada bosmang!")
    
    # Launch RDP
    subprocess.Popen(["mstsc.exe", "server_connect.rdp"])
    
    print("Serverga ulanish (20 soniya kutilmoqda...)")
    time.sleep(20)
    
    # Check if RDP is in focus using pygetwindow
    try:
        import pygetwindow as gw
        active_window = gw.getActiveWindow()
        if not active_window:
            print("Xato: Oyna topilmadi.")
            return

        title = active_window.title.lower()
        if "188.137.233.108" not in title and "remote desktop" not in title and "удален" not in title:
            print(f"XAVFSIZLIK TO'XTATISHI! RDP oynasi faol emas. Hozirgi oyna: {title}")
            return
            
        import pyperclip
        pyperclip.copy("cmd")
        pyautogui.hotkey('win', 'r')
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.press('enter')
        time.sleep(3) # cmd qora oyna ochilishini kutamiz
        
        # Endi ochiq CMD oynasiga butun uzun buyruqni paste qilamiz yoxud u kiritiladi:
        ps_cmd = (
            "powershell.exe -Command \""
            "$ErrorActionPreference = 'SilentlyContinue'; "
            "$d = if (Test-Path 'C:\\pdf_bot') { 'C:\\pdf_bot' } else { 'C:\\pdf-ai-bot' }; "
            "if (-not $d) { $d = 'C:\\pdf_bot'; New-Item -ItemType Directory -Force -Path $d }; "
            "cd $d; "
            "[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; "
            "Invoke-WebRequest -Uri 'https://github.com/fazliddinakbarov13-netizen/pdf-ai-bot/archive/refs/heads/master.zip' -OutFile 'master.zip'; "
            "Expand-Archive 'master.zip' -DestinationPath 'temp' -Force; "
            "Copy-Item 'temp\\pdf-ai-bot-master\\*' -Destination . -Force -Recurse; "
            "Remove-Item 'master.zip' -Force; "
            "Remove-Item 'temp' -Recurse -Force; "
            "C:\\Python311\\python.exe -m pip install -r requirements.txt; "
            "Restart-Computer -Force"
            "\""
        )
        pyperclip.copy(ps_cmd)
        time.sleep(1)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.press('enter')
        
        print("Barchasi muvaffaqiyatli topshirildi! Server o'chib yonadi va bot yangilanadi.")
    except Exception as e:
        print(f"Kutilmagan xatolik: {e}")

if __name__ == "__main__":
    main()
