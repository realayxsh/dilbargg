#!/bin/bash
  # One-command AWS setup for Dilbar Discord Bot
  # Run on fresh Ubuntu EC2:  bash aws-setup.sh
  set -e

  echo "=== Installing system packages ==="
  sudo apt-get update -y -q
  sudo apt-get install -y -q python3 python3-pip git ffmpeg

  echo "=== Cloning bot ==="
  git clone https://github.com/realayxsh/dilbargg.git ~/dilbargg 2>/dev/null || (cd ~/dilbargg && git pull)

  BOT_DIR="$HOME/dilbargg/Hui-1"

  echo "=== Installing Python packages ==="
  pip3 install --break-system-packages -q -r "$BOT_DIR/requirements.txt"

  echo ""
  if [ ! -f "$BOT_DIR/.env" ]; then
      read -rp "Discord Bot Token: " BOT_TOKEN
      read -rp "MongoDB URI:       " BOT_MONGO
      printf "TOKEN=%s\nMONGO_URI=%s\n" "$BOT_TOKEN" "$BOT_MONGO" > "$BOT_DIR/.env"
      echo ".env saved."
  else
      echo ".env already exists — skipping."
  fi

  echo "=== Starting bot service ==="
  sudo tee /etc/systemd/system/dilbar-bot.service > /dev/null << SVCEOF
  [Unit]
  Description=Dilbar Discord Bot
  After=network.target

  [Service]
  Type=simple
  User=$USER
  WorkingDirectory=$BOT_DIR
  ExecStart=/usr/bin/python3 main.py
  Restart=always
  RestartSec=10
  Environment=PYTHONUNBUFFERED=1
  EnvironmentFile=$BOT_DIR/.env

  [Install]
  WantedBy=multi-user.target
  SVCEOF

  sudo systemctl daemon-reload
  sudo systemctl enable dilbar-bot
  sudo systemctl restart dilbar-bot

  echo ""
  echo "================================"
  echo " Bot is running!"
  echo " Logs   : sudo journalctl -u dilbar-bot -f"
  echo " Stop   : sudo systemctl stop dilbar-bot"
  echo " Update : cd ~/dilbargg && git pull && sudo systemctl restart dilbar-bot"
  echo "================================"
  