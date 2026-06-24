#!/bin/bash
  # One-command AWS setup for Dilbar Discord Bot
  # Run on fresh Ubuntu EC2:  bash aws-setup.sh
  set -e

  echo "=== Installing system packages ==="
  sudo apt-get update -y -q
  sudo apt-get install -y -q python3.12 python3.12-venv python3.12-dev python3-pip git ffmpeg build-essential

  echo "=== Cloning bot ==="
  git clone https://github.com/realayxsh/dilbargg.git ~/dilbargg 2>/dev/null || (cd ~/dilbargg && git pull)

  BOT_DIR="$HOME/dilbargg/Hui-1"

  echo "=== Creating Python 3.12 virtual environment ==="
  python3.12 -m venv "$HOME/dilbargg/venv"
  source "$HOME/dilbargg/venv/bin/activate"

  echo "=== Installing Python packages ==="
  pip install --upgrade pip -q
  pip install -q -r "$BOT_DIR/requirements.txt"

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
  VENV_PYTHON="$HOME/dilbargg/venv/bin/python"

  sudo tee /etc/systemd/system/dilbar-bot.service > /dev/null << SVCEOF
  [Unit]
  Description=Dilbar Discord Bot
  After=network.target

  [Service]
  Type=simple
  User=$USER
  WorkingDirectory=$BOT_DIR
  ExecStart=$VENV_PYTHON main.py
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
  echo " Update : cd ~/dilbargg && git pull && source ~/dilbargg/venv/bin/activate && pip install -q -r ~/dilbargg/Hui-1/requirements.txt && sudo systemctl restart dilbar-bot"
  echo "================================"
  