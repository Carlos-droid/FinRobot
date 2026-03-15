import json
import os
import time
from finrobot_engine import run_finrobot_analysis

CARTERA_PATH = "/home/ia/FinRobot-master/finrobot-backend/data/cartera.json"

def compare_process():
    if not os.path.exists(CARTERA_PATH):
        print(f"Error: No se encuentra {CARTERA_PATH}")
        return

    with open(CARTERA_PATH, "r") as f:
        cartera = json.load(f)

    print(f"=== Iniciando Comparación Local (7B) vs NIM (Large MoE) ===")

    for asset in cartera:
        symbol = asset["symbol"]
        name = asset["name"]
        
        # 1. Ejecutar Local
        print(f"\n--- Analizando {symbol} con Local 7B ---")
        try:
            run_finrobot_analysis(symbol, name, model_type="local")
        except Exception as e:
            print(f"Error Local {symbol}: {e}")

        # 2. Ejecutar NIM
        print(f"\n--- Analizando {symbol} con NVIDIA NIM ---")
        try:
            run_finrobot_analysis(symbol, name, model_type="nim")
        except Exception as e:
            print(f"Error NIM {symbol}: {e}")

        # Pequeña pausa entre modelos para no saturar
        time.sleep(2)

    print("\n=== Proceso de Comparación Finalizado ===")

if __name__ == "__main__":
    compare_process()
