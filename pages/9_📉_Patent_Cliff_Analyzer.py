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
    from medequity_utils.patent_cliff_analyzer import PatentCliffAnalyzer
    import yfinance as yf
except ImportError as e:
    st.error(f"Import error: {e}")

# Page configuration
st.set_page_config(
    page_title="Patent Cliff Analyzer",
    page_icon="📉",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
.patent-header {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.patent-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #ff6b6b;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.risk-high { border-left-color: #ef4444; background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); }
.risk-medium { border-left-color: #f59e0b; background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); }
.risk-low { border-left-color: #10b981; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); }

.impact-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #0ea5e9;
}
</style>
""", unsafe_allow_html=True)

# Initialize analyzer
if 'patent_analyzer' not in st.session_state:
    st.session_state.patent_analyzer = PatentCliffAnalyzer()

def main():
    st.markdown("""
    <div class="patent-header">
        <h1>📉 Patent Cliff Analyzer</h1>
        <p>Track Patent Expirations & Estimate Revenue Impact</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Patent Analysis", "📊 Revenue Impact", "🧬 Biosimilar Threats"])
    
    with tab1:
        show_patent_analysis()
    
    with tab2:
        show_revenue_impact()
    
    with tab3:
        show_biosimilar_threats()

def show_patent_analysis():
    """Show patent portfolio analysis"""
    st.markdown("### 📋 Patent Portfolio Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Healthcare Company Ticker:",
            placeholder="e.g., PFE, JNJ, MRK, ABBV",
            help="Enter a pharmaceutical company ticker",
            key="patent_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("📉 Analyze Patents", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        analyze_patents(ticker)
    else:
        show_patent_features()

def show_patent_features():
    """Show patent analysis features"""
    st.markdown("### 🌟 Patent Cliff Analysis Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **📋 Patent Tracking**
        - Active patent portfolio
        - Expiration timeline analysis
        - Technology area classification
        - Revenue attribution modeling
        """)
    
    with col2:
        st.markdown("""
        **💰 Financial Impact**
        - Revenue at risk calculations
        - Generic competition timing
        - Market share loss estimates
        - Cash flow impact projections
        """)
    
    with col3:
        st.markdown("""
        **🛡️ Risk Assessment**
        - Patent cliff severity scoring
        - Replacement pipeline strength
        - Competitive threat analysis
        - Mitigation strategy recommendations
        """)

def analyze_patents(ticker: str):
    """Analyze patent portfolio"""
    with st.spinner(f"Analyzing {ticker} patent portfolio..."):
        try:
            analysis = st.session_state.patent_analyzer.analyze_patent_portfolio(ticker)
            
            if 'error' in analysis:
                st.error(f"Error: {analysis['error']}")
                return
            
            display_patent_results(analysis)
            
        except Exception as e:
            st.error(f"Patent analysis failed: {str(e)}")

def display_patent_results(analysis):
    """Display patent analysis results"""
    ticker = analysis['ticker']
    company_name = analysis['company_name']
    portfolio = analysis['patent_portfolio']
    cliff_analysis = analysis['cliff_analysis']
    
    st.markdown(f"## 📋 {company_name} ({ticker}) - Patent Analysis")
    
    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_patents = portfolio.get('total_count', 0)
        st.metric("Total Patents", total_patents)
    
    with col2:
        active_patents = len(portfolio.get('active_patents', []))
        st.metric("Active Patents", active_patents)
    
    with col3:
        major_cliffs = len(cliff_analysis.get('major_cliffs', []))
        st.metric("Major Cliffs", major_cliffs)
    
    with col4:
        next_cliff = cliff_analysis.get('next_major_cliff')
        if next_cliff:
            years_to_cliff = next_cliff.get('years_remaining', 0)
            st.metric("Next Major Cliff", f"{years_to_cliff:.1f} years")
        else:
            st.metric("Next Major Cliff", "None identified")
    
    # Patent cliff timeline
    show_cliff_timeline(cliff_analysis)
    
    # Major patent cliffs
    show_major_cliffs(cliff_analysis.get('major_cliffs', []))

def show_cliff_timeline(cliff_analysis):
    """Show patent cliff timeline"""
    st.markdown("### 📅 Patent Expiration Timeline")
    
    timeline = cliff_analysis.get('cliff_timeline', {})
    
    if not timeline:
        st.info("No major patent cliffs identified in the next 10 years")
        return
    
    # Prepare data for visualization
    years = list(timeline.keys())
    patents_expiring = [timeline[year]['patents_expiring'] for year in years]
    revenue_impact = [timeline[year]['estimated_revenue_impact'] * 100 for year in years]
    
    # Create timeline chart
    fig = go.Figure()
    
    # Add bars for number of patents
    fig.add_trace(go.Bar(
        x=years,
        y=patents_expiring,
        name='Patents Expiring',
        marker_color='lightblue',
        yaxis='y'
    ))
    
    # Add line for revenue impact
    fig.add_trace(go.Scatter(
        x=years,
        y=revenue_impact,
        mode='lines+markers',
        name='Revenue Impact (%)',
        line=dict(color='red', width=3),
        yaxis='y2'
    ))
    
    fig.update_layout(
        title='Patent Cliff Timeline',
        xaxis_title='Year',
        yaxis=dict(title='Number of Patents', side='left'),
        yaxis2=dict(title='Revenue Impact (%)', side='right', overlaying='y'),
        height=400
    )
    
    st.plotly_chart(fig, use_container_width=True)

def show_major_cliffs(major_cliffs):
    """Show major patent cliffs"""
    st.markdown("### 🚨 Major Patent Cliffs")
    
    if not major_cliffs:
        st.info("No major patent cliffs identified")
        return
    
    for cliff in major_cliffs:
        severity = cliff.get('severity', 'Medium')
        
        if severity == 'High':
            card_class = "risk-high"
        elif severity == 'Medium':
            card_class = "risk-medium"
        else:
            card_class = "risk-low"
        
        st.markdown(f"""
        <div class="patent-card {card_class}">
            <h4>{cliff.get('title', 'Unknown Patent')}</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                <div><strong>Patent Number:</strong><br>{cliff.get('patent_number', 'Unknown')}</div>
                <div><strong>Expiry Date:</strong><br>{cliff.get('expiry_date', 'Unknown')}</div>
                <div><strong>Years Remaining:</strong><br>{cliff.get('years_remaining', 0):.1f}</div>
                <div><strong>Revenue Impact:</strong><br>{cliff.get('revenue_impact', 0):.1%}</div>
            </div>
            <p style="margin-top: 1rem;"><strong>Severity:</strong> {severity}</p>
        </div>
        """, unsafe_allow_html=True)

def show_revenue_impact():
    """Show revenue impact analysis"""
    st.markdown("### 💰 Revenue Impact Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Company Ticker for Revenue Impact:",
            placeholder="e.g., PFE, JNJ, MRK",
            key="revenue_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        impact_btn = st.button("💰 Calculate Impact", type="primary", use_container_width=True)
    
    if ticker and impact_btn:
        calculate_revenue_impact(ticker)
    else:
        show_impact_methodology()

def show_impact_methodology():
    """Show impact calculation methodology"""
    st.markdown("### 📊 Revenue Impact Methodology")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **💡 Impact Calculation Factors:**
        - Current product revenue attribution
        - Generic competition entry timing
        - Historical market share erosion rates
        - Biosimilar competition landscape
        """)
    
    with col2:
        st.markdown("""
        **📈 Typical Impact Ranges:**
        - Small molecules: 80-90% revenue loss
        - Biologics: 15-30% revenue loss
        - Complex generics: 60-80% revenue loss
        - Orphan drugs: 40-60% revenue loss
        """)

def calculate_revenue_impact(ticker: str):
    """Calculate revenue impact of patent cliffs"""
    with st.spinner(f"Calculating revenue impact for {ticker}..."):
        try:
            analysis = st.session_state.patent_analyzer.analyze_patent_portfolio(ticker)
            
            if 'error' in analysis:
                st.error(f"Error: {analysis['error']}")
                return
            
            financial_impact = analysis.get('financial_impact', {})
            revenue_data = analysis.get('revenue_data', {})
            
            display_financial_impact(financial_impact, revenue_data, ticker)
            
        except Exception as e:
            st.error(f"Revenue impact calculation failed: {str(e)}")

def display_financial_impact(financial_impact, revenue_data, ticker):
    """Display financial impact analysis"""
    
    if 'error' in financial_impact:
        st.error(f"Error calculating financial impact: {financial_impact['error']}")
        return
    
    st.markdown(f"## 💰 Financial Impact Analysis - {ticker}")
    
    # Overall metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_revenue = revenue_data.get('current_annual_revenue', 0)
        st.metric("Current Revenue", f"${current_revenue:.1f}B")
    
    with col2:
        revenue_at_risk = financial_impact.get('total_revenue_at_risk', 0)
        st.metric("Revenue at Risk", f"${revenue_at_risk:.1f}B")
    
    with col3:
        risk_score = financial_impact.get('portfolio_risk_score', 0)
        st.metric("Portfolio Risk", f"{risk_score:.1f}%")
    
    with col4:
        risk_level = financial_impact.get('risk_level', 'Unknown')
        st.metric("Risk Level", risk_level)
    
    # Year-by-year impact
    impact_by_year = financial_impact.get('impact_by_year', {})
    
    if impact_by_year:
        st.markdown("### 📅 Year-by-Year Impact Scenarios")
        
        for year, impact in impact_by_year.items():
            st.markdown(f"""
            <div class="impact-card">
                <h4>Year {year}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                    <div><strong>Revenue at Risk:</strong><br>${impact.get('revenue_at_risk', 0):.1f}B</div>
                    <div><strong>Expected Loss:</strong><br>${impact.get('expected_loss_to_generics', 0):.1f}B</div>
                    <div><strong>% of Total Revenue:</strong><br>{impact.get('percentage_of_total_revenue', 0):.1f}%</div>
                    <div><strong>Patents Expiring:</strong><br>{impact.get('patents_expiring', 0)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_biosimilar_threats():
    """Show biosimilar threat analysis"""
    st.markdown("### 🧬 Biosimilar Competition Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Company Ticker for Biosimilar Analysis:",
            placeholder="e.g., AMGN, BIIB, REGN",
            key="biosimilar_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        biosimilar_btn = st.button("🧬 Analyze Threats", type="primary", use_container_width=True)
    
    if ticker and biosimilar_btn:
        analyze_biosimilar_threats(ticker)
    else:
        show_biosimilar_info()

def show_biosimilar_info():
    """Show biosimilar threat information"""
    st.markdown("### 🧬 Biosimilar Competition Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🎯 Key Biosimilar Factors:**
        - Manufacturing complexity barriers
        - Regulatory approval pathways
        - Physician adoption patterns
        - Payer formulary decisions
        """)
    
    with col2:
        st.markdown("""
        **📊 Typical Market Impact:**
        - First biosimilar: 15-25% share loss
        - Multiple biosimilars: 30-50% share loss
        - Time to impact: 1-3 years
        - Price erosion: 20-40% over 5 years
        """)

def analyze_biosimilar_threats(ticker: str):
    """Analyze biosimilar competition threats"""
    with st.spinner(f"Analyzing biosimilar threats for {ticker}..."):
        try:
            threats = st.session_state.patent_analyzer.analyze_biosimilar_threats(ticker)
            
            if 'error' in threats:
                st.error(f"Error: {threats['error']}")
                return
            
            display_biosimilar_threats(threats)
            
        except Exception as e:
            st.error(f"Biosimilar analysis failed: {str(e)}")

def display_biosimilar_threats(threats):
    """Display biosimilar threat analysis"""
    ticker = threats['ticker']
    biosimilar_threats = threats.get('biosimilar_threats', [])
    total_revenue_at_risk = threats.get('total_revenue_at_risk', 0)
    
    st.markdown(f"## 🧬 Biosimilar Threats - {ticker}")
    
    if not biosimilar_threats:
        st.info("No significant biosimilar threats identified")
        return
    
    # Overall threat metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Products at Risk", len(biosimilar_threats))
    
    with col2:
        st.metric("Revenue at Risk", f"${total_revenue_at_risk:.1f}B")
    
    with col3:
        avg_threat = np.mean([1 if threat['threat_level'] == 'High' else 0.5 for threat in biosimilar_threats])
        st.metric("Avg Threat Level", f"{avg_threat:.1f}/1.0")
    
    # Individual product threats
    st.markdown("### 🎯 Product-Specific Threats")
    
    for threat in biosimilar_threats:
        threat_level = threat.get('threat_level', 'Unknown')
        
        if threat_level == 'Very High':
            card_class = "risk-high"
        elif threat_level == 'High':
            card_class = "risk-medium"
        else:
            card_class = "risk-low"
        
        st.markdown(f"""
        <div class="patent-card {card_class}">
            <h4>{threat.get('product_name', 'Unknown Product')}</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                <div><strong>Annual Revenue:</strong><br>${threat.get('annual_revenue', 0):.1f}B</div>
                <div><strong>Patent Expiry:</strong><br>{threat.get('patent_expiry', 'Unknown')}</div>
                <div><strong>Threat Level:</strong><br>{threat_level}</div>
                <div><strong>Market Share Loss:</strong><br>{threat.get('estimated_market_share_loss', 0):.0%}</div>
            </div>
            <p style="margin-top: 1rem;"><strong>Competitors:</strong> {len(threat.get('biosimilar_competitors', []))}</p>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 