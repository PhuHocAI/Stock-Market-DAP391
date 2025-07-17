import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import google.generativeai as genai
import time

# Page config
st.set_page_config(
    page_title="Stock Market Dashboard",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Import custom modules
from technical_indicators import calculate_technical_indicators
from news_scraper import get_stock_news
from chatbot import render_chatbot

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 2rem;
        color: #1f77b4;
    }
    
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    
    /* Chatbot container */
    .chatbot-container {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1000;
        width: 350px;
        height: 500px;
        background: white;
        border-radius: 10px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        display: none;
    }
    
    .chatbot-toggle {
        position: fixed;
        bottom: 20px;
        right: 20px;
        z-index: 1001;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        background: #1f77b4;
        color: white;
        border: none;
        cursor: pointer;
        font-size: 24px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown('<h1 class="main-header">📈 Stock Market Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar for stock selection
    with st.sidebar:
        st.header("Stock Selection")
        
        # Popular stocks
        popular_stocks = {
            "Apple": "AAPL",
            "Microsoft": "MSFT", 
            "Google": "GOOGL",
            "Amazon": "AMZN",
            "Tesla": "TSLA",
            "Meta": "META",
            "Netflix": "NFLX",
            "NVIDIA": "NVDA"
        }
        
        stock_option = st.selectbox(
            "Choose a popular stock:",
            options=list(popular_stocks.keys())
        )
        
        symbol = st.text_input(
            "Or enter stock symbol:",
            value=popular_stocks[stock_option],
            placeholder="e.g., AAPL, MSFT"
        ).upper()
        
        # Date range selection
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Start Date",
                value=datetime.now() - timedelta(days=365)
            )
        with col2:
            end_date = st.date_input(
                "End Date",
                value=datetime.now()
            )
        
        # Chart type selection
        chart_type = st.selectbox(
            "Chart Type:",
            ["Candlestick", "Line", "Area", "OHLC"]
        )
        
        # Technical indicators
        st.subheader("Technical Indicators")
        show_sma = st.checkbox("Simple Moving Average (SMA)")
        sma_period = st.slider("SMA Period", 5, 200, 20) if show_sma else 20
        
        show_ema = st.checkbox("Exponential Moving Average (EMA)")
        ema_period = st.slider("EMA Period", 5, 200, 12) if show_ema else 12
        
        show_bollinger = st.checkbox("Bollinger Bands")
        show_rsi = st.checkbox("RSI")
        show_macd = st.checkbox("MACD")
        show_volume = st.checkbox("Volume", value=True)

    # Main content tabs
    tab1, tab2 = st.tabs(["📊 Dashboard", "📰 News"])
    
    with tab1:
        render_dashboard(symbol, start_date, end_date, chart_type, 
                        show_sma, sma_period, show_ema, ema_period,
                        show_bollinger, show_rsi, show_macd, show_volume)
    
    with tab2:
        render_news_tab(symbol)
    
    # Render chatbot
    render_chatbot()

def render_dashboard(symbol, start_date, end_date, chart_type, 
                    show_sma, sma_period, show_ema, ema_period,
                    show_bollinger, show_rsi, show_macd, show_volume):
    
    try:
        # Fetch stock data
        with st.spinner(f"Loading data for {symbol}..."):
            stock = yf.Ticker(symbol)
            data = stock.history(start=start_date, end=end_date)
            info = stock.info
        
        if data.empty:
            st.error(f"No data found for symbol {symbol}")
            return
        
        # Display stock info
        col1, col2, col3, col4 = st.columns(4)
        
        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2] if len(data) > 1 else current_price
        price_change = current_price - prev_price
        price_change_pct = (price_change / prev_price) * 100
        
        with col1:
            st.metric(
                label="Current Price",
                value=f"${current_price:.2f}",
                delta=f"{price_change:+.2f} ({price_change_pct:+.2f}%)"
            )
        
        with col2:
            st.metric(
                label="Volume",
                value=f"{data['Volume'].iloc[-1]:,}"
            )
        
        with col3:
            st.metric(
                label="High (52W)",
                value=f"${data['High'].max():.2f}"
            )
        
        with col4:
            st.metric(
                label="Low (52W)",
                value=f"${data['Low'].min():.2f}"
            )
        
        # Calculate technical indicators
        data_with_indicators = calculate_technical_indicators(
            data, sma_period, ema_period
        )
        
        # Create main chart
        fig = create_stock_chart(
            data_with_indicators, symbol, chart_type,
            show_sma, show_ema, show_bollinger, show_volume
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Technical indicators charts
        if show_rsi or show_macd:
            render_technical_charts(data_with_indicators, show_rsi, show_macd)
        
        # Stock information
        if info:
            render_stock_info(info)
        
        # Data table
        with st.expander("📋 Raw Data"):
            st.dataframe(data_with_indicators.tail(100))
    
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")

def create_stock_chart(data, symbol, chart_type, show_sma, show_ema, show_bollinger, show_volume):
    # Create subplots
    rows = 2 if show_volume else 1
    fig = make_subplots(
        rows=rows, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=[f'{symbol} Stock Price', 'Volume'] if show_volume else [f'{symbol} Stock Price'],
        row_width=[0.7, 0.3] if show_volume else [1.0]
    )
    
    # Main price chart
    if chart_type == "Candlestick":
        fig.add_trace(
            go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="Price"
            ),
            row=1, col=1
        )
    elif chart_type == "Line":
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4')
            ),
            row=1, col=1
        )
    elif chart_type == "Area":
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['Close'],
                fill='tonexty',
                mode='lines',
                name='Close Price',
                line=dict(color='#1f77b4')
            ),
            row=1, col=1
        )
    elif chart_type == "OHLC":
        fig.add_trace(
            go.Ohlc(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name="OHLC"
            ),
            row=1, col=1
        )
    
    # Add technical indicators
    if show_sma and 'SMA' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['SMA'],
                mode='lines',
                name='SMA',
                line=dict(color='orange', width=2)
            ),
            row=1, col=1
        )
    
    if show_ema and 'EMA' in data.columns:
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['EMA'],
                mode='lines',
                name='EMA',
                line=dict(color='red', width=2)
            ),
            row=1, col=1
        )
    
    if show_bollinger and all(col in data.columns for col in ['BB_Upper', 'BB_Lower']):
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Upper'],
                mode='lines',
                name='BB Upper',
                line=dict(color='gray', width=1),
                showlegend=False
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Scatter(
                x=data.index,
                y=data['BB_Lower'],
                mode='lines',
                name='BB Lower',
                line=dict(color='gray', width=1),
                fill='tonexty',
                fillcolor='rgba(128,128,128,0.1)',
                showlegend=False
            ),
            row=1, col=1
        )
    
    # Volume chart
    if show_volume:
        colors = ['red' if close < open else 'green' 
                 for close, open in zip(data['Close'], data['Open'])]
        
        fig.add_trace(
            go.Bar(
                x=data.index,
                y=data['Volume'],
                name='Volume',
                marker_color=colors,
                opacity=0.7
            ),
            row=2, col=1
        )
    
    # Update layout
    fig.update_layout(
        title=f'{symbol} Stock Analysis',
        yaxis_title='Price ($)',
        xaxis_rangeslider_visible=False,
        height=600 if show_volume else 500,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )
    
    if show_volume:
        fig.update_yaxes(title_text="Volume", row=2, col=1)
    
    return fig

