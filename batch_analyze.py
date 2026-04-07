import argparse
import json
import os
import time
from finrobot_engine import run_finrobot_analysis
from finrobot.utils import get_current_date

CARTERA_PATH = "/home/ia/FinRobot-master/finrobot-backend/data/cartera.json"

def batch_process(force_reanalyze=False):
    if not os.path.exists(CARTERA_PATH):
        print(f"Error: No se encuentra {CARTERA_PATH}")
        return

    with open(CARTERA_PATH, "r") as f:
        cartera = json.load(f)

    print(f"=== Iniciando Procesamiento por Lotes de {len(cartera)} activos ===")

    current_date = get_current_date()

    for asset in cartera:
        symbol = asset["symbol"]
        name = asset["name"]
        
        # Saltamos si ya tiene análisis reciente (hoy) y no forzamos reanálisis
        last_date = asset.get("last_analysis_date")
        if not force_reanalyze and last_date == current_date:
            print(f"Saltando {symbol} - Análisis ya realizado hoy ({last_date})")
            continue

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
    parser = argparse.ArgumentParser(description="Procesamiento por lotes de activos financieros.")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Forzar el reanálisis de todos los activos, ignorando si ya fueron analizados hoy."
    )
    args = parser.parse_args()

    batch_process(force_reanalyze=args.force)
