import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import numpy as np
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from streamlit_option_menu import option_menu
import warnings
warnings.filterwarnings('ignore')

# Add parent directory to path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

from medequity_utils.advanced_insider_screens import AdvancedInsiderScreens

# Page configuration
st.set_page_config(
    page_title="Advanced Insider Screens - MedEquity Analyzer",
    page_icon="🎯",
    layout="wide"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .advanced-header {
        background: linear-gradient(135deg, #7c3aed 0%, #2563eb 50%, #059669 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .screen-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #7c3aed;
        transition: all 0.3s ease;
    }
    
    .screen-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .edge-indicator {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.25rem;
    }
    
    .insider-metric {
        background: #fef3c7;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #f59e0b;
    }
    
    .conviction-high { border-left-color: #22c55e; background: #dcfce7; }
    .conviction-medium { border-left-color: #f59e0b; background: #fef3c7; }
    .conviction-low { border-left-color: #ef4444; background: #fee2e2; }
    
    .chart-container {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .real-time-badge {
        background: #059669;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #7c3aed, transparent);
        margin: 2rem 0;
        border: none;
    }
    
    .stock-highlight {
        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #f59e0b;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedInsiderScreensPage:
    """Advanced insider trading screens for investment edge"""
    
    def __init__(self):
        if 'advanced_screens' not in st.session_state:
            st.session_state.advanced_screens = AdvancedInsiderScreens()
        
        self.screener = st.session_state.advanced_screens

def main():
    st.markdown("""
    <div class="advanced-header">
        <h1>🎯 Advanced Insider Screens</h1>
        <p style="font-size: 1.3rem;">Professional-Grade Investment Edge Detection</p>
        <div class="real-time-badge">🔴 REAL-TIME SCREENS • 💡 EDGE GENERATION • 📊 INSTITUTIONAL QUALITY</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize page
    if 'advanced_page' not in st.session_state:
        st.session_state.advanced_page = AdvancedInsiderScreensPage()
    
    page = st.session_state.advanced_page
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["🚀 Run All Screens", "📊 Individual Stock Analysis", "📈 Price + Insider Charts", "💎 Screen Results"],
        icons=["rocket", "graph-up", "bar-chart", "gem"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#7c3aed", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#7c3aed"},
        }
    )
    
    if selected == "🚀 Run All Screens":
        show_run_all_screens(page)
    elif selected == "📊 Individual Stock Analysis":
        show_individual_analysis(page)
    elif selected == "📈 Price + Insider Charts":
        show_price_insider_charts(page)
    elif selected == "💎 Screen Results":
        show_screen_results(page)

def show_run_all_screens(page):
    """Show interface to run all edge-generating screens"""
    st.markdown("### 🚀 Run All Edge-Generating Screens")
    
    st.markdown("""
    <div class="screen-card">
        <h4>🎯 What These Screens Do</h4>
        <p><strong>🔥 Heavy Insider Accumulation</strong>: Find stocks where multiple insiders are buying significant amounts</p>
        <p><strong>💎 Smart Money Convergence</strong>: Identify stocks where both insiders and institutions are bullish</p>
        <p><strong>🎯 Undervalued with Insider Buying</strong>: Discover undervalued stocks with insider confidence</p>
        <p><strong>⚡ Momentum + Insider Activity</strong>: Catch stocks with price momentum backed by insider buying</p>
        <p><strong>🏆 Executive Confidence Play</strong>: Track C-suite executives putting their money where their mouth is</p>
        <p><strong>🔍 Hidden Gem Discovery</strong>: Uncover under-the-radar stocks with strong insider activity</p>
        <p><strong>⚠️ Insider Selling Alerts</strong>: Get warned about concerning insider selling patterns</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        if st.button("🚀 Run All Screens", type="primary", use_container_width=True):
            run_all_screens(page)
    
    # Display results if available
    if 'all_screen_results' in st.session_state and st.session_state.all_screen_results:
        display_all_screen_results(st.session_state.all_screen_results)

def run_all_screens(page):
    """Run all edge-generating screens"""
    with st.spinner("🔍 Running all edge-generating screens across the market..."):
        try:
            results = page.screener.run_edge_generating_screens()
            st.session_state.all_screen_results = results
            
            total_opportunities = sum(len(screen_results) for screen_results in results.values())
            st.success(f"✅ Screening complete! Found {total_opportunities} total opportunities across all screens")
            
        except Exception as e:
            st.error(f"Screening failed: {str(e)}")

def display_all_screen_results(results):
    """Display results from all screens"""
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    st.markdown("### 📊 Screening Results Summary")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_opportunities = sum(len(screen_results) for screen_results in results.values())
    screens_with_results = len([s for s in results.values() if len(s) > 0])
    
    with col1:
        st.metric("Total Opportunities", total_opportunities)
    
    with col2:
        st.metric("Active Screens", f"{screens_with_results}/7")
    
    with col3:
        # Find screen with most results
        max_screen = max(results.items(), key=lambda x: len(x[1]), default=("None", []))
        st.metric("Top Screen", max_screen[0].split(' ')[1] if max_screen[1] else "None")
    
    with col4:
        # Count high conviction opportunities (assuming they have conviction scores)
        high_conviction = 0
        for screen_results in results.values():
            for result in screen_results:
                if result.get('conviction_score', 0) >= 80:
                    high_conviction += 1
        st.metric("High Conviction", high_conviction)
    
    # Display each screen's results
    for screen_name, screen_results in results.items():
        if screen_results:
            st.markdown(f"#### {screen_name}")
            
            # Create results dataframe
            df_data = []
            for result in screen_results[:5]:  # Top 5 per screen
                df_data.append({
                    'Symbol': result['symbol'],
                    'Company': result.get('company_name', result['symbol'])[:40] + '...' if len(result.get('company_name', '')) > 40 else result.get('company_name', result['symbol']),
                    **{k: v for k, v in result.items() if k not in ['symbol', 'company_name'] and isinstance(v, (int, float, str))}
                })
            
            if df_data:
                df = pd.DataFrame(df_data)
                
                # Format numerical columns
                for col in df.columns:
                    if col in ['market_cap', 'total_executive_value', 'net_insider_value', 'largest_purchase']:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: f"${x:,.0f}" if isinstance(x, (int, float)) and x > 0 else x)
                    elif col in ['percent_market_cap_bought', 'percent_market_cap_sold']:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: f"{x:.3f}%" if isinstance(x, (int, float)) else x)
                    elif col in ['conviction_score', 'timing_score', 'pe_ratio', 'peg_ratio']:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: f"{x:.1f}" if isinstance(x, (int, float)) else x)
                
                st.dataframe(df, use_container_width=True)
                
                # Highlight top pick
                if len(screen_results) > 0:
                    top_pick = screen_results[0]
                    st.markdown(f"""
                    <div class="stock-highlight">
                        <h5>🎯 Top Pick: {top_pick['symbol']} - {top_pick.get('company_name', '')}</h5>
                        <p><strong>Why it's highlighted:</strong> {get_highlight_reason(screen_name, top_pick)}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.info(f"No opportunities found in {screen_name}")

def get_highlight_reason(screen_name, result):
    """Get explanation for why a stock is highlighted"""
    if "Heavy Insider Accumulation" in screen_name:
        return f"Exceptional insider buying: {result.get('insider_buyers', 0)} different insiders bought {result.get('percent_market_cap_bought', 0):.3f}% of market cap"
    elif "Smart Money Convergence" in screen_name:
        return f"Perfect alignment: {result.get('institutional_ownership', 0):.1f}% institutional ownership + {result.get('insider_buyers', 0)} insider buyers"
    elif "Undervalued" in screen_name:
        return f"Value + insider confidence: P/E {result.get('pe_ratio', 0):.1f}, PEG {result.get('peg_ratio', 0):.1f} with ${result.get('net_insider_value', 0):,.0f} net insider buying"
    elif "Momentum" in screen_name:
        return f"Strong momentum: {result.get('momentum_20d', 0):.1f}% gain in 20 days with insider validation"
    elif "Executive Confidence" in screen_name:
        return f"Leadership conviction: {result.get('executive_purchases', 0)} C-suite purchases totaling ${result.get('total_executive_value', 0):,.0f}"
    elif "Hidden Gem" in screen_name:
        return f"Under-the-radar opportunity: ${result.get('market_cap', 0):,.0f} market cap with {result.get('revenue_growth', 0):.1f}% growth + insider buying"
    elif "Selling Alert" in screen_name:
        return f"Warning: {result.get('insider_sellers', 0)} insiders sold {result.get('percent_market_cap_sold', 0):.3f}% of market cap"
    else:
        return "High-potential opportunity based on insider activity patterns"

def show_individual_analysis(page):
    """Show individual stock analysis with advanced metrics"""
    st.markdown("### 📊 Individual Stock Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Analysis Configuration")
        
        symbol = st.text_input("Stock Symbol:", value="PFE").upper()
        lookback_days = st.slider("Analysis Period (Days):", 30, 365, 90)
        
        if st.button("🔍 Analyze Stock", type="primary", use_container_width=True):
            analyze_individual_stock(page, symbol, lookback_days)
    
    with col2:
        if 'individual_analysis_advanced' in st.session_state:
            display_individual_analysis_advanced(st.session_state.individual_analysis_advanced)

def analyze_individual_stock(page, symbol, lookback_days):
    """Run advanced analysis on individual stock"""
    with st.spinner(f"🔍 Running comprehensive analysis on {symbol}..."):
        try:
            metrics = page.screener.get_comprehensive_insider_metrics(symbol, lookback_days)
            
            if 'error' in metrics:
                st.error(f"Analysis failed: {metrics['error']}")
                return
            
            st.session_state.individual_analysis_advanced = metrics
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

def display_individual_analysis_advanced(metrics):
    """Display advanced individual analysis results"""
    symbol = metrics['symbol']
    company_name = metrics.get('company_name', symbol)
    insider_metrics = metrics.get('insider_metrics', {})
    valuation_metrics = metrics.get('valuation_metrics', {})
    
    st.markdown(f"#### 📊 {symbol} - {company_name}")
    
    # Key metrics overview
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("Market Cap", f"${metrics.get('market_cap', 0):,.0f}")
        st.metric("Insider Buyers", insider_metrics.get('unique_insider_buyers', 0))
    
    with col2:
        st.metric("Current Price", f"${metrics.get('current_price', 0):.2f}")
        st.metric("Insider Sellers", insider_metrics.get('unique_insider_sellers', 0))
    
    with col3:
        st.metric("P/E Ratio", f"{valuation_metrics.get('pe_ratio', 0):.1f}")
        st.metric("% Market Cap Bought", f"{insider_metrics.get('percent_market_cap_bought', 0):.3f}%")
    
    with col4:
        st.metric("PEG Ratio", f"{valuation_metrics.get('peg_ratio', 0):.1f}")
        st.metric("Net Insider Value", f"${insider_metrics.get('net_insider_value', 0):,.0f}")
    
    with col5:
        st.metric("Revenue Growth", f"{valuation_metrics.get('revenue_growth', 0)*100:.1f}%")
        conviction = insider_metrics.get('insider_conviction_score', 0)
        st.metric("Conviction Score", f"{conviction:.0f}/100")
    
    # Detailed insider metrics
    st.markdown("#### 🎯 Advanced Insider Metrics")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("##### Buying Activity")
        
        conviction_class = "conviction-high" if conviction >= 70 else "conviction-medium" if conviction >= 50 else "conviction-low"
        
        st.markdown(f"""
        <div class="insider-metric {conviction_class}">
            <strong>Insider Conviction Score:</strong> {conviction:.1f}/100<br>
            <strong>Unique Buyers:</strong> {insider_metrics.get('unique_insider_buyers', 0)}<br>
            <strong>Total Shares Bought:</strong> {insider_metrics.get('total_shares_bought', 0):,}<br>
            <strong>Avg Purchase Size:</strong> ${insider_metrics.get('avg_purchase_size_usd', 0):,.0f}<br>
            <strong>Largest Purchase:</strong> ${insider_metrics.get('largest_purchase_usd', 0):,.0f}
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("##### Selling Activity")
        
        st.markdown(f"""
        <div class="insider-metric">
            <strong>Unique Sellers:</strong> {insider_metrics.get('unique_insider_sellers', 0)}<br>
            <strong>Total Shares Sold:</strong> {insider_metrics.get('total_shares_sold', 0):,}<br>
            <strong>Avg Sale Size:</strong> ${insider_metrics.get('avg_sale_size_usd', 0):,.0f}<br>
            <strong>Largest Sale:</strong> ${insider_metrics.get('largest_sale_usd', 0):,.0f}<br>
            <strong>Buy/Sell Ratio:</strong> {insider_metrics.get('buy_sell_value_ratio', 0):.2f}
        </div>
        """, unsafe_allow_html=True)
    
    # Valuation vs Growth Analysis
    st.markdown("#### ⚖️ Valuation vs Growth Analysis")
    
    pe_ratio = valuation_metrics.get('pe_ratio', 0)
    peg_ratio = valuation_metrics.get('peg_ratio', 0)
    revenue_growth = valuation_metrics.get('revenue_growth', 0) * 100
    
    # Create valuation assessment
    valuation_assessment = assess_valuation(pe_ratio, peg_ratio, revenue_growth, insider_metrics)
    
    st.markdown(f"""
    <div class="metric-card">
        <h4>Valuation Assessment</h4>
        <p><strong>P/E Ratio:</strong> {pe_ratio:.1f} {'(Reasonable)' if 0 < pe_ratio < 25 else '(High)' if pe_ratio >= 25 else '(N/A)'}</p>
        <p><strong>PEG Ratio:</strong> {peg_ratio:.2f} {'(Attractive)' if 0 < peg_ratio < 1.5 else '(Fair)' if peg_ratio < 2.5 else '(Expensive)' if peg_ratio > 0 else '(N/A)'}</p>
        <p><strong>Revenue Growth:</strong> {revenue_growth:.1f}% {'(Strong)' if revenue_growth > 15 else '(Moderate)' if revenue_growth > 5 else '(Slow)'}</p>
        <p><strong>Overall Assessment:</strong> {valuation_assessment}</p>
    </div>
    """, unsafe_allow_html=True)

def assess_valuation(pe_ratio, peg_ratio, revenue_growth, insider_metrics):
    """Assess overall valuation attractiveness"""
    score = 0
    reasons = []
    
    # P/E assessment
    if 0 < pe_ratio < 15:
        score += 2
        reasons.append("Low P/E")
    elif 15 <= pe_ratio < 25:
        score += 1
        reasons.append("Reasonable P/E")
    
    # PEG assessment
    if 0 < peg_ratio < 1.0:
        score += 2
        reasons.append("Excellent PEG")
    elif 1.0 <= peg_ratio < 1.5:
        score += 1
        reasons.append("Good PEG")
    
    # Growth assessment
    if revenue_growth > 15:
        score += 2
        reasons.append("Strong growth")
    elif revenue_growth > 5:
        score += 1
        reasons.append("Moderate growth")
    
    # Insider confidence
    conviction = insider_metrics.get('insider_conviction_score', 0)
    if conviction >= 70:
        score += 2
        reasons.append("High insider confidence")
    elif conviction >= 50:
        score += 1
        reasons.append("Moderate insider confidence")
    
    # Final assessment
    if score >= 6:
        return f"🟢 Highly Attractive - {', '.join(reasons)}"
    elif score >= 4:
        return f"🟡 Moderately Attractive - {', '.join(reasons)}"
    elif score >= 2:
        return f"🟠 Fair Value - {', '.join(reasons)}"
    else:
        return f"🔴 Potentially Overvalued - Limited positive factors"

def show_price_insider_charts(page):
    """Show price charts with insider activity overlay"""
    st.markdown("### 📈 Price + Insider Activity Charts")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("#### Chart Configuration")
        
        symbol = st.text_input("Stock Symbol:", value="PFE", key="chart_symbol").upper()
        period = st.selectbox("Time Period:", ["3mo", "6mo", "1y", "2y"])
        
        if st.button("📊 Generate Chart", type="primary", use_container_width=True):
            generate_price_insider_chart(page, symbol, period)
    
    with col2:
        if 'price_insider_chart_data' in st.session_state:
            display_price_insider_chart(st.session_state.price_insider_chart_data)

def generate_price_insider_chart(page, symbol, period):
    """Generate price chart with insider activity overlay"""
    with st.spinner(f"📊 Generating chart for {symbol}..."):
        try:
            chart_data = page.screener.generate_price_insider_overlay_data(symbol, period)
            
            if 'error' in chart_data:
                st.error(f"Chart generation failed: {chart_data['error']}")
                return
            
            st.session_state.price_insider_chart_data = chart_data
            
        except Exception as e:
            st.error(f"Chart generation failed: {str(e)}")

def display_price_insider_chart(chart_data):
    """Display price chart with insider activity"""
    symbol = chart_data['symbol']
    price_data = chart_data['price_data']
    insider_transactions = chart_data['insider_transactions']
    summary_stats = chart_data['summary_stats']
    
    # Summary stats
    st.markdown(f"#### 📊 {symbol} - Price Action with Insider Activity")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", summary_stats['total_transactions'])
    
    with col2:
        st.metric("Buy Transactions", summary_stats['buy_transactions'])
    
    with col3:
        st.metric("Sell Transactions", summary_stats['sell_transactions'])
    
    with col4:
        st.metric("Date Range", summary_stats['date_range'])
    
    # Create the chart
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f"{symbol} Price with Insider Activity", "Trading Volume"),
        row_heights=[0.7, 0.3]
    )
    
    # Price line
    fig.add_trace(
        go.Scatter(
            x=price_data.index,
            y=price_data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#1f77b4', width=2)
        ),
        row=1, col=1
    )
    
    # Add insider transactions as markers
    for transaction in insider_transactions:
        annotation = transaction['chart_annotation']
        
        fig.add_trace(
            go.Scatter(
                x=[annotation['x']],
                y=[annotation['y']],
                mode='markers',
                name=f"{transaction['insider_name']} - {transaction['transaction_type']}",
                marker=dict(
                    symbol=annotation['symbol'],
                    size=annotation['size'],
                    color=annotation['color'],
                    line=dict(color='white', width=1)
                ),
                hovertemplate=f"<b>{transaction['insider_name']}</b><br>" +
                             f"{transaction['title']}<br>" +
                             f"{transaction['transaction_type']}: {transaction['shares']:,} shares<br>" +
                             f"Value: ${transaction['value']:,.0f}<br>" +
                             f"Price: ${transaction['price_at_trade']:.2f}<br>" +
                             f"Performance Since: {transaction['performance_since']:+.1f}%<br>" +
                             f"Date: {transaction['date'].strftime('%Y-%m-%d')}<extra></extra>",
                showlegend=False
            ),
            row=1, col=1
        )
    
    # Volume bars
    fig.add_trace(
        go.Bar(
            x=price_data.index,
            y=price_data['Volume'],
            name='Volume',
            marker_color='rgba(31, 119, 180, 0.3)'
        ),
        row=2, col=1
    )
    
    fig.update_layout(
        title=f"{symbol} - Price Action with Insider Trading Activity",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Transaction details table
    if insider_transactions:
        st.markdown("#### 📋 Insider Transaction Details")
        
        transaction_data = []
        for tx in insider_transactions:
            transaction_data.append({
                'Date': tx['date'].strftime('%Y-%m-%d'),
                'Insider': tx['insider_name'],
                'Title': tx['title'],
                'Type': tx['transaction_type'],
                'Shares': f"{tx['shares']:,}",
                'Price': f"${tx['price_at_trade']:.2f}",
                'Value': f"${tx['value']:,.0f}",
                'Performance Since': f"{tx['performance_since']:+.1f}%"
            })
        
        df = pd.DataFrame(transaction_data)
        
        # Color code performance
        def color_performance(val):
            if '+' in val:
                return 'background-color: #dcfce7; color: #166534'
            elif '-' in val:
                return 'background-color: #fee2e2; color: #dc2626'
            else:
                return ''
        
        styled_df = df.style.applymap(color_performance, subset=['Performance Since'])
        st.dataframe(styled_df, use_container_width=True)

def show_screen_results(page):
    """Show stored screen results for detailed analysis"""
    st.markdown("### 💎 Screen Results Analysis")
    
    if 'all_screen_results' not in st.session_state or not st.session_state.all_screen_results:
        st.info("No screen results available. Please run the screens first.")
        return
    
    results = st.session_state.all_screen_results
    
    # Screen selector
    screen_names = list(results.keys())
    selected_screen = st.selectbox("Select Screen for Detailed Analysis:", screen_names)
    
    if selected_screen and results[selected_screen]:
        screen_results = results[selected_screen]
        
        st.markdown(f"#### {selected_screen} - Detailed Results")
        
        # Show all results for selected screen
        for i, result in enumerate(screen_results):
            with st.expander(f"{result['symbol']} - {result.get('company_name', '')}"):
                
                # Display all metrics
                col1, col2 = st.columns(2)
                
                with col1:
                    for key, value in result.items():
                        if key not in ['symbol', 'company_name'] and isinstance(value, (int, float)):
                            if key in ['market_cap', 'total_executive_value', 'net_insider_value']:
                                st.write(f"**{key.title()}:** ${value:,.0f}")
                            elif key in ['percent_market_cap_bought', 'percent_market_cap_sold']:
                                st.write(f"**{key.title()}:** {value:.3f}%")
                            elif key in ['conviction_score', 'timing_score', 'pe_ratio', 'peg_ratio']:
                                st.write(f"**{key.title()}:** {value:.1f}")
                            else:
                                st.write(f"**{key.title()}:** {value}")
                
                with col2:
                    # Generate quick analysis button
                    if st.button(f"📊 Quick Analysis", key=f"analysis_{i}"):
                        quick_analysis_metrics = page.screener.get_comprehensive_insider_metrics(result['symbol'], 90)
                        if 'error' not in quick_analysis_metrics:
                            st.session_state[f'quick_analysis_{i}'] = quick_analysis_metrics
                    
                    # Show quick analysis if available
                    if f'quick_analysis_{i}' in st.session_state:
                        metrics = st.session_state[f'quick_analysis_{i}']
                        insider_metrics = metrics.get('insider_metrics', {})
                        
                        st.write("**Quick Analysis:**")
                        st.write(f"• Conviction Score: {insider_metrics.get('insider_conviction_score', 0):.0f}/100")
                        st.write(f"• Timing Score: {insider_metrics.get('timing_score', 0):.0f}/100")
                        st.write(f"• Buy/Sell Ratio: {insider_metrics.get('buy_sell_value_ratio', 0):.1f}")
    
    else:
        st.info(f"No results found for {selected_screen}")

if __name__ == "__main__":
    main() 