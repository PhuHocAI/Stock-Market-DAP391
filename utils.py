"""
Utility functions for the Stock Dashboard application
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import streamlit as st
import yfinance as yf

def format_number(num, prefix="", suffix=""):
    """
    Format numbers with appropriate suffixes (K, M, B, T)
    """
    if pd.isna(num) or num == 0:
        return "N/A"
    
    if abs(num) >= 1e12:
        return f"{prefix}{num/1e12:.2f}T{suffix}"
    elif abs(num) >= 1e9:
        return f"{prefix}{num/1e9:.2f}B{suffix}"
    elif abs(num) >= 1e6:
        return f"{prefix}{num/1e6:.2f}M{suffix}"
    elif abs(num) >= 1e3:
        return f"{prefix}{num/1e3:.2f}K{suffix}"
    else:
        return f"{prefix}{num:.2f}{suffix}"

def format_percentage(value, decimals=2):
    """
    Format percentage values
    """
    if pd.isna(value):
        return "N/A"
    return f"{value:.{decimals}f}%"

def format_currency(value, currency="$"):
    """
    Format currency values
    """
    if pd.isna(value):
        return "N/A"
    return f"{currency}{value:,.2f}"

def validate_stock_symbol(symbol):
    """
    Validate if a stock symbol exists and has data
    """
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        return bool(info.get('symbol') or info.get('shortName'))
    except:
        return False

def get_market_status():
    """
    Get current market status (open/closed)
    """
    try:
        # Get current time in EST (market timezone)
        now = datetime.now()
        
        # Simple market hours check (9:30 AM - 4:00 PM EST, Monday-Friday)
        if now.weekday() < 5:  # Monday = 0, Friday = 4
            market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
            
            if market_open <= now <= market_close:
                return "OPEN"
            else:
                return "CLOSED"
        else:
            return "CLOSED"
    except:
        return "UNKNOWN"

def calculate_price_change(current, previous):
    """
    Calculate price change and percentage change
    """
    if pd.isna(current) or pd.isna(previous) or previous == 0:
        return 0, 0
    
    change = current - previous
    change_pct = (change / previous) * 100
    
    return change, change_pct

def get_trading_session_info():
    """
    Get information about current trading session
    """
    market_status = get_market_status()
    now = datetime.now()
    
    if market_status == "OPEN":
        next_close = now.replace(hour=16, minute=0, second=0, microsecond=0)
        time_to_close = next_close - now
        return {
            "status": "Market Open",
            "message": f"Market closes in {time_to_close}",
            "color": "green"
        }
    else:
        # Calculate next market open
        next_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        if now.hour >= 16 or now.weekday() >= 5:
            # Market closed for the day or weekend
            days_ahead = 1 if now.weekday() < 4 else (7 - now.weekday())
            next_open += timedelta(days=days_ahead)
        
        return {
            "status": "Market Closed",
            "message": f"Market opens at {next_open.strftime('%Y-%m-%d %H:%M')}",
            "color": "red"
        }

def create_alert_system():
    """
    Create a simple alert system for price movements
    """
    if 'alerts' not in st.session_state:
        st.session_state.alerts = []
    
    return st.session_state.alerts

def add_price_alert(symbol, target_price, alert_type="above"):
    """
    Add a price alert
    """
    alerts = create_alert_system()
    
    alert = {
        "symbol": symbol,
        "target_price": target_price,
        "alert_type": alert_type,  # "above" or "below"
        "created_at": datetime.now(),
        "triggered": False
    }
    
    alerts.append(alert)
    st.session_state.alerts = alerts

def check_price_alerts(symbol, current_price):
    """
    Check if any price alerts should be triggered
    """
    alerts = create_alert_system()
    triggered_alerts = []
    
    for alert in alerts:
        if alert["symbol"] == symbol and not alert["triggered"]:
            if (alert["alert_type"] == "above" and current_price >= alert["target_price"]) or \
               (alert["alert_type"] == "below" and current_price <= alert["target_price"]):
                alert["triggered"] = True
                triggered_alerts.append(alert)
    
    return triggered_alerts

def export_data_to_csv(data, filename):
    """
    Export DataFrame to CSV
    """
    try:
        csv = data.to_csv(index=True)
        return csv
    except Exception as e:
        st.error(f"Error exporting data: {e}")
        return None

def calculate_portfolio_metrics(holdings):
    """
    Calculate basic portfolio metrics
    """
    if not holdings:
        return {}
    
    total_value = sum(holding["value"] for holding in holdings)
    total_cost = sum(holding["cost"] for holding in holdings)
    
    return {
        "total_value": total_value,
        "total_cost": total_cost,
        "total_gain_loss": total_value - total_cost,
        "total_gain_loss_pct": ((total_value - total_cost) / total_cost) * 100 if total_cost > 0 else 0
    }

def get_sector_performance():
    """
    Get sector performance data
    """
    sector_etfs = {
        "Technology": "XLK",
        "Healthcare": "XLV",
        "Financial": "XLF",
        "Energy": "XLE",
        "Consumer Discretionary": "XLY",
        "Consumer Staples": "XLP",
        "Industrial": "XLI",
        "Materials": "XLB",
        "Utilities": "XLU",
        "Real Estate": "XLRE",
        "Communication": "XLC"
    }
    
    sector_data = {}
    
    for sector, etf in sector_etfs.items():
        try:
            ticker = yf.Ticker(etf)
            hist = ticker.history(period="5d")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change_pct = ((current - previous) / previous) * 100
                
                sector_data[sector] = {
                    "price": current,
                    "change_pct": change_pct,
                    "symbol": etf
                }
        except:
            continue
    
    return sector_data

def create_watchlist():
    """
    Create and manage a stock watchlist
    """
    if 'watchlist' not in st.session_state:
        st.session_state.watchlist = []
    
    return st.session_state.watchlist

def add_to_watchlist(symbol):
    """
    Add a symbol to watchlist
    """
    watchlist = create_watchlist()
    if symbol not in watchlist:
        watchlist.append(symbol.upper())
        st.session_state.watchlist = watchlist
        return True
    return False

def remove_from_watchlist(symbol):
    """
    Remove a symbol from watchlist
    """
    watchlist = create_watchlist()
    if symbol in watchlist:
        watchlist.remove(symbol)
        st.session_state.watchlist = watchlist
        return True
    return False

def get_economic_indicators():
    """
    Get basic economic indicators
    """
    indicators = {
        "S&P 500": "^GSPC",
        "Dow Jones": "^DJI",
        "NASDAQ": "^IXIC",
        "VIX": "^VIX",
        "10Y Treasury": "^TNX",
        "USD Index": "DX-Y.NYB"
    }
    
    indicator_data = {}
    
    for name, symbol in indicators.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            if not hist.empty:
                current = hist['Close'].iloc[-1]
                previous = hist['Close'].iloc[-2] if len(hist) > 1 else current
                change = current - previous
                change_pct = (change / previous) * 100 if previous != 0 else 0
                
                indicator_data[name] = {
                    "value": current,
                    "change": change,
                    "change_pct": change_pct,
                    "symbol": symbol
                }
        except:
            continue
    
    return indicator_data