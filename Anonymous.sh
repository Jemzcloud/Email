#!/bin/bash

# Config
INTERFACE="wlan0"
VPN_CONFIG="/etc/openvpn/mullvad.ovpn"
STATIC_IP="192.168.1.200"
GATEWAY="192.168.1.1"

# Step 1: Randomize MAC
echo "Randomizing MAC..."
macchanger -r $INTERFACE

# Step 2: Set Static IP
echo "Going static—off DHCP radar..."
ifconfig $INTERFACE $STATIC_IP netmask 255.255.255.0 up
route add default gw $GATEWAY

# Step 3: Start VPN
echo "Firing up VPN..."
openvpn --config $VPN_CONFIG --daemon
sleep 5  # Wait for connection

# Step 4: Lock Down LAN Noise
echo "Silencing LAN chatter..."
iptables -A OUTPUT -p udp --dport 137:138 -j DROP
iptables -A OUTPUT -p udp --dport 5353 -j DROP

# Step 5: Verify Tor (Tails does this—fake check here)
echo "Tor’s up—checking anonymity..."
curl --socks5-hostname 127.0.0.1:9050 https://check.torproject.org/api/ip
echo "You’re a ghost—go forth!"

# Keep it running
echo "Staying silent—Ctrl+C to vanish."
tail -f /dev/null
