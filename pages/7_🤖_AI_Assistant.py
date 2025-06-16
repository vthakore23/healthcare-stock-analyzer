import streamlit as st
import openai
import pandas as pd
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json
import requests

# Page configuration
st.set_page_config(
    page_title="AI Assistant - Healthcare Analyzer | June 2025",
    page_icon="🤖",
    layout="wide"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .ai-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        max-height: 600px;
        overflow-y: auto;
    }
    
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 4px 18px;
        margin: 1rem 0;
        margin-left: 20%;
        box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
    }
    
    .ai-message {
        background: #f8fafc;
        color: #1e293b;
        padding: 1rem 1.5rem;
        border-radius: 18px 18px 18px 4px;
        margin: 1rem 0;
        margin-right: 20%;
        border-left: 4px solid #667eea;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    .prompt-suggestion {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 12px;
        margin: 0.5rem;
        cursor: pointer;
        transition: all 0.3s ease;
        border: 1px solid #cbd5e1;
    }
    
    .prompt-suggestion:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
        border-color: #667eea;
    }
    
    .typing-indicator {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        color: #667eea;
        font-style: italic;
    }
    
    .typing-dots {
        display: flex;
        gap: 4px;
    }
    
    .typing-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #667eea;
        animation: typing 1.4s infinite ease-in-out;
    }
    
    .typing-dot:nth-child(1) { animation-delay: -0.32s; }
    .typing-dot:nth-child(2) { animation-delay: -0.16s; }
    
    @keyframes typing {
        0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
        40% { transform: scale(1); opacity: 1; }
    }
    
    .ai-badge {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        display: inline-block;
        margin-bottom: 1rem;
    }
    
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .feature-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

class StockAnalysisAI:
    """AI Assistant specialized for stock analysis and healthcare investing"""
    
    def __init__(self):
        self.client = None
        self.setup_openai()
        
    def setup_openai(self):
        """Setup OpenAI client with API key"""
        api_key = st.secrets.get("OPENAI_API_KEY") if hasattr(st, 'secrets') else None
        
        if not api_key:
            # For demo purposes, we'll use a placeholder
            st.warning("⚠️ OpenAI API key not configured. Using demo mode.")
            return
        
        try:
            self.client = openai.OpenAI(api_key=api_key)
        except Exception as e:
            st.error(f"Failed to initialize OpenAI client: {e}")
    
    def get_stock_context(self, symbol):
        """Get current stock data for context"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1y")
            
            if hist.empty:
                return None
                
            current_price = hist['Close'][-1]
            change_1d = ((current_price - hist['Close'][-2]) / hist['Close'][-2] * 100) if len(hist) > 1 else 0
            
            context = {
                'symbol': symbol,
                'company': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'price': current_price,
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'change_1d': change_1d,
                'volume': info.get('volume', 0),
                'beta': info.get('beta', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'fifty_two_week_high': info.get('fiftyTwoWeekHigh', 0),
                'fifty_two_week_low': info.get('fiftyTwoWeekLow', 0)
            }
            
            return context
            
        except Exception as e:
            return None
    
    def generate_response(self, query, stock_context=None):
        """Generate AI response for stock analysis queries"""
        
        if not self.client:
            # Demo response for when API is not available
            return self.generate_demo_response(query, stock_context)
        
        try:
            # Build context-aware prompt
            system_prompt = """You are a professional stock analyst and healthcare investment expert. 
            You provide detailed, accurate, and actionable investment analysis. Your expertise includes:
            - Fundamental analysis (P/E ratios, revenue growth, profit margins)
            - Healthcare sector knowledge (FDA approvals, clinical trials, regulatory risks)
            - Technical analysis (support/resistance, momentum indicators)
            - Market trends and economic factors
            - Risk assessment and portfolio management
            
            Always provide specific, data-driven insights and mention key risks. 
            Keep responses professional but accessible."""
            
            user_prompt = query
            
            if stock_context:
                user_prompt += f"\n\nCurrent data for {stock_context['symbol']}:\n"
                user_prompt += f"Company: {stock_context['company']}\n"
                user_prompt += f"Sector: {stock_context['sector']}\n"
                user_prompt += f"Current Price: ${stock_context['price']:.2f}\n"
                user_prompt += f"Market Cap: ${stock_context['market_cap']/1e9:.1f}B\n"
                user_prompt += f"P/E Ratio: {stock_context['pe_ratio']:.1f}\n"
                user_prompt += f"1-Day Change: {stock_context['change_1d']:+.2f}%\n"
            
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            return f"I apologize, but I'm experiencing technical difficulties. Error: {str(e)}"
    
    def generate_demo_response(self, query, stock_context=None):
        """Generate demo responses when OpenAI API is not available"""
        
        query_lower = query.lower()
        
        if stock_context:
            symbol = stock_context['symbol']
            company = stock_context['company']
            price = stock_context['price']
            change = stock_context['change_1d']
            
            if 'analyze' in query_lower or 'analysis' in query_lower:
                return f"""**Analysis for {symbol} - {company}**

