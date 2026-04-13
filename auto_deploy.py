import pyautogui
import time
import os
import pygetwindow as gw
import pyperclip

def main():
    print("Botni ekranda ochiq holda ishga tushirish skripti...")
    print("Iltimos tegmang...")
    
    # RDP ulanishini avtomatik ochish
    print("Server ochiqligini tekshirish yoxud ochilishini kutish...")
    import subprocess
    try:
        subprocess.Popen(["mstsc.exe", "server_connect.rdp"])
    except FileNotFoundError:
        pass
    
    time.sleep(15) # RDP to'liq ochilishi va ko'pik chiqishiga vaqt berish

    # RDP ochiq ekanini tekshirish
    try:
        active_window = gw.getActiveWindow()
        if active_window and ("188.137" in active_window.title or "remote desktop" in active_window.title.lower() or "удален" in active_window.title.lower()):
            pass
        else:
            rdp = None
            for w in gw.getAllWindows():
                if '188.137' in w.title:
                    rdp = w
                    break
            if rdp:
                rdp.activate()
                time.sleep(1)
    except:
        pass
        
    time.sleep(2)
            
    # Server ichida qora oynani (CMD) ochish
    pyperclip.copy("cmd")
    pyautogui.hotkey('win', 'r')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    
    # CMD oynasi ochilishi uchun uzog'i 3 sekund kutamiz
    time.sleep(3)
    
    # Yuklanadigan tayyor kod
    # Mahalliy .env faylini o'qish
    env_lines = []
    with open('.env', 'r', encoding='utf-8') as f:
        env_lines = [line.strip() for line in f if line.strip()]
    
    env_echos = []
    for idx, env_line in enumerate(env_lines):
        if idx == 0:
            env_echos.append(f"echo {env_line}> .env")
        else:
            env_echos.append(f"echo {env_line}>> .env")
    
    env_echos_str = "\n".join(env_echos)
    
    cmd_payload = f"""
if exist "C:\\pdf_bot" cd /d "C:\\pdf_bot"
if exist "C:\\pdf-ai-bot" cd /d "C:\\pdf-ai-bot"
taskkill /F /IM python.exe
curl -H "Cache-Control: no-cache" -L -o master.zip https://github.com/fazliddinakbarov13-netizen/pdf-ai-bot/archive/refs/heads/master.zip
powershell -c "Expand-Archive -Path 'master.zip' -DestinationPath 'temp' -Force"
xcopy /Y /E /H temp\\pdf-ai-bot-master\\* .
rd /S /Q temp
del /Q master.zip
{env_echos_str}
python main.py
"""
    
    pyperclip.copy(cmd_payload + "\n\n")
    
    # Send Ctrl+V
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    
    print("Muvaffaqiyatli! Server ekranida xato bo'lsa darhol ko'rinadi.")

if __name__ == "__main__":
    main()
