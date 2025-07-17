import streamlit as st
import google.generativeai as genai
from datetime import datetime
import json

def render_chatbot():
    """
    Render the chatbot interface
    """
    # Initialize session state for chatbot
    if 'chatbot_messages' not in st.session_state:
        st.session_state.chatbot_messages = []
    
    if 'chatbot_visible' not in st.session_state:
        st.session_state.chatbot_visible = False
    
    # Chatbot toggle button
    st.markdown("""
    <script>
    function toggleChatbot() {
        var chatbot = document.querySelector('.chatbot-container');
        if (chatbot.style.display === 'none' || chatbot.style.display === '') {
            chatbot.style.display = 'block';
        } else {
            chatbot.style.display = 'none';
        }
    }
    </script>
    
    <button class="chatbot-toggle" onclick="toggleChatbot()">💬</button>
    """, unsafe_allow_html=True)
    
    # Chatbot container
    with st.container():
        st.markdown('<div class="chatbot-container" id="chatbot">', unsafe_allow_html=True)
        
        # Chatbot header
        st.markdown("""
        <div style="background: #1f77b4; color: white; padding: 1rem; border-radius: 10px 10px 0 0;">
            <h4 style="margin: 0;">📈 Stock Assistant</h4>
            <small>Ask me about stocks, trading, or market analysis!</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat messages container
        chat_container = st.container()
        
        with chat_container:
            # Display chat messages
            for message in st.session_state.chatbot_messages:
                if message["role"] == "user":
                    st.markdown(f"""
                    <div style="text-align: right; margin: 0.5rem 0;">
                        <div style="background: #e3f2fd; padding: 0.5rem 1rem; border-radius: 15px 15px 5px 15px; display: inline-block; max-width: 80%;">
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="text-align: left; margin: 0.5rem 0;">
                        <div style="background: #f5f5f5; padding: 0.5rem 1rem; border-radius: 15px 15px 15px 5px; display: inline-block; max-width: 80%;">
                            {message["content"]}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Chat input
        user_input = st.text_input(
            "Type your message...",
            key="chatbot_input",
            placeholder="Ask about stocks, market trends, or trading strategies..."
        )
        
        col1, col2 = st.columns([3, 1])
        with col1:
            send_button = st.button("Send", key="send_chatbot")
        with col2:
            clear_button = st.button("Clear", key="clear_chatbot")
        
        if send_button and user_input:
            handle_chatbot_message(user_input)
        
        if clear_button:
            st.session_state.chatbot_messages = []
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

def handle_chatbot_message(user_input):
    """
    Handle user message and generate AI response
    """
    # Add user message to chat
    st.session_state.chatbot_messages.append({
        "role": "user",
        "content": user_input,
        "timestamp": datetime.now()
    })
    
    try:
        # Configure Gemini API (you need to set your API key)
        # Get your API key from: https://makersuite.google.com/app/apikey
        GEMINI_API_KEY = "YOUR_GEMINI_API_KEY_HERE"  # Replace with your actual API key
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            response = get_fallback_response(user_input)
        else:
            genai.configure(api_key=GEMINI_API_KEY)
            model = genai.GenerativeModel('gemini-pro')
            
            # Create context-aware prompt
            system_prompt = """
            You are a helpful stock market and trading assistant. You provide accurate, 
            helpful information about stocks, trading strategies, market analysis, and 
            financial concepts. Keep responses concise but informative. Always remind 
            users that this is not financial advice and they should do their own research 
            or consult with financial professionals.
            
            Current context: You are integrated into a stock market dashboard application 
            that shows real-time stock data, technical indicators, and news.
            """
            
            full_prompt = f"{system_prompt}\n\nUser question: {user_input}"
            
            response = model.generate_content(full_prompt)
            ai_response = response.text
        
        # Add AI response to chat
        st.session_state.chatbot_messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now()
        })
        
    except Exception as e:
        error_response = f"I'm sorry, I encountered an error: {str(e)}. Please try again or rephrase your question."
        st.session_state.chatbot_messages.append({
            "role": "assistant",
            "content": error_response,
            "timestamp": datetime.now()
        })
    
    # Clear input and rerun
    st.session_state.chatbot_input = ""
    st.rerun()

