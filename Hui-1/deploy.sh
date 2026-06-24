#!/bin/bash
  set -e

  REPO_DIR="\$HOME/dilbargg"
  BOT_DIR="\$REPO_DIR/Hui-1"
  SERVICE_NAME="hui-bot"

  echo "=== Writing service file ==="
  sudo tee /etc/systemd/system/\$SERVICE_NAME.service > /dev/null << EOF
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

  echo "=== Checking token ==="
  if [ ! -f "\$BOT_DIR/.env" ]; then
      echo ""
      echo "No .env file found. Enter your Discord bot token:"
      read -r TOKEN
      echo "TOKEN=\$TOKEN" > "\$BOT_DIR/.env"
      echo ".env created."
  else
      echo ".env already exists, skipping."
  fi

  echo "=== Installing dependencies ==="
  pip3 install --break-system-packages -q -r "\$BOT_DIR/requirements.txt"

  echo "=== Starting bot ==="
  sudo systemctl daemon-reload
  sudo systemctl enable \$SERVICE_NAME
  sudo systemctl restart \$SERVICE_NAME

  echo ""
  echo "=== Done! Showing logs (Ctrl+C to exit logs) ==="
  sudo journalctl -u \$SERVICE_NAME -f
  