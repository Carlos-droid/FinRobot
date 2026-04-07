import json
import os
import time
import argparse
from datetime import datetime, timedelta
from finrobot_engine import run_finrobot_analysis

CARTERA_PATH = "/home/ia/FinRobot-master/finrobot-backend/data/cartera.json"

def batch_process(skip_recent=True):
    if not os.path.exists(CARTERA_PATH):
        print(f"Error: No se encuentra {CARTERA_PATH}")
        return

    with open(CARTERA_PATH, "r") as f:
        cartera = json.load(f)

    print(f"=== Iniciando Procesamiento por Lotes de {len(cartera)} activos ===")

    now = datetime.now()

    for asset in cartera:
        symbol = asset["symbol"]
        name = asset["name"]
        
        if skip_recent:
            last_date_str = asset.get("last_analysis_date")
            if last_date_str and last_date_str != "N/A":
                try:
                    last_date = datetime.strptime(last_date_str, "%Y-%m-%d")
                    if (now - last_date).days <= 7:
                        print(f"[INFO] Skipping {symbol} - already analyzed on {last_date_str}")
                        continue
                except ValueError:
                    # Si hay un error de formato, ignoramos la verificación y procedemos
                    pass

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
    parser = argparse.ArgumentParser(description="Batch analyze assets in cartera.")
    parser.add_argument("--force", action="store_true", help="Force analysis of all assets, ignoring recent ones.")
    args = parser.parse_args()

    batch_process(skip_recent=not args.force)
