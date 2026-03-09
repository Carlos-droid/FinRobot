"""
FinRobot — Test E2E: Análisis de Banco Santander (SAN.MC)

Usa:
  - YFinance para datos financieros (gratis)
  - Ollama (local) como LLM vía AutoGen SingleAssistant
  - SAN.MC (Bolsa de Madrid, EUR)

Nota: Santander es un filer extranjero en la SEC (20-F, no 10-K),
por lo que usamos datos de YFinance directamente.
"""

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv
load_dotenv()

from finrobot.data_source.yfinance_utils import YFinanceUtils

# ── 1. Obtener datos financieros de Santander ──────────────

TICKER = "SAN.MC"  # Bolsa de Madrid
print("=" * 60)
print(f"📊  Análisis Financiero: Banco Santander ({TICKER})")
print("=" * 60)

# Info básica
print("\n▸ Obteniendo información de la empresa...")
info = YFinanceUtils.get_stock_info(TICKER)
print(f"  Nombre: {info.get('shortName', 'N/A')}")
print(f"  Sector: {info.get('sector', 'N/A')}")
print(f"  Industria: {info.get('industry', 'N/A')}")
print(f"  Moneda: {info.get('currency', 'N/A')}")
print(f"  País: {info.get('country', 'N/A')}")

# Income Statement
print("\n▸ Estado de Resultados...")
income = YFinanceUtils.get_income_stmt(TICKER)
income_str = income.to_string()
print(f"  Filas: {len(income)}, formato: {income.shape}")

# Balance Sheet
print("\n▸ Balance General...")
balance = YFinanceUtils.get_balance_sheet(TICKER)
balance_str = balance.to_string()
print(f"  Filas: {len(balance)}, formato: {balance.shape}")

# Cash Flow
print("\n▸ Flujo de Caja...")
cashflow = YFinanceUtils.get_cash_flow(TICKER)
cashflow_str = cashflow.to_string()
print(f"  Filas: {len(cashflow)}, formato: {cashflow.shape}")

# Stock price
print("\n▸ Precio (últimos 6 meses)...")
hist = YFinanceUtils.get_stock_data(TICKER, "2025-09-01", "2026-03-01")
print(f"  Último cierre: {hist['Close'].iloc[-1]:.2f} EUR")
print(f"  52w High: {hist['High'].max():.2f} EUR")
print(f"  52w Low: {hist['Low'].min():.2f} EUR")

# ── 2. Análisis con LLM (Ollama) vía AutoGen ──────────────

print("\n" + "=" * 60)
print("🤖  Lanzando agente analista con Ollama...")
print("=" * 60)

from finrobot import get_auto_config, SingleAssistant

# Usar el modelo que tengamos disponible en Ollama
ollama_model = os.getenv("OLLAMA_MODEL", "gemma3n:e4b")
llm_config = get_auto_config(prefer_local=True, temperature=0.3)
# Override model with what's actually available
llm_config["config_list"][0]["model"] = ollama_model
llm_config["config_list"][0]["base_url"] = "http://localhost:11434/v1"

print(f"  Modelo: {llm_config['config_list'][0]['model']}")

# Crear prompt de análisis
analysis_prompt = f"""Analiza los siguientes datos financieros de Banco Santander (SAN.MC, Bolsa de Madrid) 
y proporciona un resumen ejecutivo de su situación financiera. Responde en español.

ESTADO DE RESULTADOS:
{income_str}

BALANCE GENERAL (primeras columnas):
{balance_str[:3000]}

FLUJO DE CAJA:
{cashflow_str[:2000]}

DATOS DE MERCADO:
- Último cierre: {hist['Close'].iloc[-1]:.2f} EUR
- Máximo 6m: {hist['High'].max():.2f} EUR
- Mínimo 6m: {hist['Low'].min():.2f} EUR

Proporciona:
1. Resumen ejecutivo (3-4 líneas)
2. Fortalezas clave (3 puntos)
3. Riesgos principales (3 puntos)
4. Perspectiva (alcista/bajista/neutral) con justificación

Responde directamente con el análisis. Cuando termines, escribe TERMINATE.
"""

# Lanzar agente
agent_config = {
    "name": "Santander_Analyst",
    "profile": "Eres un analista financiero senior especializado en el sector bancario europeo. Proporcionas análisis concisos, basados en datos y en español.",
    "toolkits": [],
}

try:
    analyst = SingleAssistant(
        agent_config=agent_config,
        llm_config=llm_config,
    )
    analyst.chat(analysis_prompt)
    print("\n✅ Análisis completado con éxito")
except Exception as e:
    print(f"\n❌ Error en el agente: {e}")
    import traceback
    traceback.print_exc()
