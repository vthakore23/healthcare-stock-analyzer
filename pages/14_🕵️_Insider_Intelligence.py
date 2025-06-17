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

from medequity_utils.insider_intelligence import InsiderIntelligence

# Page configuration
st.set_page_config(
    page_title="Insider Intelligence - MedEquity Analyzer",
    page_icon="🕵️",
    layout="wide"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .insider-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 50%, #581c87 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .smart-money-card {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #1e3a8a;
    }
    
    .insider-signal {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
    
    .signal-high { border-left: 4px solid #ef4444; }
    .signal-medium { border-left: 4px solid #f59e0b; }
    .signal-low { border-left: 4px solid #10b981; }
    
    .score-circle {
        width: 120px;
        height: 120px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2rem;
        font-weight: bold;
        color: white;
        margin: 0 auto;
    }
    
    .trading-activity {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    .valuation-metrics {
        background: linear-gradient(135deg, #fef3c7 0%, #fed7aa 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
    }
    
    .real-time-badge {
        background: #10b981;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    
    .metric-highlight {
        font-size: 1.5rem;
        font-weight: 700;
        color: #1e3a8a;
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #1e3a8a, transparent);
        margin: 2rem 0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

class InsiderIntelligencePage:
    """Advanced insider trading intelligence dashboard"""
    
    def __init__(self):
        if 'insider_intelligence' not in st.session_state:
            st.session_state.insider_intelligence = InsiderIntelligence()
        
        self.insider_intel = st.session_state.insider_intelligence
        
        self.healthcare_stocks = [
            'PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'GSK', 'NVO', 'UNH', 'CVS',
            'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD', 'AMGN', 'ILMN', 'SGEN',
            'MDT', 'ABT', 'SYK', 'BSX', 'EW', 'ISRG', 'DXCM', 'HOLX', 'TMO', 'DHR',
            'LH', 'DGX', 'QGEN', 'A', 'TECH', 'IQV', 'VEEV', 'TDOC', 'DOCS', 'HIMS'
        ]

def main():
    st.markdown("""
    <div class="insider-header">
        <h1>🕵️ Insider Intelligence</h1>
        <p style="font-size: 1.3rem;">Smart Money Tracking & Analysis Platform</p>
        <div class="real-time-badge">🔴 LIVE INSIDER DATA • 📊 INSTITUTIONAL TRACKING • 🎯 SMART MONEY SIGNALS</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize page
    if 'insider_page' not in st.session_state:
        st.session_state.insider_page = InsiderIntelligencePage()
    
    page = st.session_state.insider_page
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["📊 Individual Analysis", "🔍 Insider Screens", "📈 Smart Money Charts", "⚖️ Valuation Analysis"],
        icons=["graph-up", "search", "trending-up", "calculator"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#1e3a8a", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#1e3a8a"},
        }
    )
    
    if selected == "📊 Individual Analysis":
        show_individual_analysis(page)
    elif selected == "🔍 Insider Screens":
        show_insider_screens(page)
    elif selected == "📈 Smart Money Charts":
        show_smart_money_charts(page)
    elif selected == "⚖️ Valuation Analysis":
        show_valuation_analysis(page)

def show_individual_analysis(page):
    """Show individual stock insider analysis"""
    st.markdown("### 📊 Individual Stock Analysis")
    
    col1, col2 = st.columns([2, 3])
    
    with col1:
        st.markdown("#### Stock Selection")
        
        # Stock input
        symbol = st.text_input("Enter Stock Symbol:", value="PFE", key="individual_symbol").upper()
        
        # Analysis parameters
        lookback_days = st.slider("Analysis Period (Days):", 30, 365, 90)
        
        if st.button("🔍 Analyze Insider Activity", type="primary", use_container_width=True):
            analyze_individual_stock(page, symbol, lookback_days)
    
    with col2:
        if 'individual_analysis' in st.session_state and st.session_state.individual_analysis:
            display_individual_results(st.session_state.individual_analysis)

def analyze_individual_stock(page, symbol, lookback_days):
    """Analyze individual stock insider activity"""
    with st.spinner(f"🔍 Analyzing insider activity for {symbol}..."):
        try:
            insider_data = page.insider_intel.get_insider_data(symbol, lookback_days)
            
            if 'error' in insider_data:
                st.error(f"Error analyzing {symbol}: {insider_data['error']}")
                return
            
            st.session_state.individual_analysis = insider_data
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

def display_individual_results(insider_data):
    """Display individual stock analysis results"""
    st.markdown("#### Analysis Results")
    
    symbol = insider_data['symbol']
    metrics = insider_data.get('metrics', {})
    smart_money_score = insider_data.get('smart_money_score', {})
    
    # Smart Money Score Display
    score = smart_money_score.get('score', 0)
    rating = smart_money_score.get('rating', 'Unknown')
    color = smart_money_score.get('color', '#94a3b8')
    
    st.markdown(f"""
    <div class="smart-money-card">
        <h3>{symbol} - Smart Money Analysis</h3>
        <div class="score-circle" style="background: {color};">
            {score}
        </div>
        <p style="text-align: center; font-size: 1.2rem; font-weight: 600; margin-top: 1rem;">
            {rating}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Transactions", metrics.get('total_transactions', 0))
        st.metric("Insider Purchases", metrics.get('purchase_transactions', 0))
    
    with col2:
        st.metric("Insider Sales", metrics.get('sale_transactions', 0))
        buy_sell_ratio = metrics.get('buy_sell_ratio', 0)
        st.metric("Buy/Sell Ratio", f"{buy_sell_ratio:.2f}")
    
    with col3:
        net_activity = metrics.get('net_insider_activity', 0)
        st.metric("Net Activity", f"${net_activity:,.0f}")
        sentiment = metrics.get('insider_sentiment', 'Neutral')
        st.metric("Sentiment", sentiment)
    
    with col4:
        confidence = metrics.get('confidence_score', 0)
        st.metric("Confidence Score", f"{confidence:.1f}")
        exec_txns = metrics.get('executive_transactions', 0)
        st.metric("Executive Activity", exec_txns)
    
    # Signals
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🚨 Risk Signals")
        risk_signals = insider_data.get('risk_signals', [])
        if risk_signals:
            for signal in risk_signals:
                severity_class = f"signal-{signal['severity'].lower()}"
                st.markdown(f"""
                <div class="insider-signal {severity_class}">
                    <strong>{signal['type']}</strong><br>
                    {signal['description']}<br>
                    <small>Confidence: {signal['confidence']}%</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant risk signals detected")
    
    with col2:
        st.markdown("#### 🎯 Opportunity Signals")
        opportunity_signals = insider_data.get('opportunity_signals', [])
        if opportunity_signals:
            for signal in opportunity_signals:
                severity_class = f"signal-{signal['severity'].lower()}"
                st.markdown(f"""
                <div class="insider-signal {severity_class}">
                    <strong>{signal['type']}</strong><br>
                    {signal['description']}<br>
                    <small>Confidence: {signal['confidence']}%</small>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No significant opportunity signals detected")
    
    # Insider Transactions Table
    st.markdown("#### 📋 Recent Insider Transactions")
    insider_trades = insider_data.get('insider_trades', [])
    
    if insider_trades:
        trades_df = pd.DataFrame(insider_trades)
        trades_df['value_formatted'] = trades_df['value'].apply(lambda x: f"${x:,.0f}")
        trades_df['shares_formatted'] = trades_df['shares'].apply(lambda x: f"{x:,}")
        
        display_cols = ['date', 'insider_name', 'title', 'transaction_type', 'shares_formatted', 'price', 'value_formatted']
        st.dataframe(
            trades_df[display_cols].rename(columns={
                'date': 'Date',
                'insider_name': 'Insider',
                'title': 'Title',
                'transaction_type': 'Type',
                'shares_formatted': 'Shares',
                'price': 'Price',
                'value_formatted': 'Value'
            }),
            use_container_width=True
        )
    else:
        st.info("No recent insider transactions found")

def show_insider_screens(page):
    """Show insider trading screens"""
    st.markdown("### 🔍 Insider Trading Screens")
    
    # Screen selection
    screens = page.insider_intel.get_insider_screening_filters()
    selected_screen = st.selectbox("Select Screen:", list(screens.keys()))
    
    screen_info = screens[selected_screen]
    st.info(f"**{selected_screen}**: {screen_info['description']}")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("#### Screen Parameters")
        
        # Customize screen parameters
        if st.checkbox("Customize Parameters"):
            st.markdown("**Filter Adjustments:**")
            
            min_market_cap = st.number_input("Min Market Cap ($B):", value=1.0, min_value=0.1, step=0.5)
            max_lookback = st.number_input("Max Lookback Days:", value=90, min_value=30, max_value=365, step=15)
            min_confidence = st.slider("Min Confidence Score:", 0, 100, 50)
        
        if st.button("🚀 Run Screen", type="primary", use_container_width=True):
            run_insider_screen(page, selected_screen)
    
    with col2:
        if 'screen_results' in st.session_state and st.session_state.screen_results:
            display_screen_results(st.session_state.screen_results, selected_screen)

def run_insider_screen(page, screen_name):
    """Run insider trading screen"""
    with st.spinner(f"🔍 Running {screen_name} across all stocks..."):
        try:
            results = page.insider_intel.screen_stocks_by_insider_activity(
                symbols=page.healthcare_stocks,
                screen_type=screen_name,
                max_workers=10
            )
            
            st.session_state.screen_results = results
            st.session_state.screen_name = screen_name
            
            if results:
                st.success(f"✅ Found {len(results)} matches for {screen_name}")
            else:
                st.warning(f"⚠️ No matches found for {screen_name}")
                
        except Exception as e:
            st.error(f"Screen failed: {str(e)}")

def display_screen_results(results, screen_name):
    """Display screening results"""
    st.markdown(f"#### 📊 {screen_name} Results")
    
    if not results:
        st.info("No stocks match the current criteria")
        return
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Matches", len(results))
    
    with col2:
        avg_score = np.mean([r.get('smart_money_score', {}).get('score', 0) for r in results])
        st.metric("Avg Smart Money Score", f"{avg_score:.1f}")
    
    with col3:
        high_confidence = len([r for r in results if r.get('smart_money_score', {}).get('score', 0) >= 70])
        st.metric("High Confidence", high_confidence)
    
    with col4:
        opportunities = sum(len(r.get('opportunity_signals', [])) for r in results)
        st.metric("Total Opportunities", opportunities)
    
    # Results table
    results_data = []
    for result in results:
        smart_money = result.get('smart_money_score', {})
        metrics = result.get('insider_metrics', {})
        
        results_data.append({
            'Symbol': result['symbol'],
            'Company': result['company_name'][:40] + '...' if len(result['company_name']) > 40 else result['company_name'],
            'Smart Money Score': smart_money.get('score', 0),
            'Rating': smart_money.get('rating', 'Unknown'),
            'Insider Purchases': metrics.get('purchase_transactions', 0),
            'Net Activity': f"${metrics.get('net_insider_activity', 0):,.0f}",
            'Confidence': f"{metrics.get('confidence_score', 0):.1f}",
            'Opportunities': len(result.get('opportunity_signals', [])),
            'Risks': len(result.get('risk_signals', []))
        })
    
    if results_data:
        results_df = pd.DataFrame(results_data)
        
        # Color code the ratings
        def color_rating(val):
            color_map = {
                'Very Strong Buy': 'background-color: #22c55e; color: white',
                'Strong Buy': 'background-color: #16a34a; color: white',
                'Buy': 'background-color: #65a30d; color: white',
                'Hold': 'background-color: #ca8a04; color: white',
                'Sell': 'background-color: #dc2626; color: white',
                'Strong Sell': 'background-color: #991b1b; color: white'
            }
            return color_map.get(val, '')
        
        styled_df = results_df.style.applymap(color_rating, subset=['Rating'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Detailed view for selected stock
        selected_symbol = st.selectbox("Select for Detailed View:", [r['Symbol'] for r in results_data])
        
        if selected_symbol:
            selected_result = next(r for r in results if r['symbol'] == selected_symbol)
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("##### 🎯 Opportunity Signals")
                opportunities = selected_result.get('opportunity_signals', [])
                for opp in opportunities:
                    st.markdown(f"• **{opp['type']}**: {opp['description']} (Confidence: {opp['confidence']}%)")
            
            with col2:
                st.markdown("##### ⚠️ Risk Signals")
                risks = selected_result.get('risk_signals', [])
                for risk in risks:
                    st.markdown(f"• **{risk['type']}**: {risk['description']} (Confidence: {risk['confidence']}%)")

def show_smart_money_charts(page):
    """Show smart money charts and visualizations"""
    st.markdown("### 📈 Smart Money Charts")
    
    col1, col2 = st.columns([1, 3])
    
    with col1:
        st.markdown("#### Chart Configuration")
        
        symbol = st.text_input("Stock Symbol:", value="PFE").upper()
        chart_type = st.selectbox("Chart Type:", [
            "Price with Insider Activity",
            "Insider Buying vs Selling",
            "Smart Money Score Trend",
            "Institutional vs Insider Activity",
            "Volume vs Insider Activity"
        ])
        
        period = st.selectbox("Time Period:", ["3mo", "6mo", "1y", "2y"])
        
        if st.button("📊 Generate Chart", type="primary", use_container_width=True):
            generate_smart_money_chart(page, symbol, chart_type, period)
    
    with col2:
        if 'chart_data' in st.session_state:
            display_smart_money_chart(st.session_state.chart_data, st.session_state.chart_type)

def generate_smart_money_chart(page, symbol, chart_type, period):
    """Generate smart money charts"""
    with st.spinner(f"📊 Generating {chart_type} chart for {symbol}..."):
        try:
            # Get stock data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            # Get insider data
            lookback_days = {'3mo': 90, '6mo': 180, '1y': 365, '2y': 730}[period]
            insider_data = page.insider_intel.get_insider_data(symbol, lookback_days)
            
            chart_data = {
                'symbol': symbol,
                'price_data': hist,
                'insider_data': insider_data,
                'period': period
            }
            
            st.session_state.chart_data = chart_data
            st.session_state.chart_type = chart_type
            
        except Exception as e:
            st.error(f"Chart generation failed: {str(e)}")

def display_smart_money_chart(chart_data, chart_type):
    """Display the generated chart"""
    symbol = chart_data['symbol']
    price_data = chart_data['price_data']
    insider_data = chart_data['insider_data']
    
    if chart_type == "Price with Insider Activity":
        fig = create_price_insider_chart(symbol, price_data, insider_data)
    elif chart_type == "Insider Buying vs Selling":
        fig = create_buy_sell_chart(symbol, insider_data)
    elif chart_type == "Smart Money Score Trend":
        fig = create_score_trend_chart(symbol, insider_data)
    elif chart_type == "Institutional vs Insider Activity":
        fig = create_institutional_chart(symbol, insider_data)
    else:
        fig = create_volume_insider_chart(symbol, price_data, insider_data)
    
    st.plotly_chart(fig, use_container_width=True)

def create_price_insider_chart(symbol, price_data, insider_data):
    """Create price chart with insider activity overlay"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=(f"{symbol} Price with Insider Activity", "Trading Volume"),
        row_heights=[0.7, 0.3]
    )
    
    # Price chart
    fig.add_trace(
        go.Scatter(
            x=price_data.index,
            y=price_data['Close'],
            mode='lines',
            name='Price',
            line=dict(color='#1e3a8a', width=2)
        ),
        row=1, col=1
    )
    
    # Add insider transactions
    insider_trades = insider_data.get('insider_trades', [])
    
    for trade in insider_trades:
        trade_date = pd.to_datetime(trade['date'])
        if trade_date in price_data.index:
            price_at_trade = price_data.loc[trade_date, 'Close']
            
            color = '#22c55e' if trade['transaction_type'] == 'Purchase' else '#ef4444'
            symbol_marker = 'triangle-up' if trade['transaction_type'] == 'Purchase' else 'triangle-down'
            
            fig.add_trace(
                go.Scatter(
                    x=[trade_date],
                    y=[price_at_trade],
                    mode='markers',
                    name=f"{trade['insider_name']} - {trade['transaction_type']}",
                    marker=dict(
                        symbol=symbol_marker,
                        size=12,
                        color=color,
                        line=dict(color='white', width=1)
                    ),
                    hovertemplate=f"<b>{trade['insider_name']}</b><br>" +
                                 f"{trade['title']}<br>" +
                                 f"{trade['transaction_type']}: {trade['shares']:,} shares<br>" +
                                 f"Value: ${trade['value']:,.0f}<br>" +
                                 f"Date: {trade['date']}<extra></extra>",
                    showlegend=False
                ),
                row=1, col=1
            )
    
    # Volume chart
    fig.add_trace(
        go.Bar(
            x=price_data.index,
            y=price_data['Volume'],
            name='Volume',
            marker_color='rgba(30, 58, 138, 0.3)'
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
    
    return fig

def create_buy_sell_chart(symbol, insider_data):
    """Create insider buying vs selling chart"""
    insider_trades = insider_data.get('insider_trades', [])
    
    if not insider_trades:
        fig = go.Figure()
        fig.add_annotation(text="No insider trading data available", 
                          xref="paper", yref="paper", x=0.5, y=0.5)
        return fig
    
    # Aggregate by month
    trades_df = pd.DataFrame(insider_trades)
    trades_df['date'] = pd.to_datetime(trades_df['date'])
    trades_df['month'] = trades_df['date'].dt.to_period('M')
    
    monthly_activity = trades_df.groupby(['month', 'transaction_type'])['value'].sum().unstack(fill_value=0)
    
    fig = go.Figure()
    
    if 'Purchase' in monthly_activity.columns:
        fig.add_trace(
            go.Bar(
                x=monthly_activity.index.astype(str),
                y=monthly_activity['Purchase'],
                name='Insider Purchases',
                marker_color='#22c55e'
            )
        )
    
    if 'Sale' in monthly_activity.columns:
        fig.add_trace(
            go.Bar(
                x=monthly_activity.index.astype(str),
                y=-monthly_activity['Sale'],  # Negative for visual effect
                name='Insider Sales',
                marker_color='#ef4444'
            )
        )
    
    fig.update_layout(
        title=f"{symbol} - Monthly Insider Buying vs Selling",
        xaxis_title="Month",
        yaxis_title="Transaction Value ($)",
        barmode='relative',
        height=400
    )
    
    return fig

def create_score_trend_chart(symbol, insider_data):
    """Create smart money score trend chart"""
    # This would normally track score over time
    # For now, show current score breakdown
    
    smart_money_score = insider_data.get('smart_money_score', {})
    components = smart_money_score.get('components', {})
    
    fig = go.Figure()
    
    categories = list(components.keys())
    values = list(components.values())
    
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker_color=['#1e3a8a', '#3730a3', '#581c87', '#7c3aed']
        )
    )
    
    fig.update_layout(
        title=f"{symbol} - Smart Money Score Components",
        xaxis_title="Component",
        yaxis_title="Score Contribution",
        height=400
    )
    
    return fig

def create_institutional_chart(symbol, insider_data):
    """Create institutional vs insider activity chart"""
    institutional_data = insider_data.get('institutional_data', {})
    insider_metrics = insider_data.get('metrics', {})
    
    # Create comparison chart
    categories = ['Institutional Ownership %', 'Insider Buy/Sell Ratio', 'Executive Activity Score']
    
    institutional_ownership = institutional_data.get('total_institutional_ownership', 0)
    buy_sell_ratio = min(insider_metrics.get('buy_sell_ratio', 0) * 20, 100)  # Scale for visualization
    executive_score = min(insider_metrics.get('executive_transactions', 0) * 10, 100)  # Scale for visualization
    
    values = [institutional_ownership, buy_sell_ratio, executive_score]
    
    fig = go.Figure()
    
    fig.add_trace(
        go.Bar(
            x=categories,
            y=values,
            marker_color=['#1e3a8a', '#22c55e', '#f59e0b']
        )
    )
    
    fig.update_layout(
        title=f"{symbol} - Institutional vs Insider Activity",
        xaxis_title="Activity Type",
        yaxis_title="Score/Percentage",
        height=400
    )
    
    return fig

def create_volume_insider_chart(symbol, price_data, insider_data):
    """Create volume vs insider activity chart"""
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        subplot_titles=("Trading Volume", "Insider Activity Value"),
        row_heights=[0.6, 0.4]
    )
    
    # Volume chart
    fig.add_trace(
        go.Bar(
            x=price_data.index,
            y=price_data['Volume'],
            name='Volume',
            marker_color='rgba(30, 58, 138, 0.5)'
        ),
        row=1, col=1
    )
    
    # Insider activity
    insider_trades = insider_data.get('insider_trades', [])
    if insider_trades:
        trades_df = pd.DataFrame(insider_trades)
        trades_df['date'] = pd.to_datetime(trades_df['date'])
        
        for _, trade in trades_df.iterrows():
            color = '#22c55e' if trade['transaction_type'] == 'Purchase' else '#ef4444'
            
            fig.add_trace(
                go.Bar(
                    x=[trade['date']],
                    y=[trade['value']],
                    name=f"{trade['transaction_type']}",
                    marker_color=color,
                    showlegend=False
                ),
                row=2, col=1
            )
    
    fig.update_layout(
        title=f"{symbol} - Volume vs Insider Activity",
        height=500
    )
    
    return fig

def show_valuation_analysis(page):
    """Show valuation analysis with insider activity"""
    st.markdown("### ⚖️ Valuation Analysis")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### Analysis Parameters")
        
        symbols_input = st.text_area("Stock Symbols (comma-separated):", value="PFE,JNJ,MRK,ABBV,LLY")
        symbols = [s.strip().upper() for s in symbols_input.split(',')]
        
        metrics_to_analyze = st.multiselect(
            "Valuation Metrics:",
            ["P/E Ratio", "PEG Ratio", "Price to Book", "EV/Revenue", "Dividend Yield"],
            default=["P/E Ratio", "PEG Ratio"]
        )
        
        if st.button("📊 Run Valuation Analysis", type="primary", use_container_width=True):
            run_valuation_analysis(page, symbols, metrics_to_analyze)
    
    with col2:
        if 'valuation_results' in st.session_state:
            display_valuation_results(st.session_state.valuation_results)

def run_valuation_analysis(page, symbols, metrics):
    """Run valuation analysis with insider data"""
    with st.spinner("📊 Running valuation analysis..."):
        try:
            results = []
            
            for symbol in symbols:
                # Get stock data
                ticker = yf.Ticker(symbol)
                info = ticker.info
                
                # Get insider data
                insider_data = page.insider_intel.get_insider_data(symbol, 90)
                
                result = {
                    'symbol': symbol,
                    'name': info.get('longName', symbol),
                    'pe_ratio': info.get('trailingPE', 0),
                    'peg_ratio': info.get('pegRatio', 0),
                    'price_to_book': info.get('priceToBook', 0),
                    'ev_revenue': info.get('enterpriseToRevenue', 0),
                    'dividend_yield': info.get('dividendYield', 0) * 100 if info.get('dividendYield') else 0,
                    'market_cap': info.get('marketCap', 0),
                    'revenue_growth': info.get('revenueGrowth', 0) * 100 if info.get('revenueGrowth') else 0,
                    'smart_money_score': insider_data.get('smart_money_score', {}).get('score', 0),
                    'insider_sentiment': insider_data.get('metrics', {}).get('insider_sentiment', 'Neutral'),
                    'net_insider_activity': insider_data.get('metrics', {}).get('net_insider_activity', 0)
                }
                
                results.append(result)
            
            st.session_state.valuation_results = results
            
        except Exception as e:
            st.error(f"Valuation analysis failed: {str(e)}")

def display_valuation_results(results):
    """Display valuation analysis results"""
    st.markdown("#### 📊 Valuation Analysis Results")
    
    if not results:
        st.info("No valuation data available")
        return
    
    # Create comparison table
    df = pd.DataFrame(results)
    
    # Display key metrics
    display_cols = ['symbol', 'name', 'pe_ratio', 'peg_ratio', 'revenue_growth', 
                   'smart_money_score', 'insider_sentiment', 'net_insider_activity']
    
    display_df = df[display_cols].copy()
    display_df.columns = ['Symbol', 'Company', 'P/E Ratio', 'PEG Ratio', 'Revenue Growth %', 
                         'Smart Money Score', 'Insider Sentiment', 'Net Insider Activity']
    
    # Format numbers
    display_df['P/E Ratio'] = display_df['P/E Ratio'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
    display_df['PEG Ratio'] = display_df['PEG Ratio'].apply(lambda x: f"{x:.2f}" if x > 0 else "N/A")
    display_df['Revenue Growth %'] = display_df['Revenue Growth %'].apply(lambda x: f"{x:.1f}%" if x != 0 else "N/A")
    display_df['Net Insider Activity'] = display_df['Net Insider Activity'].apply(lambda x: f"${x:,.0f}")
    
    st.dataframe(display_df, use_container_width=True)
    
    # Valuation vs Growth scatter plot
    fig = px.scatter(
        df,
        x='pe_ratio',
        y='revenue_growth',
        size='smart_money_score',
        color='insider_sentiment',
        hover_data=['symbol', 'name'],
        title="Valuation vs Growth with Smart Money Overlay",
        labels={
            'pe_ratio': 'P/E Ratio',
            'revenue_growth': 'Revenue Growth %',
            'smart_money_score': 'Smart Money Score'
        }
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)
    
    # Value opportunities
    st.markdown("#### 💎 Value Opportunities")
    
    # Find stocks with good valuation metrics and positive insider activity
    opportunities = []
    for result in results:
        pe_ratio = result.get('pe_ratio', 999)
        peg_ratio = result.get('peg_ratio', 999)
        smart_money_score = result.get('smart_money_score', 0)
        net_activity = result.get('net_insider_activity', 0)
        
        # Define opportunity criteria
        if (pe_ratio > 0 and pe_ratio < 20 and 
            peg_ratio > 0 and peg_ratio < 1.5 and 
            smart_money_score > 60 and 
            net_activity > 0):
            opportunities.append(result)
    
    if opportunities:
        st.success(f"Found {len(opportunities)} value opportunities with positive insider sentiment!")
        
        for opp in opportunities:
            st.markdown(f"""
            <div class="valuation-metrics">
                <h4>{opp['symbol']} - {opp['name']}</h4>
                <div style="display: flex; justify-content: space-between;">
                    <div><strong>P/E:</strong> {opp['pe_ratio']:.2f}</div>
                    <div><strong>PEG:</strong> {opp['peg_ratio']:.2f}</div>
                    <div><strong>Smart Money:</strong> {opp['smart_money_score']:.1f}</div>
                    <div><strong>Insider Activity:</strong> ${opp['net_insider_activity']:,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("No clear value opportunities found with current criteria")

if __name__ == "__main__":
    main() 