#!/bin/bash
# install_systemd.sh - FinRobot x ATLAS systemd installation script

set -e

SYSTEMD_DIR="/etc/systemd/system"
LOCAL_DIR=$(pwd)/systemd

echo "Installing FinRobot systemd units..."

# Copy files
sudo cp $LOCAL_DIR/finrobot.service $SYSTEMD_DIR/
sudo cp $LOCAL_DIR/finrobot-dlq-worker.service $SYSTEMD_DIR/
sudo cp $LOCAL_DIR/finrobot-autoresearch.service $SYSTEMD_DIR/
sudo cp $LOCAL_DIR/finrobot-autoresearch.timer $SYSTEMD_DIR/

# Reload systemd
sudo systemctl daemon-reload

echo "Enabling services..."
sudo systemctl enable finrobot.service
sudo systemctl enable finrobot-dlq-worker.service
sudo systemctl enable finrobot-autoresearch.timer

echo "Done. Use 'systemctl start finrobot' to launch."
