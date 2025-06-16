# Healthcare Screener Page

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import time

# Add the parent directory to the path to import custom modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from medequity_utils.dynamic_scraper import HealthcareScraper
    from medequity_utils.healthcare_classifier import classify_healthcare_company
    from medequity_utils.metrics_calculator import calculate_healthcare_metrics
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Healthcare Screener - Healthcare Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .screener-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .filter-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stock-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .score-excellent { color: #00C851; font-weight: bold; }
    .score-good { color: #33b5e5; font-weight: bold; }
    .score-average { color: #ffbb33; font-weight: bold; }
    .score-poor { color: #ff4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = HealthcareScraper()

if 'screener_results' not in st.session_state:
    st.session_state.screener_results = []

def main():
    st.markdown("""
    <div class="screener-header">
        <h1>🔍 Healthcare Stock Screener</h1>
        <p style="font-size: 1.2rem;">Discover and filter healthcare stocks with advanced criteria</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Quick Screens", "🔧 Custom Filters", "📊 Results Analysis"])
    
    with tab1:
        show_quick_screens()
    
    with tab2:
        show_custom_filters()
    
    with tab3:
        show_results_analysis()

def show_quick_screens():
    """Show pre-built quick screening options"""
    st.markdown("### 🚀 Pre-Built Screens")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="filter-card">
            <h3>🧬 High R&D Biotechs</h3>
            <p>Companies with >30% R&D intensity and strong pipeline</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Run High R&D Screen", key="high_rd_screen", use_container_width=True):
            run_quick_screen("high_rd")
    
    with col2:
        st.markdown("""
        <div class="filter-card">
            <h3>💰 Profitable Growth</h3>
            <p>Profitable companies with >15% revenue growth</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Run Profitable Growth Screen", key="profitable_growth_screen", use_container_width=True):
            run_quick_screen("profitable_growth")
    
    with col3:
        st.markdown("""
        <div class="filter-card">
            <h3>📈 Large Cap Leaders</h3>
            <p>Market cap >$50B with strong fundamentals</p>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🔍 Run Large Cap Screen", key="large_cap_screen", use_container_width=True):
            run_quick_screen("large_cap")

def show_custom_filters():
    """Show custom filtering interface"""
    st.markdown("### 🔧 Custom Screening Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🏷️ Company Characteristics")
        
        # Subsector filter
        subsectors = ["All", "Biotechnology", "Pharmaceuticals", "Medical Devices", 
                     "Healthcare Services", "Diagnostics", "Digital Health"]
        selected_subsector = st.selectbox("Subsector:", subsectors)
        
        # Market cap filter
        market_cap_range = st.select_slider(
            "Market Cap Range:",
            options=["Nano (<$300M)", "Micro ($300M-$2B)", "Small ($2B-$10B)", 
                    "Mid ($10B-$50B)", "Large ($50B+)", "All"],
            value="All"
        )
        
        # Growth stage filter
        growth_stages = ["All", "Early Stage", "Growth", "Mature", "Commercial"]
        selected_growth = st.selectbox("Growth Stage:", growth_stages)
    
    with col2:
        st.markdown("#### 📊 Financial Metrics")
        
        # Revenue filter
        revenue_min = st.number_input("Min Revenue (Billions):", min_value=0.0, value=0.0, step=0.1)
        
        # R&D Intensity filter
        rd_intensity_min = st.slider("Min R&D Intensity (%):", 0, 50, 0)
        
        # Profit margin filter
        profit_margin_min = st.slider("Min Profit Margin (%):", -50, 50, -50)
        
        # MedEquity Score filter
        medequity_score_min = st.slider("Min MedEquity Score:", 0, 100, 0)
    
    # Custom screen button
    if st.button("🚀 Run Custom Screen", type="primary", use_container_width=True):
        filters = {
            'subsector': selected_subsector,
            'market_cap_range': market_cap_range,
            'growth_stage': selected_growth,
            'revenue_min': revenue_min,
            'rd_intensity_min': rd_intensity_min,
            'profit_margin_min': profit_margin_min,
            'medequity_score_min': medequity_score_min
        }
        run_custom_screen(filters)

def show_results_analysis():
    """Show screening results and analysis"""
    if not st.session_state.screener_results:
        st.info("No screening results yet. Run a screen from the Quick Screens or Custom Filters tabs.")
        return
    
    st.markdown("### 📊 Screening Results")
    
    results = st.session_state.screener_results
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 Companies Found", len(results))
    
    with col2:
        avg_score = sum(r.get('medequity_score', 0) for r in results) / len(results) if results else 0
        st.metric("🎯 Avg MedEquity Score", f"{avg_score:.1f}")
    
    with col3:
        profitable_count = sum(1 for r in results if r.get('profit_margin', 0) > 0)
        st.metric("💰 Profitable", f"{profitable_count}/{len(results)}")
    
    with col4:
        high_rd_count = sum(1 for r in results if r.get('rd_intensity', 0) > 0.2)
        st.metric("🔬 High R&D", f"{high_rd_count}/{len(results)}")
    
    # Results table
    if results:
        df = create_results_dataframe(results)
        
        # Sort options
        sort_by = st.selectbox("Sort by:", 
                              ["MedEquity Score", "Market Cap", "Revenue", "R&D Intensity", "Profit Margin"])
        
        # Apply sorting
        sort_column_map = {
            "MedEquity Score": "MedEquity Score",
            "Market Cap": "Market Cap ($B)",
            "Revenue": "Revenue ($B)",
            "R&D Intensity": "R&D Intensity (%)",
            "Profit Margin": "Profit Margin (%)"
        }
        
        if sort_by in sort_column_map:
            df = df.sort_values(sort_column_map[sort_by], ascending=False)
        
        # Display table
        st.dataframe(df, use_container_width=True)
        
        # Charts
        create_results_charts(df)

def run_quick_screen(screen_type: str):
    """Run pre-built screening logic"""
    
    # Define healthcare stock universe (simplified for demo)
    healthcare_tickers = [
        # Biotechnology
        "MRNA", "BNTX", "REGN", "VRTX", "BIIB", "GILD", "AMGN",
        # Pharmaceuticals  
        "PFE", "JNJ", "MRK", "ABBV", "LLY", "BMY", "AZN",
        # Medical Devices
        "MDT", "ABT", "SYK", "ISRG", "DXCM", "BSX", "EW",
        # Healthcare Services
        "UNH", "CVS", "CI", "HUM", "ANTM",
        # Diagnostics
        "LH", "DGX", "ILMN", "TMO", "QGEN"
    ]
    
    with st.spinner(f"🔍 Running {screen_type} screen on {len(healthcare_tickers)} companies..."):
        
        results = []
        progress_bar = st.progress(0)
        
        # Screen stocks based on type
        for i, ticker in enumerate(healthcare_tickers):
            try:
                # Get basic data for screening
                stock_data = get_basic_stock_data(ticker)
                if stock_data and meets_screen_criteria(stock_data, screen_type):
                    results.append(stock_data)
                    
                progress_bar.progress((i + 1) / len(healthcare_tickers))
                
            except Exception as e:
                continue  # Skip problematic tickers
        
        progress_bar.empty()
        st.session_state.screener_results = results
        
        st.success(f"✅ Screen complete! Found {len(results)} companies matching criteria.")

def run_custom_screen(filters: dict):
    """Run custom screening with user-defined filters"""
    
    # Healthcare universe
    healthcare_tickers = [
        "MRNA", "BNTX", "REGN", "VRTX", "BIIB", "GILD", "AMGN",
        "PFE", "JNJ", "MRK", "ABBV", "LLY", "BMY", "AZN",
        "MDT", "ABT", "SYK", "ISRG", "DXCM", "BSX", "EW",
        "UNH", "CVS", "CI", "HUM", "ANTM",
        "LH", "DGX", "ILMN", "TMO", "QGEN"
    ]
    
    with st.spinner(f"🔍 Running custom screen on {len(healthcare_tickers)} companies..."):
        
        results = []
        progress_bar = st.progress(0)
        
        for i, ticker in enumerate(healthcare_tickers):
            try:
                stock_data = get_basic_stock_data(ticker)
                if stock_data and meets_custom_criteria(stock_data, filters):
                    results.append(stock_data)
                    
                progress_bar.progress((i + 1) / len(healthcare_tickers))
                
            except Exception as e:
                continue
        
        progress_bar.empty()
        st.session_state.screener_results = results
        
        st.success(f"✅ Custom screen complete! Found {len(results)} companies matching criteria.")

def get_basic_stock_data(ticker: str) -> dict:
    """Get basic stock data for screening"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or len(info) < 5:
            return None
        
        # Calculate basic metrics
        market_cap = info.get('marketCap', 0)
        revenue = info.get('totalRevenue', 0)
        profit_margin = info.get('profitMargins', 0)
        
        # Estimate R&D intensity (simplified)
        rd_expenses = info.get('researchAndDevelopment', 0)
        rd_intensity = (rd_expenses / revenue) if revenue and rd_expenses else 0
        
        # Simple scoring (for demo)
        medequity_score = calculate_simple_score(info, rd_intensity)
        
        return {
            'ticker': ticker,
            'name': info.get('longName', ticker),
            'market_cap': market_cap,
            'revenue': revenue,
            'profit_margin': profit_margin,
            'rd_intensity': rd_intensity,
            'medequity_score': medequity_score,
            'sector': info.get('sector', ''),
            'industry': info.get('industry', ''),
            'pe_ratio': info.get('trailingPE', 0),
            'current_price': info.get('currentPrice', 0)
        }
        
    except Exception as e:
        return None

def calculate_simple_score(info: dict, rd_intensity: float) -> float:
    """Calculate a simple MedEquity-style score for screening"""
    score = 50  # Base score
    
    # Market cap factor
    market_cap = info.get('marketCap', 0)
    if market_cap > 50e9:
        score += 10
    elif market_cap > 10e9:
        score += 5
    
    # Profitability factor
    profit_margin = info.get('profitMargins', 0)
    if profit_margin and profit_margin > 0.2:
        score += 15
    elif profit_margin and profit_margin > 0:
        score += 5
    
    # R&D factor
    if rd_intensity > 0.3:
        score += 10
    elif rd_intensity > 0.15:
        score += 5
    
    # Revenue growth factor
    revenue_growth = info.get('revenueGrowth', 0)
    if revenue_growth and revenue_growth > 0.2:
        score += 10
    elif revenue_growth and revenue_growth > 0:
        score += 5
    
    # Debt factor
    debt_to_equity = info.get('debtToEquity', 0)
    if debt_to_equity and debt_to_equity < 0.5:
        score += 5
    
    return min(max(score, 0), 100)

def meets_screen_criteria(data: dict, screen_type: str) -> bool:
    """Check if stock meets quick screen criteria"""
    
    if screen_type == "high_rd":
        return (data.get('rd_intensity', 0) > 0.25 and 
                data.get('medequity_score', 0) > 60)
    
    elif screen_type == "profitable_growth":
        return (data.get('profit_margin', 0) > 0.15 and 
                data.get('revenue', 0) > 1e9)
    
    elif screen_type == "large_cap":
        return (data.get('market_cap', 0) > 50e9 and 
                data.get('medequity_score', 0) > 65)
    
    return False

def meets_custom_criteria(data: dict, filters: dict) -> bool:
    """Check if stock meets custom filter criteria"""
    
    # Revenue filter
    if data.get('revenue', 0) < filters['revenue_min'] * 1e9:
        return False
    
    # R&D intensity filter
    if data.get('rd_intensity', 0) * 100 < filters['rd_intensity_min']:
        return False
    
    # Profit margin filter
    if data.get('profit_margin', 0) * 100 < filters['profit_margin_min']:
        return False
    
    # MedEquity score filter
    if data.get('medequity_score', 0) < filters['medequity_score_min']:
        return False
    
    # Market cap filter
    market_cap = data.get('market_cap', 0)
    if filters['market_cap_range'] != "All":
        if filters['market_cap_range'] == "Nano (<$300M)" and market_cap >= 300e6:
            return False
        elif filters['market_cap_range'] == "Micro ($300M-$2B)" and (market_cap < 300e6 or market_cap >= 2e9):
            return False
        elif filters['market_cap_range'] == "Small ($2B-$10B)" and (market_cap < 2e9 or market_cap >= 10e9):
            return False
        elif filters['market_cap_range'] == "Mid ($10B-$50B)" and (market_cap < 10e9 or market_cap >= 50e9):
            return False
        elif filters['market_cap_range'] == "Large ($50B+)" and market_cap < 50e9:
            return False
    
    return True

def create_results_dataframe(results: list) -> pd.DataFrame:
    """Create a formatted DataFrame from screening results"""
    
    df_data = []
    for result in results:
        df_data.append({
            'Ticker': result.get('ticker', ''),
            'Company': result.get('name', '')[:30] + '...' if len(result.get('name', '')) > 30 else result.get('name', ''),
            'MedEquity Score': result.get('medequity_score', 0),
            'Market Cap ($B)': result.get('market_cap', 0) / 1e9,
            'Revenue ($B)': result.get('revenue', 0) / 1e9,
            'R&D Intensity (%)': result.get('rd_intensity', 0) * 100,
            'Profit Margin (%)': result.get('profit_margin', 0) * 100,
            'P/E Ratio': result.get('pe_ratio', 0),
            'Price ($)': result.get('current_price', 0)
        })
    
    df = pd.DataFrame(df_data)
    
    # Format columns
    df['MedEquity Score'] = df['MedEquity Score'].round(1)
    df['Market Cap ($B)'] = df['Market Cap ($B)'].round(2)
    df['Revenue ($B)'] = df['Revenue ($B)'].round(2)
    df['R&D Intensity (%)'] = df['R&D Intensity (%)'].round(1)
    df['Profit Margin (%)'] = df['Profit Margin (%)'].round(1)
    df['P/E Ratio'] = df['P/E Ratio'].round(1)
    df['Price ($)'] = df['Price ($)'].round(2)
    
    return df

def create_results_charts(df: pd.DataFrame):
    """Create visualization charts for screening results"""
    
    st.markdown("### 📊 Results Visualization")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # MedEquity Score distribution
        fig1 = px.histogram(
            df, 
            x='MedEquity Score', 
            nbins=20,
            title="MedEquity Score Distribution",
            color_discrete_sequence=['#1f77b4']
        )
        fig1.update_layout(height=300)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Market Cap vs R&D Intensity scatter
        fig2 = px.scatter(
            df, 
            x='Market Cap ($B)', 
            y='R&D Intensity (%)',
            color='MedEquity Score',
            hover_data=['Ticker', 'Company'],
            title="Market Cap vs R&D Intensity",
            color_continuous_scale='Viridis'
        )
        fig2.update_layout(height=300)
        st.plotly_chart(fig2, use_container_width=True)
    
    # Top performers table
    st.markdown("### 🏆 Top Performers by MedEquity Score")
    top_performers = df.nlargest(10, 'MedEquity Score')[['Ticker', 'Company', 'MedEquity Score', 'Market Cap ($B)', 'R&D Intensity (%)']]
    st.dataframe(top_performers, use_container_width=True)

if __name__ == "__main__":
    main()
