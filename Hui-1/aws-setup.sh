#!/bin/bash
# Run this script on a fresh AWS EC2 Ubuntu 22.04 instance
# Usage: bash aws-setup.sh

set -e

echo "=== Updating system ==="
sudo apt-get update -y && sudo apt-get upgrade -y

echo "=== Installing Python 3.11, pip, git, ffmpeg ==="
sudo apt-get install -y python3.11 python3.11-venv python3-pip git ffmpeg

echo "=== Cloning your bot ==="
git clone https://github.com/realayxsh/dilbargg.git ~/dilbargg

echo "=== Installing Python dependencies ==="
cd ~/dilbargg
pip3 install -r requirements.txt

echo "=== Setting up environment file ==="
if [ ! -f .env ]; then
    cp .env.example .env
    echo ""
    echo ">>> IMPORTANT: Edit ~/dilbargg/.env and set your TOKEN:"
    echo "    nano ~/dilbargg/.env"
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
echo ""
echo "To update the bot later:"
echo "  cd ~/dilbargg && git pull && sudo systemctl restart hui-bot"
