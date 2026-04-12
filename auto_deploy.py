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
            "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/fazliddinakbarov13-netizen/pdf-ai-bot/master/main.py' -OutFile 'C:\\pdf-ai-bot\\main.py' -ErrorAction SilentlyContinue; "
            "Invoke-WebRequest -Uri 'https://raw.githubusercontent.com/fazliddinakbarov13-netizen/pdf-ai-bot/master/main.py' -OutFile 'C:\\pdf_bot\\main.py' -ErrorAction SilentlyContinue; "
            "python.exe -m pip install pdf2docx docx2pdf python-docx; "
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
