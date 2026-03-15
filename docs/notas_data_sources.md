# Notas: Fuentes de Datos Financieros

## Alpha Vantage — Límites

- **Límite diario**: 25 solicitudes/día (plan gratuito)
- **Límite por minuto**: 5 solicitudes/minuto

---

## Yahoo Finance (yfinance)

### 2.1.1 — `yf.download()` (API directa)

Función específica de `yfinance` para descarga masiva de datos.

```python
import yfinance as yf
import pandas as pd
import os
from datetime import datetime

OUTPUT_DIRECTORY = '/content'
DATE_START = '2010-01-04'
DATE_END = datetime.today().strftime('%Y-%m-%d')

stocks_to_download = {
    "IBE.MC": "Iberdrola.csv",
    "TEF.MC": "Telefonica.csv",
    "R4.MC": "Renta4.csv",
    "^IBEX": "Ibex35.csv",
    "^GSPC": "Sp500.csv"
}

if __name__ == '__main__':
    if not os.path.exists(OUTPUT_DIRECTORY):
        os.makedirs(OUTPUT_DIRECTORY)

    all_value_closures_list = []

    for stock_symbol, filename in stocks_to_download.items():
        stock_name = filename.replace(".csv", "")
        print(f"\nDescargando: {stock_name} ({stock_symbol})")

        try:
            df = yf.download(stock_symbol, start=DATE_START, end=DATE_END,
                           progress=False, auto_adjust=False)

            if df is not None and not df.empty:
                df.index.name = 'Date'
                all_value_closures = df[['Close']].copy()
                all_value_closures.columns = [stock_symbol]
                all_value_closures_list.append(all_value_closures)

                filepath = os.path.join(OUTPUT_DIRECTORY, filename)
                all_value_closures.to_csv(filepath)
                print(f"Guardado en '{filepath}'")
            else:
                print(f"No se encontraron datos para {stock_name}")

        except Exception as e:
            print(f"Error: {e}")
```

### 2.1.2 — `yf.download()` con `.xs()` (multi-ticker)

```python
import yfinance as yf
import pandas as pd

ticker = '^IBEX'
start = '2010-01-04'
end = '2024-12-30'

df = yf.download(ticker, start, end, progress=False, auto_adjust=False)
df.index = pd.to_datetime(df.index).strftime('%Y-%m-%d')
df.index = pd.to_datetime(df.index)
df.index.name = 'Date'
all_value_closes = df.xs(ticker, level=1, axis=1)
all_value_closes[:3]
```

### `ticker.history()` (pandas_datareader)

Función más general de `pandas_datareader` — accede a múltiples fuentes:
- Yahoo Finance
- Google Finance
- Alpha Vantage
- etc.

Requiere especificar fuente: `source='yahoo'`, rango de fechas, frecuencia.

---

## Resumen de fuentes configuradas en FinRobot

| Fuente | Variable `.env` | Uso |
|---|---|---|
| FMP | `FMP_API_KEY` | Datos financieros principales |
| Finnhub | `FINNHUB_API_KEY` | Datos complementarios |
| Alpha Vantage | `ALPHA_VANTAGE_API_KEY` | Reserva (25 req/día) |
| Yahoo Finance | (sin key) | `yfinance` gratis, sin límite duro |
| SEC EDGAR | `SEC_IDENTITY_NAME/EMAIL` | `edgartools` gratis |
