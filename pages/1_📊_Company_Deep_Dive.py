import streamlit as st
import sys
import os

# Add the parent directory to the path to import custom modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from medequity_utils.dynamic_scraper import HealthcareScraper
    from medequity_utils.healthcare_classifier import classify_healthcare_company
    from medequity_utils.metrics_calculator import calculate_healthcare_metrics
    from medequity_utils.data_validation import validate_data
    import yfinance as yf
    import plotly.graph_objects as go
    import plotly.express as px
    import pandas as pd
    import numpy as np
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Company Deep Dive - Healthcare Analyzer | June 2025",
    page_icon="📊",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 0.5rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1f77b4;
    }
    
    .score-display {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        margin: 1rem 0;
    }
    
    .excellent-score { color: #00C851; }
    .good-score { color: #33b5e5; }
    .average-score { color: #ffbb33; }
    .poor-score { color: #ff4444; }
    
    .deep-dive-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = HealthcareScraper()

def main():
    st.markdown("""
    <div class="deep-dive-header">
        <h1>📊 Company Deep Dive Analysis</h1>
        <p style="font-size: 1.2rem;">Comprehensive healthcare company analysis with advanced metrics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Input section
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "🔍 Enter Healthcare Company Ticker:",
            placeholder="e.g., MRNA, PFE, JNJ, ISRG",
            help="Enter any healthcare company ticker for comprehensive analysis"
        ).upper().strip()
        
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🚀 Deep Dive Analysis", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        perform_deep_dive_analysis(ticker)
    elif ticker:
        st.info("👆 Click 'Deep Dive Analysis' to begin comprehensive analysis")
    else:
        show_deep_dive_features()

def show_deep_dive_features():
    """Show the features of deep dive analysis"""
    st.markdown("### 🌟 Deep Dive Analysis Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🎯 Advanced Scoring</h3>
            <ul>
                <li>MedEquity Proprietary Score</li>
                <li>Component-level analysis</li>
                <li>Peer comparison rankings</li>
                <li>Risk-adjusted valuations</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>🧬 Healthcare Intelligence</h3>
            <ul>
                <li>AI-powered classification</li>
                <li>Pipeline analysis</li>
                <li>R&D efficiency metrics</li>
                <li>Regulatory risk assessment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 Market Analysis</h3>
            <ul>
                <li>Technical indicators</li>
                <li>Volume analysis</li>
                <li>Support/resistance levels</li>
                <li>Sentiment tracking</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def perform_deep_dive_analysis(ticker: str):
    """Perform comprehensive deep dive analysis"""
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Phase 1: Data Collection
        status_text.text("🔍 Collecting comprehensive data...")
        progress_bar.progress(25)
        
        company_data = st.session_state.scraper.fetch_company_data(ticker)
        
        if 'error' in company_data:
            st.error(f"❌ Error analyzing {ticker}: {company_data['error']}")
            return
            
        # Phase 2: Advanced Analytics
        status_text.text("🧬 Running advanced analytics...")
        progress_bar.progress(50)
        
        classification = classify_healthcare_company(company_data)
        company_data['classification'] = classification
        
        # Phase 3: Metrics Calculation
        status_text.text("📊 Calculating comprehensive metrics...")
        progress_bar.progress(75)
        
        metrics = calculate_healthcare_metrics(company_data)
        company_data['metrics'] = metrics
        
        # Phase 4: Validation
        status_text.text("✅ Validating and finalizing...")
        progress_bar.progress(100)
        
        validation_result = validate_data(company_data)
        
        # Clear progress
        progress_bar.empty()
        status_text.empty()
        
        # Display results
        display_deep_dive_results(company_data, validation_result)
        
    except Exception as e:
        st.error(f"❌ Analysis failed: {str(e)}")
        progress_bar.empty()
        status_text.empty()

def display_deep_dive_results(data: dict, validation: dict):
    """Display comprehensive deep dive results"""
    
    ticker = data.get('ticker', 'Unknown')
    name = data.get('name', ticker)
    is_healthcare = data.get('is_healthcare', False)
    classification = data.get('classification')
    metrics = data.get('metrics', {})
    
    # Header section
    st.markdown(f"## 🏢 {name} ({ticker})")
    
    if not is_healthcare:
        st.warning("⚠️ This company is not classified as healthcare. Limited analysis available.")
        return
    
    # Executive Summary
    create_executive_summary(data, metrics, classification)
    
    # Key Metrics Dashboard
    create_key_metrics_dashboard(metrics, data)
    
    # Detailed Analysis Sections
    col1, col2 = st.columns(2)
    
    with col1:
        create_financial_deep_dive(data, metrics)
        create_pipeline_deep_dive(data)
    
    with col2:
        create_valuation_analysis(data, metrics)
        create_risk_analysis(data, metrics, classification)
    
    # Market Analysis
    create_market_analysis(data)
    
    # Competitive Analysis
    create_competitive_analysis(data, classification)

def create_executive_summary(data: dict, metrics: dict, classification):
    """Create executive summary section"""
    st.markdown("### 📋 Executive Summary")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        score = metrics.get('medequity_score', 50)
        score_class = get_score_class(score)
        recommendation = get_investment_recommendation(score)
        
        st.markdown(f"""
        <div class="metric-card" style="text-align: center;">
            <h3>MedEquity Score</h3>
            <div class="score-display {score_class}">{score:.0f}/100</div>
            <p><strong>{recommendation}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if classification:
            st.markdown(f"""
            <div class="metric-card">
                <h4>🏷️ Company Profile</h4>
                <p><strong>Subsector:</strong> {classification.primary_subsector}</p>
                <p><strong>Business Model:</strong> {classification.business_model}</p>
                <p><strong>Growth Stage:</strong> {classification.growth_stage}</p>
                <p><strong>Risk Profile:</strong> {classification.risk_profile}</p>
                <p><strong>Market Cap Tier:</strong> {classification.market_cap_tier}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        # Key highlights
        highlights = generate_key_highlights(data, metrics)
        st.markdown(f"""
        <div class="metric-card">
            <h4>🎯 Key Highlights</h4>
            {''.join([f'<p>• {highlight}</p>' for highlight in highlights])}
        </div>
        """, unsafe_allow_html=True)

def create_key_metrics_dashboard(metrics: dict, data: dict):
    """Create comprehensive metrics dashboard"""
    st.markdown("### 📊 Key Metrics Dashboard")
    
    # Row 1: Financial Health
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        revenue = metrics.get('revenue_billions', 0)
        st.metric("💰 Revenue", f"${revenue:.2f}B" if revenue > 0 else "N/A")
    
    with col2:
        rd_intensity = metrics.get('rd_intensity_pct', 0)
        st.metric("🔬 R&D Intensity", f"{rd_intensity:.1f}%" if rd_intensity > 0 else "N/A")
    
    with col3:
        profit_margin = metrics.get('profit_margin_pct', 0)
        st.metric("💵 Profit Margin", f"{profit_margin:.1f}%" if profit_margin != 0 else "N/A")
    
    with col4:
        pipeline_count = len(data.get('pipeline', []))
        st.metric("💊 Pipeline Count", str(pipeline_count))
    
    with col5:
        market_cap = metrics.get('market_cap_billions', 0)
        st.metric("🏢 Market Cap", f"${market_cap:.2f}B" if market_cap > 0 else "N/A")

def create_financial_deep_dive(data: dict, metrics: dict):
    """Create detailed financial analysis"""
    st.markdown("### 💰 Financial Deep Dive")
    
    financials = data.get('financials', {})
    
    # Financial strength score
    financial_scores = []
    if 'profit_margin_score' in metrics:
        financial_scores.append(('Profitability', metrics['profit_margin_score'] * 100))
    if 'liquidity_score' in metrics:
        financial_scores.append(('Liquidity', metrics['liquidity_score'] * 100))
    if 'debt_score' in metrics:
        financial_scores.append(('Debt Management', metrics['debt_score'] * 100))
    
    if financial_scores:
        df = pd.DataFrame(financial_scores, columns=['Metric', 'Score'])
        fig = px.bar(df, x='Metric', y='Score', title="Financial Health Components")
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)

def create_pipeline_deep_dive(data: dict):
    """Create detailed pipeline analysis"""
    st.markdown("### 💊 Pipeline Deep Dive")
    
    pipeline = data.get('pipeline', [])
    
    if not pipeline:
        st.info("No pipeline data available")
        return
    
    # Pipeline phase analysis
    phases = {}
    for item in pipeline:
        if isinstance(item, dict) and 'phase' in item:
            phase = item['phase']
            phases[phase] = phases.get(phase, 0) + 1
    
    if phases:
        # Create pipeline visualization
        fig = px.pie(
            values=list(phases.values()),
            names=list(phases.keys()),
            title="Pipeline Distribution by Phase"
        )
        fig.update_layout(height=300)
        st.plotly_chart(fig, use_container_width=True)
        
        # Pipeline value estimation
        phase_values = {
            'Preclinical': 1, 'Phase I': 2, 'Phase II': 4, 
            'Phase III': 8, 'Approved/Commercial': 15
        }
        
        total_value = sum(phase_values.get(phase, 1) * count for phase, count in phases.items())
        st.metric("📈 Pipeline Value Score", str(total_value))

def create_valuation_analysis(data: dict, metrics: dict):
    """Create valuation analysis"""
    st.markdown("### 📈 Valuation Analysis")
    
    financials = data.get('financials', {})
    
    # Valuation metrics
    valuation_data = []
    
    pe_ratio = financials.get('pe_ratio')
    if pe_ratio:
        valuation_data.append(['P/E Ratio', pe_ratio, 'Lower is generally better'])
    
    peg_ratio = financials.get('peg_ratio')
    if peg_ratio:
        valuation_data.append(['PEG Ratio', peg_ratio, '<1.0 is attractive'])
    
    price_to_book = financials.get('price_to_book')
    if price_to_book:
        valuation_data.append(['Price/Book', price_to_book, 'Asset-based valuation'])
    
    if valuation_data:
        df = pd.DataFrame(valuation_data, columns=['Metric', 'Value', 'Interpretation'])
        st.dataframe(df, use_container_width=True)

def create_risk_analysis(data: dict, metrics: dict, classification):
    """Create risk analysis"""
    st.markdown("### ⚖️ Risk Analysis")
    
    risk_factors = []
    
    # Subsector risk
    if classification:
        risk_factors.append(f"**Subsector Risk:** {classification.regulatory_risk}")
    
    # Financial risk
    debt_equity = metrics.get('debt_to_equity', 0)
    if debt_equity > 0:
        risk_level = "High" if debt_equity > 1.0 else "Medium" if debt_equity > 0.5 else "Low"
        risk_factors.append(f"**Debt Risk:** {risk_level} (D/E: {debt_equity:.2f})")
    
    # Beta risk
    beta = metrics.get('beta', 0)
    if beta > 0:
        volatility = "High" if beta > 1.5 else "Medium" if beta > 1.0 else "Low"
        risk_factors.append(f"**Volatility Risk:** {volatility} (β: {beta:.2f})")
    
    # Display risk factors
    for factor in risk_factors:
        st.markdown(f"• {factor}")

def create_market_analysis(data: dict):
    """Create market analysis section"""
    st.markdown("### 📈 Market Analysis")
    
    ticker = data.get('ticker')
    if not ticker:
        st.error("No ticker available for market analysis")
        return
    
    try:
        # Get market data and create chart
        stock = yf.Ticker(ticker)
        hist = stock.history(period="6mo")
        
        if not hist.empty:
            # Create candlestick chart
            fig = go.Figure(data=go.Candlestick(
                x=hist.index,
                open=hist['Open'],
                high=hist['High'],
                low=hist['Low'],
                close=hist['Close'],
                name=ticker
            ))
            
            fig.update_layout(
                title=f"{ticker} - 6 Month Price Chart",
                yaxis_title="Price ($)",
                height=400
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
    except Exception as e:
        st.error(f"Could not load market data: {e}")

def create_competitive_analysis(data: dict, classification):
    """Create competitive analysis"""
    st.markdown("### 🏆 Competitive Analysis")
    
    if classification:
        # Get peer companies (simplified)
        peer_tickers = get_peer_companies(classification.primary_subsector)
        
        if peer_tickers:
            st.markdown(f"**Peer Companies in {classification.primary_subsector}:**")
            
            cols = st.columns(min(len(peer_tickers), 5))
            for i, peer in enumerate(peer_tickers[:5]):
                with cols[i]:
                    st.button(peer, key=f"peer_{peer}")

def get_peer_companies(subsector: str) -> list:
    """Get peer companies by subsector"""
    peer_map = {
        'Biotechnology': ['MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB'],
        'Pharmaceuticals': ['PFE', 'JNJ', 'MRK', 'ABBV', 'LLY'],
        'Medical Devices': ['MDT', 'ABT', 'SYK', 'ISRG', 'DXCM'],
        'Healthcare Services': ['UNH', 'CVS', 'CI', 'HUM'],
        'Diagnostics': ['LH', 'DGX', 'ILMN', 'TMO']
    }
    return peer_map.get(subsector, [])

def get_score_class(score: float) -> str:
    """Get CSS class for score display"""
    if score >= 80:
        return "excellent-score"
    elif score >= 65:
        return "good-score"
    elif score >= 45:
        return "average-score"
    else:
        return "poor-score"

def get_investment_recommendation(score: float) -> str:
    """Get investment recommendation based on score"""
    if score >= 80:
        return "Strong Buy"
    elif score >= 65:
        return "Buy"
    elif score >= 45:
        return "Hold"
    else:
        return "Caution"

def generate_key_highlights(data: dict, metrics: dict) -> list:
    """Generate key highlights for the company"""
    highlights = []
    
    # Revenue highlight
    revenue = metrics.get('revenue_billions', 0)
    if revenue > 10:
        highlights.append(f"Large scale: ${revenue:.1f}B revenue")
    elif revenue > 1:
        highlights.append(f"Growing scale: ${revenue:.1f}B revenue")
    
    # R&D highlight
    rd_intensity = metrics.get('rd_intensity_pct', 0)
    if rd_intensity > 20:
        highlights.append(f"R&D focused: {rd_intensity:.0f}% intensity")
    
    # Pipeline highlight
    pipeline_count = len(data.get('pipeline', []))
    if pipeline_count > 5:
        highlights.append(f"Rich pipeline: {pipeline_count} programs")
    
    # Profitability highlight
    profit_margin = metrics.get('profit_margin_pct', 0)
    if profit_margin > 20:
        highlights.append(f"Highly profitable: {profit_margin:.0f}% margin")
    elif profit_margin > 0:
        highlights.append(f"Profitable: {profit_margin:.0f}% margin")
    
    return highlights[:4]  # Return top 4 highlights

if __name__ == "__main__":
    main()
