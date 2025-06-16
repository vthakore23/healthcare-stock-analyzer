import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Portfolio Tracker - Healthcare Analyzer",
    page_icon="📈",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .portfolio-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .holding-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .gain { color: #28a745; font-weight: bold; }
    .loss { color: #dc3545; font-weight: bold; }
    .neutral { color: #6c757d; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = []

def main():
    st.markdown("""
    <div class="portfolio-header">
        <h1>📈 Healthcare Portfolio Tracker</h1>
        <p style="font-size: 1.2rem;">Monitor your healthcare investment portfolio</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📊 Portfolio Overview", "➕ Add Holdings", "📋 Holdings Manager"])
    
    with tab1:
        show_portfolio_overview()
    
    with tab2:
        show_add_holdings()
    
    with tab3:
        show_holdings_manager()

def show_portfolio_overview():
    """Show portfolio overview and performance"""
    if not st.session_state.portfolio:
        st.info("No holdings in portfolio. Add holdings in the 'Add Holdings' tab.")
        show_demo_portfolio()
        return
    
    st.markdown("### 📊 Portfolio Performance")
    
    # Calculate portfolio metrics
    portfolio_data = calculate_portfolio_metrics()
    
    # Display key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💰 Total Value", f"${portfolio_data['total_value']:,.2f}")
    
    with col2:
        st.metric("📈 Total Gain/Loss", 
                 f"${portfolio_data['total_gain_loss']:,.2f}",
                 delta=f"{portfolio_data['total_return_pct']:+.2f}%")
    
    with col3:
        st.metric("🏢 Holdings", len(st.session_state.portfolio))
    
    with col4:
        st.metric("💊 Healthcare %", f"{portfolio_data['healthcare_pct']:.1f}%")
    
    # Portfolio allocation chart
    create_allocation_charts(portfolio_data)
    
    # Performance chart
    create_performance_chart()
    
    # Holdings table
    show_holdings_table()

def show_add_holdings():
    """Interface to add new holdings"""
    st.markdown("### ➕ Add New Holding")
    
    col1, col2 = st.columns(2)
    
    with col1:
        ticker = st.text_input("Ticker Symbol:", placeholder="e.g., MRNA").upper()
        shares = st.number_input("Number of Shares:", min_value=0.0, step=1.0)
        purchase_price = st.number_input("Purchase Price per Share:", min_value=0.0, step=0.01)
    
    with col2:
        purchase_date = st.date_input("Purchase Date:", value=datetime.now().date())
        holding_type = st.selectbox("Holding Type:", ["Long", "Short"])
        notes = st.text_area("Notes (optional):", placeholder="Investment thesis, target price, etc.")
    
    if st.button("➕ Add Holding", type="primary", use_container_width=True):
        if ticker and shares > 0 and purchase_price > 0:
            add_holding(ticker, shares, purchase_price, purchase_date, holding_type, notes)
            st.success(f"✅ Added {shares} shares of {ticker} to portfolio")
            st.rerun()
        else:
            st.error("Please fill in all required fields")

def show_holdings_manager():
    """Manage existing holdings"""
    st.markdown("### 📋 Holdings Manager")
    
    if not st.session_state.portfolio:
        st.info("No holdings to manage. Add holdings first.")
        return
    
    # Holdings table with edit/delete options
    for i, holding in enumerate(st.session_state.portfolio):
        with st.expander(f"{holding['ticker']} - {holding['shares']} shares"):
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                st.write(f"**Purchase Price:** ${holding['purchase_price']:.2f}")
                st.write(f"**Purchase Date:** {holding['purchase_date']}")
                st.write(f"**Type:** {holding['type']}")
                if holding['notes']:
                    st.write(f"**Notes:** {holding['notes']}")
            
            with col2:
                # Get current price
                current_price = get_current_price(holding['ticker'])
                if current_price:
                    current_value = holding['shares'] * current_price
                    cost_basis = holding['shares'] * holding['purchase_price']
                    gain_loss = current_value - cost_basis
                    gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
                    
                    st.write(f"**Current Price:** ${current_price:.2f}")
                    st.write(f"**Current Value:** ${current_value:,.2f}")
                    
                    color_class = "gain" if gain_loss >= 0 else "loss"
                    st.markdown(f"**Gain/Loss:** <span class='{color_class}'>${gain_loss:+,.2f} ({gain_loss_pct:+.2f}%)</span>", 
                               unsafe_allow_html=True)
            
            with col3:
                if st.button(f"🗑️ Remove", key=f"remove_{i}"):
                    st.session_state.portfolio.pop(i)
                    st.success(f"Removed {holding['ticker']} from portfolio")
                    st.rerun()

def show_demo_portfolio():
    """Show demo portfolio for new users"""
    st.markdown("### 🎯 Demo Portfolio")
    st.info("Here's what your portfolio overview would look like with some holdings:")
    
    demo_holdings = [
        {"ticker": "MRNA", "shares": 100, "purchase_price": 150.00, "current_price": 180.50},
        {"ticker": "PFE", "shares": 200, "purchase_price": 45.00, "current_price": 42.30},
        {"ticker": "REGN", "shares": 50, "purchase_price": 600.00, "current_price": 720.80},
    ]
    
    # Demo metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_value = sum(h['shares'] * h['current_price'] for h in demo_holdings)
        st.metric("💰 Total Value", f"${total_value:,.2f}")
    
    with col2:
        cost_basis = sum(h['shares'] * h['purchase_price'] for h in demo_holdings)
        gain_loss = total_value - cost_basis
        st.metric("📈 Total Gain/Loss", f"${gain_loss:+,.2f}")
    
    with col3:
        st.metric("🏢 Holdings", len(demo_holdings))
    
    with col4:
        st.metric("💊 Healthcare %", "100.0%")
    
    # Demo holdings table
    df = pd.DataFrame(demo_holdings)
    df['Cost Basis'] = df['shares'] * df['purchase_price']
    df['Current Value'] = df['shares'] * df['current_price']
    df['Gain/Loss'] = df['Current Value'] - df['Cost Basis']
    df['Return %'] = (df['Gain/Loss'] / df['Cost Basis']) * 100
    
    st.dataframe(df[['ticker', 'shares', 'purchase_price', 'current_price', 'Current Value', 'Gain/Loss', 'Return %']], 
                use_container_width=True)

def add_holding(ticker: str, shares: float, purchase_price: float, purchase_date, holding_type: str, notes: str):
    """Add a new holding to the portfolio"""
    holding = {
        'ticker': ticker,
        'shares': shares,
        'purchase_price': purchase_price,
        'purchase_date': purchase_date,
        'type': holding_type,
        'notes': notes,
        'date_added': datetime.now()
    }
    st.session_state.portfolio.append(holding)

def calculate_portfolio_metrics():
    """Calculate portfolio performance metrics"""
    total_value = 0
    total_cost_basis = 0
    healthcare_value = 0
    
    healthcare_tickers = {
        "MRNA", "BNTX", "PFE", "JNJ", "MRK", "ABBV", "LLY", "REGN", "VRTX", "BIIB",
        "MDT", "ABT", "SYK", "ISRG", "DXCM", "UNH", "CVS", "CI", "LH", "DGX"
    }
    
    for holding in st.session_state.portfolio:
        current_price = get_current_price(holding['ticker'])
        if current_price:
            current_value = holding['shares'] * current_price
            cost_basis = holding['shares'] * holding['purchase_price']
            
            total_value += current_value
            total_cost_basis += cost_basis
            
            if holding['ticker'] in healthcare_tickers:
                healthcare_value += current_value
    
    total_gain_loss = total_value - total_cost_basis
    total_return_pct = (total_gain_loss / total_cost_basis) * 100 if total_cost_basis > 0 else 0
    healthcare_pct = (healthcare_value / total_value) * 100 if total_value > 0 else 0
    
    return {
        'total_value': total_value,
        'total_cost_basis': total_cost_basis,
        'total_gain_loss': total_gain_loss,
        'total_return_pct': total_return_pct,
        'healthcare_value': healthcare_value,
        'healthcare_pct': healthcare_pct
    }

def get_current_price(ticker: str) -> float:
    """Get current stock price"""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return info.get('currentPrice') or info.get('regularMarketPrice', 0)
    except:
        return 0

def create_allocation_charts(portfolio_data: dict):
    """Create portfolio allocation visualizations"""
    st.markdown("### 🥧 Portfolio Allocation")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Allocation by holding
        allocation_data = []
        for holding in st.session_state.portfolio:
            current_price = get_current_price(holding['ticker'])
            if current_price:
                current_value = holding['shares'] * current_price
                allocation_data.append({
                    'Ticker': holding['ticker'],
                    'Value': current_value,
                    'Percentage': (current_value / portfolio_data['total_value']) * 100
                })
        
        if allocation_data:
            df = pd.DataFrame(allocation_data)
            fig = px.pie(df, values='Value', names='Ticker', title="Allocation by Holding")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Healthcare vs Non-Healthcare
        healthcare_data = [
            {'Category': 'Healthcare', 'Value': portfolio_data['healthcare_value']},
            {'Category': 'Non-Healthcare', 'Value': portfolio_data['total_value'] - portfolio_data['healthcare_value']}
        ]
        
        df_hc = pd.DataFrame(healthcare_data)
        fig_hc = px.pie(df_hc, values='Value', names='Category', title="Healthcare vs Non-Healthcare")
        st.plotly_chart(fig_hc, use_container_width=True)

def create_performance_chart():
    """Create portfolio performance chart"""
    st.markdown("### 📈 Performance Overview")
    
    # This would typically show historical performance
    # For demo, showing gain/loss by holding
    performance_data = []
    
    for holding in st.session_state.portfolio:
        current_price = get_current_price(holding['ticker'])
        if current_price:
            current_value = holding['shares'] * current_price
            cost_basis = holding['shares'] * holding['purchase_price']
            gain_loss_pct = ((current_value - cost_basis) / cost_basis) * 100 if cost_basis > 0 else 0
            
            performance_data.append({
                'Ticker': holding['ticker'],
                'Return %': gain_loss_pct,
                'Gain/Loss $': current_value - cost_basis
            })
    
    if performance_data:
        df = pd.DataFrame(performance_data)
        
        fig = px.bar(
            df, 
            x='Ticker', 
            y='Return %',
            color='Return %',
            color_continuous_scale=['red', 'yellow', 'green'],
            title="Return by Holding"
        )
        st.plotly_chart(fig, use_container_width=True)

def show_holdings_table():
    """Show detailed holdings table"""
    st.markdown("### 📋 Holdings Details")
    
    holdings_data = []
    for holding in st.session_state.portfolio:
        current_price = get_current_price(holding['ticker'])
        if current_price:
            current_value = holding['shares'] * current_price
            cost_basis = holding['shares'] * holding['purchase_price']
            gain_loss = current_value - cost_basis
            gain_loss_pct = (gain_loss / cost_basis) * 100 if cost_basis > 0 else 0
            
            holdings_data.append({
                'Ticker': holding['ticker'],
                'Shares': holding['shares'],
                'Purchase Price': f"${holding['purchase_price']:.2f}",
                'Current Price': f"${current_price:.2f}",
                'Cost Basis': f"${cost_basis:,.2f}",
                'Current Value': f"${current_value:,.2f}",
                'Gain/Loss': f"${gain_loss:+,.2f}",
                'Return %': f"{gain_loss_pct:+.2f}%",
                'Purchase Date': holding['purchase_date']
            })
    
    if holdings_data:
        df = pd.DataFrame(holdings_data)
        st.dataframe(df, use_container_width=True)

if __name__ == "__main__":
    main()
