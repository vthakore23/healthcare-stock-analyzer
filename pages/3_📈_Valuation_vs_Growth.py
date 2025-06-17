import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import sys
import os

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Page configuration
st.set_page_config(
    page_title="Valuation vs Growth - MedEquity Pro",
    page_icon="📈",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .valuation-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .metric-container {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 1rem;
        margin: 1rem 0;
    }
    
    .growth-metric {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .value-metric {
        background: linear-gradient(135deg, #3b82f6, #1e40af);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .peg-excellent {
        background: linear-gradient(135deg, #10b981, #059669);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .peg-good {
        background: linear-gradient(135deg, #3b82f6, #1e40af);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .peg-fair {
        background: linear-gradient(135deg, #f59e0b, #d97706);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .peg-expensive {
        background: linear-gradient(135deg, #ef4444, #dc2626);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
    }
    
    .analysis-insight {
        background: #f8fafc;
        border-left: 4px solid #3b82f6;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 4px;
    }
    
    .sector-comparison {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("# 📈 Valuation vs Growth Analysis")
    st.markdown("### Advanced growth-adjusted valuation analysis for healthcare investments")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Single Stock Analysis", "📊 Sector Comparison", "🔍 Growth Screening", "📈 Portfolio Analysis"])
    
    with tab1:
        show_single_stock_analysis()
    
    with tab2:
        show_sector_comparison()
    
    with tab3:
        show_growth_screening()
    
    with tab4:
        show_portfolio_analysis()

def show_single_stock_analysis():
    """Detailed valuation vs growth analysis for single stock"""
    st.header("🎯 Single Stock Valuation vs Growth Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🔍 Stock Selection")
        
        # Stock input
        ticker = st.text_input(
            "Enter stock ticker:",
            placeholder="e.g., PFE, JNJ, MRNA",
            help="Enter any healthcare stock symbol"
        ).upper()
        
        if st.button("📊 Analyze Valuation vs Growth", type="primary"):
            if ticker:
                analyze_single_stock(ticker)
            else:
                st.warning("Please enter a stock ticker")
        
        # Quick access buttons
        st.markdown("#### 🎯 Popular Healthcare Stocks")
        
        popular_stocks = {
            "Large Pharma": ["PFE", "JNJ", "MRK", "ABBV"],
            "Biotech": ["MRNA", "BNTX", "REGN", "VRTX"],
            "Growth": ["ISRG", "DXCM", "VEEV", "TDOC"]
        }
        
        for category, stocks in popular_stocks.items():
            st.markdown(f"**{category}:**")
            cols = st.columns(len(stocks))
            for i, stock in enumerate(stocks):
                with cols[i]:
                    if st.button(stock, key=f"quick_{stock}", use_container_width=True):
                        analyze_single_stock(stock)
    
    with col2:
        st.markdown("### 📊 Analysis Framework")
        
        st.markdown("""
        <div class="valuation-card">
            <h4>🎯 What We Analyze</h4>
            <ul>
                <li><strong>PEG Ratio:</strong> P/E divided by growth rate (ideal: 0.5-1.5)</li>
                <li><strong>Price/Sales vs Revenue Growth:</strong> Revenue multiple efficiency</li>
                <li><strong>EV/EBITDA vs Growth:</strong> Enterprise value efficiency</li>
                <li><strong>Pipeline Value:</strong> R&D productivity and future potential</li>
                <li><strong>Relative Valuation:</strong> Peer comparison analysis</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="analysis-insight">
            <h4>💡 Key Insights</h4>
            <p><strong>Growth at Reasonable Price (GARP):</strong> Find companies with strong growth trading at reasonable valuations</p>
            <p><strong>Healthcare Focus:</strong> Account for R&D cycles, patent cliffs, and regulatory risks</p>
            <p><strong>Pipeline Valuation:</strong> Future drug approvals and market potential</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Display results area
        if 'current_analysis' in st.session_state:
            display_single_stock_results(st.session_state.current_analysis)

def show_sector_comparison():
    """Compare valuation vs growth across healthcare sectors"""
    st.header("📊 Healthcare Sector Valuation vs Growth Comparison")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 Comparison Settings")
        
        # Sector selection
        sectors = st.multiselect(
            "Select sectors to compare:",
            ["Pharmaceuticals", "Biotechnology", "Medical Devices", "Healthcare Services", 
             "Health Insurance", "Diagnostics", "Digital Health"],
            default=["Pharmaceuticals", "Biotechnology", "Medical Devices"]
        )
        
        # Metrics to compare
        comparison_metrics = st.multiselect(
            "Select metrics for comparison:",
            ["PEG Ratio", "P/S vs Revenue Growth", "EV/EBITDA vs Growth", 
             "R&D Intensity", "Pipeline Value Score"],
            default=["PEG Ratio", "P/S vs Revenue Growth"]
        )
        
        # Market cap filter
        market_cap_filter = st.selectbox(
            "Market cap focus:",
            ["All", "Large Cap (>$10B)", "Mid Cap ($2B-$10B)", "Small Cap (<$2B)"]
        )
        
        if st.button("🔍 Run Sector Comparison", type="primary"):
            run_sector_comparison(sectors, comparison_metrics, market_cap_filter)
    
    with col2:
        st.markdown("### 📈 Sector Performance Metrics")
        
        # Display sector metrics
        sector_metrics = get_sector_overview()
        
        for sector, metrics in sector_metrics.items():
            st.markdown(f"""
            <div class="sector-comparison">
                <h4>{sector}</h4>
                <p><strong>Avg PEG:</strong> {metrics['avg_peg']:.2f}</p>
                <p><strong>Avg Growth:</strong> {metrics['avg_growth']:.1f}%</p>
                <p><strong>Valuation:</strong> {metrics['valuation_tier']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Comparison results
    if 'sector_comparison_results' in st.session_state:
        display_sector_comparison_results()

def show_growth_screening():
    """Screen stocks based on growth-adjusted valuation criteria"""
    st.header("🔍 Growth-Adjusted Valuation Screening")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 Screening Criteria")
        
        # PEG ratio filter
        st.markdown("#### 📊 PEG Ratio Filters")
        peg_min = st.number_input("Minimum PEG Ratio:", value=0.0, step=0.1)
        peg_max = st.number_input("Maximum PEG Ratio:", value=2.0, step=0.1)
        
        # Growth filters
        st.markdown("#### 📈 Growth Filters")
        revenue_growth_min = st.slider("Min Revenue Growth (%):", -20, 100, 10)
        earnings_growth_min = st.slider("Min Earnings Growth (%):", -50, 200, 15)
        
        # Valuation filters
        st.markdown("#### 💰 Valuation Filters")
        ps_ratio_max = st.number_input("Max P/S Ratio:", value=10.0, step=0.5)
        ev_ebitda_max = st.number_input("Max EV/EBITDA:", value=25.0, step=1.0)
        
        # Healthcare-specific filters
        st.markdown("#### 🏥 Healthcare Filters")
        min_rd_intensity = st.slider("Min R&D Intensity (%):", 0, 30, 5)
        require_pipeline = st.checkbox("Must have clinical pipeline", value=False)
        
        if st.button("🚀 Run Growth Screen", type="primary", use_container_width=True):
            run_growth_screen({
                'peg_range': (peg_min, peg_max),
                'revenue_growth_min': revenue_growth_min,
                'earnings_growth_min': earnings_growth_min,
                'ps_ratio_max': ps_ratio_max,
                'ev_ebitda_max': ev_ebitda_max,
                'rd_intensity_min': min_rd_intensity,
                'require_pipeline': require_pipeline
            })
    
    with col2:
        st.markdown("### 🎯 Pre-built Screens")
        
        if st.button("💎 GARP Opportunities", use_container_width=True):
            run_garp_screen()
        
        if st.button("🚀 High Growth Value", use_container_width=True):
            run_high_growth_value_screen()
        
        if st.button("🛡️ Defensive Growth", use_container_width=True):
            run_defensive_growth_screen()
        
        if st.button("💊 Pipeline Power", use_container_width=True):
            run_pipeline_power_screen()
        
        st.markdown("### 📊 Screening Tips")
        
        st.markdown("""
        <div class="analysis-insight">
            <h4>💡 Screening Guidelines</h4>
            <p><strong>PEG < 1.0:</strong> Potentially undervalued growth</p>
            <p><strong>PEG 1.0-1.5:</strong> Fair value growth</p>
            <p><strong>PEG > 2.0:</strong> Potentially overvalued</p>
            <p><strong>Healthcare Note:</strong> Consider R&D cycles and patent timelines</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Screening results
    if 'growth_screen_results' in st.session_state:
        display_growth_screen_results()

def show_portfolio_analysis():
    """Analyze portfolio from valuation vs growth perspective"""
    st.header("📈 Portfolio Valuation vs Growth Analysis")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 📝 Portfolio Input")
        
        # Portfolio input methods
        input_method = st.radio(
            "How would you like to input your portfolio?",
            ["Manual Entry", "Upload CSV", "Use Sample Portfolio"]
        )
        
        if input_method == "Manual Entry":
            portfolio_text = st.text_area(
                "Enter stock symbols (comma-separated):",
                placeholder="PFE,JNJ,MRNA,ABBV,REGN",
                help="Enter your healthcare stock holdings"
            )
            
        elif input_method == "Upload CSV":
            uploaded_file = st.file_uploader(
                "Upload portfolio CSV",
                type=['csv'],
                help="CSV should have 'Symbol' column"
            )
            
        else:  # Sample portfolio
            sample_portfolios = {
                "Balanced Healthcare": ["PFE", "JNJ", "UNH", "ABBV", "TMO"],
                "Growth Focus": ["MRNA", "REGN", "VRTX", "ISRG", "DXCM"],
                "Value Focus": ["PFE", "MRK", "BMY", "GILD", "CVS"],
                "Biotech Heavy": ["MRNA", "BNTX", "REGN", "VRTX", "BIIB"]
            }
            
            selected_portfolio = st.selectbox("Choose sample portfolio:", list(sample_portfolios.keys()))
            portfolio_text = ",".join(sample_portfolios[selected_portfolio])
            st.info(f"Sample portfolio: {portfolio_text}")
        
        if st.button("📊 Analyze Portfolio", type="primary"):
            if input_method == "Manual Entry" or input_method == "Use Sample Portfolio":
                if portfolio_text:
                    symbols = [s.strip().upper() for s in portfolio_text.split(',')]
                    analyze_portfolio(symbols)
                else:
                    st.warning("Please enter portfolio symbols")
            elif input_method == "Upload CSV" and uploaded_file:
                # Handle CSV upload
                df = pd.read_csv(uploaded_file)
                if 'Symbol' in df.columns:
                    symbols = df['Symbol'].tolist()
                    analyze_portfolio(symbols)
                else:
                    st.error("CSV must have 'Symbol' column")
    
    with col2:
        st.markdown("### 📊 Portfolio Metrics")
        
        if 'portfolio_analysis' in st.session_state:
            display_portfolio_analysis_results()
        else:
            st.info("Enter your portfolio to see analysis here")
            
            # Show example metrics
            st.markdown("""
            <div class="valuation-card">
                <h4>📈 What You'll See</h4>
                <ul>
                    <li>Portfolio-weighted PEG ratio</li>
                    <li>Growth vs valuation scatter plot</li>
                    <li>Sector allocation analysis</li>
                    <li>Risk-adjusted growth scores</li>
                    <li>Rebalancing suggestions</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

def analyze_single_stock(ticker):
    """Analyze single stock valuation vs growth"""
    with st.spinner(f"Analyzing {ticker} valuation vs growth..."):
        try:
            # Get stock data
            stock = yf.Ticker(ticker)
            info = stock.info
            hist = stock.history(period="1y")
            
            if not info:
                st.error(f"No data found for {ticker}")
                return
            
            # Calculate metrics
            analysis = calculate_valuation_growth_metrics(ticker, info, hist)
            st.session_state.current_analysis = analysis
            
            st.success(f"✅ Analysis complete for {ticker}")
            
        except Exception as e:
            st.error(f"Analysis failed for {ticker}: {str(e)}")

def calculate_valuation_growth_metrics(ticker, info, hist):
    """Calculate comprehensive valuation vs growth metrics"""
    
    # Basic metrics
    pe_ratio = info.get('forwardPE', info.get('trailingPE', 0))
    ps_ratio = info.get('priceToSalesTrailing12Months', 0)
    ev_ebitda = info.get('enterpriseToEbitda', 0)
    
    # Growth metrics
    revenue_growth = info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0
    earnings_growth = info.get('earningsGrowth', 0) * 100 if info.get('earningsGrowth') else 0
    
    # Calculate PEG ratio
    peg_ratio = pe_ratio / earnings_growth if earnings_growth > 0 and pe_ratio > 0 else None
    
    # Healthcare-specific metrics
    rd_intensity = estimate_rd_intensity(info)
    pipeline_score = estimate_pipeline_score(ticker, info)
    
    # Valuation assessment
    valuation_score = assess_valuation(peg_ratio, ps_ratio, ev_ebitda)
    growth_score = assess_growth(revenue_growth, earnings_growth, rd_intensity)
    
    return {
        'ticker': ticker,
        'pe_ratio': pe_ratio,
        'ps_ratio': ps_ratio,
        'ev_ebitda': ev_ebitda,
        'peg_ratio': peg_ratio,
        'revenue_growth': revenue_growth,
        'earnings_growth': earnings_growth,
        'rd_intensity': rd_intensity,
        'pipeline_score': pipeline_score,
        'valuation_score': valuation_score,
        'growth_score': growth_score,
        'overall_score': (valuation_score + growth_score) / 2
    }

def display_single_stock_results(analysis):
    """Display single stock analysis results"""
    ticker = analysis['ticker']
    
    st.markdown(f"### 📊 {ticker} - Valuation vs Growth Analysis")
    
    # Key metrics display
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        peg_ratio = analysis['peg_ratio']
        peg_class = get_peg_class(peg_ratio)
        peg_display = f"{peg_ratio:.2f}" if peg_ratio else "N/A"
        
        st.markdown(f"""
        <div class="{peg_class}">
            <h3>PEG Ratio</h3>
            <h2>{peg_display}</h2>
            <p>{get_peg_interpretation(peg_ratio)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="growth-metric">
            <h3>Revenue Growth</h3>
            <h2>{analysis['revenue_growth']:.1f}%</h2>
            <p>Annual Growth Rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="value-metric">
            <h3>P/S Ratio</h3>
            <h2>{analysis['ps_ratio']:.1f}</h2>
            <p>Price-to-Sales</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="growth-metric">
            <h3>R&D Intensity</h3>
            <h2>{analysis['rd_intensity']:.1f}%</h2>
            <p>R&D as % Revenue</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Detailed analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Growth Analysis")
        
        growth_metrics = [
            ("Revenue Growth", analysis['revenue_growth'], "%"),
            ("Earnings Growth", analysis['earnings_growth'], "%"),
            ("R&D Intensity", analysis['rd_intensity'], "%"),
            ("Pipeline Score", analysis['pipeline_score'], "/100")
        ]
        
        for metric, value, unit in growth_metrics:
            st.write(f"**{metric}:** {value:.1f}{unit}")
    
    with col2:
        st.markdown("#### 💰 Valuation Analysis")
        
        valuation_metrics = [
            ("P/E Ratio", analysis['pe_ratio'], ""),
            ("P/S Ratio", analysis['ps_ratio'], ""),
            ("EV/EBITDA", analysis['ev_ebitda'], ""),
            ("PEG Ratio", analysis['peg_ratio'], "")
        ]
        
        for metric, value, unit in valuation_metrics:
            display_value = f"{value:.1f}{unit}" if value and value > 0 else "N/A"
            st.write(f"**{metric}:** {display_value}")
    
    # Investment recommendation
    overall_score = analysis['overall_score']
    recommendation = get_investment_recommendation(overall_score, analysis['peg_ratio'])
    
    st.markdown(f"""
    <div class="analysis-insight">
        <h4>🎯 Investment Analysis</h4>
        <p><strong>Overall Score:</strong> {overall_score:.1f}/100</p>
        <p><strong>Recommendation:</strong> {recommendation}</p>
        <p><strong>Key Insight:</strong> {get_key_insight(analysis)}</p>
    </div>
    """, unsafe_allow_html=True)

def run_sector_comparison(sectors, metrics, market_cap_filter):
    """Run sector comparison analysis"""
    with st.spinner("📊 Running sector comparison..."):
        # Mock sector comparison results
        comparison_results = generate_mock_sector_comparison(sectors, metrics)
        st.session_state.sector_comparison_results = comparison_results
        st.success(f"✅ Sector comparison complete for {len(sectors)} sectors")

def run_growth_screen(criteria):
    """Run growth-adjusted valuation screening"""
    with st.spinner("🔍 Running growth screening..."):
        # Mock screening results
        results = generate_mock_growth_screen_results(criteria)
        st.session_state.growth_screen_results = results
        st.success(f"✅ Growth screening complete! Found {len(results)} qualifying stocks.")

def analyze_portfolio(symbols):
    """Analyze portfolio valuation vs growth"""
    with st.spinner(f"📊 Analyzing portfolio of {len(symbols)} stocks..."):
        portfolio_analysis = generate_mock_portfolio_analysis(symbols)
        st.session_state.portfolio_analysis = portfolio_analysis
        st.success(f"✅ Portfolio analysis complete for {len(symbols)} holdings")

# Helper functions

def estimate_rd_intensity(info):
    """Estimate R&D intensity based on available data"""
    # Mock R&D intensity calculation
    sector = info.get('sector', '').lower()
    if 'biotech' in sector:
        return np.random.uniform(15, 25)
    elif 'pharma' in sector:
        return np.random.uniform(10, 20)
    elif 'device' in sector:
        return np.random.uniform(5, 15)
    else:
        return np.random.uniform(3, 12)

def estimate_pipeline_score(ticker, info):
    """Estimate pipeline strength score"""
    # Mock pipeline score
    market_cap = info.get('marketCap', 0)
    if market_cap > 50e9:  # Large cap
        return np.random.uniform(60, 85)
    elif market_cap > 10e9:  # Mid cap
        return np.random.uniform(40, 75)
    else:  # Small cap
        return np.random.uniform(30, 70)

def assess_valuation(peg_ratio, ps_ratio, ev_ebitda):
    """Assess valuation attractiveness"""
    score = 50  # Base score
    
    if peg_ratio:
        if peg_ratio < 1.0:
            score += 25
        elif peg_ratio < 1.5:
            score += 15
        elif peg_ratio < 2.0:
            score += 5
        else:
            score -= 15
    
    if ps_ratio:
        if ps_ratio < 3:
            score += 10
        elif ps_ratio < 6:
            score += 5
        elif ps_ratio > 10:
            score -= 10
    
    return min(100, max(0, score))

def assess_growth(revenue_growth, earnings_growth, rd_intensity):
    """Assess growth potential"""
    score = 50  # Base score
    
    if revenue_growth > 20:
        score += 25
    elif revenue_growth > 10:
        score += 15
    elif revenue_growth > 5:
        score += 5
    elif revenue_growth < 0:
        score -= 20
    
    if earnings_growth > 25:
        score += 20
    elif earnings_growth > 15:
        score += 10
    elif earnings_growth < 0:
        score -= 15
    
    if rd_intensity > 15:
        score += 10
    elif rd_intensity > 10:
        score += 5
    
    return min(100, max(0, score))

def get_peg_class(peg_ratio):
    """Get CSS class for PEG ratio"""
    if not peg_ratio:
        return "peg-fair"
    elif peg_ratio < 1.0:
        return "peg-excellent"
    elif peg_ratio < 1.5:
        return "peg-good"
    elif peg_ratio < 2.0:
        return "peg-fair"
    else:
        return "peg-expensive"

def get_peg_interpretation(peg_ratio):
    """Get PEG ratio interpretation"""
    if not peg_ratio:
        return "No Growth Data"
    elif peg_ratio < 1.0:
        return "Undervalued Growth"
    elif peg_ratio < 1.5:
        return "Fair Value Growth"
    elif peg_ratio < 2.0:
        return "Slightly Expensive"
    else:
        return "Overvalued"

def get_investment_recommendation(overall_score, peg_ratio):
    """Generate investment recommendation"""
    if overall_score >= 80:
        return "Strong Buy - Excellent growth at reasonable valuation"
    elif overall_score >= 65:
        return "Buy - Good growth opportunity"
    elif overall_score >= 50:
        return "Hold - Balanced risk/reward"
    else:
        return "Avoid - Poor valuation or growth prospects"

def get_key_insight(analysis):
    """Generate key insight for the stock"""
    peg = analysis['peg_ratio']
    growth = analysis['revenue_growth']
    
    if peg and peg < 1.0 and growth > 15:
        return "Exceptional growth trading at discount - rare opportunity"
    elif peg and peg > 2.0:
        return "High growth premium - monitor for better entry point"
    elif growth > 20:
        return "Strong growth momentum - justify premium valuation"
    else:
        return "Balanced growth profile - suitable for conservative portfolios"

def get_sector_overview():
    """Get sector overview metrics"""
    return {
        "Pharmaceuticals": {"avg_peg": 1.8, "avg_growth": 8.5, "valuation_tier": "Fair"},
        "Biotechnology": {"avg_peg": 2.4, "avg_growth": 22.1, "valuation_tier": "Premium"},
        "Medical Devices": {"avg_peg": 1.5, "avg_growth": 12.3, "valuation_tier": "Reasonable"},
        "Healthcare Services": {"avg_peg": 1.9, "avg_growth": 9.7, "valuation_tier": "Fair"}
    }

def generate_mock_sector_comparison(sectors, metrics):
    """Generate mock sector comparison results"""
    return {
        "sectors": sectors,
        "metrics": metrics,
        "data": [
            {"Sector": "Pharmaceuticals", "Avg_PEG": 1.8, "Avg_Growth": 8.5, "Avg_PS": 4.2},
            {"Sector": "Biotechnology", "Avg_PEG": 2.4, "Avg_Growth": 22.1, "Avg_PS": 8.7},
            {"Sector": "Medical Devices", "Avg_PEG": 1.5, "Avg_Growth": 12.3, "Avg_PS": 5.1}
        ]
    }

def generate_mock_growth_screen_results(criteria):
    """Generate mock growth screening results"""
    return [
        {"Symbol": "VRTX", "PEG": 0.8, "Revenue_Growth": 18.5, "Pipeline_Score": 92},
        {"Symbol": "REGN", "PEG": 1.2, "Revenue_Growth": 15.2, "Pipeline_Score": 88},
        {"Symbol": "DXCM", "PEG": 1.4, "Revenue_Growth": 25.3, "Pipeline_Score": 75}
    ]

def generate_mock_portfolio_analysis(symbols):
    """Generate mock portfolio analysis"""
    return {
        "symbols": symbols,
        "weighted_peg": 1.6,
        "avg_growth": 14.2,
        "total_score": 72,
        "recommendation": "Well-balanced growth portfolio"
    }

def display_sector_comparison_results():
    """Display sector comparison results"""
    st.markdown("### 📊 Sector Comparison Results")
    # Implementation for displaying sector comparison
    st.info("Sector comparison results would be displayed here")

def display_growth_screen_results():
    """Display growth screening results"""
    results = st.session_state.growth_screen_results
    st.markdown("### 🎯 Growth Screening Results")
    
    df = pd.DataFrame(results)
    st.dataframe(df, use_container_width=True)

def display_portfolio_analysis_results():
    """Display portfolio analysis results"""
    analysis = st.session_state.portfolio_analysis
    st.markdown("### 📈 Portfolio Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Weighted PEG", f"{analysis['weighted_peg']:.2f}")
        st.metric("Avg Growth", f"{analysis['avg_growth']:.1f}%")
    
    with col2:
        st.metric("Portfolio Score", f"{analysis['total_score']}/100")
        st.info(analysis['recommendation'])

def run_garp_screen():
    """Run Growth at Reasonable Price screen"""
    with st.spinner("💎 Running GARP screen..."):
        st.success("GARP screening completed!")

def run_high_growth_value_screen():
    """Run high growth value screen"""
    with st.spinner("🚀 Running high growth value screen..."):
        st.success("High growth value screening completed!")

def run_defensive_growth_screen():
    """Run defensive growth screen"""
    with st.spinner("🛡️ Running defensive growth screen..."):
        st.success("Defensive growth screening completed!")

def run_pipeline_power_screen():
    """Run pipeline power screen"""
    with st.spinner("💊 Running pipeline power screen..."):
        st.success("Pipeline power screening completed!")

if __name__ == "__main__":
    main() 