**Current Situation:**
• Trading at ${price:.2f} ({change:+.2f}% today)
• Market Cap: ${stock_context['market_cap']/1e9:.1f}B
• P/E Ratio: {stock_context['pe_ratio']:.1f}

**Key Observations:**
• The stock is currently {'above' if change > 0 else 'below'} yesterday's close
• Healthcare sector positioning appears {'strong' if stock_context['sector'] == 'Healthcare' else 'diversified'}
• Technical momentum is {'positive' if change > 0 else 'negative'} in the short term

**Investment Considerations:**
• Consider the broader healthcare regulatory environment
• Monitor upcoming FDA catalysts if applicable
• Evaluate valuation relative to growth prospects
• Assess portfolio allocation and risk tolerance

*Note: This is a demo response. Connect OpenAI API for detailed analysis.*"""
            
            elif 'buy' in query_lower or 'sell' in query_lower:
                return f"""**Investment Perspective on {symbol}**

**Current Metrics:**
• Price: ${price:.2f}
• Recent Performance: {change:+.2f}% (1-day)
• Valuation: P/E {stock_context['pe_ratio']:.1f}

**Factors to Consider:**
• **Fundamental Strength:** Evaluate earnings growth, revenue trends, and competitive position
• **Sector Dynamics:** Healthcare regulations, patent cliffs, clinical trial outcomes
• **Technical Setup:** Support/resistance levels, volume patterns, momentum indicators
• **Risk Management:** Position sizing, portfolio diversification, stop-loss levels

**Recommendation Framework:**
• Strong fundamentals + positive technicals = Potential buy consideration
• Weak fundamentals or negative trends = Exercise caution
• Always consider your risk tolerance and investment timeline

*Demo mode active. Enable OpenAI API for personalized recommendations.*"""
        
        else:
            if 'healthcare' in query_lower:
                return """**Healthcare Sector Overview (June 2025)**

**Key Trends:**
• AI-driven drug discovery accelerating development timelines
• Personalized medicine and genomics gaining traction
• Regulatory environment becoming more streamlined
• ESG factors increasingly important for investors

**Investment Opportunities:**
• Biotech companies with strong pipelines
• Medical technology firms with innovative solutions
• Healthcare services with recurring revenue models
• Companies benefiting from aging demographics

**Risk Factors:**
• Regulatory approval uncertainties
• Patent cliff exposures
• Healthcare policy changes
• Clinical trial failures

*Connect OpenAI for detailed sector analysis and stock recommendations.*"""
            
            elif 'market' in query_lower:
                return """**Market Analysis (June 2025)**

**Current Environment:**
• Fed policy stabilizing after 2024-2025 cycle
• Healthcare benefiting from demographic tailwinds
• Technology integration driving efficiency gains
• Global markets showing resilience

**Key Considerations:**
• Interest rate environment affecting valuations
• Geopolitical factors influencing supply chains
• Innovation cycles creating opportunities
• ESG mandates reshaping investment flows

**Strategy Recommendations:**
• Diversification across healthcare subsectors
• Focus on quality companies with strong moats
• Consider both growth and value opportunities
• Monitor regulatory and policy developments

*Demo response. Enable AI for real-time market insights.*"""
            
            else:
                return """**Stock Analysis Assistant Ready**

I'm here to help with your investment analysis questions! I can provide insights on:

• **Individual Stock Analysis:** Fundamental metrics, technical patterns, risk assessment
• **Healthcare Sector Trends:** FDA approvals, clinical trials, regulatory changes
• **Market Analysis:** Trends, opportunities, risk factors
• **Portfolio Strategy:** Diversification, allocation, risk management

**Sample Questions:**
• "Analyze MRNA stock fundamentals"
• "What are the healthcare investment trends in 2025?"
• "Should I buy or sell Pfizer stock?"
• "How do I evaluate biotech companies?"

*Note: Currently in demo mode. Connect OpenAI API for detailed AI-powered analysis.*"""
        
        return "I'm here to help with your investment questions! Please ask me about stocks, healthcare trends, or market analysis."

def main():
    st.markdown("""
    <div class="ai-header">
        <h1>🤖 AI Investment Assistant</h1>
        <p style="font-size: 1.3rem;">ChatGPT-powered stock analysis and healthcare investment insights</p>
        <span class="ai-badge">🧠 POWERED BY GPT-4 • 📊 REAL-TIME DATA • 🏥 HEALTHCARE SPECIALIST</span>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize AI assistant
    if 'ai_assistant' not in st.session_state:
        st.session_state.ai_assistant = StockAnalysisAI()
    
    # Initialize chat history
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        show_chat_interface()
    
    with col2:
        show_quick_actions()

