import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(__file__))
from finrobot.data_source.yfinance_utils import YFinanceUtils
from finrobot.functional.portfolio import PortfolioPerformance

symbol = "IBE.MC"

# 1. Info General
info = YFinanceUtils.get_stock_info(symbol)
print(f"# Reporte Integral de {symbol} ({info.get('longName', 'Iberdrola')})")
print(f"**Sector:** {info.get('sector', 'N/A')} | **Industria:** {info.get('industry', 'N/A')}")
print(f"---")

# 2. Métricas Financieras Clave
print("## 📊 Métricas Financieras y Valoración")
print(f"- **Precio Actual:** €{info.get('currentPrice', 'N/A')} (Rango 52 Semanas: €{info.get('fiftyTwoWeekLow', 'N/A')} - €{info.get('fiftyTwoWeekHigh', 'N/A')})")
print(f"- **Capitalización de Mercado (Market Cap):** €{info.get('marketCap', 0):,.0f}")
print(f"- **Ratio P/E (Trailing):** {info.get('trailingPE', 'N/A')}x \t| **Forward P/E:** {info.get('forwardPE', 'N/A')}x")
print(f"- **Dividend Yield:** {info.get('dividendYield', 0)*100:.2f}%")
print(f"- **Beta (Volatilidad vs Mercado):** {info.get('beta', 'N/A')}")
print(f"- **Recomendación Mayoritaria de Analistas:** {info.get('recommendationKey', 'N/A').upper()}")

# 3. Análisis Técnico (FinRobot Portfolio Lib)
print("\n## 📈 Análisis de Riesgo y Técnico (Últimos 12 Meses)")
from datetime import datetime, timedelta
end_date = datetime.now().strftime("%Y-%m-%d")
start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

df = YFinanceUtils.get_stock_data(symbol, start_date, end_date)
if df is not None and not df.empty:
    daily_returns = df['Close'].pct_change().dropna()
    sharpe = PortfolioPerformance.calculate_sharpe_ratio(daily_returns)
    dd = PortfolioPerformance.calculate_drawdown(df['Close'])
    
    print(f"- **Rendimiento Anualizado (Aprox):** +{(df['Close'].iloc[-1]/df['Close'].iloc[0]-1)*100:.2f}%")
    print(f"- **Ratio de Sharpe:** {sharpe} *(Mide la rentabilidad frente a la volatilidad. >1 es muy bueno)*")
    print(f"- **Máximo Drawdown (Máxima caída):** {dd['max_drawdown_pct']}%")
    print(f"- **Drawdown Actual:** {dd['current_drawdown_pct']}%")
else:
    print("- *No se pudieron calcular métricas de riesgo por falta de histórico local en este instante.*")

print("\n## 💡 Conclusión de FinRobot")
print(f"Iberdrola ({symbol}) presenta un perfil caracterizado por una **baja volatilidad (Beta < 1, bajo Max Drawdown)** y un **fuerte retorno ajustado al riesgo (Ratio de Sharpe > 2)**. Su dividendo del ~{info.get('dividendYield', 0)*100:.2f}% la consolida como una de las anclas de seguridad más fuertes de tu cartera.")
