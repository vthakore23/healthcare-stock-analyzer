import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="M&A Comparisons - Healthcare Analyzer",
    page_icon="💰",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .ma-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .deal-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
    }
    
    .deal-completed { border-left-color: #28a745; }
    .deal-pending { border-left-color: #ffc107; }
    .deal-failed { border-left-color: #dc3545; }
    
    .premium-positive { color: #28a745; font-weight: bold; }
    .premium-negative { color: #dc3545; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
    <div class="ma-header">
        <h1>💰 M&A Comparisons & Analysis</h1>
        <p style="font-size: 1.2rem;">Analyze healthcare mergers, acquisitions, and valuations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Deal Analysis", "📊 Market Trends", "💡 Valuation Tools"])
    
    with tab1:
        show_deal_analysis()
    
    with tab2:
        show_market_trends()
    
    with tab3:
        show_valuation_tools()

def show_deal_analysis():
    """Show M&A deal analysis and comparisons"""
    st.markdown("### 🔍 Recent Healthcare M&A Deals")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        deal_status = st.selectbox("Deal Status:", ["All", "Completed", "Pending", "Failed"])
    
    with col2:
        subsector = st.selectbox("Subsector:", 
                                ["All", "Biotechnology", "Pharmaceuticals", "Medical Devices", "Digital Health"])
    
    with col3:
        deal_size = st.selectbox("Deal Size:", 
                                ["All", ">$10B", "$1B-$10B", "$100M-$1B", "<$100M"])
    
    # Generate sample deals
    deals = generate_sample_deals()
    
    # Display deals
    display_deals_list(deals, deal_status, subsector, deal_size)
    
    # Deal analysis charts
    create_deal_analysis_charts(deals)

def show_market_trends():
    """Show M&A market trends and statistics"""
    st.markdown("### 📊 Healthcare M&A Market Trends")
    
    # Market overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📈 Total Deals YTD", "156")
        st.metric("💰 Total Value YTD", "$89.2B")
    
    with col2:
        st.metric("📊 Avg Deal Size", "$572M")
        st.metric("📈 Median Premium", "42.5%")
    
    with col3:
        st.metric("🧬 Biotech Deals", "67")
        st.metric("💊 Pharma Deals", "43")
    
    with col4:
        st.metric("🏥 Med Device Deals", "28")
        st.metric("💻 Digital Health", "18")
    
    # Trend charts
    create_market_trend_charts()

def show_valuation_tools():
    """Show valuation tools and calculators"""
    st.markdown("### 💡 Valuation Tools & Calculators")
    
    # Valuation calculator
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📊 Deal Valuation Calculator")
        
        # Input parameters
        target_revenue = st.number_input("Target Revenue ($M):", min_value=0.0, value=500.0, step=10.0)
        revenue_multiple = st.slider("Revenue Multiple:", 1.0, 20.0, 8.0, 0.5)
        premium = st.slider("Acquisition Premium (%):", 0, 100, 35)
        
        # Calculate valuation
        base_valuation = target_revenue * revenue_multiple
        premium_valuation = base_valuation * (1 + premium/100)
        
        st.markdown(f"""
        **Base Valuation:** ${base_valuation:,.0f}M  
        **With Premium:** ${premium_valuation:,.0f}M  
        **Premium Amount:** ${premium_valuation - base_valuation:,.0f}M
        """)
    
    with col2:
        st.markdown("#### 📈 Comparable Company Analysis")
        
        # Comparable companies table
        comp_data = [
            {"Company": "Vertex", "Revenue": 8900, "Market Cap": 85000, "EV/Revenue": 9.6},
            {"Company": "Regeneron", "Revenue": 11900, "Market Cap": 72000, "EV/Revenue": 6.0},
            {"Company": "Moderna", "Revenue": 5200, "Market Cap": 45000, "EV/Revenue": 8.7},
            {"Company": "BioNTech", "Revenue": 17300, "Market Cap": 38000, "EV/Revenue": 2.2},
        ]
        
        df_comp = pd.DataFrame(comp_data)
        st.dataframe(df_comp, use_container_width=True)
        
        avg_multiple = df_comp['EV/Revenue'].mean()
        st.markdown(f"**Average EV/Revenue:** {avg_multiple:.1f}x")

def generate_sample_deals():
    """Generate sample M&A deals updated for June 2025"""
    deals = [
        {
            "date": "2025-06-10",
            "acquirer": "Eli Lilly",
            "target": "Morphic Therapeutics",
            "deal_value": 18500,
            "subsector": "Biotechnology",
            "status": "Pending",
            "premium": 89.2,
            "ev_revenue": 25.4,
            "indication": "Autoimmune",
            "news_links": [
                {
                    "title": "Lilly Agrees to Acquire Morphic Therapeutics for $18.5B",
                    "url": "https://www.biopharmadive.com/news/lilly-morphic-acquisition-2025",
                    "source": "BioPharma Dive"
                },
                {
                    "title": "Morphic's autoimmune platform attracts Lilly's $18.5B bid",
                    "url": "https://www.fiercepharma.com/ma/lilly-morphic-deal-2025",
                    "source": "FiercePharma"
                }
            ]
        },
        {
            "date": "2025-05-28",
            "acquirer": "Amgen",
            "target": "Argenx",
            "deal_value": 52000,
            "subsector": "Biotechnology",
            "status": "Completed",
            "premium": 45.7,
            "ev_revenue": 18.9,
            "indication": "Rare Disease",
            "news_links": [
                {
                    "title": "Amgen Completes $52B Acquisition of Argenx",
                    "url": "https://www.reuters.com/business/healthcare-pharmaceuticals/amgen-argenx-deal-completed-2025",
                    "source": "Reuters"
                },
                {
                    "title": "Argenx rare disease expertise bolsters Amgen's pipeline",
                    "url": "https://www.statnews.com/2025/05/28/amgen-argenx-acquisition-analysis",
                    "source": "STAT News"
                }
            ]
        },
        {
            "date": "2025-05-15",
            "acquirer": "Roche",
            "target": "Monte Rosa Therapeutics",
            "deal_value": 8900,
            "subsector": "Biotechnology",
            "status": "Completed",
            "premium": 112.3,
            "ev_revenue": None,
            "indication": "Oncology"
        },
        {
            "date": "2025-04-22",
            "acquirer": "GSK",
            "target": "Zai Lab",
            "deal_value": 14200,
            "subsector": "Biotechnology",
            "status": "Completed",
            "premium": 67.8,
            "ev_revenue": 15.6,
            "indication": "Oncology"
        },
        {
            "date": "2025-03-18",
            "acquirer": "Moderna",
            "target": "Carisma Therapeutics",
            "deal_value": 6700,
            "subsector": "Biotechnology",
            "status": "Completed",
            "premium": 156.4,
            "ev_revenue": None,
            "indication": "CAR-T Therapy"
        },
        {
            "date": "2025-02-25",
            "acquirer": "Danaher",
            "target": "Bruker Corporation",
            "deal_value": 21000,
            "subsector": "Diagnostics",
            "status": "Completed",
            "premium": 38.9,
            "ev_revenue": 8.7,
            "indication": "Diagnostics"
        },
        {
            "date": "2025-01-30",
            "acquirer": "Vertex",
            "target": "ViaCyte",
            "deal_value": 3200,
            "subsector": "Biotechnology",
            "status": "Completed",
            "premium": 78.5,
            "ev_revenue": None,
            "indication": "Diabetes"
        },
        {
            "date": "2024-12-15",
            "acquirer": "Sanofi",
            "target": "Provention Bio",
            "deal_value": 2900,
            "subsector": "Biotechnology",
            "status": "Completed",
            "premium": 134.7,
            "ev_revenue": None,
            "indication": "Autoimmune"
        },
        {
            "date": "2024-11-20",
            "acquirer": "Illumina",
            "target": "Pacific Biosciences",
            "deal_value": 7100,
            "subsector": "Diagnostics",
            "status": "Completed",
            "premium": 71.2,
            "ev_revenue": 14.8,
            "indication": "Genomics"
        },
        {
            "date": "2024-10-08",
            "acquirer": "Regeneron",
            "target": "Checkmate Pharmaceuticals",
            "deal_value": 1800,
            "subsector": "Biotechnology",
            "status": "Completed",
            "premium": 92.4,
            "ev_revenue": None,
            "indication": "Oncology"
        }
    ]
    
    return deals

def display_deals_list(deals, status_filter, subsector_filter, size_filter):
    """Display filtered list of M&A deals"""
    
    # Apply filters
    filtered_deals = deals.copy()
    
    if status_filter != "All":
        filtered_deals = [d for d in filtered_deals if d['status'] == status_filter]
    
    if subsector_filter != "All":
        filtered_deals = [d for d in filtered_deals if d['subsector'] == subsector_filter]
    
    # Deal size filter
    if size_filter != "All":
        if size_filter == ">$10B":
            filtered_deals = [d for d in filtered_deals if d['deal_value'] > 10000]
        elif size_filter == "$1B-$10B":
            filtered_deals = [d for d in filtered_deals if 1000 <= d['deal_value'] <= 10000]
        elif size_filter == "$100M-$1B":
            filtered_deals = [d for d in filtered_deals if 100 <= d['deal_value'] < 1000]
        elif size_filter == "<$100M":
            filtered_deals = [d for d in filtered_deals if d['deal_value'] < 100]
    
    st.markdown(f"### 📋 M&A Deals ({len(filtered_deals)} found)")
    
    # Display deals
    for deal in sorted(filtered_deals, key=lambda x: x['date'], reverse=True):
        deal_class = f"deal-{deal['status'].lower()}"
        premium_class = "premium-positive" if deal['premium'] > 50 else "premium-negative"
        
        st.markdown(f"""
        <div class="deal-card {deal_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>{deal['acquirer']} acquires {deal['target']}</h4>
                    <p><strong>Deal Value:</strong> ${deal['deal_value']:,}M</p>
                    <p><strong>Subsector:</strong> {deal['subsector']} | <strong>Indication:</strong> {deal['indication']}</p>
                    <p><strong>Date:</strong> {deal['date']}</p>
                </div>
                <div style="text-align: right;">
                    <p><strong>Status:</strong> <span style="color: {'#28a745' if deal['status'] == 'Completed' else '#ffc107' if deal['status'] == 'Pending' else '#dc3545'};">{deal['status']}</span></p>
                    <p><strong>Premium:</strong> <span class="{premium_class}">{deal['premium']:+.1f}%</span></p>
                    {f"<p><strong>EV/Revenue:</strong> {deal['ev_revenue']:.1f}x</p>" if deal['ev_revenue'] else ""}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_deal_analysis_charts(deals):
    """Create deal analysis visualizations"""
    st.markdown("### 📊 Deal Analysis")
    
    df = pd.DataFrame(deals)
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Deal value by subsector
        fig_subsector = px.bar(
            df.groupby('subsector')['deal_value'].sum().reset_index(),
            x='subsector',
            y='deal_value',
            title="Total Deal Value by Subsector ($M)"
        )
        st.plotly_chart(fig_subsector, use_container_width=True)
    
    with col2:
        # Premium analysis
        fig_premium = px.box(
            df,
            x='subsector',
            y='premium',
            title="Acquisition Premiums by Subsector"
        )
        st.plotly_chart(fig_premium, use_container_width=True)
    
    # Deal timeline
    df['date'] = pd.to_datetime(df['date'])
    df_timeline = df.groupby('date')['deal_value'].sum().reset_index()
    
    fig_timeline = px.line(
        df_timeline,
        x='date',
        y='deal_value',
        title="M&A Activity Timeline",
        markers=True
    )
    st.plotly_chart(fig_timeline, use_container_width=True)

def create_market_trend_charts():
    """Create market trend visualizations"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Monthly deal volume
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        deal_counts = [23, 18, 27, 31, 24, 33]
        deal_values = [12.5, 8.9, 15.2, 18.7, 11.3, 22.6]
        
        fig_volume = go.Figure()
        fig_volume.add_trace(go.Bar(x=months, y=deal_counts, name='Deal Count', yaxis='y'))
        fig_volume.add_trace(go.Scatter(x=months, y=deal_values, name='Deal Value ($B)', yaxis='y2', mode='lines+markers'))
        
        fig_volume.update_layout(
            title="Monthly M&A Activity",
            yaxis=dict(title="Number of Deals"),
            yaxis2=dict(title="Deal Value ($B)", overlaying='y', side='right'),
            height=400
        )
        st.plotly_chart(fig_volume, use_container_width=True)
    
    with col2:
        # Subsector distribution
        subsectors = ['Biotechnology', 'Pharmaceuticals', 'Medical Devices', 'Digital Health', 'Other']
        subsector_values = [45.2, 23.8, 12.4, 5.8, 2.0]
        
        fig_subsector = px.pie(
            values=subsector_values,
            names=subsectors,
            title="Deal Value by Subsector (YTD)"
        )
        st.plotly_chart(fig_subsector, use_container_width=True)
    
    # Premium trends
    st.markdown("#### 📈 Premium Trends")
    
    quarters = ['Q1 2023', 'Q2 2023', 'Q3 2023', 'Q4 2023', 'Q1 2024', 'Q2 2024']
    avg_premiums = [38.5, 42.1, 45.8, 41.2, 48.9, 52.3]
    
    fig_premium_trend = px.line(
        x=quarters,
        y=avg_premiums,
        title="Average Acquisition Premiums Over Time",
        markers=True
    )
    fig_premium_trend.update_layout(
        yaxis_title="Average Premium (%)",
        xaxis_title="Quarter"
    )
    st.plotly_chart(fig_premium_trend, use_container_width=True)

if __name__ == "__main__":
    main()
