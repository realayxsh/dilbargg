#!/bin/bash
sudo cp ~/dilbargg/Hui-1/bot.service /etc/systemd/system/hui-bot.service
sudo systemctl daemon-reload
sudo systemctl restart hui-bot
echo ""
echo "Bot restarted! Logs:"
sudo journalctl -u hui-bot -f