def render_technical_charts(data, show_rsi, show_macd):
    if show_rsi and 'RSI' in data.columns:
        st.subheader("📊 RSI (Relative Strength Index)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(
            go.Scatter(
                x=data.index,
                y=data['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple')
            )
        )
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought (70)")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold (30)")
        fig_rsi.update_layout(
            title="RSI Indicator",
            yaxis_title="RSI",
            height=300,
            yaxis=dict(range=[0, 100])
        )
        st.plotly_chart(fig_rsi, use_container_width=True)
    
    if show_macd and all(col in data.columns for col in ['MACD', 'MACD_Signal', 'MACD_Histogram']):
        st.subheader("📊 MACD (Moving Average Convergence Divergence)")
        fig_macd = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            subplot_titles=['MACD Line & Signal', 'MACD Histogram']
        )
        
        fig_macd.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        fig_macd.add_trace(
            go.Scatter(
                x=data.index,
                y=data['MACD_Signal'],
                mode='lines',
                name='Signal',
                line=dict(color='red')
            ),
            row=1, col=1
        )
        
        colors = ['red' if val < 0 else 'green' for val in data['MACD_Histogram']]
        fig_macd.add_trace(
            go.Bar(
                x=data.index,
                y=data['MACD_Histogram'],
                name='Histogram',
                marker_color=colors
            ),
            row=2, col=1
        )
        
        fig_macd.update_layout(height=400, title="MACD Indicator")
        st.plotly_chart(fig_macd, use_container_width=True)

def render_stock_info(info):
    st.subheader("📋 Company Information")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Company Name:** {info.get('longName', 'N/A')}")
        st.write(f"**Sector:** {info.get('sector', 'N/A')}")
        st.write(f"**Industry:** {info.get('industry', 'N/A')}")
        st.write(f"**Market Cap:** ${info.get('marketCap', 0):,}")
        st.write(f"**P/E Ratio:** {info.get('trailingPE', 'N/A')}")
    
    with col2:
        st.write(f"**52 Week High:** ${info.get('fiftyTwoWeekHigh', 'N/A')}")
        st.write(f"**52 Week Low:** ${info.get('fiftyTwoWeekLow', 'N/A')}")
        st.write(f"**Dividend Yield:** {info.get('dividendYield', 0)*100:.2f}%" if info.get('dividendYield') else "**Dividend Yield:** N/A")
        st.write(f"**Beta:** {info.get('beta', 'N/A')}")
        st.write(f"**Average Volume:** {info.get('averageVolume', 0):,}")

def render_news_tab(symbol):
    st.header(f"📰 Latest News for {symbol}")
    
    try:
        news_data = get_stock_news(symbol)
        
        if news_data:
            for article in news_data[:10]:  # Show top 10 articles
                with st.container():
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader(article['title'])
                        st.write(article['summary'])
                        st.caption(f"Published: {article['published']}")
                        if article['link']:
                            st.markdown(f"[Read more]({article['link']})")
                    
                    with col2:
                        if article.get('image'):
                            st.image(article['image'], width=200)
                    
                    st.divider()
        else:
            st.info("No news articles found for this symbol.")
    
    except Exception as e:
        st.error(f"Error loading news: {str(e)}")

if __name__ == "__main__":
    main()