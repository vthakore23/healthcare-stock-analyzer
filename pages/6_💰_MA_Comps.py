import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add the medequity_utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'medequity_utils'))

try:
    from live_ma_scraper import LiveMADealscraper
except ImportError:
    st.error("Could not import M&A scraper. Please check the installation.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="M&A Comparables Analysis",
    page_icon="💰",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.metric-card {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    padding: 1rem;
    border-radius: 10px;
    color: white;
    text-align: center;
    margin: 0.5rem 0;
}

.deal-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #667eea;
    margin: 1rem 0;
}

.deal-value {
    font-size: 2rem;
    font-weight: bold;
    color: #667eea;
}

.deal-premium {
    background: #e8f5e8;
    color: #2e7d32;
    padding: 0.2rem 0.5rem;
    border-radius: 15px;
    font-size: 0.9rem;
    font-weight: bold;
}

.negative-premium {
    background: #ffebee;
    color: #c62828;
}

.status-completed {
    background: #e8f5e8;
    color: #2e7d32;
    padding: 0.2rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: bold;
}

.status-pending {
    background: #fff3e0;
    color: #ef6c00;
    padding: 0.2rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
    font-weight: bold;
}

.therapeutic-area {
    background: #f3e5f5;
    color: #7b1fa2;
    padding: 0.2rem 0.8rem;
    border-radius: 15px;
    font-size: 0.8rem;
}

.source-link {
    color: #1976d2;
    text-decoration: none;
    font-weight: 500;
}

