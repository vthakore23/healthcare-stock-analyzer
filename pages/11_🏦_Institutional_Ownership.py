import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Add the parent directory to the path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from medequity_utils.institutional_ownership_tracker import InstitutionalOwnershipTracker
    import yfinance as yf
except ImportError as e:
    st.error(f"Import error: {e}")

# Page configuration
st.set_page_config(
    page_title="Institutional Ownership Tracker",
    page_icon="🏦",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
.ownership-header {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.institution-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #059669;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.smart-money-card {
    background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    border-left: 4px solid #22c55e;
}

.increase-card { border-left-color: #10b981; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); }
.decrease-card { border-left-color: #ef4444; background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); }
.neutral-card { border-left-color: #6b7280; background: linear-gradient(135deg, #f9fafb 0%, #f3f4f6 100%); }

.insider-activity {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #f59e0b;
}

.grade-a { color: #10b981; font-weight: bold; }
.grade-b { color: #f59e0b; font-weight: bold; }
.grade-c { color: #ef4444; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# Initialize tracker
if 'ownership_tracker' not in st.session_state:
    st.session_state.ownership_tracker = InstitutionalOwnershipTracker()

def main():
    st.markdown("""
    <div class="ownership-header">
        <h1>🏦 Institutional Ownership Tracker</h1>
        <p>Monitor Smart Money • Track Insider Activity • Analyze Institutional Flows</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Ownership Analysis", 
        "💰 Smart Money Score", 
        "👨‍💼 Insider Activity", 
        "🔄 Ownership Changes"
    ])
    
    with tab1:
        show_ownership_analysis()
    
    with tab2:
        show_smart_money_analysis()
    
    with tab3:
        show_insider_activity()
    
    with tab4:
        show_ownership_changes()

def show_ownership_analysis():
    """Show institutional ownership analysis"""
    st.markdown("### 📊 Institutional Ownership Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Healthcare Company Ticker:",
            placeholder="e.g., MRNA, PFE, JNJ, REGN",
            help="Enter a healthcare company ticker for ownership analysis",
            key="ownership_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🏦 Analyze Ownership", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        analyze_institutional_ownership(ticker)
    else:
        show_ownership_features()

def show_ownership_features():
    """Show ownership analysis features"""
    st.markdown("### 🌟 Institutional Ownership Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🏦 Institution Tracking**
        - Major institutional holders
        - Healthcare-focused funds
        - Hedge fund positions
        - ETF holdings analysis
        """)
    
    with col2:
        st.markdown("""
        **💡 Smart Money Metrics**
        - Quality institution scoring
        - Recent activity analysis
        - Healthcare specialization
        - Concentration metrics
        """)
    
    with col3:
        st.markdown("""
        **📈 Activity Monitoring**
        - Position changes tracking
        - Insider buying/selling
        - Flow direction analysis
        - Alert generation
        """)

def analyze_institutional_ownership(ticker: str):
    """Analyze institutional ownership"""
    with st.spinner(f"Analyzing institutional ownership for {ticker}..."):
        try:
            ownership_data = st.session_state.ownership_tracker.analyze_institutional_ownership(ticker)
            
            if 'error' in ownership_data:
                st.error(f"Error: {ownership_data['error']}")
                return
            
            display_ownership_results(ownership_data)
            
        except Exception as e:
            st.error(f"Ownership analysis failed: {str(e)}")

def display_ownership_results(ownership_data):
    """Display ownership analysis results"""
    ticker = ownership_data['ticker']
    company_name = ownership_data['company_name']
    holders = ownership_data.get('institutional_holders', {})
    smart_money = ownership_data.get('smart_money_score', {})
    
    st.markdown(f"## 🏦 {company_name} ({ticker}) - Ownership Analysis")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_institutions = holders.get('number_of_institutions', 0)
        st.metric("Total Institutions", total_institutions)
    
    with col2:
        total_ownership = holders.get('total_institutional_ownership', 0)
        st.metric("Institutional Ownership", f"{total_ownership:.1f}%")
    
    with col3:
        top10_concentration = holders.get('top_10_concentration', 0)
        st.metric("Top 10 Concentration", f"{top10_concentration:.1f}%")
    
    with col4:
        smart_score = smart_money.get('total_score', 0)
        st.metric("Smart Money Score", f"{smart_score:.0f}/100")
    
    # Smart Money Score breakdown
    show_smart_money_breakdown(smart_money)
    
    # Major institutional holders
    show_major_holders(holders)

def show_smart_money_breakdown(smart_money):
    """Show smart money score breakdown"""
    st.markdown("### 💡 Smart Money Score Breakdown")
    
    if 'error' in smart_money:
        st.error(f"Smart money analysis error: {smart_money['error']}")
        return
    
    total_score = smart_money.get('total_score', 0)
    grade = smart_money.get('grade', 'Unknown')
    interpretation = smart_money.get('interpretation', 'No interpretation available')
    components = smart_money.get('score_components', {})
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        # Determine grade color
        if grade.startswith('A'):
            grade_class = "grade-a"
        elif grade.startswith('B'):
            grade_class = "grade-b"
        else:
            grade_class = "grade-c"
        
        st.markdown(f"""
        <div class="smart-money-card">
            <h3>Smart Money Grade</h3>
            <h1 class="{grade_class}" style="margin: 0.5rem 0; font-size: 3rem;">{grade}</h1>
            <h2 style="color: #059669; margin: 0;">{total_score:.0f}/100</h2>
            <p style="margin-top: 1rem; font-style: italic;">{interpretation}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if components:
            # Score components chart
            component_names = list(components.keys())
            component_values = list(components.values())
            
            fig = px.bar(
                x=component_values,
                y=[name.replace('_', ' ').title() for name in component_names],
                orientation='h',
                title='Smart Money Score Components',
                color=component_values,
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def show_major_holders(holders):
    """Show major institutional holders"""
    st.markdown("### 🏛️ Major Institutional Holders")
    
    major_holders = holders.get('major_holders', [])
    
    if not major_holders:
        st.info("No institutional holder data available")
        return
    
    # Create DataFrame for display
    holder_data = []
    for holder in major_holders[:10]:  # Top 10
        holder_data.append({
            'Institution': holder.get('institution', 'Unknown'),
            'Shares': f"{holder.get('shares', 0):,}",
            'Percent Outstanding': f"{holder.get('percent_out', 0):.2f}%",
            'Value (M)': f"${holder.get('value', 0)/1e6:.1f}M",
            'Date Reported': holder.get('date_reported', 'Unknown')
        })
    
    df = pd.DataFrame(holder_data)
    st.dataframe(df, use_container_width=True)
    
    # Top holders visualization
    if len(major_holders) >= 5:
        top_5 = major_holders[:5]
        names = [holder['institution'][:20] + '...' if len(holder['institution']) > 20 
                else holder['institution'] for holder in top_5]
        percentages = [holder.get('percent_out', 0) for holder in top_5]
        
        fig = px.pie(
            values=percentages,
            names=names,
            title='Top 5 Institutional Holders'
        )
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)

def show_smart_money_analysis():
    """Show smart money analysis tab"""
    st.markdown("### 💰 Smart Money Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Company Ticker for Smart Money Analysis:",
            placeholder="e.g., MRNA, REGN, VRTX",
            key="smart_money_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        smart_btn = st.button("💰 Analyze Smart Money", type="primary", use_container_width=True)
    
    if ticker and smart_btn:
        analyze_smart_money(ticker)
    else:
        show_smart_money_info()

def show_smart_money_info():
    """Show smart money information"""
    st.markdown("### 💡 Smart Money Scoring Methodology")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Scoring Components (25 points each):**
        - **Institutional Concentration:** Higher ownership by top institutions
        - **Quality of Institutions:** Presence of tier-1 investment managers
        - **Recent Activity:** Net institutional flows and position changes
        - **Healthcare Specialization:** Holdings by healthcare-focused funds
        """)
    
    with col2:
        st.markdown("""
        **🎯 Grade Interpretation:**
        - **A+ (80-100):** Strong institutional support with high-quality investors
        - **A (70-79):** Good institutional backing with quality managers
        - **B (50-69):** Moderate institutional interest
        - **C (30-49):** Limited institutional support
        - **D (<30):** Weak institutional backing
        """)

def analyze_smart_money(ticker: str):
    """Analyze smart money for ticker"""
    with st.spinner(f"Analyzing smart money for {ticker}..."):
        try:
            ownership_data = st.session_state.ownership_tracker.analyze_institutional_ownership(ticker)
            
            if 'error' in ownership_data:
                st.error(f"Error: {ownership_data['error']}")
                return
            
            smart_money = ownership_data.get('smart_money_score', {})
            healthcare_exposure = ownership_data.get('healthcare_fund_exposure', {})
            
            display_smart_money_details(smart_money, healthcare_exposure, ticker)
            
        except Exception as e:
            st.error(f"Smart money analysis failed: {str(e)}")

def display_smart_money_details(smart_money, healthcare_exposure, ticker):
    """Display detailed smart money analysis"""
    st.markdown(f"## 💰 Smart Money Analysis - {ticker}")
    
    # Healthcare fund exposure
    if healthcare_exposure and not healthcare_exposure.get('error'):
        st.markdown("### 🏥 Healthcare Fund Exposure")
        
        holdings = healthcare_exposure.get('healthcare_etf_holdings', [])
        total_exposure = healthcare_exposure.get('total_etf_exposure', 0)
        focus_score = healthcare_exposure.get('healthcare_focus_score', 0)
        
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.metric("Total ETF Exposure", f"{total_exposure:.2f}%")
            st.metric("Healthcare Focus Score", f"{focus_score:.0f}/100")
        
        with col2:
            if holdings:
                # ETF holdings chart
                etf_names = [holding['etf_name'][:20] + '...' if len(holding['etf_name']) > 20 
                           else holding['etf_name'] for holding in holdings]
                percentages = [holding.get('holding_percentage', 0) for holding in holdings]
                
                fig = px.bar(
                    x=percentages,
                    y=etf_names,
                    orientation='h',
                    title='Healthcare ETF Holdings',
                    color=percentages,
                    color_continuous_scale='Blues'
                )
                fig.update_layout(height=300, showlegend=False)
                st.plotly_chart(fig, use_container_width=True)
        
        # Individual ETF holdings
        if holdings:
            st.markdown("#### 📋 Individual ETF Holdings")
            for holding in holdings:
                st.markdown(f"""
                <div class="institution-card">
                    <h4>{holding.get('etf_name', 'Unknown ETF')} ({holding.get('etf_ticker', 'N/A')})</h4>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                        <div><strong>Holding Percentage:</strong> {holding.get('holding_percentage', 0):.2f}%</div>
                        <div><strong>Focus Area:</strong> {holding.get('focus_area', 'Unknown')}</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

def show_insider_activity():
    """Show insider activity analysis"""
    st.markdown("### 👨‍💼 Insider Activity Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Company Ticker for Insider Analysis:",
            placeholder="e.g., MRNA, PFE, REGN",
            key="insider_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        insider_btn = st.button("👨‍💼 Analyze Insiders", type="primary", use_container_width=True)
    
    if ticker and insider_btn:
        analyze_insider_activity(ticker)
    else:
        show_insider_info()

def show_insider_info():
    """Show insider activity information"""
    st.markdown("### 📊 Insider Activity Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **👨‍💼 Tracked Insider Roles:**
        - Chief Executive Officer (CEO)
        - Chief Financial Officer (CFO)
        - Chief Operating Officer (COO)
        - Board Directors
        - C-Suite Executives
        """)
    
    with col2:
        st.markdown("""
        **📈 Activity Analysis:**
        - Buy/sell transaction tracking
        - Net insider sentiment scoring
        - Transaction value analysis
        - Timing pattern recognition
        - Alert generation for significant moves
        """)

def analyze_insider_activity(ticker: str):
    """Analyze insider activity"""
    with st.spinner(f"Analyzing insider activity for {ticker}..."):
        try:
            ownership_data = st.session_state.ownership_tracker.analyze_institutional_ownership(ticker)
            
            if 'error' in ownership_data:
                st.error(f"Error: {ownership_data['error']}")
                return
            
            insider_activity = ownership_data.get('insider_activity', {})
            display_insider_details(insider_activity, ticker)
            
        except Exception as e:
            st.error(f"Insider analysis failed: {str(e)}")

def display_insider_details(insider_activity, ticker):
    """Display insider activity details"""
    st.markdown(f"## 👨‍💼 Insider Activity - {ticker}")
    
    if 'error' in insider_activity:
        st.error(f"Insider activity error: {insider_activity['error']}")
        return
    
    net_activity = insider_activity.get('net_insider_activity', 0)
    sentiment = insider_activity.get('insider_sentiment', 'Unknown')
    transactions = insider_activity.get('recent_transactions', [])
    
    # Overall metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Recent Transactions", len(transactions))
    
    with col2:
        st.metric("Net Activity", f"${net_activity:,.0f}")
    
    with col3:
        # Sentiment color
        if sentiment == 'Bullish':
            sentiment_color = "#10b981"
        elif sentiment == 'Bearish':
            sentiment_color = "#ef4444"
        else:
            sentiment_color = "#6b7280"
        
        st.markdown(f"""
        <div style="text-align: center;">
            <h3>Insider Sentiment</h3>
            <h2 style="color: {sentiment_color};">{sentiment}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent transactions
    if transactions:
        st.markdown("### 📋 Recent Insider Transactions")
        
        # Transaction summary chart
        buy_value = sum(trans['value'] for trans in transactions if trans['transaction_type'] == 'Buy')
        sell_value = sum(trans['value'] for trans in transactions if trans['transaction_type'] == 'Sell')
        
        if buy_value > 0 or sell_value > 0:
            fig = px.bar(
                x=['Buys', 'Sells'],
                y=[buy_value, sell_value],
                color=['Buys', 'Sells'],
                color_discrete_map={'Buys': '#10b981', 'Sells': '#ef4444'},
                title='Insider Transaction Value (Last 90 Days)'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
        
        # Individual transactions
        for transaction in transactions[:10]:  # Show last 10
            transaction_type = transaction.get('transaction_type', 'Unknown')
            
            if transaction_type == 'Buy':
                card_class = "increase-card"
            else:
                card_class = "decrease-card"
            
            st.markdown(f"""
            <div class="insider-activity {card_class}">
                <h4>{transaction.get('insider_title', 'Unknown Title')} - {transaction_type}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                    <div><strong>Date:</strong><br>{transaction.get('date', 'Unknown')}</div>
                    <div><strong>Shares:</strong><br>{transaction.get('shares', 0):,}</div>
                    <div><strong>Price:</strong><br>${transaction.get('price', 0):.2f}</div>
                    <div><strong>Value:</strong><br>${transaction.get('value', 0):,.0f}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_ownership_changes():
    """Show ownership changes analysis"""
    st.markdown("### 🔄 Institutional Ownership Changes")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Company Ticker for Change Analysis:",
            placeholder="e.g., MRNA, REGN, VRTX",
            key="changes_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        changes_btn = st.button("🔄 Analyze Changes", type="primary", use_container_width=True)
    
    if ticker and changes_btn:
        analyze_ownership_changes(ticker)
    else:
        show_changes_info()

def show_changes_info():
    """Show ownership changes information"""
    st.markdown("### 📊 Ownership Change Tracking")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📈 Tracked Changes:**
        - Quarterly position increases
        - Position decreases and exits
        - New institutional positions
        - Closed positions analysis
        """)
    
    with col2:
        st.markdown("""
        **🎯 Analysis Features:**
        - Net institutional flow calculation
        - Change magnitude scoring
        - Trend identification
        - Smart money movement tracking
        """)

def analyze_ownership_changes(ticker: str):
    """Analyze ownership changes"""
    with st.spinner(f"Analyzing ownership changes for {ticker}..."):
        try:
            ownership_data = st.session_state.ownership_tracker.analyze_institutional_ownership(ticker)
            
            if 'error' in ownership_data:
                st.error(f"Error: {ownership_data['error']}")
                return
            
            changes = ownership_data.get('ownership_changes', {})
            display_changes_details(changes, ticker)
            
        except Exception as e:
            st.error(f"Ownership changes analysis failed: {str(e)}")

def display_changes_details(changes, ticker):
    """Display ownership changes details"""
    st.markdown(f"## 🔄 Ownership Changes - {ticker}")
    
    if 'error' in changes:
        st.error(f"Ownership changes error: {changes['error']}")
        return
    
    net_flow = changes.get('net_institutional_flow', 0)
    increases = changes.get('recent_increases', [])
    decreases = changes.get('recent_decreases', [])
    
    # Flow summary
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Recent Increases", len(increases))
    
    with col2:
        st.metric("Recent Decreases", len(decreases))
    
    with col3:
        flow_color = "#10b981" if net_flow > 0 else "#ef4444" if net_flow < 0 else "#6b7280"
        st.markdown(f"""
        <div style="text-align: center;">
            <h3>Net Institutional Flow</h3>
            <h2 style="color: {flow_color};">{net_flow:+.1f}%</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Position increases
    if increases:
        st.markdown("### 📈 Recent Position Increases")
        for increase in increases:
            st.markdown(f"""
            <div class="institution-card increase-card">
                <h4>{increase.get('institution', 'Unknown Institution')}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                    <div><strong>Change:</strong><br>+{increase.get('change_percent', 0):.1f}%</div>
                    <div><strong>New Position:</strong><br>{increase.get('new_position_size', 0):.2f}%</div>
                    <div><strong>Quarter:</strong><br>{increase.get('quarter', 'Unknown')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    
    # Position decreases
    if decreases:
        st.markdown("### 📉 Recent Position Decreases")
        for decrease in decreases:
            st.markdown(f"""
            <div class="institution-card decrease-card">
                <h4>{decrease.get('institution', 'Unknown Institution')}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                    <div><strong>Change:</strong><br>{decrease.get('change_percent', 0):.1f}%</div>
                    <div><strong>New Position:</strong><br>{decrease.get('new_position_size', 0):.2f}%</div>
                    <div><strong>Quarter:</strong><br>{decrease.get('quarter', 'Unknown')}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 