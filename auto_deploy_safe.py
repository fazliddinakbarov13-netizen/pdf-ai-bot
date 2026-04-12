import pyautogui
import time
import subprocess
import sys

def main():
    try:
        import pygetwindow as gw
    except ImportError:
        return

    print("RDP ishga tushirilmoqda...")
    subprocess.Popen(["mstsc.exe", "server_connect.rdp"])
    
    # 40 soniyagacha kutamiz va oynani topamiz
    win = None
    for _ in range(40):
        time.sleep(1)
        rdp_windows = [w for w in gw.getAllWindows() if "188" in w.title or "remote desktop" in w.title.lower() or "удален" in w.title.lower()]
        if rdp_windows:
            win = rdp_windows[0]
            break
            
    if not win:
        print("XATO: RDP oynasi 40 soniya ichida ochilmadi.")
        return

    print("RDP oynasi topildi! Diqqat qiling...")
    time.sleep(5) # Oyna to'liq yuklanishi uchun qoshimcha 5 soniya
    
    try:
        if not win.isActive:
            win.restore()
            win.activate()
            time.sleep(2)
    except:
        pass
        
    try:
        # Click center of the RDP
        cx = (win.left + win.right) // 2
        cy = (win.top + win.bottom) // 2
        pyautogui.click(cx, cy)
        time.sleep(2)
    except:
        pass

    import pyperclip
    pyperclip.copy("cmd")
    pyautogui.hotkey('win', 'r')
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(3) # cmd qora oyna ochilishini kutamiz
    
    ps_cmd = (
        "powershell.exe -Command \""
        "cd C:\\pdf-ai-bot; "
        "git fetch --all; "
        "git reset --hard origin/master; "
        "C:\\Python311\\python.exe -m pip install -r requirements.txt; "
        "Restart-Computer -Force"
        "\""
    )
    pyperclip.copy(ps_cmd)
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1)
    pyautogui.press('enter')
    
    print("Muvaffaqiyatli tugatildi!")

if __name__ == "__main__":
    main()