.source-link:hover {
    text-decoration: underline;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.title("💰 M&A Comparables Analysis")
    st.markdown("### Real-Time Healthcare M&A Deals & Valuation Analysis")
    
    # Initialize the live M&A scraper
    if 'ma_scraper' not in st.session_state:
        st.session_state.ma_scraper = LiveMADealscraper()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter M&A Deals")
    
    with st.spinner("🔄 Loading live M&A data..."):
        all_deals = st.session_state.ma_scraper.get_live_ma_deals()
    
    if not all_deals:
        st.error("Could not load M&A deals data. Please try again later.")
        return
    
    # Filter options
    deal_size_min = st.sidebar.slider(
        "Minimum Deal Size ($B)", 
        0.0, 50.0, 0.0, 0.5,
        help="Filter deals by minimum transaction value"
    )
    
    therapeutic_areas = list(set([deal.get('therapeutic_area', 'Other') for deal in all_deals]))
    selected_areas = st.sidebar.multiselect(
        "Therapeutic Areas", 
        therapeutic_areas, 
        default=therapeutic_areas,
        help="Filter by therapeutic focus area"
    )
    
    deal_status = st.sidebar.multiselect(
        "Deal Status",
        ['Completed', 'Pending'],
        default=['Completed', 'Pending']
    )
    
    show_recent_only = st.sidebar.checkbox(
        "Show Recent Deals Only (Last 12 Months)",
        value=False
    )
    
    # Apply filters
    filtered_deals = []
    for deal in all_deals:
        # Size filter
        if deal.get('deal_value', 0) < deal_size_min:
            continue
        
        # Therapeutic area filter
        if deal.get('therapeutic_area', 'Other') not in selected_areas:
            continue
        
        # Status filter
        if deal.get('status', 'Completed') not in deal_status:
            continue
        
        # Recent deals filter
        if show_recent_only and not deal.get('is_recent', False):
            continue
        
        filtered_deals.append(deal)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Live Deals Dashboard", "📈 Deal Analytics", "🔍 Comparable Analysis", "💡 Market Insights"])
    
    with tab1:
        show_deals_dashboard(filtered_deals)
    
    with tab2:
        show_deal_analytics(filtered_deals)
    
    with tab3:
        show_comparable_analysis(filtered_deals)
    
    with tab4:
        show_market_insights(all_deals)

def show_deals_dashboard(deals):
    """Show live deals dashboard"""
    
    if not deals:
        st.info("No deals match your current filters. Try adjusting the criteria.")
        return
    
    # Key metrics
    total_value = sum([d.get('deal_value', 0) for d in deals])
    avg_premium = np.mean([float(d.get('premium', '0').replace('%', '')) for d in deals if d.get('premium', 'N/A') != 'N/A'])
    completed_deals = len([d for d in deals if d.get('status') == 'Completed'])
    pending_deals = len([d for d in deals if d.get('status') == 'Pending'])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>${total_value:.1f}B</h3>
            <p>Total Deal Volume</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{avg_premium:.0f}%</h3>
            <p>Average Premium</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{completed_deals}</h3>
            <p>Completed Deals</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{pending_deals}</h3>
            <p>Pending Deals</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Recent deals list
    st.markdown("#### 🔥 Recent M&A Deals")
    
    for deal in sorted(deals, key=lambda x: x.get('announcement_date', '2020-01-01'), reverse=True)[:10]:
        
        # Calculate colors and status
        status_class = "status-completed" if deal.get('status') == 'Completed' else "status-pending"
        
        premium_value = deal.get('premium', 'N/A')
        premium_class = "deal-premium"
        if premium_value != 'N/A':
            try:
                premium_num = float(premium_value.replace('%', ''))
                if premium_num < 0:
                    premium_class += " negative-premium"
            except:
                pass
        
        # Market reaction info
        market_reaction = deal.get('market_reaction', {})
        reaction_text = ""
        if market_reaction.get('reaction_percent'):
            reaction_color = "green" if market_reaction['reaction_percent'] > 0 else "red"
            reaction_text = f"<span style='color: {reaction_color}'>Market: {market_reaction['reaction_percent']:+.1f}%</span>"
        
        st.markdown(f"""
        <div class="deal-card">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <h4>{deal.get('acquirer', 'N/A')} acquiring {deal.get('target', 'N/A')}</h4>
                    <div style="margin: 0.5rem 0;">
                        <span class="{status_class}">{deal.get('status', 'Unknown')}</span>
                        <span class="therapeutic-area" style="margin-left: 0.5rem;">{deal.get('therapeutic_area', 'N/A')}</span>
                        {f'<span class="{premium_class}" style="margin-left: 0.5rem;">Premium: {premium_value}</span>' if premium_value != 'N/A' else ''}
                    </div>
                    <p style="margin: 0.5rem 0; color: #666;">{deal.get('deal_rationale', 'Strategic acquisition')}</p>
                    <div style="font-size: 0.9rem; color: #888;">
                        <strong>Announced:</strong> {datetime.strptime(deal.get('announcement_date', '2024-01-01'), '%Y-%m-%d').strftime('%B %d, %Y')} 
                        ({deal.get('days_since_announcement', 0)} days ago)
                        {f' | {reaction_text}' if reaction_text else ''}
                    </div>
                </div>
                <div style="text-align: right;">
                    <div class="deal-value">{deal.get('deal_value_formatted', 'N/A')}</div>
                    <div style="margin-top: 0.5rem;">
                        <a href="{deal.get('source_url', '#')}" target="_blank" class="source-link">
                            📰 View Press Release
                        </a>
                    </div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Search functionality
    st.markdown("---")
    st.markdown("#### 🔍 Search Deals")
    
    search_term = st.text_input("Search by company name, drug, or therapeutic area:")
    
    if search_term:
        search_results = st.session_state.ma_scraper.search_deals(search_term)
        
        if search_results:
            st.markdown(f"Found {len(search_results)} deals matching '{search_term}':")
            
            for deal in search_results[:5]:
                st.markdown(f"""
                **{deal.get('acquirer')} → {deal.get('target')}** ({deal.get('deal_value_formatted', 'N/A')})  
                *{deal.get('therapeutic_area', 'N/A')} | {deal.get('status', 'Unknown')}*  
                [View Details]({deal.get('source_url', '#')})
                """)
        else:
            st.info(f"No deals found matching '{search_term}'")

def show_deal_analytics(deals):
    """Show deal analytics and visualizations"""
    
    if not deals:
        st.info("No deals to analyze with current filters.")
        return
    
    # Deal size distribution
    st.markdown("#### 📊 Deal Size Distribution")
    
    deal_values = [d.get('deal_value', 0) for d in deals if d.get('deal_value', 0) > 0]
    
    if deal_values:
        fig = px.histogram(
            x=deal_values,
            nbins=10,
            title="Distribution of Deal Sizes",
            labels={'x': 'Deal Value ($B)', 'y': 'Number of Deals'}
        )
        fig.update_traces(marker_color='#667eea')
        st.plotly_chart(fig, use_container_width=True)
    
    # Premium analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 💰 Premium Analysis")
        
        premiums = []
        premium_labels = []
        
        for deal in deals:
            if deal.get('premium', 'N/A') != 'N/A':
                try:
                    premium_val = float(deal.get('premium', '0').replace('%', ''))
                    premiums.append(premium_val)
                    premium_labels.append(f"{deal.get('acquirer', '')} → {deal.get('target', '')}")
                except:
                    continue
        
        if premiums:
            fig = go.Figure(data=go.Bar(
                x=premium_labels,
                y=premiums,
                marker_color=['#00C851' if p > 0 else '#ff4444' for p in premiums]
            ))
            
            fig.update_layout(
                title="Acquisition Premiums",
                xaxis_title="Deal",
                yaxis_title="Premium (%)",
                xaxis={'tickangle': 45}
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🏥 Therapeutic Areas")
        
        # Count by therapeutic area
        area_counts = {}
        for deal in deals:
            area = deal.get('therapeutic_area', 'Other')
            area_counts[area] = area_counts.get(area, 0) + 1
        
        if area_counts:
            fig = px.pie(
                values=list(area_counts.values()),
                names=list(area_counts.keys()),
                title="Deals by Therapeutic Area"
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Timeline analysis
    st.markdown("#### 📅 Deal Timeline")
    
    # Group deals by month
    monthly_data = {}
    monthly_value = {}
    
    for deal in deals:
        try:
            deal_date = datetime.strptime(deal.get('announcement_date', '2024-01-01'), '%Y-%m-%d')
            month_key = deal_date.strftime('%Y-%m')
            
            monthly_data[month_key] = monthly_data.get(month_key, 0) + 1
            monthly_value[month_key] = monthly_value.get(month_key, 0) + deal.get('deal_value', 0)
        except:
            continue
    
    if monthly_data:
        months = sorted(monthly_data.keys())
        counts = [monthly_data[m] for m in months]
        values = [monthly_value[m] for m in months]
        
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        
        fig.add_trace(
            go.Bar(x=months, y=counts, name="Deal Count", marker_color='#667eea'),
            secondary_y=False,
        )
        
        fig.add_trace(
            go.Scatter(x=months, y=values, name="Deal Value ($B)", mode='lines+markers', marker_color='#764ba2'),
            secondary_y=True,
        )
        
        fig.update_xaxes(title_text="Month")
        fig.update_yaxes(title_text="Number of Deals", secondary_y=False)
        fig.update_yaxes(title_text="Deal Value ($B)", secondary_y=True)
        
        fig.update_layout(title_text="M&A Activity Over Time")
        
        st.plotly_chart(fig, use_container_width=True)

def show_comparable_analysis(deals):
    """Show comparable deal analysis"""
    
    st.markdown("#### 🎯 Comparable Deals Analysis")
    
    # Company search
    col1, col2 = st.columns([2, 1])
    
    with col1:
        target_company = st.text_input(
            "Enter company ticker or name to find comparable deals:",
            placeholder="e.g., PFE, Pfizer, Bristol Myers"
        )
    
    with col2:
        min_deal_size = st.number_input("Min Deal Size ($B)", value=1.0, step=0.5)
    
    if target_company:
        # Find comparable deals
        comparable_deals = []
        
        # First, find deals involving the target company
        direct_deals = [d for d in deals if target_company.lower() in d.get('acquirer', '').lower() or target_company.lower() in d.get('target', '').lower()]
        
        if direct_deals:
            st.markdown(f"##### 🎯 Direct Deals Involving '{target_company}'")
            
            for deal in direct_deals:
                st.markdown(f"""
                **{deal.get('acquirer')} → {deal.get('target')}**  
                💰 Value: {deal.get('deal_value_formatted', 'N/A')} | Premium: {deal.get('premium', 'N/A')} | Status: {deal.get('status', 'Unknown')}  
                🏥 {deal.get('therapeutic_area', 'N/A')} | 📅 {deal.get('announcement_date', 'N/A')}  
                📝 {deal.get('deal_rationale', 'Strategic acquisition')}  
                [📰 Press Release]({deal.get('source_url', '#')})
                """)
        
        # Find therapeutic area matches
        if direct_deals:
            therapeutic_areas = list(set([d.get('therapeutic_area', '') for d in direct_deals]))
            
            st.markdown(f"##### 🏥 Comparable Deals in Same Therapeutic Areas")
            
            for area in therapeutic_areas:
                if area:
                    area_deals = [d for d in deals if d.get('therapeutic_area', '') == area and d not in direct_deals]
                    area_deals = [d for d in area_deals if d.get('deal_value', 0) >= min_deal_size]
                    
                    if area_deals:
                        st.markdown(f"**{area} Deals:**")
                        
                        # Create comparison table
                        comp_data = []
                        for deal in area_deals[:5]:  # Top 5
                            comp_data.append({
                                'Acquirer': deal.get('acquirer', 'N/A'),
                                'Target': deal.get('target', 'N/A'),
                                'Value': deal.get('deal_value_formatted', 'N/A'),
                                'Premium': deal.get('premium', 'N/A'),
                                'Date': deal.get('announcement_date', 'N/A'),
                                'Status': deal.get('status', 'Unknown')
                            })
                        
                        if comp_data:
                            comp_df = pd.DataFrame(comp_data)
                            st.dataframe(comp_df, use_container_width=True)

def show_market_insights(all_deals):
    """Show market insights and trends"""
    
    st.markdown("#### 💡 M&A Market Insights")
    
    # Get deal statistics
    stats = st.session_state.ma_scraper.get_deal_statistics()
    
    if stats:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("##### 📈 Market Statistics")
            
            st.metric("Total Deals Tracked", stats.get('total_deals', 0))
            st.metric("Total Deal Value", f"${stats.get('total_value', 0):.1f}B")
            st.metric("Average Deal Size", f"${stats.get('average_deal_size', 0):.1f}B")
            st.metric("Average Premium", f"{stats.get('average_premium', 0):.0f}%")
        
        with col2:
            st.markdown("##### 🏢 Most Active Acquirers")
            
            active_acquirers = stats.get('most_active_acquirers', [])
            for acquirer, count in active_acquirers:
                st.write(f"**{acquirer}**: {count} deal{'s' if count > 1 else ''}")
    
    # Key trends and insights
    st.markdown("##### 🔍 Key Market Trends")
    
    insights = [
        "**Oncology M&A Dominance**: Cancer treatments continue to drive the highest-value acquisitions, with companies seeking novel platforms like ADCs (Antibody-Drug Conjugates).",
        
        "**Rare Disease Premium**: Rare disease assets command premium valuations due to regulatory advantages and pricing power.",
        
        "**Platform Technology Focus**: Acquirers are prioritizing platform technologies (like CRISPR, cell therapy) over single-asset deals.",
        
        "**Regulatory Risk**: FDA approval uncertainty continues to create significant valuation spreads in biotech M&A.",
        
        "**Cash-Rich Buyers**: Large pharma companies are sitting on substantial cash reserves, enabling large-scale acquisitions."
    ]
    
    for insight in insights:
        st.markdown(f"• {insight}")
    
    # Market outlook
    st.markdown("##### 🔮 Market Outlook")
    
    st.info("""
    **2025 M&A Outlook:**
    
    🔹 **Continued Consolidation**: Large pharma will continue acquiring biotech to replenish pipelines  
    🔹 **AI/Digital Health**: Growing interest in AI-powered drug discovery and digital therapeutics  
    🔹 **Cell & Gene Therapy**: High valuations expected for breakthrough therapies  
    🔹 **Geographic Expansion**: Increased focus on emerging markets and global expansion deals  
    🔹 **ESG Considerations**: Environmental and social factors increasingly influencing deal structures
    """)

if __name__ == "__main__":
    main()