def get_fallback_response(user_input):
    """
    Provide fallback responses when API is not configured
    """
    user_input_lower = user_input.lower()
    
    # Simple keyword-based responses
    if any(word in user_input_lower for word in ['hello', 'hi', 'hey']):
        return "Hello! I'm your stock market assistant. I can help you with questions about stocks, trading, and market analysis. How can I assist you today?"
    
    elif any(word in user_input_lower for word in ['rsi', 'relative strength']):
        return """RSI (Relative Strength Index) is a momentum oscillator that measures the speed and change of price movements. 
        
        - RSI ranges from 0 to 100
        - Above 70: Potentially overbought (sell signal)
        - Below 30: Potentially oversold (buy signal)
        - RSI helps identify trend reversals
        
        Remember: This is not financial advice. Always do your own research!"""
    
    elif any(word in user_input_lower for word in ['macd']):
        return """MACD (Moving Average Convergence Divergence) is a trend-following momentum indicator.
        
        - MACD Line: 12-day EMA minus 26-day EMA
        - Signal Line: 9-day EMA of MACD line
        - Histogram: MACD line minus Signal line
        
        Signals:
        - MACD crosses above Signal: Potential buy
        - MACD crosses below Signal: Potential sell
        
        This is educational information, not financial advice!"""
    
    elif any(word in user_input_lower for word in ['bollinger', 'bands']):
        return """Bollinger Bands consist of three lines:
        
        - Middle Band: 20-day Simple Moving Average
        - Upper Band: Middle Band + (2 × Standard Deviation)
        - Lower Band: Middle Band - (2 × Standard Deviation)
        
        Usage:
        - Price touching upper band: Potentially overbought
        - Price touching lower band: Potentially oversold
        - Band squeeze: Low volatility, potential breakout
        
        Always combine with other indicators for better analysis!"""
    
    elif any(word in user_input_lower for word in ['moving average', 'sma', 'ema']):
        return """Moving Averages smooth out price data to identify trends:
        
        **Simple Moving Average (SMA):**
        - Average of closing prices over N periods
        - Equal weight to all periods
        
        **Exponential Moving Average (EMA):**
        - More weight to recent prices
        - Responds faster to price changes
        
        Common periods: 20, 50, 200 days
        Golden Cross: 50-day MA crosses above 200-day MA (bullish)
        Death Cross: 50-day MA crosses below 200-day MA (bearish)"""
    
    elif any(word in user_input_lower for word in ['volume']):
        return """Volume is the number of shares traded in a given period:
        
        - High volume + price increase: Strong bullish signal
        - High volume + price decrease: Strong bearish signal
        - Low volume: Weak conviction in price movement
        - Volume precedes price: Volume often increases before major price moves
        
        Volume indicators help confirm price movements and identify potential reversals."""
    
    elif any(word in user_input_lower for word in ['support', 'resistance']):
        return """Support and Resistance are key technical analysis concepts:
        
        **Support:** Price level where buying interest is strong enough to prevent further decline
        **Resistance:** Price level where selling pressure prevents further advance
        
        Key points:
        - Previous resistance can become new support (and vice versa)
        - Multiple touches make levels stronger
        - Volume confirms breakouts
        - Round numbers often act as psychological levels
        
        Use these levels for entry/exit planning!"""
    
    else:
        return """I'm a stock market assistant powered by AI. I can help you with:
        
        📊 Technical Analysis (RSI, MACD, Bollinger Bands, Moving Averages)
        📈 Chart Patterns and Trends
        💹 Trading Strategies and Concepts
        📰 Market Analysis and Interpretation
        🔍 Stock Research Fundamentals
        
        Please note: I provide educational information only, not financial advice. 
        Always do your own research and consider consulting with financial professionals.
        
        What would you like to learn about?"""

def get_stock_context_response(symbol, user_input):
    """
    Generate context-aware response based on current stock being viewed
    """
    context_prompt = f"""
    The user is currently viewing stock data for {symbol}. 
    They asked: {user_input}
    
    Provide a helpful response that takes into account they are looking at {symbol} 
    specifically, while still giving general educational information about their question.
    """
    
    return context_prompt