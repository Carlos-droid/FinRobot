import json
import os
import sys
import pandas as pd
from datetime import datetime, timedelta

# Add FinRobot to path
sys.path.append(os.path.dirname(__file__))

from finrobot.data_source.yfinance_utils import YFinanceUtils
from finrobot.functional.portfolio import PortfolioPerformance

def analyze_portfolio():
    cartera_path = os.path.join(os.path.dirname(__file__), 'finrobot-backend', 'data', 'cartera.json')
    
    if not os.path.exists(cartera_path):
        print(f"Error: No se encontró el archivo cartera.json en {cartera_path}")
        return

    with open(cartera_path, 'r') as f:
        cartera = json.load(f)

    # 1 Year historical data for Risk/Drawdown metrics
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")

    print(f"Analizando cartera desde {start_date} hasta {end_date}...\n")
    
    portfolio_daily_returns = {}
    total_unrealized_pnl = 0.0
    total_investment = 0.0
    
    results = []

    for item in cartera:
        symbol = item['symbol']
        shares = item['shares']
        # Si no hay avg_cost, lo simulamos para propósitos del reporte inicial y demostramos la métrica.
        # En una versión real, esto debe leerse del JSON de la cartera.
        # Buscamos el precio de hace 1 año como "coste promedio" simulado, o el precio actual si no hay datos.
        
        try:
            df = YFinanceUtils.get_stock_data(symbol, start_date, end_date)
            if df is not None and not df.empty:
                current_price = df['Close'].iloc[-1]
                
                # Default mock for cost: Price from 6 months ago (or oldest available)
                mid_idx = len(df) // 2 if len(df) > 120 else 0
                avg_cost = df['Close'].iloc[mid_idx] 
                
                # 1. PnL 
                pnl = PortfolioPerformance.calculate_pnl(shares, avg_cost, current_price)
                
                # 2. Risk Metrics (Sharpe & Drawdown)
                # Calculate daily returns for this asset
                daily_pct_change = df['Close'].pct_change().dropna()
                sharpe = PortfolioPerformance.calculate_sharpe_ratio(daily_pct_change)
                drawdowns = PortfolioPerformance.calculate_drawdown(df['Close'])
                
                # Store weighted returns for portfolio level analysis
                portfolio_daily_returns[symbol] = daily_pct_change * (shares * current_price)
                
                total_unrealized_pnl += pnl['unrealized_pnl']
                total_investment += (shares * avg_cost)
                
                results.append({
                    "Symbol": symbol,
                    "Shares": shares,
                    "Current Price": round(current_price, 2),
                    "Simulated Avg Cost": round(avg_cost, 2),
                    "Unrealized PnL (€)": pnl['unrealized_pnl'],
                    "Unrealized PnL (%)": pnl['unrealized_pnl_pct'],
                    "Sharpe Ratio (1Y)": sharpe,
                    "Max Drawdown (%)": drawdowns['max_drawdown_pct']
                })
                print(f"✅ Analizado: {symbol}")
            else:
                print(f"⚠️ No hay datos para: {symbol}")
        except Exception as e:
            print(f"❌ Error analizando {symbol}: {e}")

    # Display individual asset results
    print("\n" + "="*80)
    print(f"{'Symbol':<10} | {'Shares':<8} | {'Price':<8} | {'PnL (%)':<10} | {'Sharpe':<10} | {'Max DD (%)':<10}")
    print("-" * 80)
    for r in results:
        print(f"{r['Symbol']:<10} | {r['Shares']:<8} | {r['Current Price']:<8} | {r['Unrealized PnL (%)']:>8.2f}% | {r['Sharpe Ratio (1Y)']:>8.2f} | {r['Max Drawdown (%)']:>8.2f}%")
        
    print("="*80)
    
    # Portfolio Level Metrics
    if total_investment > 0:
        total_pnl_pct = (total_unrealized_pnl / total_investment) * 100
        print(f"\n📊 RESUMEN GLOBAL DE CARTERA TRAS LA AUDITORÍA")
        print(f"Inversión Total Simulada: €{total_investment:,.2f}")
        print(f"Valor Actual:             €{(total_investment + total_unrealized_pnl):,.2f}")
        print(f"Ganancia/Pérdida (PnL):   €{total_unrealized_pnl:,.2f} ({total_pnl_pct:,.2f}%)")
        
        try:
            # Aggregate portfolio returns
            if portfolio_daily_returns:
                combined_returns = pd.DataFrame(portfolio_daily_returns).sum(axis=1) / (total_investment + total_unrealized_pnl)
                # Remove 0s which might represent missing data on some days
                combined_returns = combined_returns.replace(0, pd.NA).dropna()
                
                if not combined_returns.empty:
                    port_sharpe = PortfolioPerformance.calculate_sharpe_ratio(combined_returns)
                    
                    # Estimate portfolio value over time to calculate max drawdown
                    # (Simplified: assumes static shares over the 1 year period)
                    port_values = []
                    valid_dfs = {}
                    
                    for item in cartera:
                         symbol = item['symbol']
                         df = YFinanceUtils.get_stock_data(symbol, start_date, end_date)
                         if df is not None and not df.empty:
                             valid_dfs[symbol] = df['Close'] * item['shares']
                             
                    if valid_dfs:
                        port_value_series = pd.DataFrame(valid_dfs).sum(axis=1)
                        port_dd = PortfolioPerformance.calculate_drawdown(port_value_series)
                        
                        print(f"\nMétricas de Riesgo del Portafolio:")
                        print(f"- Sharpe Ratio (1Y):   {port_sharpe:.2f}")
                        print(f"- Max Drawdown (1Y):   {port_dd['max_drawdown_pct']}%")
                        print(f"- Current Drawdown:    {port_dd['current_drawdown_pct']}%")
        except Exception as e:
            print(f"Error calculating portfolio-level metrics: {e}")

if __name__ == "__main__":
    analyze_portfolio()
