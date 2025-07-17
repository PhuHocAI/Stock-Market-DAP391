import pandas as pd
import numpy as np

def calculate_technical_indicators(data, sma_period=20, ema_period=12):
    """
    Calculate various technical indicators for stock data
    """
    df = data.copy()
    
    # Simple Moving Average (SMA)
    df['SMA'] = df['Close'].rolling(window=sma_period).mean()
    
    # Exponential Moving Average (EMA)
    df['EMA'] = df['Close'].ewm(span=ema_period).mean()
    
    # Bollinger Bands
    df['BB_Middle'] = df['Close'].rolling(window=20).mean()
    bb_std = df['Close'].rolling(window=20).std()
    df['BB_Upper'] = df['BB_Middle'] + (bb_std * 2)
    df['BB_Lower'] = df['BB_Middle'] - (bb_std * 2)
    
    # RSI (Relative Strength Index)
    df['RSI'] = calculate_rsi(df['Close'])
    
    # MACD (Moving Average Convergence Divergence)
    macd_data = calculate_macd(df['Close'])
    df['MACD'] = macd_data['MACD']
    df['MACD_Signal'] = macd_data['Signal']
    df['MACD_Histogram'] = macd_data['Histogram']
    
    # Stochastic Oscillator
    stoch_data = calculate_stochastic(df)
    df['Stoch_K'] = stoch_data['%K']
    df['Stoch_D'] = stoch_data['%D']
    
    # Average True Range (ATR)
    df['ATR'] = calculate_atr(df)
    
    # Volume indicators
    df['Volume_SMA'] = df['Volume'].rolling(window=20).mean()
    df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA']
    
    return df

def calculate_rsi(prices, period=14):
    """
    Calculate Relative Strength Index (RSI)
    """
    delta = prices.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    
    rs = gain / loss
    rsi = 100 - (100 / (1 + rs))
    
    return rsi

def calculate_macd(prices, fast=12, slow=26, signal=9):
    """
    Calculate MACD (Moving Average Convergence Divergence)
    """
    ema_fast = prices.ewm(span=fast).mean()
    ema_slow = prices.ewm(span=slow).mean()
    
    macd = ema_fast - ema_slow
    macd_signal = macd.ewm(span=signal).mean()
    macd_histogram = macd - macd_signal
    
    return {
        'MACD': macd,
        'Signal': macd_signal,
        'Histogram': macd_histogram
    }

def calculate_stochastic(data, k_period=14, d_period=3):
    """
    Calculate Stochastic Oscillator
    """
    low_min = data['Low'].rolling(window=k_period).min()
    high_max = data['High'].rolling(window=k_period).max()
    
    k_percent = 100 * ((data['Close'] - low_min) / (high_max - low_min))
    d_percent = k_percent.rolling(window=d_period).mean()
    
    return {
        '%K': k_percent,
        '%D': d_percent
    }

def calculate_atr(data, period=14):
    """
    Calculate Average True Range (ATR)
    """
    high_low = data['High'] - data['Low']
    high_close = np.abs(data['High'] - data['Close'].shift())
    low_close = np.abs(data['Low'] - data['Close'].shift())
    
    true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    atr = true_range.rolling(window=period).mean()
    
    return atr

def calculate_williams_r(data, period=14):
    """
    Calculate Williams %R
    """
    high_max = data['High'].rolling(window=period).max()
    low_min = data['Low'].rolling(window=period).min()
    
    williams_r = -100 * ((high_max - data['Close']) / (high_max - low_min))
    
    return williams_r

def calculate_cci(data, period=20):
    """
    Calculate Commodity Channel Index (CCI)
    """
    typical_price = (data['High'] + data['Low'] + data['Close']) / 3
    sma_tp = typical_price.rolling(window=period).mean()
    mean_deviation = typical_price.rolling(window=period).apply(
        lambda x: np.abs(x - x.mean()).mean()
    )
    
    cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
    
    return cci

def calculate_momentum(prices, period=10):
    """
    Calculate Momentum indicator
    """
    return prices.diff(period)

def calculate_roc(prices, period=12):
    """
    Calculate Rate of Change (ROC)
    """
    return ((prices / prices.shift(period)) - 1) * 100