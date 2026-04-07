from fastapi import FastAPI, BackgroundTasks, HTTPException, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import json
import os
import re
import subprocess
from typing import List, Dict, Any, Literal

# ── Project root: parent of finrobot-backend/ ──
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV_PYTHON = os.path.join(PROJECT_ROOT, "venv", "bin", "python")
ENGINE_SCRIPT = os.path.join(PROJECT_ROOT, "finrobot_engine.py")

class DataFormat(BaseModel):
    data_type: str
    parse_as: Literal["text", "table", "chart"]

class OmniWidgetResponse(BaseModel):
    content: Any
    data_format: DataFormat
    citable: bool = Field(default=False)

app = FastAPI(title="FinRobot OpenBB Backend")

ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://pro.openbb.co,https://pro.openbb.dev,http://localhost:1420"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization", "Accept"],
)

class GenericResponse(BaseModel):
    data: Any

class MarkdownResponse(BaseModel):
    markdown: str

class ChartResponse(BaseModel):
    data: List[Dict[str, Any]]
    layout: Dict[str, Any]

@app.get("/")
def read_root():
    return {"status": "FinRobot Backend is running", "endpoints": ["/widgets.json", "/apps.json"]}

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

@app.get("/widgets.json")
@app.get("/widgets.json/widgets.json")
def get_widgets():
    try:
        with open(os.path.join(os.path.dirname(__file__), "widgets.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/apps.json")
@app.get("/apps.json/apps.json")
@app.get("/widgets.json/apps.json")
def get_apps():
    try:
        with open(os.path.join(os.path.dirname(__file__), "apps.json"), "r") as f:
            return json.load(f)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/widgets.json/templates.json")
def get_templates():
    return []

@app.get("/widgets.json/agents.json")
def get_agents():
    return []

# ─────────────────────────────────────────────
# WATCHLIST endpoint
# ─────────────────────────────────────────────
WATCHLIST_DEFAULT = [
    t.strip() for t in os.getenv(
        "WATCHLIST_TICKERS",
        "AI.MC,DIA.MC,GRF.MC,IBE.MC,IAG.MC,LOG.MC,MAP.MC,MVC.MC,RED.MC,REP.MC,TEF.MC,SAN.MC,ITX.MC"
    ).split(",")
]

@app.get("/api/watchlist")
@app.get("/widgets.json/api/watchlist")
def get_watchlist(tickers: str = ""):
    """Returns live market data for a list of tickers (comma-separated)."""
    import yfinance as yf

    ticker_list = [t.strip().upper() for t in tickers.split(",") if t.strip()] if tickers else WATCHLIST_DEFAULT

    results = []
    for symbol in ticker_list:
        try:
            t = yf.Ticker(symbol)
            info = t.fast_info
            hist = t.history(period="2d")

            price = round(float(info.last_price), 3) if hasattr(info, "last_price") and info.last_price else None
            prev_close = round(float(info.previous_close), 3) if hasattr(info, "previous_close") and info.previous_close else None

            change_1d_pct = None
            if price and prev_close and prev_close != 0:
                change_1d_pct = round((price - prev_close) / prev_close * 100, 2)

            # 52-week high / low
            week52_high = round(float(info.year_high), 3) if hasattr(info, "year_high") and info.year_high else None
            week52_low  = round(float(info.year_low), 3)  if hasattr(info, "year_low")  and info.year_low  else None

            volume = int(hist["Volume"].iloc[-1]) if not hist.empty else None

            # Market cap (from info dict — fast_info doesn't always carry this)
            full_info = t.info
            mktcap = full_info.get("marketCap")
            pe_ratio = full_info.get("trailingPE")
            name = full_info.get("longName") or full_info.get("shortName") or symbol

            results.append({
                "symbol":       symbol,
                "name":         name,
                "price":        price,
                "change_1d_pct": change_1d_pct,
                "volume":       volume,
                "market_cap":   mktcap,
                "pe_ratio":     round(pe_ratio, 2) if pe_ratio else None,
                "52w_high":     week52_high,
                "52w_low":      week52_low,
            })
        except Exception as e:
            results.append({
                "symbol": symbol,
                "name": symbol,
                "price": None,
                "change_1d_pct": None,
                "volume": None,
                "market_cap": None,
                "pe_ratio": None,
                "52w_high": None,
                "52w_low": None,
            })

    return results

@app.get("/api/cartera/summary", response_model=GenericResponse)
@app.get("/widgets.json/api/cartera/summary", response_model=GenericResponse)
def get_cartera_summary():
    try:
        with open(os.path.join(DATA_DIR, "cartera.json"), "r") as f:
            data = json.load(f)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading cartera: {str(e)}")

@app.get("/api/radar/summary", response_model=GenericResponse)
@app.get("/widgets.json/api/radar/summary", response_model=GenericResponse)
def get_radar_summary():
    try:
        with open(os.path.join(DATA_DIR, "radar.json"), "r") as f:
            data = json.load(f)
        return {"data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading radar: {str(e)}")

@app.get("/api/ticker/analysis")
@app.get("/widgets.json/api/ticker/analysis")
def get_ticker_analysis(finrobot_symbol: str = "LOG.MC", model_type: str = "local"):
    try:
        # Read FinRobot reports from the output directory
        symbol_dir = finrobot_symbol.replace(".", "_")
        report_path = os.path.join(PROJECT_ROOT, f"reporte_{symbol_dir}_{model_type}.md")
        
        content = ""
        if os.path.exists(report_path):
            with open(report_path, "r") as f:
                content = f.read()
        else:
            # Fallback to general report if model-specific doesn't exist
            fallback_path = os.path.join(PROJECT_ROOT, f"reporte_{symbol_dir}.md")
            if os.path.exists(fallback_path):
                 with open(fallback_path, "r") as f:
                    content = f.read()
                    
        if not content:
            return f"# No hay datos\n\nNo se ha encontrado el informe para {finrobot_symbol} con el modelo {model_type}."

        # Extract only the Analyst_Agent report from the AutoGen raw log
        match = re.search(r"Analyst_Agent \(to chat_manager\):\s*([\s\S]+?)\s*-{80}", content)
        if match:
            # Reformat to just the clean markdown
            content = f"# Informe del Analista ({finrobot_symbol})\n\n{match.group(1).strip()}"
        
        # Return raw string for OpenBB Markdown widget
        return content
    except Exception as e:
         raise HTTPException(status_code=500, detail=f"Error reading analysis: {str(e)}")

@app.get("/api/ticker/chart", response_model=ChartResponse)
@app.get("/widgets.json/api/ticker/chart", response_model=ChartResponse)
def get_ticker_chart(finrobot_symbol: str = "LOG.MC"):
    try:
        import yfinance as yf
        ticker = yf.Ticker(finrobot_symbol)
        hist = ticker.history(period="6mo")
        
        if hist.empty:
            return {"data": [], "layout": {}}
        
        trace = {
            "type": "candlestick",
            "x": hist.index.strftime("%Y-%m-%d").tolist(),
            "open": hist["Open"].tolist(),
            "high": hist["High"].tolist(),
            "low": hist["Low"].tolist(),
            "close": hist["Close"].tolist(),
            "name": finrobot_symbol,
            "increasing": {"line": {"color": "#26a69a"}},
            "decreasing": {"line": {"color": "#ef5350"}}
        }
        
        layout = {
            "title": f"Evolución del Precio - {finrobot_symbol}",
            "xaxis": {"rangeslider": {"visible": False}},
            "paper_bgcolor": "rgba(0,0,0,0)",
            "plot_bgcolor": "rgba(0,0,0,0)",
            "font": {"color": "#ffffff"}
        }
        
        return {"data": [trace], "layout": layout}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching chart data: {str(e)}")

def run_finrobot_bg(ticker: str, model: str):
    try:
        import logging
        logging.info(f"[FinRobot BG] Launching analysis: ticker={ticker}, model={model}")
        subprocess.Popen([
            VENV_PYTHON, 
            ENGINE_SCRIPT, 
            ticker, ticker, model
        ])
    except Exception as e:
        import logging
        logging.error(f"[FinRobot BG] Error: {e}")

@app.get("/api/analyzer/run")
@app.get("/widgets.json/api/analyzer/run")
@app.post("/api/analyzer/run")
@app.post("/widgets.json/api/analyzer/run")
def run_analyzer(request: Request, background_tasks: BackgroundTasks, data: str | dict | None = Body(default=None)):
    import logging
    logging.info(f"[Analyzer] Method {request.method} received.")
    
    if request.method == "GET":
        logging.warning("[Analyzer] GET request on Omni endpoint. Frontend might be sending GET instead of POST.")
        ticker_from_get = request.query_params.get("prompt") or request.query_params.get("ticker_to_run", "")
        ticker = ticker_from_get.strip().upper()
        model = request.query_params.get("model_type", "local").strip()
        
        if not ticker:
            return "⚠️ **Error**: Debes introducir un símbolo (ej. ITX.MC) en el widget anterior o configurar bien los parámetros."
        
        background_tasks.add_task(run_finrobot_bg, ticker, model)
        return (
            f"## ✅ Análisis lanzado en Modo de Compatibilidad\n\n"
            f"**Ticker:** `{ticker}`\n**Modelo:** `{model}`\n\n"
            f"ℹ️ **Información Ténica:** Parece que tu OpenBB Workspace tiene cacheados los parámetros antiguos del widget (Modo Markdown - GET). "
            f"El análisis se ha lanzado correctamente en segundo plano, pero para disfrutar de toda la interactividad del nuevo widget Omni (POST), "
            f"por favor elimina este widget de tu Dashboard y vuelve a añadirlo desde el menú de Apps, o limpia la caché de tu OpenBB Workspace."
        )
    else:
        if isinstance(data, str):
            try:
                data = json.loads(data)
            except Exception:
                data = {}
        if not data or not isinstance(data, dict):
            data = {}

        # 'ticker_to_run' is the visible field in the widget; 'prompt' is the hidden text area
        # Read from ticker_to_run first, then prompt, skipping null/None values
        raw_ticker = data.get("ticker_to_run") or data.get("prompt") or ""
        # data.get() may return Python None if OpenBB sends JSON null
        if raw_ticker is None:
            raw_ticker = ""
        ticker = str(raw_ticker).strip().upper()
        model = str(data.get("model_type") or "local").strip()


    logging.info(f"[Analyzer] Parsed: prompt='{ticker}', model_type='{model}'")
    
    if not ticker:
        return OmniWidgetResponse(
            content="⚠️ **Error**: Debes introducir un símbolo (ej. ITX.MC, SAN.MC) antes de pulsar Run.",
            data_format=DataFormat(data_type="object", parse_as="text"),
            citable=False
        )
    
    background_tasks.add_task(run_finrobot_bg, ticker, model)
    
    return OmniWidgetResponse(
        content=f"## ✅ Análisis lanzado\n\n**Ticker:** `{ticker}`\n**Modelo:** `{model}`\n\nLos agentes de FinRobot están trabajando en segundo plano. El informe estará disponible en el widget **Reporte FinRobot** en unos minutos.",
        data_format=DataFormat(data_type="object", parse_as="text"),
        citable=False
    )

