"""
Configuration file for the Stock Dashboard application
"""

# API Configuration
GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your actual Gemini API key

# Default Settings
DEFAULT_STOCK_SYMBOLS = {
    "Apple": "AAPL",
    "Microsoft": "MSFT", 
    "Google": "GOOGL",
    "Amazon": "AMZN",
    "Tesla": "TSLA",
    "Meta": "META",
    "Netflix": "NFLX",
    "NVIDIA": "NVDA",
    "Berkshire Hathaway": "BRK-B",
    "Johnson & Johnson": "JNJ"
}

# Technical Indicator Settings
TECHNICAL_INDICATORS = {
    "SMA_PERIODS": [5, 10, 20, 50, 100, 200],
    "EMA_PERIODS": [12, 26, 50],
    "RSI_PERIOD": 14,
    "MACD_FAST": 12,
    "MACD_SLOW": 26,
    "MACD_SIGNAL": 9,
    "BOLLINGER_PERIOD": 20,
    "BOLLINGER_STD": 2,
    "STOCHASTIC_K": 14,
    "STOCHASTIC_D": 3,
    "ATR_PERIOD": 14
}

# Chart Settings
CHART_COLORS = {
    "BULLISH": "#00ff00",
    "BEARISH": "#ff0000",
    "NEUTRAL": "#1f77b4",
    "SMA": "#ff7f0e",
    "EMA": "#d62728",
    "BOLLINGER": "#9467bd",
    "VOLUME": "#8c564b"
}

# News Settings
NEWS_SOURCES = {
    "YAHOO_FINANCE": "https://feeds.finance.yahoo.com/rss/2.0/headline",
    "MAX_ARTICLES": 15,
    "CACHE_DURATION": 300  # 5 minutes in seconds
}

# Chatbot Settings
CHATBOT_CONFIG = {
    "MAX_MESSAGES": 50,
    "RESPONSE_TIMEOUT": 30,
    "FALLBACK_RESPONSES": True
}

# App Settings
APP_CONFIG = {
    "PAGE_TITLE": "Stock Market Dashboard",
    "PAGE_ICON": "📈",
    "LAYOUT": "wide",
    "SIDEBAR_STATE": "expanded"
}