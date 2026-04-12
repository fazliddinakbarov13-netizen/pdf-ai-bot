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
            
        print("RDP faol! Buyruqlar kiritilmoqda...")
        import pyperclip
        cmd_full = "cmd.exe /c \"cd C:\\pdf-ai-bot && git fetch --all && git reset --hard origin/master && git pull && C:\\Python311\\python.exe -m pip install -r requirements.txt && shutdown /r /t 0\""
        pyperclip.copy(cmd_full)
        
        pyautogui.hotkey('win', 'r')
        time.sleep(2)
        pyautogui.hotkey('ctrl', 'v')
        time.sleep(1)
        pyautogui.press('enter')
        
        print("Barchasi muvaffaqiyatli topshirildi! Server o'chib yonadi va bot yangilanadi.")
    except Exception as e:
        print(f"Kutilmagan xatolik: {e}")

if __name__ == "__main__":
    main()
