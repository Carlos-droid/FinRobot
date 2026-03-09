#!/bin/bash
# FinRobot Backend Launch Script

PROJECT_DIR="/home/ia/FinRobot-master"
BACKEND_DIR="$PROJECT_DIR/finrobot-backend"
VENV_PYTHON="$PROJECT_DIR/venv/bin/python"

echo "Iniciando backend de FinRobot..."
cd "$BACKEND_DIR" || exit

# Lanzar uvicorn
"$VENV_PYTHON" -m uvicorn main:app --port 8080 --host 0.0.0.0

echo "El servidor se ha detenido. Presiona cualquier tecla para salir."
read -n 1 -s
