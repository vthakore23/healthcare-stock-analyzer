import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import time
import warnings
warnings.filterwarnings('ignore')

# Import custom modules
try:
    from medequity_utils.dynamic_scraper import HealthcareScraper
    from medequity_utils.healthcare_classifier import classify_healthcare_company
    from medequity_utils.metrics_calculator import calculate_healthcare_metrics
    from medequity_utils.data_validation import validate_data
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Healthcare Stock Analyzer",
    page_icon="💊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Enhanced CSS for ultra-modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        font-size: 4rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 2rem;
        background: linear-gradient(135deg, #ffffff 0%, #f8f9ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 4px 20px rgba(255,255,255,0.3);
        letter-spacing: -2px;
    }
    
    .metric-card {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        padding: 2rem;
        border-radius: 20px;
        margin: 1rem 0;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
        border: 1px solid rgba(255, 255, 255, 0.3);
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 4px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    .positive {
        color: #00C851;
        font-weight: bold;
    }
    
    .negative {
        color: #ff4444;
        font-weight: bold;
    }
    
    .neutral {
        color: #33b5e5;
        font-weight: bold;
    }
    
    .subsector-badge {
        background: linear-gradient(45deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 25px;
        font-size: 0.9rem;
        font-weight: bold;
        display: inline-block;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .score-display {
        font-size: 3.5rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .excellent-score { color: #00C851; }
    .good-score { color: #33b5e5; }
    .average-score { color: #ffbb33; }
    .poor-score { color: #ff4444; }
    
    .analysis-section {
        background: rgba(255, 255, 255, 0.98);
        backdrop-filter: blur(20px);
        padding: 3rem;
        border-radius: 24px;
        margin: 2rem 0;
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .analysis-section::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(102, 126, 234, 0.5), transparent);
    }
    
    .sidebar-section {
        background: rgba(255, 255, 255, 0.15);
        backdrop-filter: blur(20px);
        color: white;
        padding: 1.5rem;
        border-radius: 16px;
        margin: 1.5rem 0;
        border: 1px solid rgba(255, 255, 255, 0.2);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
    }
    
    .quick-stat {
        background-color: rgba(255,255,255,0.1);
        padding: 0.5rem;
        border-radius: 8px;
        margin: 0.25rem 0;
        backdrop-filter: blur(10px);
    }
    
    .pipeline-phase {
        background: linear-gradient(45deg, #ff6b6b, #ee5a52);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.8rem;
        margin: 0.2rem;
        display: inline-block;
    }
    
    .news-sentiment-positive {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .news-sentiment-negative {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .news-sentiment-neutral {
        background-color: #e2e3e5;
        border-left: 4px solid #6c757d;
        padding: 0.75rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .loading-animation {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 200px;
    }
    
    .financial-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .financial-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2.5rem;
        border-radius: 20px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.2);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .financial-card:hover {
        transform: translateY(-8px) scale(1.03);
        box-shadow: 0 20px 50px rgba(102, 126, 234, 0.4);
    }
    
    .financial-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: linear-gradient(45deg, transparent 30%, rgba(255,255,255,0.1) 50%, transparent 70%);
        transform: rotate(45deg);
        transition: all 0.6s;
        opacity: 0;
    }
    
    .financial-card:hover::before {
        opacity: 1;
        transform: rotate(45deg) translate(50%, 50%);
    }
    
    .glow-button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 1rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }
    
    .glow-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.5);
    }
    
    .floating-panel {
        background: rgba(255, 255, 255, 0.95);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2rem;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.1);
        border: 1px solid rgba(255, 255, 255, 0.3);
        margin: 2rem 0;
    }
    
    .neon-text {
        color: #667eea;
        text-shadow: 0 0 10px rgba(102, 126, 234, 0.5);
        font-weight: 700;
    }
    
    .pulse-animation {
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = HealthcareScraper()

if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []

if 'last_analysis' not in st.session_state:
    st.session_state.last_analysis = None

def main():
    # Header
    st.markdown('<h1 class="main-header">💊 Healthcare Stock Analyzer</h1>', unsafe_allow_html=True)
    st.markdown("### 🚀 Advanced Healthcare Investment Intelligence Platform")
    
    # Enhanced Sidebar
    with st.sidebar:
        st.markdown("""
        <div class="sidebar-section">
            <h2 style="text-align: center; margin-bottom: 1rem;">🎯 Quick Actions</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # Recent analyses
        if st.session_state.analysis_history:
            st.markdown("**📊 Recent Analyses:**")
            for i, ticker in enumerate(st.session_state.analysis_history[-5:]):
                if st.button(f"🔍 {ticker}", key=f"recent_{i}", use_container_width=True):
                    st.session_state.ticker_input = ticker
                    st.rerun()
        
        st.markdown("---")
        
        # Market Overview
        st.markdown("""
        <div class="sidebar-section">
            <h3 style="text-align: center;">📈 Market Pulse</h3>
        </div>
        """, unsafe_allow_html=True)
        
        display_market_overview()
        
        st.markdown("---")
        
        # Quick Tips
        st.markdown("""
        <div class="sidebar-section">
            <h3>💡 Pro Tips</h3>
            <ul style="font-size: 0.9rem;">
                <li>Try any stock ticker - not just healthcare!</li>
                <li>Healthcare stocks get detailed analysis</li>
                <li>Check the Healthcare Score for investment insights</li>
                <li>Explore pipeline data for biotech companies</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    # Main content
    create_main_interface()

def display_market_overview():
    """Display enhanced market overview"""
    try:
        # S&P 500
        with st.spinner("📊 Loading market data..."):
            spy_data = get_market_data("SPY", "S&P 500")
            xlv_data = get_market_data("XLV", "Healthcare ETF")
            ibb_data = get_market_data("IBB", "Biotech ETF")
        
        market_data = [spy_data, xlv_data, ibb_data]
        
        for data in market_data:
            if data:
                change_class = "positive" if data['change'] >= 0 else "negative"
                st.markdown(f"""
                <div class="quick-stat">
                    <strong>{data['name']}</strong><br>
                    <span class="{change_class}">${data['price']:.2f} ({data['change']:+.2f}%)</span>
                </div>
                """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown("📊 Market data temporarily unavailable")

def get_market_data(ticker: str, name: str) -> dict:
    """Get market data for a ticker"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        if info:
            price = info.get('regularMarketPrice', 0)
            change = info.get('regularMarketChangePercent', 0)
            return {'name': name, 'price': price, 'change': change}
    except:
        pass
    return None

def create_main_interface():
    """Create the main user interface"""
    
    # Input Section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker_input = st.text_input(
            "🔍 Enter any stock ticker symbol:",
            value=st.session_state.get('ticker_input', ''),
            placeholder="e.g., MRNA, PFE, AAPL, TSLA, or any stock symbol",
            help="Enter any valid stock ticker. Healthcare companies get comprehensive analysis!",
            key="main_ticker_input"
        ).upper().strip()
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)  # Spacing
        analyze_button = st.button("🚀 Analyze Now", type="primary", use_container_width=True)

    # Quick Access Buttons
    create_quick_access_section()
    
    # Analysis Section
    if ticker_input and (analyze_button or st.session_state.get('auto_analyze', False)):
        st.session_state.ticker_input = ticker_input
        analyze_stock_comprehensive(ticker_input)
    elif ticker_input:
        st.info("👆 Click 'Analyze Now' to start comprehensive analysis")
    else:
        create_welcome_section()

def create_quick_access_section():
    """Create quick access buttons for popular stocks"""
    st.markdown("### 🎯 Popular Healthcare Stocks")
    
    sample_categories = {
        "🧬 Biotech Giants": ["MRNA", "BNTX", "REGN", "VRTX", "BIIB"],
        "💊 Big Pharma": ["PFE", "JNJ", "MRK", "ABBV", "LLY"], 
        "🏥 Med Devices": ["MDT", "ABT", "SYK", "ISRG", "DXCM"],
        "🔬 Diagnostics": ["LH", "DGX", "ILMN", "TMO", "QGEN"]
    }
    
    for category, tickers in sample_categories.items():
        with st.expander(category, expanded=False):
            cols = st.columns(len(tickers))
            for i, ticker in enumerate(tickers):
                with cols[i]:
                    if st.button(ticker, key=f"quick_{ticker}", use_container_width=True):
                        st.session_state.ticker_input = ticker
                        st.session_state.auto_analyze = True
                        st.rerun()

def create_welcome_section():
    """Create welcome section with features"""
    st.markdown("""
    <div class="floating-panel">
        <h2 class="neon-text" style="text-align: center; font-size: 3rem; margin-bottom: 1rem;">
            🌟 Welcome to Healthcare Stock Analyzer
        </h2>
        <p style="text-align: center; font-size: 1.4rem; color: #666; font-weight: 300; margin-bottom: 2rem;">
            Your AI-powered healthcare investment intelligence platform for June 2025
        </p>
        <div style="text-align: center; margin: 2rem 0;">
            <div style="display: inline-block; padding: 1rem 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                        border-radius: 50px; color: white; font-weight: 600; box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);">
                ✨ Latest Data • Real-time Analysis • Professional Grade
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature highlights
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="financial-card">
            <h3>🔍 Universal Analysis</h3>
            <p>Analyze ANY stock ticker with intelligent healthcare detection</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="financial-card">
            <h3>🧬 Healthcare Intelligence</h3>
            <p>Advanced pipeline analysis, R&D metrics, and regulatory insights</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="financial-card">
            <h3>📊 Healthcare Score</h3>
            <p>Proprietary 0-100 scoring system for investment decisions</p>
        </div>
        """, unsafe_allow_html=True)

def analyze_stock_comprehensive(ticker: str):
    """Comprehensive stock analysis with enhanced UI"""
    
    # Add to history
    if ticker not in st.session_state.analysis_history:
        st.session_state.analysis_history.append(ticker)
        if len(st.session_state.analysis_history) > 10:
            st.session_state.analysis_history = st.session_state.analysis_history[-10:]
    
    # Progress indicator
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Phase 1: Data Collection
        status_text.text("🔍 Collecting market data...")
        progress_bar.progress(20)
        
        company_data = st.session_state.scraper.fetch_company_data(ticker)
        
        if 'error' in company_data:
            st.error(f"❌ Error analyzing {ticker}: {company_data['error']}")
            return
        
        progress_bar.progress(40)
        
        # Phase 2: Healthcare Classification
        status_text.text("🧬 Running healthcare classification...")
        classification = classify_healthcare_company(company_data)
        company_data['classification'] = classification
        progress_bar.progress(60)
        
        # Phase 3: Metrics Calculation
        status_text.text("📊 Calculating advanced metrics...")
        healthcare_metrics = calculate_healthcare_metrics(company_data)
        company_data['healthcare_metrics'] = healthcare_metrics
        progress_bar.progress(80)
        
        # Phase 4: Final Analysis
        status_text.text("🎯 Finalizing analysis...")
        progress_bar.progress(100)
        
        # Store for session
        st.session_state.last_analysis = company_data
        
        # Clear progress indicators
        progress_bar.empty()
        status_text.empty()
        
        # Display comprehensive results
        display_enhanced_analysis(company_data)
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def display_enhanced_analysis(data: dict):
    """Display enhanced analysis results"""
    
    ticker = data.get('ticker', 'Unknown')
    name = data.get('name', ticker)
    is_healthcare = data.get('is_healthcare', False)
    classification = data.get('classification')
    metrics = data.get('healthcare_metrics', {})
    
    # Header Section
    create_analysis_header(ticker, name, is_healthcare, classification, metrics, data)
    
    if not is_healthcare:
        st.warning(f"⚠️ {ticker} is not classified as a healthcare company. Showing basic financial analysis.")
        display_basic_financial_analysis(data)
        return
    
    # Healthcare Analysis Sections
    create_healthcare_score_section(metrics)
    create_financial_dashboard(data, metrics)
    create_healthcare_insights_section(data, classification)
    create_price_analysis_section(data)
    create_pipeline_section(data)
    create_news_sentiment_section(data)

def create_analysis_header(ticker: str, name: str, is_healthcare: bool, classification, metrics: dict, data: dict):
    """Create enhanced analysis header"""
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        st.markdown(f"""
        <div class="analysis-section">
            <h1 style="margin-bottom: 0.5rem;">📊 {name}</h1>
            <h2 style="color: #666; margin-top: 0;">({ticker})</h2>
        </div>
        """, unsafe_allow_html=True)
        
        if is_healthcare and classification:
            st.markdown(f'<span class="subsector-badge">{classification.primary_subsector}</span>', 
                       unsafe_allow_html=True)
        else:
            st.markdown('<span class="subsector-badge" style="background: linear-gradient(45deg, #ffbb33, #ff8800);">⚠️ Non-Healthcare</span>', 
                       unsafe_allow_html=True)
    
    with col2:
        basic_info = data.get('basic_info', {})
        if basic_info.get('marketCap'):
            market_cap = basic_info['marketCap']
            cap_display = f"${market_cap/1e9:.2f}B" if market_cap > 1e9 else f"${market_cap/1e6:.0f}M"
            st.metric("💰 Market Cap", cap_display)
    
    with col3:
        price_data = data.get('price_history', {})
        if price_data and 'current_price' in price_data:
            current_price = price_data['current_price']
            price_change_1d = price_data.get('price_changes', {}).get('1d', 0)
            
            st.metric(
                "💵 Current Price", 
                f"${current_price:.2f}",
                delta=f"{price_change_1d:+.2f}%" if price_change_1d else None
            )

def create_healthcare_score_section(metrics: dict):
    """Create Healthcare Score display section"""
    
    st.markdown("### 🎯 Healthcare Investment Score")
    
    score = metrics.get('medequity_score', 50)
    
    # Determine score class and interpretation
    if score >= 80:
        score_class = "excellent-score"
        interpretation = "🌟 Excellent Investment Opportunity"
        recommendation = "Strong Buy Consideration"
    elif score >= 65:
        score_class = "good-score"
        interpretation = "👍 Good Investment Potential"
        recommendation = "Buy Consideration"
    elif score >= 45:
        score_class = "average-score"
        interpretation = "⚖️ Average Investment Merit"
        recommendation = "Hold/Neutral"
    else:
        score_class = "poor-score"
        interpretation = "⚠️ Below Average Performance"
        recommendation = "Caution Advised"
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        st.markdown("#### Score Breakdown")
        # Component scores (if available)
        components = [
            ("Financial Health", metrics.get('financial_health_score', 0.5) * 100),
            ("Growth Potential", metrics.get('growth_score', 0.5) * 100),
            ("Innovation Pipeline", metrics.get('pipeline_score', 0) * 100),
            ("Market Position", metrics.get('market_position_score', 0.5) * 100),
            ("Risk Management", metrics.get('risk_score', 0.5) * 100)
        ]
        
        for component, comp_score in components:
            st.write(f"• **{component}:** {comp_score:.0f}/100")
    
    with col2:
        st.markdown(f"""
        <div class="analysis-section" style="text-align: center;">
            <div class="score-display {score_class}">{score:.0f}/100</div>
            <h3>{interpretation}</h3>
            <p style="font-size: 1.2rem; font-weight: bold; color: #1f77b4;">{recommendation}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("#### Percentile Rankings")
        rankings = [
            ("vs Healthcare Peers", metrics.get('peer_percentile', 50)),
            ("P/E Ratio", metrics.get('pe_percentile', 50)),
            ("R&D Intensity", metrics.get('rd_percentile', 50)),
            ("Profit Margins", metrics.get('profit_margin_percentile', 50))
        ]
        
        for metric_name, percentile in rankings:
            if percentile:
                st.write(f"• **{metric_name}:** {percentile:.0f}th %ile")

def create_financial_dashboard(data: dict, metrics: dict):
    """Create financial metrics dashboard"""
    
    st.markdown("### 💰 Financial Performance Dashboard")
    
    financials = data.get('financials', {})
    
    # Key metrics grid
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        rd_intensity = metrics.get('rd_intensity_pct', 0)
        if rd_intensity > 0:
            st.metric("🔬 R&D Intensity", f"{rd_intensity:.1f}%")
        else:
            st.metric("🔬 R&D Intensity", "N/A")
    
    with col2:
        revenue_growth = metrics.get('revenue_growth_pct', 0)
        if revenue_growth != 0:
            st.metric("📈 Revenue Growth", f"{revenue_growth:+.1f}%")
        else:
            st.metric("📈 Revenue Growth", "N/A")
    
    with col3:
        profit_margin = metrics.get('profit_margin_pct', 0)
        if profit_margin != 0:
            st.metric("💵 Profit Margin", f"{profit_margin:.1f}%")
        else:
            st.metric("💵 Profit Margin", "N/A")
    
    with col4:
        pe_ratio = financials.get('pe_ratio')
        if pe_ratio:
            st.metric("📊 P/E Ratio", f"{pe_ratio:.1f}")
        else:
            st.metric("📊 P/E Ratio", "N/A")
    
    with col5:
        debt_equity = financials.get('debt_to_equity')
        if debt_equity is not None:
            st.metric("⚖️ Debt/Equity", f"{debt_equity:.2f}")
        else:
            st.metric("⚖️ Debt/Equity", "N/A")
    
    # Additional financial details
    with st.expander("📈 Detailed Financial Metrics", expanded=False):
        display_detailed_financials(metrics, financials)

def display_detailed_financials(metrics: dict, financials: dict):
    """Display detailed financial metrics"""
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💹 Profitability & Efficiency")
        
        financial_metrics = [
            ("Revenue", metrics.get('revenue_billions', 0), "B", "💰"),
            ("Gross Margin", metrics.get('gross_margin_pct', 0), "%", "📊"),
            ("Operating Margin", metrics.get('operating_margin_pct', 0), "%", "⚙️"),
            ("Return on Equity", metrics.get('roe_pct', 0), "%", "📈"),
            ("Free Cash Flow", metrics.get('fcf_billions', 0), "B", "💵")
        ]
        
        for name, value, unit, icon in financial_metrics:
            if value != 0:
                st.write(f"{icon} **{name}:** {value:.2f}{unit}")
            else:
                st.write(f"{icon} **{name}:** N/A")
    
    with col2:
        st.markdown("#### ⚖️ Risk & Valuation")
        
        risk_metrics = [
            ("Beta", metrics.get('beta', 0), "", "📊"),
            ("Current Ratio", metrics.get('current_ratio', 0), "", "💧"),
            ("PEG Ratio", metrics.get('peg_ratio', 0), "", "📈"),
            ("Price-to-Book", metrics.get('price_to_book', 0), "", "📚"),
            ("Dividend Yield", financials.get('dividend_yield', 0)*100 if financials.get('dividend_yield') else 0, "%", "💰")
        ]
        
        for name, value, unit, icon in risk_metrics:
            if value != 0:
                st.write(f"{icon} **{name}:** {value:.2f}{unit}")
            else:
                st.write(f"{icon} **{name}:** N/A")

def create_healthcare_insights_section(data: dict, classification):
    """Create healthcare-specific insights"""
    
    if not classification:
        return
    
    st.markdown("### 🏥 Healthcare Intelligence Insights")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🏷️ Classification Details")
        st.write(f"**Primary Subsector:** {classification.primary_subsector}")
        if classification.secondary_subsector:
            st.write(f"**Secondary:** {classification.secondary_subsector}")
        st.write(f"**Market Cap Tier:** {classification.market_cap_tier}")
        st.write(f"**Confidence:** {classification.confidence_score:.1%}")
    
    with col2:
        st.markdown("#### 📊 Business Profile")
        st.write(f"**Business Model:** {classification.business_model}")
        st.write(f"**Growth Stage:** {classification.growth_stage}")
        st.write(f"**Risk Profile:** {classification.risk_profile}")
    
    with col3:
        st.markdown("#### 📅 June 2025 Analysis")
        st.write("**Data Currency:** ✅ Current")
        st.write("**Market Environment:** Post-2024 cycle")
        st.write("**Regulatory Climate:** Updated FDA guidance")
        st.write("**AI Integration:** Enhanced algorithms")
    
    with col3:
        st.markdown("#### 💰 Revenue Model")
        if classification.revenue_model:
            for model in classification.revenue_model[:3]:  # Show top 3
                st.write(f"• {model}")

def create_price_analysis_section(data: dict):
    """Create price analysis section with charts"""
    
    st.markdown("### 📈 Price Performance Analysis")
    
    ticker = data.get('ticker')
    if not ticker:
        st.error("No ticker data available")
        return
    
    try:
        # Create price chart
        stock = yf.Ticker(ticker)
        hist = stock.history(period="1y")
        
        if hist.empty:
            st.error("No price data available")
            return
        
        # Create interactive candlestick chart
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name=ticker,
            increasing_line_color='#00C851',
            decreasing_line_color='#ff4444'
        ))
        
        # Add moving averages
        if len(hist) > 20:
            hist['MA20'] = hist['Close'].rolling(window=20).mean()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['MA20'],
                name='20-day MA',
                line=dict(color='orange', width=1)
            ))
        
        if len(hist) > 50:
            hist['MA50'] = hist['Close'].rolling(window=50).mean()
            fig.add_trace(go.Scatter(
                x=hist.index, y=hist['MA50'],
                name='50-day MA', 
                line=dict(color='blue', width=1)
            ))
        
        fig.update_layout(
            title=f"{ticker} - 1 Year Price Chart with Moving Averages",
            yaxis_title="Price ($)",
            xaxis_title="Date",
            height=500,
            template="plotly_white"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Performance metrics
        display_performance_metrics(data)
        
    except Exception as e:
        st.error(f"Error creating price chart: {e}")

def display_performance_metrics(data: dict):
    """Display performance metrics"""
    
    price_changes = data.get('price_history', {}).get('price_changes', {})
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    periods = [
        ("1 Day", price_changes.get('1d', 0)),
        ("1 Week", price_changes.get('1w', 0)),
        ("1 Month", price_changes.get('1m', 0)),
        ("3 Months", price_changes.get('3m', 0)),
        ("YTD", price_changes.get('ytd', 0))
    ]
    
    for i, (period, change) in enumerate(periods):
        color = "positive" if change >= 0 else "negative"
        with [col1, col2, col3, col4, col5][i]:
            st.markdown(f"""
            <div class="metric-card" style="text-align: center;">
                <h4>{period}</h4>
                <span class="{color}" style="font-size: 1.5rem;">{change:+.2f}%</span>
            </div>
            """, unsafe_allow_html=True)

def create_pipeline_section(data: dict):
    """Create pipeline analysis section"""
    
    pipeline = data.get('pipeline', [])
    
    if not pipeline:
        st.markdown("### 💊 Clinical Pipeline")
        st.info("No pipeline data available for this company")
        return
    
    st.markdown("### 💊 Clinical Pipeline Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🧪 Pipeline Programs")
        
        # Display pipeline items
        for i, item in enumerate(pipeline[:8]):  # Show top 8
            if isinstance(item, dict):
                phase = item.get('phase', 'Unknown')
                indication = item.get('indication', 'Various')
                description = item.get('description', 'No description available')
                
                st.markdown(f"""
                <div class="metric-card">
                    <span class="pipeline-phase">{phase}</span>
                    <h4>{indication}</h4>
                    <p style="font-size: 0.9rem; color: #666;">{description[:100]}{'...' if len(description) > 100 else ''}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        # Pipeline phase distribution
        phases = {}
        for item in pipeline:
            if isinstance(item, dict) and 'phase' in item:
                phase = item['phase']
                phases[phase] = phases.get(phase, 0) + 1
        
        if phases:
            fig = px.pie(
                values=list(phases.values()),
                names=list(phases.keys()),
                title="Pipeline Distribution by Development Phase",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

def create_news_sentiment_section(data: dict):
    """Create news and sentiment analysis section"""
    
    news = data.get('news', [])
    
    if not news:
        st.markdown("### 📰 News & Sentiment Analysis")
        st.info("No recent news data available")
        return
    
    st.markdown("### 📰 Recent News & Market Sentiment")
    
    # Sentiment analysis
    sentiment_counts = {'positive': 0, 'negative': 0, 'neutral': 0}
    
    for article in news:
        if isinstance(article, dict) and 'sentiment' in article:
            sentiment = article['sentiment']
            sentiment_counts[sentiment] = sentiment_counts.get(sentiment, 0) + 1
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📊 Sentiment Overview")
        
        total_articles = sum(sentiment_counts.values())
        if total_articles > 0:
            # Sentiment chart
            fig = px.pie(
                values=list(sentiment_counts.values()),
                names=[s.title() for s in sentiment_counts.keys()],
                title="News Sentiment Distribution",
                color_discrete_map={
                    'Positive': '#00C851',
                    'Negative': '#ff4444', 
                    'Neutral': '#33b5e5'
                }
            )
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 📰 Recent Headlines")
        
        for article in news[:6]:  # Show top 6 articles
            if isinstance(article, dict):
                title = article.get('title', 'No title')
                source = article.get('source', 'Unknown')
                sentiment = article.get('sentiment', 'neutral')
                
                sentiment_class = f"news-sentiment-{sentiment}"
                sentiment_emoji = "📈" if sentiment == 'positive' else "📉" if sentiment == 'negative' else "📊"
                
                st.markdown(f"""
                <div class="{sentiment_class}">
                    <strong>{sentiment_emoji} {title}</strong><br>
                    <small style="color: #666;">Source: {source}</small>
                </div>
                """, unsafe_allow_html=True)

def display_basic_financial_analysis(data: dict):
    """Display basic financial analysis for non-healthcare companies"""
    
    st.markdown("### 📊 Basic Financial Analysis")
    
    basic_info = data.get('basic_info', {})
    financials = data.get('financials', {})
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        pe_ratio = financials.get('pe_ratio')
        st.metric("P/E Ratio", f"{pe_ratio:.2f}" if pe_ratio else "N/A")
    
    with col2:
        profit_margin = financials.get('profit_margins')
        if profit_margin:
            st.metric("Profit Margin", f"{profit_margin*100:.2f}%")
        else:
            st.metric("Profit Margin", "N/A")
    
    with col3:
        revenue_growth = financials.get('revenue_growth')
        if revenue_growth:
            st.metric("Revenue Growth", f"{revenue_growth*100:+.2f}%")
        else:
            st.metric("Revenue Growth", "N/A")
    
    with col4:
        debt_equity = financials.get('debt_to_equity')
        st.metric("Debt/Equity", f"{debt_equity:.2f}" if debt_equity else "N/A")
    
    # Price chart
    create_price_analysis_section(data)

if __name__ == "__main__":
    main()
