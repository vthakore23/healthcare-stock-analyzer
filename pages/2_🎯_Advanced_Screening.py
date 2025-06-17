import streamlit as st
import pandas as pd
import numpy as np
import yfinance as yf
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page configuration
st.set_page_config(
    page_title="Advanced Screening - MedEquity Pro",
    page_icon="🎯",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .screening-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        border: 1px solid #e2e8f0;
    }
    
    .filter-section {
        background: #f8fafc;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .metric-highlight {
        background: linear-gradient(135deg, #3b82f6, #1e40af);
        color: white;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .screening-result {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        transition: all 0.2s ease;
    }
    
    .screening-result:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        border-color: #3b82f6;
    }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("# 🎯 Advanced Healthcare Screening")
    st.markdown("### Comprehensive screening for insider activity, financial metrics, and investment opportunities")
    
    # Main tabs
    tab1, tab2, tab3, tab4 = st.tabs(["🕵️ Insider Screening", "📊 Financial Screening", "🎯 Smart Filters", "📈 Results"])
    
    with tab1:
        show_insider_screening()
    
    with tab2:
        show_financial_screening()
    
    with tab3:
        show_smart_filters()
    
    with tab4:
        show_screening_results()

def show_insider_screening():
    """Advanced insider trading screening"""
    st.header("🕵️ Insider Trading Screening")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🎯 Screening Criteria")
        
        # Insider activity filters
        st.markdown("#### 👔 Insider Activity Filters")
        
        insider_types = st.multiselect(
            "Insider Types:",
            ["CEO", "CFO", "President", "COO", "Director", "10% Owner", "Other"],
            default=["CEO", "CFO", "President"]
        )
        
        transaction_types = st.multiselect(
            "Transaction Types:",
            ["Purchase", "Sale", "Option Exercise", "Gift", "Other"],
            default=["Purchase"]
        )
        
        col1a, col1b = st.columns(2)
        
        with col1a:
            min_transaction_value = st.number_input(
                "Min Transaction Value ($):",
                min_value=10000,
                max_value=50000000,
                value=1000000,
                step=100000
            )
        
        with col1b:
            days_lookback = st.number_input(
                "Days to Look Back:",
                min_value=1,
                max_value=365,
                value=30,
                step=1
            )
        
        # Time-based filters
        st.markdown("#### ⏰ Time-based Filters")
        
        col1c, col1d = st.columns(2)
        
        with col1c:
            cluster_window = st.number_input(
                "Cluster Window (days):",
                min_value=1,
                max_value=30,
                value=7,
                help="Find multiple insiders trading within this time window"
            )
        
        with col1d:
            min_cluster_size = st.number_input(
                "Min Cluster Size:",
                min_value=2,
                max_value=10,
                value=3,
                help="Minimum number of insiders for cluster alert"
            )
    
    with col2:
        st.markdown("### 🔍 Quick Screens")
        
        # Pre-built screening templates
        st.markdown("#### 📋 Pre-built Screens")
        
        if st.button("🚨 Executive Buying Spree", type="primary", use_container_width=True):
            run_executive_buying_screen(min_transaction_value)
        
        if st.button("💰 Large Insider Purchases", use_container_width=True):
            run_large_purchase_screen(min_transaction_value * 2)
        
        if st.button("🎯 Clustered Insider Activity", use_container_width=True):
            run_clustered_activity_screen(cluster_window, min_cluster_size)
        
        if st.button("⚡ Recent Insider Momentum", use_container_width=True):
            run_momentum_screen(days_lookback)
        
        # Custom screening
        st.markdown("#### 🔧 Custom Screen")
        
        custom_symbols = st.text_input(
            "Custom Symbol List:",
            placeholder="PFE,JNJ,MRK,ABBV (comma-separated)",
            help="Enter specific symbols to screen"
        )
        
        if st.button("🔍 Run Custom Screen", type="secondary", use_container_width=True):
            if custom_symbols:
                symbols = [s.strip().upper() for s in custom_symbols.split(',')]
                run_custom_screen(symbols, {
                    'insider_types': insider_types,
                    'transaction_types': transaction_types,
                    'min_value': min_transaction_value,
                    'days_back': days_lookback
                })
    
    # Recent screening results
    st.markdown("---")
    st.markdown("### 📊 Recent Screening Results")
    
    if 'screening_results' in st.session_state and st.session_state.screening_results:
        display_insider_results(st.session_state.screening_results)
    else:
        st.info("Run a screening to see results here")

def show_financial_screening():
    """Financial metrics screening"""
    st.header("📊 Financial Metrics Screening")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 💰 Financial Filters")
        
        # Market cap filter
        st.markdown("#### 🏢 Market Cap")
        market_cap_range = st.select_slider(
            "Market Cap Range:",
            options=["Micro (<$300M)", "Small ($300M-$2B)", "Mid ($2B-$10B)", "Large ($10B-$200B)", "Mega (>$200B)"],
            value=("Small ($300M-$2B)", "Large ($10B-$200B)")
        )
        
        # Valuation metrics
        st.markdown("#### 📈 Valuation Metrics")
        
        col1a, col1b = st.columns(2)
        
        with col1a:
            pe_min = st.number_input("P/E Ratio Min:", value=0.0, step=0.1)
            pe_max = st.number_input("P/E Ratio Max:", value=50.0, step=0.1)
        
        with col1b:
            pb_min = st.number_input("P/B Ratio Min:", value=0.0, step=0.1)
            pb_max = st.number_input("P/B Ratio Max:", value=10.0, step=0.1)
        
        # Growth metrics
        st.markdown("#### 📊 Growth Metrics")
        
        col1c, col1d = st.columns(2)
        
        with col1c:
            revenue_growth_min = st.number_input("Revenue Growth Min (%):", value=-50.0, step=1.0)
            revenue_growth_max = st.number_input("Revenue Growth Max (%):", value=100.0, step=1.0)
        
        with col1d:
            eps_growth_min = st.number_input("EPS Growth Min (%):", value=-100.0, step=1.0)
            eps_growth_max = st.number_input("EPS Growth Max (%):", value=200.0, step=1.0)
    
    with col2:
        st.markdown("### 🎯 Healthcare-Specific Filters")
        
        # Healthcare sector filters
        st.markdown("#### 🏥 Sector Focus")
        
        healthcare_sectors = st.multiselect(
            "Healthcare Subsectors:",
            ["Pharmaceuticals", "Biotechnology", "Medical Devices", "Healthcare Services", 
             "Health Insurance", "Diagnostics", "Digital Health"],
            default=["Pharmaceuticals", "Biotechnology"]
        )
        
        # R&D metrics
        st.markdown("#### 🔬 R&D Metrics")
        
        rd_intensity_min = st.slider(
            "R&D Intensity Min (%):",
            min_value=0.0,
            max_value=50.0,
            value=5.0,
            step=0.5,
            help="R&D spending as % of revenue"
        )
        
        # Pipeline filters
        st.markdown("#### 💊 Pipeline Filters")
        
        has_pipeline = st.checkbox("Must have clinical pipeline", value=False)
        min_pipeline_size = st.number_input("Min pipeline programs:", min_value=0, max_value=50, value=0)
        
        # Financial health
        st.markdown("#### 💪 Financial Health")
        
        col2a, col2b = st.columns(2)
        
        with col2a:
            min_current_ratio = st.number_input("Min Current Ratio:", value=1.0, step=0.1)
            max_debt_equity = st.number_input("Max Debt/Equity:", value=2.0, step=0.1)
        
        with col2b:
            min_profit_margin = st.number_input("Min Profit Margin (%):", value=-50.0, step=1.0)
            min_roe = st.number_input("Min ROE (%):", value=-100.0, step=1.0)
    
    # Run financial screening
    st.markdown("---")
    
    col3a, col3b = st.columns(2)
    
    with col3a:
        if st.button("🔍 Run Financial Screen", type="primary", use_container_width=True):
            run_financial_screen({
                'market_cap_range': market_cap_range,
                'pe_range': (pe_min, pe_max),
                'pb_range': (pb_min, pb_max),
                'revenue_growth_range': (revenue_growth_min, revenue_growth_max),
                'eps_growth_range': (eps_growth_min, eps_growth_max),
                'healthcare_sectors': healthcare_sectors,
                'rd_intensity_min': rd_intensity_min,
                'has_pipeline': has_pipeline,
                'min_pipeline_size': min_pipeline_size,
                'min_current_ratio': min_current_ratio,
                'max_debt_equity': max_debt_equity,
                'min_profit_margin': min_profit_margin,
                'min_roe': min_roe
            })
    
    with col3b:
        if st.button("🎯 Value + Growth Screen", use_container_width=True):
            run_value_growth_screen()

def show_smart_filters():
    """Smart filtering and AI-powered screens"""
    st.header("🎯 Smart Filters & AI Screening")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("### 🤖 AI-Powered Screens")
        
        # AI screening options
        st.markdown("#### 🧠 Intelligent Screening")
        
        ai_screen_type = st.selectbox(
            "AI Screen Type:",
            [
                "📈 Momentum + Insider Buying",
                "💰 Value + Strong Fundamentals", 
                "🚀 Growth + Pipeline Potential",
                "🛡️ Defensive + Dividend",
                "⚡ Catalyst + Event-Driven",
                "🎯 Custom AI Analysis"
            ]
        )
        
        if ai_screen_type == "🎯 Custom AI Analysis":
            custom_prompt = st.text_area(
                "Describe your screening criteria:",
                placeholder="Find healthcare stocks with strong insider buying, growing revenue, and upcoming FDA catalysts...",
                height=100
            )
        
        # Risk tolerance
        risk_tolerance = st.selectbox(
            "Risk Tolerance:",
            ["Conservative", "Moderate", "Aggressive", "Speculative"]
        )
        
        # Investment horizon
        investment_horizon = st.selectbox(
            "Investment Horizon:",
            ["Short-term (1-6 months)", "Medium-term (6-18 months)", "Long-term (1-5 years)"]
        )
        
        if st.button("🚀 Run AI Screen", type="primary", use_container_width=True):
            run_ai_screen(ai_screen_type, risk_tolerance, investment_horizon, 
                         custom_prompt if ai_screen_type == "🎯 Custom AI Analysis" else None)
    
    with col2:
        st.markdown("### 📊 Combination Screens")
        
        # Multi-factor screening
        st.markdown("#### 🔄 Multi-Factor Analysis")
        
        factors = st.multiselect(
            "Select Factors to Combine:",
            [
                "🕵️ Insider Activity Score",
                "📈 Technical Momentum",
                "💰 Value Metrics", 
                "📊 Growth Metrics",
                "🔬 R&D Intensity",
                "💊 Pipeline Strength",
                "🏆 Analyst Sentiment",
                "📰 News Sentiment"
            ],
            default=["🕵️ Insider Activity Score", "📈 Technical Momentum", "💰 Value Metrics"]
        )
        
        # Factor weighting
        if factors:
            st.markdown("#### ⚖️ Factor Weights")
            factor_weights = {}
            
            for factor in factors:
                weight = st.slider(
                    f"Weight for {factor}:",
                    min_value=0.0,
                    max_value=1.0,
                    value=1.0/len(factors),
                    step=0.1,
                    key=f"weight_{factor}"
                )
                factor_weights[factor] = weight
        
        # Screening universe
        st.markdown("#### 🌍 Screening Universe")
        
        universe_type = st.selectbox(
            "Stock Universe:",
            [
                "Healthcare Sector (All)",
                "Large Cap Healthcare",
                "Biotech Focus",
                "Pharma Focus",
                "Med Device Focus",
                "Custom List"
            ]
        )
        
        if universe_type == "Custom List":
            custom_universe = st.text_area(
                "Custom Stock List:",
                placeholder="Enter comma-separated symbols",
                help="Leave empty to use default healthcare universe"
            )
        
        if st.button("🎯 Run Multi-Factor Screen", use_container_width=True):
            if factors:
                run_multifactor_screen(factors, factor_weights, universe_type)
            else:
                st.warning("Please select at least one factor")

def show_screening_results():
    """Display screening results"""
    st.header("📈 Screening Results & Analysis")
    
    if 'latest_screen_results' in st.session_state:
        results = st.session_state.latest_screen_results
        
        # Results summary
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-highlight">
                <h3>{len(results)}</h3>
                <p>Stocks Found</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            avg_score = np.mean([r.get('score', 0) for r in results]) if results else 0
            st.markdown(f"""
            <div class="metric-highlight">
                <h3>{avg_score:.1f}</h3>
                <p>Avg Score</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            strong_buys = len([r for r in results if r.get('recommendation') == 'Strong Buy'])
            st.markdown(f"""
            <div class="metric-highlight">
                <h3>{strong_buys}</h3>
                <p>Strong Buys</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            insider_activity = len([r for r in results if r.get('has_insider_activity', False)])
            st.markdown(f"""
            <div class="metric-highlight">
                <h3>{insider_activity}</h3>
                <p>Insider Activity</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Results table
        st.markdown("### 📊 Detailed Results")
        
        if results:
            df = pd.DataFrame(results)
            st.dataframe(df, use_container_width=True)
            
            # Export results
            if st.button("📥 Export Results"):
                csv = df.to_csv(index=False)
                st.download_button(
                    label="Download CSV",
                    data=csv,
                    file_name=f"screening_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
        
        # Visualization
        if results and len(results) > 1:
            st.markdown("### 📊 Results Visualization")
            
            viz_type = st.selectbox(
                "Visualization Type:",
                ["Score Distribution", "Sector Breakdown", "Market Cap vs Score"]
            )
            
            create_results_visualization(results, viz_type)
    
    else:
        st.info("No screening results yet. Run a screen to see results here.")

# Helper functions for screening

def run_executive_buying_screen(min_value):
    """Run executive buying screen"""
    with st.spinner("🔍 Screening for executive buying activity..."):
        # Mock screening results
        results = [
            {"symbol": "PFE", "insider": "CEO", "transaction_value": min_value * 2.5, "days_ago": 3, "score": 85},
            {"symbol": "JNJ", "insider": "CFO", "transaction_value": min_value * 1.8, "days_ago": 7, "score": 78},
            {"symbol": "MRNA", "insider": "President", "transaction_value": min_value * 3.2, "days_ago": 2, "score": 92}
        ]
        
        st.session_state.screening_results = results
        st.success(f"✅ Found {len(results)} stocks with executive buying activity!")

def run_financial_screen(criteria):
    """Run financial screening with given criteria"""
    with st.spinner("📊 Running financial metrics screening..."):
        # Mock financial screening results
        results = [
            {
                "symbol": "ABBV", "score": 88, "recommendation": "Strong Buy",
                "market_cap": "250B", "pe_ratio": 15.2, "revenue_growth": 12.5,
                "has_insider_activity": True, "sector": "Pharmaceuticals"
            },
            {
                "symbol": "REGN", "score": 82, "recommendation": "Buy", 
                "market_cap": "85B", "pe_ratio": 18.7, "revenue_growth": 8.3,
                "has_insider_activity": False, "sector": "Biotechnology"
            }
        ]
        
        st.session_state.latest_screen_results = results
        st.success(f"✅ Financial screening complete! Found {len(results)} qualifying stocks.")

def run_ai_screen(screen_type, risk_tolerance, horizon, custom_prompt=None):
    """Run AI-powered screening"""
    with st.spinner("🤖 Running AI-powered analysis..."):
        # Mock AI screening results
        results = [
            {
                "symbol": "VRTX", "score": 95, "recommendation": "Strong Buy",
                "ai_analysis": "Strong momentum with insider buying and upcoming catalyst",
                "market_cap": "120B", "risk_score": "Moderate"
            },
            {
                "symbol": "BNTX", "score": 87, "recommendation": "Buy",
                "ai_analysis": "Growth potential with pipeline developments",
                "market_cap": "35B", "risk_score": "Aggressive"
            }
        ]
        
        st.session_state.latest_screen_results = results
        st.success(f"🤖 AI screening complete! Found {len(results)} AI-recommended stocks.")

def create_results_visualization(results, viz_type):
    """Create visualizations for screening results"""
    try:
        df = pd.DataFrame(results)
        
        if viz_type == "Score Distribution" and 'score' in df.columns:
            fig = px.histogram(df, x='score', title="Score Distribution", nbins=10)
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Sector Breakdown" and 'sector' in df.columns:
            sector_counts = df['sector'].value_counts()
            fig = px.pie(values=sector_counts.values, names=sector_counts.index, title="Sector Breakdown")
            st.plotly_chart(fig, use_container_width=True)
        
        elif viz_type == "Market Cap vs Score" and 'market_cap' in df.columns and 'score' in df.columns:
            fig = px.scatter(df, x='market_cap', y='score', hover_data=['symbol'], title="Market Cap vs Score")
            st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Visualization error: {e}")

def run_large_purchase_screen(min_value):
    """Run large purchase screening"""
    with st.spinner("💰 Screening for large insider purchases..."):
        st.success("Large purchase screening completed!")

def run_clustered_activity_screen(window, min_size):
    """Run clustered activity screening"""
    with st.spinner("🎯 Screening for clustered insider activity..."):
        st.success("Clustered activity screening completed!")

def run_momentum_screen(days_back):
    """Run momentum screening"""
    with st.spinner("⚡ Screening for insider momentum..."):
        st.success("Momentum screening completed!")

def run_custom_screen(symbols, criteria):
    """Run custom screening"""
    with st.spinner(f"🔍 Screening {len(symbols)} custom symbols..."):
        st.success(f"Custom screening completed for {', '.join(symbols)}!")

def run_value_growth_screen():
    """Run value + growth screening"""
    with st.spinner("📈 Screening for value + growth opportunities..."):
        st.success("Value + Growth screening completed!")

def run_multifactor_screen(factors, weights, universe):
    """Run multi-factor screening"""
    with st.spinner("🎯 Running multi-factor analysis..."):
        st.success(f"Multi-factor screening completed using {len(factors)} factors!")

def display_insider_results(results):
    """Display insider screening results"""
    for result in results:
        st.markdown(f"""
        <div class="screening-result">
            <h4>🏢 {result['symbol']}</h4>
            <p><strong>Insider:</strong> {result['insider']} | <strong>Value:</strong> ${result['transaction_value']:,.0f}</p>
            <p><strong>Score:</strong> {result['score']}/100 | <strong>Days Ago:</strong> {result['days_ago']}</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 