def show_chat_interface():
    """Show the main chat interface"""
    st.markdown("### 💬 Chat with AI Assistant")
    
    # Chat container
    chat_container = st.container()
    
    with chat_container:
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        
        # Display chat history
        if st.session_state.chat_history:
            for message in st.session_state.chat_history:
                if message['role'] == 'user':
                    st.markdown(f'<div class="user-message">👤 {message["content"]}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="ai-message">🤖 {message["content"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="ai-message">
                🤖 Welcome! I'm your AI investment assistant specialized in stock analysis and healthcare investing. 
                How can I help you today?
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Input area
    st.markdown("---")
    
    # Stock context input
    col1, col2 = st.columns([3, 1])
    
    with col1:
        stock_symbol = st.text_input("Stock Symbol (optional):", placeholder="e.g., MRNA, PFE, NVDA")
    
    with col2:
        include_data = st.checkbox("Include real-time data", value=True)
    
    # Chat input
    user_input = st.text_area(
        "Your Question:",
        placeholder="Ask me about stock analysis, healthcare trends, market insights, or investment strategies...",
        height=100
    )
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🚀 Send Message", type="primary", use_container_width=True):
            if user_input.strip():
                process_user_message(user_input, stock_symbol if include_data else None)
    
    with col2:
        if st.button("🔄 Clear Chat", use_container_width=True):
            st.session_state.chat_history = []
            st.rerun()
    
    with col3:
        if st.button("📊 Get Market Update", use_container_width=True):
            process_user_message("What's happening in the markets today?", None)

def show_quick_actions():
    """Show quick action buttons and suggestions"""
    st.markdown("### ⚡ Quick Actions")
    
    # Suggested prompts
    st.markdown("#### 💡 Suggested Questions")
    
    suggestions = [
        "Analyze the healthcare sector trends",
        "Compare biotech vs pharma investments",
        "What are the top healthcare stocks in 2025?",
        "Explain FDA approval process impact on stocks",
        "How to evaluate a biotech company?",
        "Market sentiment for healthcare stocks",
        "Investment risks in pharmaceutical companies",
        "AI impact on drug discovery stocks"
    ]
    
    for suggestion in suggestions:
        if st.button(f"💭 {suggestion}", key=f"suggestion_{suggestion[:20]}", use_container_width=True):
            process_user_message(suggestion, None)
    
    # Quick stock analysis
    st.markdown("---")
    st.markdown("#### 🔍 Quick Stock Analysis")
    
    popular_stocks = {
        "🧬 MRNA": "MRNA",
        "💊 PFE": "PFE", 
        "🏥 UNH": "UNH",
        "🔬 REGN": "REGN",
        "💉 LLY": "LLY",
        "🧪 VRTX": "VRTX"
    }
    
    for display_name, symbol in popular_stocks.items():
        if st.button(f"{display_name} Analysis", key=f"stock_{symbol}", use_container_width=True):
            process_user_message(f"Provide a detailed analysis of {symbol} stock", symbol)
    
    # Features showcase
    st.markdown("---")
    st.markdown("#### 🌟 AI Capabilities")
    
    capabilities = [
        "📈 Technical Analysis",
        "📊 Fundamental Analysis", 
        "🏥 Healthcare Expertise",
        "📰 Market News Analysis",
        "💰 Risk Assessment",
        "🎯 Investment Strategy"
    ]
    
    for capability in capabilities:
        st.markdown(f"""
        <div class="feature-card">
            <strong>{capability}</strong>
        </div>
        """, unsafe_allow_html=True)

def process_user_message(user_input, stock_symbol=None):
    """Process user message and generate AI response"""
    
    # Add user message to history
    st.session_state.chat_history.append({
        'role': 'user',
        'content': user_input,
        'timestamp': datetime.now()
    })
    
    # Show typing indicator
    with st.spinner("🤖 AI is analyzing..."):
        # Get stock context if symbol provided
        stock_context = None
        if stock_symbol and stock_symbol.strip():
            stock_context = st.session_state.ai_assistant.get_stock_context(stock_symbol.upper().strip())
        
        # Generate AI response
        ai_response = st.session_state.ai_assistant.generate_response(user_input, stock_context)
        
        # Add AI response to history
        st.session_state.chat_history.append({
            'role': 'assistant',
            'content': ai_response,
            'timestamp': datetime.now()
        })
    
    # Rerun to update chat display
    st.rerun()

def show_typing_indicator():
    """Show typing indicator animation"""
    st.markdown("""
    <div class="typing-indicator">
        🤖 AI is thinking
        <div class="typing-dots">
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
            <div class="typing-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 