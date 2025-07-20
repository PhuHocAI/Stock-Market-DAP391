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
    
    # Add custom CSS for better styling - Light Theme
    st.markdown("""
    <style>
    .chatbot-container {
        border: none;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 50%, #ffffff 100%);
        margin: 15px 0;
        overflow: hidden;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(0,0,0,0.05);
    }

    .chatbot-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem 1.5rem;
        border-radius: 20px 20px 0 0;
        position: relative;
        overflow: hidden;
    }
    
    .chatbot-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .chatbot-header h4 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: 700;
        color: #ffffff;
        text-shadow: 0 2px 4px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .chatbot-header small {
        opacity: 0.95;
        font-size: 1rem;
        color: #ffffff;
        text-shadow: 0 1px 2px rgba(0,0,0,0.2);
        position: relative;
        z-index: 1;
    }
    
    .chat-messages {
        padding: 1.5rem;
        max-height: 450px;
        overflow-y: auto;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        color: #2c3e50;
    }

    .user-message {
        text-align: right;
        margin: 1rem 0;
    }
    
    .user-message .message-bubble {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        display: inline-block;
        max-width: 70%;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
    }
    
    .user-message .message-bubble::after {
        content: '';
        position: absolute;
        bottom: 0;
        right: -8px;
        width: 0;
        height: 0;
        border: 8px solid transparent;
        border-left-color: #764ba2;
        border-bottom: none;
        border-right: none;
    }
    
    .assistant-message {
        text-align: left;
        margin: 1rem 0;
    }
    
    .assistant-message .message-bubble {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        display: inline-block;
        max-width: 70%;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
        position: relative;
    }
    
    .assistant-message .message-bubble::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: -8px;
        width: 0;
        height: 0;
        border: 8px solid transparent;
        border-right-color: #e9ecef;
        border-bottom: none;
        border-left: none;
    }
    

    
    .stForm {
        background: transparent;
        padding: 0;
    }
    
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid rgba(0,0,0,0.1);
        padding: 1.2rem 1.8rem;
        font-size: 1.2rem;
        background: rgba(255,255,255,0.9);
        color: #2c3e50;
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1), inset 0 2px 4px rgba(0,0,0,0.05);
        background: rgba(255,255,255,1);
        transform: translateY(-2px);
    }
    
    .stTextInput > div > div > input::placeholder {
        color: rgba(44, 62, 80, 0.6);
        font-style: italic;
    }
    
    .stButton > button {
        border-radius: 25px;
        border: none;
        padding: 1.2rem 2.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        text-transform: uppercase;
        letter-spacing: 1px;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }
    
    .stButton > button:hover::before {
        left: 100%;
    }
    
    .stButton > button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button[data-testid="baseButton-primary"]:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
        background: linear-gradient(135deg, #7c8ff0 0%, #8a5bb8 100%);
    }
    
    .stButton > button:last-child {
        background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
        color: #2c3e50;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        border: 1px solid rgba(0,0,0,0.05);
    }
      
    .stButton > button:last-child:hover {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        transform: translateY(-3px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.15);
        border-color: rgba(0,0,0,0.1);
    }
    
    .welcome-message {
        text-align: center;
        padding: 3rem 2rem;
        color: #2c3e50;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.05) 0%, rgba(118, 75, 162, 0.03) 100%);
        border-radius: 20px;
        margin: 1.5rem;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        border: 1px solid rgba(102, 126, 234, 0.1);
        backdrop-filter: blur(10px);
    }
    
    .welcome-message h5 {
        color: #2c3e50;
        margin-bottom: 1.5rem;
        font-size: 1.5rem;
        font-weight: 700;
        text-shadow: 0 1px 2px rgba(0,0,0,0.1);
    }
    
    .welcome-message p {
        color: #34495e;
        font-size: 1.1rem;
        line-height: 1.6;
    }
    
    .feature-list {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
        margin: 2rem 0;
    }
    
    .feature-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 1.2rem;
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.08) 0%, rgba(118, 75, 162, 0.05) 100%);
        border-radius: 15px;
        font-size: 1rem;
        color: #2c3e50;
        border: 1px solid rgba(102, 126, 234, 0.1);
        transition: all 0.3s ease;
        cursor: pointer;
        backdrop-filter: blur(10px);
    }
    
    .feature-item:hover {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.1) 100%);
        border-color: rgba(102, 126, 234, 0.3);
        transform: translateX(10px);
        box-shadow: 0 4px 20px rgba(102, 126, 234, 0.2);
    }
    
    .feature-item .icon {
        font-size: 1.5rem;
        min-width: 30px;
        text-align: center;
    }
    
    /* Scrollbar styling */
    .chat-messages::-webkit-scrollbar {
        width: 8px;
    }
    
    .chat-messages::-webkit-scrollbar-track {
        background: rgba(0,0,0,0.05);
        border-radius: 4px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 4px;
    }
    
    .chat-messages::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #7c8ff0 0%, #8a5bb8 100%);
    }

    div[data-testid="stForm"] div[data-testid="stHorizontalBlock"] {
        gap: 0px;
    }

    div[data-testid="stHorizontalBlock"] > div:first-child .stTextInput input {
        border-radius: 25px 0 0 25px;
    }

    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton button {
        border-radius: 0;
    }

    div[data-testid="stHorizontalBlock"] > div:last-child .stButton button {
        border-radius: 0 25px 25px 0;
        border-left: 1px solid #ccc;
    }
    div[data-testid="stHorizontalBlock"] > div:last-child .stButton button {
        border-radius: 0 25px 25px 0;
        border-left: 1px solid #ccc;
    }
    div[data-testid="stFormSubmitButtonTooltip"] {
        display: none !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Chatbot container
    with st.container():
        st.markdown('<div class="chatbot-container" id="chatbot">', unsafe_allow_html=True)
        
        # Chatbot header
        st.markdown("""
        <div class="chatbot-header">
            <h4>📈 Stock Assistant</h4>
            <small>Ask me about stocks, trading, or market analysis!</small>
        </div>
        """, unsafe_allow_html=True)
        
        # Chat messages container
        chat_container = st.container()
        
        with chat_container:
            # Display welcome message if no messages
            if not st.session_state.chatbot_messages:
                st.markdown("""
                <div class="welcome-message">
                    <h5>👋 Welcome to Stock Assistant!</h5>
                    <p>I'm your AI-powered stock market assistant. I can help you with:</p>
                    <div class="feature-list">
                        <div class="feature-item">📊 Technical Analysis (RSI, MACD, Bollinger Bands, Moving Averages)</div>
                        <div class="feature-item">📈 Chart Patterns and Trends</div>
                        <div class="feature-item">💹 Trading Strategies and Concepts</div>
                        <div class="feature-item">📰 Market Analysis and Interpretation</div>
                        <div class="feature-item">🔍 Stock Research Fundamentals</div>
                    </div>
                    <p><strong>Note:</strong> I provide educational information only, not financial advice. Always do your own research!</p>
                </div>
                """, unsafe_allow_html=True)
            
            # Display chat messages
            if st.session_state.chatbot_messages:
                st.markdown('<div class="chat-messages">', unsafe_allow_html=True)
                for message in st.session_state.chatbot_messages:
                    if message["role"] == "user":
                        st.markdown(f"""
                        <div class="user-message">
                            <div class="message-bubble">{message["content"]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div class="assistant-message">
                            <div class="message-bubble">{message["content"]}</div>
                        </div>
                        """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
        
        # Chat input using form to avoid session state issues
        # Chat input using form to avoid session state issues
        with st.form(key="chat_form", clear_on_submit=True):
            # Create columns FIRST, with the input field taking most of the space
            col1, col2, col3 = st.columns([6, 1, 1], gap="small") 

            with col1:
                user_input = st.text_input(
                    "Type your message...",
                    placeholder="Ask about stocks, market trends,...",
                    label_visibility="collapsed" # Hide the label "Type your message..."
                )
            
            with col2:
                send_button = st.form_submit_button("Send", type="primary", use_container_width=True)

            with col3:
                clear_button = st.form_submit_button("Clear", use_container_width=True)
        
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
        GEMINI_API_KEY = "AIzaSyBsfGyJSpoGrZjWeE1MQF2MaJbKa0F-i74"  # Replace with your actual API key
        
        if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
            ai_response = get_fallback_response(user_input)
        else:
            try:
                from google.generativeai.client import configure
                from google.generativeai.generative_models import GenerativeModel
                configure(api_key=GEMINI_API_KEY)
                model = GenerativeModel(model_name="gemini-1.5-flash")
                
                # Create context-aware prompt
                system_prompt = """
                You are a helpful stock market and trading assistant. You provide accurate, 
                helpful information about stocks, trading strategies, market analysis, and 
                financial concepts. Keep responses concise but informative. Always remind 
                users that this is not financial advice and they should do their own research 
                or consult with financial professionals.
                
                IMPORTANT: The user may ask questions in Vietnamese. Please respond in the same 
                language they use. If they ask in Vietnamese, respond in Vietnamese. If they 
                ask in English, respond in English. Be helpful and educational in both languages.
                
                Current context: You are integrated into a stock market dashboard application 
                that shows real-time stock data, technical indicators, and news.
                """
                
                full_prompt = f"{system_prompt}\n\nUser question: {user_input}"
                
                response = model.generate_content(full_prompt)
                ai_response = response.text
            except Exception as api_error:
                ai_response = get_fallback_response(user_input)
        
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
    
    # Rerun to refresh the chat
    st.rerun()

def get_fallback_response(user_input):
    """
    Provide fallback responses when API is not configured
    """
    user_input_lower = user_input.lower()
    
    # Check if user is asking in Vietnamese
    vietnamese_keywords = [
        'xin chào', 'chào', 'hello', 'hi', 'hey', 
        'trading', 'giao dịch', 'chứng khoán', 'cổ phiếu',
        'rsi', 'macd', 'bollinger', 'bands', 'dải', 'trung bình động',
        'sma', 'ema', 'volume', 'khối lượng', 'support', 'resistance',
        'hỗ trợ', 'kháng cự', 'giải thích', 'là gì', 'thế nào'
    ]
    is_vietnamese = any(word in user_input_lower for word in vietnamese_keywords)
    
    # Simple keyword-based responses
    if any(word in user_input_lower for word in ['hello', 'hi', 'hey', 'xin chào', 'chào']):
        if is_vietnamese:
            return "Xin chào! Tôi là trợ lý thị trường chứng khoán của bạn. Tôi có thể giúp bạn với các câu hỏi về cổ phiếu, giao dịch và phân tích thị trường. Tôi có thể hỗ trợ bạn như thế nào hôm nay?"
        else:
            return "Hello! I'm your stock market assistant. I can help you with questions about stocks, trading, and market analysis. How can I assist you today?"
    
    elif any(word in user_input_lower for word in ['rsi', 'relative strength']):
        if is_vietnamese:
            return """RSI (Chỉ số Sức mạnh Tương đối) là một bộ dao động động lượng đo tốc độ và sự thay đổi của chuyển động giá.
            
            - RSI dao động từ 0 đến 100
            - Trên 70: Có thể quá mua (tín hiệu bán)
            - Dưới 30: Có thể quá bán (tín hiệu mua)
            - RSI giúp xác định sự đảo chiều xu hướng
            
            Lưu ý: Đây không phải là lời khuyên tài chính. Luôn tự nghiên cứu!"""
        else:
            return """RSI (Relative Strength Index) is a momentum oscillator that measures the speed and change of price movements. 
            
            - RSI ranges from 0 to 100
            - Above 70: Potentially overbought (sell signal)
            - Below 30: Potentially oversold (buy signal)
            - RSI helps identify trend reversals
            
            Remember: This is not financial advice. Always do your own research!"""
    
    elif any(word in user_input_lower for word in ['macd']):
        if is_vietnamese:
            return """MACD (Trung bình Động Hội tụ Phân kỳ) là chỉ báo động lượng theo xu hướng.
            
            - Đường MACD: EMA 12 ngày trừ EMA 26 ngày
            - Đường Tín hiệu: EMA 9 ngày của đường MACD
            - Biểu đồ: Đường MACD trừ Đường Tín hiệu
            
            Tín hiệu:
            - MACD cắt lên trên Tín hiệu: Tiềm năng mua
            - MACD cắt xuống dưới Tín hiệu: Tiềm năng bán
            
            Đây là thông tin giáo dục, không phải lời khuyên tài chính!"""
        else:
            return """MACD (Moving Average Convergence Divergence) is a trend-following momentum indicator.
            
            - MACD Line: 12-day EMA minus 26-day EMA
            - Signal Line: 9-day EMA of MACD line
            - Histogram: MACD line minus Signal line
            
            Signals:
            - MACD crosses above Signal: Potential buy
            - MACD crosses below Signal: Potential sell
            
            This is educational information, not financial advice!"""
    
    elif any(word in user_input_lower for word in ['bollinger', 'bands']):
        if is_vietnamese:
            return """Dải Bollinger bao gồm ba đường:
            
            - Dải Giữa: Trung bình động đơn giản 20 ngày
            - Dải Trên: Dải Giữa + (2 × Độ lệch chuẩn)
            - Dải Dưới: Dải Giữa - (2 × Độ lệch chuẩn)
            
            Cách sử dụng:
            - Giá chạm dải trên: Có thể quá mua
            - Giá chạm dải dưới: Có thể quá bán
            - Dải thu hẹp: Biến động thấp, tiềm năng breakout
            
            Luôn kết hợp với các chỉ báo khác để phân tích tốt hơn!"""
        else:
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
        if is_vietnamese:
            return """Trung bình động làm mượt dữ liệu giá để xác định xu hướng:
            
            **Trung bình động đơn giản (SMA):**
            - Trung bình của giá đóng cửa trong N chu kỳ
            - Trọng số bằng nhau cho tất cả chu kỳ
            
            **Trung bình động hàm mũ (EMA):**
            - Trọng số cao hơn cho giá gần đây
            - Phản ứng nhanh hơn với thay đổi giá
            
            Chu kỳ phổ biến: 20, 50, 200 ngày
            Golden Cross: MA 50 ngày cắt lên trên MA 200 ngày (tăng giá)
            Death Cross: MA 50 ngày cắt xuống dưới MA 200 ngày (giảm giá)"""
        else:
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
        if is_vietnamese:
            return """Khối lượng là số lượng cổ phiếu được giao dịch trong một khoảng thời gian:
            
            - Khối lượng cao + giá tăng: Tín hiệu tăng giá mạnh
            - Khối lượng cao + giá giảm: Tín hiệu giảm giá mạnh
            - Khối lượng thấp: Niềm tin yếu trong chuyển động giá
            - Khối lượng đi trước giá: Khối lượng thường tăng trước khi có chuyển động giá lớn
            
            Chỉ báo khối lượng giúp xác nhận chuyển động giá và xác định sự đảo chiều tiềm năng."""
        else:
            return """Volume is the number of shares traded in a given period:
            
            - High volume + price increase: Strong bullish signal
            - High volume + price decrease: Strong bearish signal
            - Low volume: Weak conviction in price movement
            - Volume precedes price: Volume often increases before major price moves
            
            Volume indicators help confirm price movements and identify potential reversals."""
    
    elif any(word in user_input_lower for word in ['support', 'resistance']):
        if is_vietnamese:
            return """Hỗ trợ và Kháng cự là các khái niệm phân tích kỹ thuật quan trọng:
            
            **Hỗ trợ:** Mức giá nơi lực mua đủ mạnh để ngăn giá giảm thêm
            **Kháng cự:** Mức giá nơi áp lực bán ngăn giá tăng thêm
            
            Điểm quan trọng:
            - Kháng cự trước đó có thể trở thành hỗ trợ mới (và ngược lại)
            - Nhiều lần chạm làm cho mức mạnh hơn
            - Khối lượng xác nhận breakout
            - Số tròn thường hoạt động như mức tâm lý
            
            Sử dụng các mức này để lập kế hoạch vào/lệnh!"""
        else:
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
        if is_vietnamese:
            return """Tôi là trợ lý thị trường chứng khoán được hỗ trợ bởi AI. Tôi có thể giúp bạn với:
            
            📊 Phân tích Kỹ thuật (RSI, MACD, Dải Bollinger, Trung bình động)
            📈 Mẫu biểu đồ và Xu hướng
            💹 Chiến lược Giao dịch và Khái niệm
            📰 Phân tích Thị trường và Giải thích
            🔍 Nghiên cứu Cổ phiếu Cơ bản
            
            Lưu ý: Tôi chỉ cung cấp thông tin giáo dục, không phải lời khuyên tài chính. 
            Luôn tự nghiên cứu và cân nhắc tham khảo ý kiến chuyên gia tài chính.
            
            Bạn muốn tìm hiểu về điều gì?"""
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