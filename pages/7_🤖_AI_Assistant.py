import streamlit as st
import openai
import yfinance as yf
import os

# Page configuration
st.set_page_config(
    page_title="AI Assistant - Healthcare Analyzer | June 2025",
    page_icon="🤖",
    layout="wide"
)

# Clean CSS styling
st.markdown("""
<style>
    .ai-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .chat-message {
        padding: 1rem 1.5rem;
        margin: 1rem 0;
        border-radius: 12px;
        border-left: 4px solid #667eea;
        background: #f8fafc;
    }
    
    .user-message {
        background: #e0e7ff;
        border-left-color: #3b82f6;
    }
    
    .capability-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
</style>
""", unsafe_allow_html=True)

def setup_openai():
    """Setup OpenAI client with proper error handling"""
    api_key = None
    
    # Try to get API key from secrets
    try:
        if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
            api_key = st.secrets["OPENAI_API_KEY"]
            if api_key:
                # Debug: Show first few characters
                st.caption(f"🔑 API Key loaded: {api_key[:7]}...")
    except Exception as e:
        st.warning(f"Could not access secrets: {e}")
    
    # Try environment variable as fallback
    if not api_key:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            st.caption("🔑 API Key loaded from environment")
    
    # Validate and create client
    if api_key and api_key != "your-openai-api-key-here" and api_key.startswith("sk-"):
        try:
            # Create client without testing connection immediately
            client = openai.OpenAI(api_key=api_key)
            return client, True
        except Exception as e:
            st.error(f"❌ OpenAI Client Error: {e}")
            return None, False
    else:
        if not api_key:
            st.warning("⚠️ OpenAI API key not found")
        elif not api_key.startswith("sk-"):
            st.warning("⚠️ Invalid OpenAI API key format")
        else:
            st.warning("⚠️ OpenAI API key not configured properly")
        
        st.info("""
        **To configure OpenAI:**
        1. Add your API key to `.streamlit/secrets.toml`
        2. Format: `OPENAI_API_KEY = "sk-proj-your-key"`
        3. Restart the application
        """)
        return None, False

def get_stock_data(ticker):
    """Get basic stock data for context"""
    if not ticker:
        return ""
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        context = f"""
Stock: {ticker.upper()}
Company: {info.get('longName', ticker)}
Current Price: ${info.get('regularMarketPrice', 0):.2f}
Market Cap: ${info.get('marketCap', 0)/1e9:.1f}B
Sector: {info.get('sector', 'N/A')}
Industry: {info.get('industry', 'N/A')}
P/E Ratio: {info.get('trailingPE', 'N/A')}
"""
        return context
    except:
        return f"Note: Could not fetch data for {ticker}"

def main():
    st.markdown("""
    <div class="ai-header">
        <h1>🤖 ChatGPT Investment Assistant</h1>
        <p style="font-size: 1.2rem;">GPT-4 powered stock analysis and healthcare investment insights</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Setup OpenAI
    client, api_available = setup_openai()
    
    if api_available:
        st.success("✅ GPT-4 Connected - Ready for Analysis!")
    else:
        st.info("💡 Add your OpenAI API key to `.streamlit/secrets.toml` to enable AI features")
    
    # Main interface
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 💬 Chat with GPT-4")
        
        # Company input
        company_ticker = st.text_input(
            "Company Ticker (Optional):",
            placeholder="e.g., MRNA, PFE, NVDA",
            help="Enter a stock ticker to include current data in the analysis"
        )
        
        # Prompt input
        user_prompt = st.text_area(
            "Your Question:",
            placeholder="Ask about stock analysis, market trends, investment strategies...",
            height=120,
            help="Be specific for better responses. Example: 'Analyze MRNA's competitive position in the mRNA vaccine market'"
        )
        
        # Send button
        if st.button("🚀 Send to GPT-4", type="primary", use_container_width=True):
            if user_prompt.strip():
                if client:
                    with st.spinner("🤖 GPT-4 is analyzing..."):
                        # Get stock context if ticker provided
                        stock_context = get_stock_data(company_ticker) if company_ticker else ""
                        
                        # Build full prompt
                        full_prompt = user_prompt
                        if stock_context:
                            full_prompt += f"\n\nCurrent stock data:\n{stock_context}"
                        
                        try:
                            response = client.chat.completions.create(
                                model="gpt-4",
                                messages=[
                                    {
                                        "role": "system", 
                                        "content": "You are a professional stock analyst and healthcare investment expert. Provide detailed, accurate analysis with specific insights about fundamentals, risks, and opportunities. Include key metrics and actionable recommendations."
                                    },
                                    {
                                        "role": "user", 
                                        "content": full_prompt
                                    }
                                ],
                                max_tokens=1500,
                                temperature=0.7
                            )
                            
                            # Display conversation
                            st.markdown('<div class="chat-message user-message">', unsafe_allow_html=True)
                            st.markdown(f"**You:** {user_prompt}")
                            if company_ticker:
                                st.caption(f"📊 Including data for {company_ticker.upper()}")
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                            st.markdown('<div class="chat-message">', unsafe_allow_html=True)
                            st.markdown("**GPT-4 Response:**")
                            st.markdown(response.choices[0].message.content)
                            st.markdown('</div>', unsafe_allow_html=True)
                            
                        except Exception as e:
                            st.error(f"❌ Error: {e}")
                else:
                    st.error("❌ OpenAI API not available. Please configure your API key.")
            else:
                st.warning("⚠️ Please enter a question")
    
    with col2:
        # AI Capabilities
        st.markdown("### 🧠 AI Capabilities")
        
        capabilities = [
            {
                "icon": "📊",
                "title": "Stock Analysis", 
                "desc": "Fundamental analysis, valuation metrics, financial health assessment"
            },
            {
                "icon": "🏥", 
                "title": "Healthcare Expertise",
                "desc": "FDA approvals, clinical trials, regulatory risks, biotech insights"
            },
            {
                "icon": "📈",
                "title": "Market Trends",
                "desc": "Sector analysis, competitive positioning, growth opportunities"
            },
            {
                "icon": "⚖️",
                "title": "Risk Assessment", 
                "desc": "Investment risks, portfolio implications, risk-reward analysis"
            },
            {
                "icon": "💡",
                "title": "Investment Strategy",
                "desc": "Buy/sell recommendations, timing analysis, portfolio allocation"
            }
        ]
        
        for cap in capabilities:
            st.markdown(f"""
            <div class="capability-card">
                <h4>{cap['icon']} {cap['title']}</h4>
                <p style="margin: 0; color: #64748b;">{cap['desc']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Quick Examples
        st.markdown("### 💭 Example Questions")
        
        examples = [
            "Analyze MRNA's competitive position",
            "Should I invest in biotech stocks now?", 
            "Compare Pfizer vs Moderna",
            "Healthcare sector outlook for 2025",
            "Risks in pharmaceutical investments",
            "How to evaluate a biotech company?",
            "FDA approval impact on stock prices",
            "Best healthcare ETFs to consider"
        ]
        
        for example in examples:
            if st.button(f"💬 {example}", key=f"ex_{hash(example)}", use_container_width=True):
                # Auto-fill the prompt
                st.session_state.example_prompt = example
                st.rerun()
        
        # Handle auto-filled prompts
        if 'example_prompt' in st.session_state:
            st.info(f"💡 Example copied: '{st.session_state.example_prompt}'")
            del st.session_state.example_prompt

if __name__ == "__main__":
    main() 