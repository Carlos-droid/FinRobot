import json
import os
import time
from finrobot_engine import run_finrobot_analysis

CARTERA_PATH = "/home/ia/FinRobot-master/finrobot-backend/data/cartera.json"

def batch_process():
    if not os.path.exists(CARTERA_PATH):
        print(f"Error: No se encuentra {CARTERA_PATH}")
        return

    with open(CARTERA_PATH, "r") as f:
        cartera = json.load(f)

    print(f"=== Iniciando Procesamiento por Lotes de {len(cartera)} activos ===")

    for asset in cartera:
        symbol = asset["symbol"]
        name = asset["name"]
        
        # Saltamos si ya tiene análisis reciente (opcional, pero para el usuario lo haremos todo)
        # if asset.get("last_analysis_date") != "N/A": continue

        try:
            _, report_summary = run_finrobot_analysis(symbol, name)
            
            # Actualizamos el estado en el JSON
            asset["last_analysis_date"] = time.strftime("%Y-%m-%d")
            # Extraemos una posible recomendación del texto si es posible (simplificado)
            if "COMPRAR" in report_summary.upper(): asset["finrobot_rating"] = "BUY"
            elif "VENDER" in report_summary.upper(): asset["finrobot_rating"] = "SELL"
            else: asset["finrobot_rating"] = "HOLD"
            
            # Guardamos progreso después de cada uno por seguridad
            with open(CARTERA_PATH, "w") as f:
                json.dump(cartera, f, indent=4)
                
        except Exception as e:
            print(f"Error analizando {symbol}: {str(e)}")
            continue

    print("=== Procesamiento Finalizado con Éxito ===")

if __name__ == "__main__":
    batch_process()
