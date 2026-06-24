#!/bin/bash
# Run this script on a fresh AWS EC2 Ubuntu 22.04 instance
# Usage: bash aws-setup.sh

set -e

echo "=== Updating system ==="
sudo apt-get update -y && sudo apt-get upgrade -y

echo "=== Installing Python 3.11, pip, git, ffmpeg ==="
sudo apt-get install -y python3.11 python3.11-venv python3-pip git ffmpeg

echo "=== Cloning your bot (edit the URL below to your repo) ==="
# Replace the URL below with your GitHub repo URL
# git clone https://github.com/YOUR_USERNAME/YOUR_REPO.git ~/Hui-1
# OR if you're uploading files manually, just copy them to ~/Hui-1

echo "=== Installing Python dependencies ==="
cd ~/Hui-1
pip3 install -r requirements.txt

echo "=== Setting up environment file ==="
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo ">>> IMPORTANT: Edit ~/Hui-1/.env and set your TOKEN:"
    echo "    nano ~/Hui-1/.env"
    echo ""
fi

echo "=== Installing systemd service ==="
sudo cp bot.service /etc/systemd/system/hui-bot.service
sudo systemctl daemon-reload
sudo systemctl enable hui-bot
sudo systemctl start hui-bot

echo ""
echo "=== Done! ==="
echo "Check bot status : sudo systemctl status hui-bot"
echo "View live logs   : sudo journalctl -u hui-bot -f"
echo "Restart bot      : sudo systemctl restart hui-bot"
echo "Stop bot         : sudo systemctl stop hui-bot"
