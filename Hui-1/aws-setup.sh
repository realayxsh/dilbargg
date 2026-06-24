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

  BOT_DIR="$HOME/dilbargg/Hui-1"

  echo "=== Installing Python dependencies ==="
  pip3 install --break-system-packages -r "$BOT_DIR/requirements.txt"

  echo "=== Setting up environment file ==="
  if [ ! -f "$BOT_DIR/.env" ]; then
      cp "$BOT_DIR/.env.example" "$BOT_DIR/.env"
      echo ""
      echo ">>> IMPORTANT: Edit $BOT_DIR/.env and set your TOKEN:"
      echo "    nano $BOT_DIR/.env"
      echo ""
  fi

  echo "=== Installing systemd service ==="
  sudo tee /etc/systemd/system/hui-bot.service > /dev/null << EOF
  [Unit]
  Description=Hui Discord Bot
  After=network.target

  [Service]
  Type=simple
  User=\$USER
  WorkingDirectory=\$BOT_DIR
  ExecStart=/usr/bin/python3 main.py
  Restart=always
  RestartSec=10
  Environment=PYTHONUNBUFFERED=1
  EnvironmentFile=\$BOT_DIR/.env

  [Install]
  WantedBy=multi-user.target
  EOF

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
  