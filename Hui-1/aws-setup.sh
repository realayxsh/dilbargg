#!/bin/bash
  # One-command AWS setup for Dilbar Discord Bot (Docker-based)
  # Run on any Ubuntu EC2:  bash aws-setup.sh
  set -e

  echo "=== Installing Docker ==="
  if ! command -v docker &> /dev/null; then
      curl -fsSL https://get.docker.com | sudo bash
      sudo usermod -aG docker "$USER"
      echo "Docker installed."
  else
      echo "Docker already installed."
  fi

  echo "=== Cloning bot ==="
  git clone https://github.com/realayxsh/dilbargg.git ~/dilbargg 2>/dev/null || (cd ~/dilbargg && git pull)

  echo ""
  if [ ! -f ~/dilbargg/.env ]; then
      read -rp "Discord Bot Token: " BOT_TOKEN
      read -rp "MongoDB URI:       " BOT_MONGO
      printf "TOKEN=%s\nMONGO_URI=%s\n" "$BOT_TOKEN" "$BOT_MONGO" > ~/dilbargg/.env
      echo ".env saved."
  else
      echo ".env already exists — skipping."
  fi

  echo "=== Building Docker image (first time takes ~2 min) ==="
  sudo docker build -t dilbar-bot ~/dilbargg/Hui-1

  echo "=== Setting up systemd service ==="
  ENV_FILE="/home/$USER/dilbargg/.env"

  sudo tee /etc/systemd/system/dilbar-bot.service > /dev/null << SVCEOF
  [Unit]
  Description=Dilbar Discord Bot
  After=docker.service
  Requires=docker.service

  [Service]
  Type=simple
  User=root
  Restart=always
  RestartSec=10
  ExecStartPre=-/usr/bin/docker rm -f dilbar-bot
  ExecStart=/usr/bin/docker run --name dilbar-bot --rm --env-file $ENV_FILE dilbar-bot
  ExecStop=/usr/bin/docker stop dilbar-bot

  [Install]
  WantedBy=multi-user.target
  SVCEOF

  sudo systemctl daemon-reload
  sudo systemctl enable dilbar-bot
  sudo systemctl restart dilbar-bot

  echo ""
  echo "================================"
  echo " Bot is running! (Python 3.11 inside Docker)"
  echo " Logs   : sudo journalctl -u dilbar-bot -f"
  echo " Stop   : sudo systemctl stop dilbar-bot"
  echo " Update later:"
  echo "   cd ~/dilbargg && git pull"
  echo "   sudo docker build -t dilbar-bot ~/dilbargg/Hui-1"
  echo "   sudo systemctl restart dilbar-bot"
  echo "================================"
  