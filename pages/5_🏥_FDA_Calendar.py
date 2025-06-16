import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

# Add the medequity_utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'medequity_utils'))

try:
    from live_fda_scraper import LiveFDAScaper
except ImportError:
    st.error("Could not import FDA scraper. Please check the installation.")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="FDA Calendar & Drug Approvals",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
.fda-header {
    background: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.event-card {
    background: white;
    padding: 1.5rem;
    border-radius: 10px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    margin: 1rem 0;
    border-left: 5px solid #ff6b6b;
}

.pdufa-event {
    border-left-color: #ee5a24;
    background: linear-gradient(135deg, #fff5f5 0%, #ffe8e8 100%);
}

.advisory-committee {
    border-left-color: #ffa726;
    background: linear-gradient(135deg, #fffbf0 0%, #fff3e0 100%);
}

.fda-news {
    border-left-color: #42a5f5;
    background: linear-gradient(135deg, #f3f8ff 0%, #e3f2fd 100%);
}

.high-risk {
    border-left-color: #e53e3e;
}

.medium-risk {
    border-left-color: #ffa726;
}

.low-risk {
    border-left-color: #66bb6a;
}

.days-until {
    background: #e8f5e8;
    color: #2e7d32;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.9rem;
    font-weight: bold;
    margin: 0.5rem 0;
}

.major-impact {
    background: #ffebee;
    color: #c62828;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
}

.moderate-impact {
    background: #fff3e0;
    color: #ef6c00;
    padding: 0.3rem 0.8rem;
    border-radius: 20px;
    font-size: 0.8rem;
    font-weight: bold;
}

.market-cap {
    font-size: 1.2rem;
    font-weight: bold;
    color: #1976d2;
}

.news-link {
    color: #1976d2;
    text-decoration: none;
    font-weight: 500;
    margin-right: 1rem;
}

.news-link:hover {
    text-decoration: underline;
}

.risk-high {
    color: #d32f2f;
    font-weight: bold;
}

.risk-medium {
    color: #f57c00;
    font-weight: bold;
}

.risk-low {
    color: #388e3c;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
    <div class="fda-header">
        <h1>🏥 FDA Calendar & Drug Approvals</h1>
        <p style="font-size: 1.2rem;">Track PDUFA dates, FDA decisions, and regulatory milestones</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize the FDA scraper
    if 'fda_scraper' not in st.session_state:
        st.session_state.fda_scraper = LiveFDAScaper()
    
    # Sidebar filters
    st.sidebar.header("🔍 Filter FDA Events")
    
    days_ahead = st.sidebar.slider(
        "Days Ahead to Show",
        7, 365, 60,
        help="Number of days ahead to look for FDA events"
    )
    
    event_types = st.sidebar.multiselect(
        "Event Types",
        ["PDUFA/FDA Milestone", "FDA Announcement", "FDA News"],
        default=["PDUFA/FDA Milestone", "FDA Announcement", "FDA News"]
    )
    
    risk_levels = st.sidebar.multiselect(
        "Risk Levels",
        ["High", "Medium", "Low"],
        default=["High", "Medium", "Low"]
    )
    
    show_past_events = st.sidebar.checkbox(
        "Include Recent Past Events",
        value=True,
        help="Show FDA events from the last 30 days"
    )
    
    # Load FDA calendar data
    with st.spinner("🔄 Loading live FDA calendar data..."):
        fda_events = st.session_state.fda_scraper.get_live_fda_calendar(days_ahead)
    
    if not fda_events:
        st.error("Could not load FDA calendar data. Please try again later.")
        return
    
    # Filter events
    filtered_events = []
    for event in fda_events:
        # Event type filter
        if event.get('event_type') not in event_types:
            continue
            
        # Risk level filter
        if event.get('risk_level') and event.get('risk_level') not in risk_levels:
            continue
            
        # Past events filter
        if not show_past_events and event.get('days_until', 0) < 0:
            continue
            
        filtered_events.append(event)
    
    # Main content tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📅 Upcoming Events", "📊 Event Analytics", "🧪 Clinical Trials", "📈 Market Impact"])
    
    with tab1:
        show_upcoming_events(filtered_events)
    
    with tab2:
        show_event_analytics(filtered_events)
    
    with tab3:
        show_clinical_trials()
    
    with tab4:
        show_market_impact(filtered_events)

def show_upcoming_events(events):
    """Display upcoming FDA events"""
    
    if not events:
        st.info("No FDA events match your current filters. Try adjusting the criteria.")
        return
    
    # Key metrics
    upcoming_pdufa = len([e for e in events if e.get('event_type') == 'PDUFA/FDA Milestone' and e.get('days_until', 0) > 0])
    high_risk_events = len([e for e in events if e.get('risk_level') == 'High'])
    total_market_cap = sum([e.get('market_cap', 0) for e in events if e.get('market_cap')])
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📅 Upcoming PDUFA Dates", upcoming_pdufa)
    
    with col2:
        st.metric("⚠️ High Risk Events", high_risk_events)
    
    with col3:
        st.metric("💰 Total Market Cap at Risk", f"${total_market_cap/1e9:.0f}B")
    
    with col4:
        st.metric("📊 Total Events", len(events))
    
    st.markdown("---")
    
    # Upcoming events timeline
    st.markdown("#### 📅 Upcoming FDA Events Timeline")
    
    # Sort events by date
    sorted_events = sorted(events, key=lambda x: x.get('event_date', datetime.now()))
    
    for event in sorted_events[:15]:  # Show top 15 events
        
        # Determine card class based on event type
        card_class = "event-card"
        if event.get('event_type') == 'PDUFA/FDA Milestone':
            card_class += " pdufa-event"
        elif event.get('catalyst_type') == 'FDA Advisory Committee':
            card_class += " advisory-committee"
        elif event.get('event_type') == 'FDA News':
            card_class += " fda-news"
        
        # Risk level styling
        risk_class = ""
        if event.get('risk_level'):
            risk_class = f"risk-{event.get('risk_level').lower()}"
        
        # Days until styling
        days_until = event.get('days_until', 0)
        days_text = ""
        if days_until > 0:
            days_text = f"<span class='days-until'>In {days_until} days</span>"
        elif days_until == 0:
            days_text = "<span class='days-until' style='background: #ffcdd2; color: #c62828;'>Today</span>"
        else:
            days_text = f"<span class='days-until' style='background: #f3e5f5; color: #7b1fa2;'>{abs(days_until)} days ago</span>"
        
        # Market impact styling
        impact_class = ""
        if event.get('market_impact') == 'Major':
            impact_class = "major-impact"
        elif event.get('market_impact') == 'Moderate':
            impact_class = "moderate-impact"
        
        # Format market cap
        market_cap_text = ""
        if event.get('market_cap'):
            market_cap_b = event.get('market_cap') / 1e9
            market_cap_text = f"<div class='market-cap'>${market_cap_b:.0f}B Market Cap</div>"
        
        # News links
        news_links_html = ""
        if event.get('news_links'):
            links = []
            for link in event.get('news_links', [])[:3]:  # Limit to 3 links
                links.append(f"<a href='{link.get('url', '#')}' target='_blank' class='news-link'>📰 {link.get('source', 'News')}</a>")
            news_links_html = "".join(links)
        
        st.markdown(f"""
        <div class="{card_class}">
            <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                <div style="flex: 1;">
                    <h4>{event.get('title', 'FDA Event')}</h4>
                    <div style="margin: 0.5rem 0;">
                        {days_text}
                        {f'<span class="{impact_class}" style="margin-left: 0.5rem;">{event.get("market_impact", "")}</span>' if event.get('market_impact') else ''}
                        {f'<span class="{risk_class}" style="margin-left: 0.5rem;">Risk: {event.get("risk_level", "")}</span>' if event.get('risk_level') else ''}
                    </div>
                    {f'<p><strong>Company:</strong> {event.get("company", "N/A")}</p>' if event.get('company') else ''}
                    {f'<p><strong>Drug:</strong> {event.get("drug_name", "N/A")}</p>' if event.get('drug_name') else ''}
                    {f'<p><strong>Indication:</strong> {event.get("indication", "N/A")}</p>' if event.get('indication') else ''}
                    {f'<p><strong>Event Type:</strong> {event.get("catalyst_type", event.get("event_type", "N/A"))}</p>'}
                    <div style="font-size: 0.9rem; color: #666; margin-top: 1rem;">
                        <strong>Date:</strong> {event.get('date_formatted', 'N/A')} | <strong>Source:</strong> {event.get('source', 'FDA')}
                    </div>
                    {f'<div style="margin-top: 0.5rem;">{news_links_html}</div>' if news_links_html else ''}
                </div>
                <div style="text-align: right; margin-left: 1rem;">
                    {market_cap_text}
                    {f'<div style="font-size: 0.9rem; color: #666; margin-top: 0.5rem;">Ticker: {event.get("ticker", "N/A")}</div>' if event.get('ticker') else ''}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Search functionality
    st.markdown("---")
    st.markdown("#### 🔍 Search FDA Events")
    
    search_term = st.text_input("Search by company, drug, or indication:")
    
    if search_term:
        search_results = []
        search_term = search_term.lower()
        
        for event in events:
            # Search in multiple fields
            search_fields = [
                event.get('title', ''),
                event.get('company', ''),
                event.get('drug_name', ''),
                event.get('indication', ''),
                event.get('description', '')
            ]
            
            if any(search_term in field.lower() for field in search_fields):
                search_results.append(event)
        
        if search_results:
            st.markdown(f"Found {len(search_results)} events matching '{search_term}':")
            
            for event in search_results[:5]:
                st.markdown(f"""
                **{event.get('title', 'FDA Event')}**  
                🏢 Company: {event.get('company', 'N/A')} | 💊 Drug: {event.get('drug_name', 'N/A')}  
                📅 Date: {event.get('date_formatted', 'N/A')} | ⚠️ Risk: {event.get('risk_level', 'N/A')}  
                """)
        else:
            st.info(f"No events found matching '{search_term}'")

def show_event_analytics(events):
    """Show FDA event analytics"""
    
    if not events:
        st.info("No events to analyze with current filters.")
        return
    
    # Timeline chart
    st.markdown("#### 📊 FDA Events Timeline")
    
    # Group events by month
    monthly_data = {}
    for event in events:
        if event.get('event_date'):
            month_key = event['event_date'].strftime('%Y-%m')
            if month_key not in monthly_data:
                monthly_data[month_key] = {'PDUFA': 0, 'News': 0, 'Other': 0}
            
            if event.get('event_type') == 'PDUFA/FDA Milestone':
                monthly_data[month_key]['PDUFA'] += 1
            elif event.get('event_type') == 'FDA News':
                monthly_data[month_key]['News'] += 1
            else:
                monthly_data[month_key]['Other'] += 1
    
    if monthly_data:
        months = sorted(monthly_data.keys())
        pdufa_counts = [monthly_data[m]['PDUFA'] for m in months]
        news_counts = [monthly_data[m]['News'] for m in months]
        other_counts = [monthly_data[m]['Other'] for m in months]
        
        fig = go.Figure()
        fig.add_trace(go.Bar(x=months, y=pdufa_counts, name='PDUFA/Milestones', marker_color='#ee5a24'))
        fig.add_trace(go.Bar(x=months, y=news_counts, name='FDA News', marker_color='#42a5f5'))
        fig.add_trace(go.Bar(x=months, y=other_counts, name='Other Events', marker_color='#66bb6a'))
        
        fig.update_layout(
            title="FDA Events by Month",
            xaxis_title="Month",
            yaxis_title="Number of Events",
            barmode='stack'
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Risk analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚠️ Risk Level Distribution")
        
        risk_counts = {}
        for event in events:
            risk = event.get('risk_level', 'Unknown')
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        
        if risk_counts:
            fig = px.pie(
                values=list(risk_counts.values()),
                names=list(risk_counts.keys()),
                title="Events by Risk Level",
                color_discrete_map={'High': '#e53e3e', 'Medium': '#ffa726', 'Low': '#66bb6a'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.markdown("#### 🏥 Therapeutic Areas")
        
        indication_counts = {}
        for event in events:
            indication = event.get('indication', 'Other')
            indication_counts[indication] = indication_counts.get(indication, 0) + 1
        
        if indication_counts:
            # Sort by count and take top 5
            top_indications = sorted(indication_counts.items(), key=lambda x: x[1], reverse=True)[:5]
            
            fig = px.bar(
                x=[item[1] for item in top_indications],
                y=[item[0] for item in top_indications],
                orientation='h',
                title="Top Therapeutic Areas"
            )
            fig.update_traces(marker_color='#ff6b6b')
            st.plotly_chart(fig, use_container_width=True)
    
    # Market impact analysis
    st.markdown("#### 💰 Market Impact Analysis")
    
    impact_data = {}
    impact_market_cap = {}
    
    for event in events:
        impact = event.get('market_impact', 'Unknown')
        market_cap = event.get('market_cap', 0)
        
        impact_data[impact] = impact_data.get(impact, 0) + 1
        impact_market_cap[impact] = impact_market_cap.get(impact, 0) + market_cap
    
    if impact_data:
        col1, col2 = st.columns(2)
        
        with col1:
            # Number of events by impact
            fig = px.bar(
                x=list(impact_data.keys()),
                y=list(impact_data.values()),
                title="Events by Market Impact",
                color=list(impact_data.keys()),
                color_discrete_map={'Major': '#e53e3e', 'Moderate': '#ffa726', 'Minor': '#66bb6a'}
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Market cap at risk by impact
            market_cap_b = {k: v/1e9 for k, v in impact_market_cap.items() if v > 0}
            if market_cap_b:
                fig = px.bar(
                    x=list(market_cap_b.keys()),
                    y=list(market_cap_b.values()),
                    title="Market Cap at Risk ($B)",
                    color=list(market_cap_b.keys()),
                    color_discrete_map={'Major': '#e53e3e', 'Moderate': '#ffa726', 'Minor': '#66bb6a'}
                )
                st.plotly_chart(fig, use_container_width=True)

def show_clinical_trials():
    """Show clinical trials information"""
    
    st.markdown("#### 🧪 Key Clinical Trials & Studies")
    
    # Get clinical trials data
    trials_data = st.session_state.fda_scraper.get_clinical_trials_data()
    
    if trials_data:
        for trial in trials_data:
            st.markdown(f"""
            <div class="event-card">
                <h4>{trial.get('title', 'Clinical Trial')}</h4>
                <div style="margin: 0.5rem 0;">
                    <strong>Sponsor:</strong> {trial.get('sponsor', 'N/A')} | 
                    <strong>Phase:</strong> {trial.get('phase', 'N/A')} | 
                    <strong>Status:</strong> {trial.get('status', 'N/A')}
                </div>
                <p><strong>Condition:</strong> {trial.get('condition', 'N/A')}</p>
                <p><strong>Enrollment:</strong> {trial.get('enrollment', 'N/A')} participants</p>
                <p><strong>Locations:</strong> {trial.get('locations', 'N/A')}</p>
                <p><strong>Primary Outcome:</strong> {trial.get('primary_outcome', 'N/A')}</p>
                <p><strong>Estimated Completion:</strong> {trial.get('estimated_completion', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Clinical trial statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("🔬 Active Trials", len([t for t in trials_data if 'recruiting' in t.get('status', '').lower()]))
    
    with col2:
        total_enrollment = sum([t.get('enrollment', 0) for t in trials_data])
        st.metric("👥 Total Enrollment", f"{total_enrollment:,}")
    
    with col3:
        phase_3_trials = len([t for t in trials_data if 'phase 3' in t.get('phase', '').lower()])
        st.metric("🎯 Phase 3 Trials", phase_3_trials)

def show_market_impact(events):
    """Show market impact analysis"""
    
    st.markdown("#### 📈 Market Impact Analysis")
    
    # High-impact upcoming events
    high_impact_events = [e for e in events if e.get('market_impact') == 'Major' and e.get('days_until', 0) > 0]
    
    if high_impact_events:
        st.markdown("##### 🚨 High-Impact Upcoming Events")
        
        for event in sorted(high_impact_events, key=lambda x: x.get('days_until', 999))[:5]:
            market_cap_b = event.get('market_cap', 0) / 1e9 if event.get('market_cap') else 0
            
            st.markdown(f"""
            **{event.get('company', 'N/A')} - {event.get('drug_name', 'N/A')}**  
            📅 {event.get('date_formatted', 'N/A')} ({event.get('days_until', 0)} days)  
            💰 Market Cap: ${market_cap_b:.0f}B | ⚠️ Risk: {event.get('risk_level', 'N/A')}  
            🏥 {event.get('indication', 'N/A')} | {event.get('catalyst_type', 'FDA Event')}
            """)
    
    # Market insights
    st.markdown("##### 💡 Key Market Insights")
    
    insights = [
        "**Alzheimer's Disease Focus**: Multiple major PDUFA dates for Alzheimer's treatments represent significant market opportunities and risks.",
        
        "**Rare Disease Premiums**: FDA approvals in rare diseases typically drive higher stock price movements due to favorable regulatory pathways.",
        
        "**Advisory Committee Impact**: FDA advisory committee meetings can create significant volatility even before final approval decisions.",
        
        "**Biotech Volatility**: Smaller biotech companies face higher percentage price movements on FDA decisions due to pipeline concentration.",
        
        "**Patent Cliff Considerations**: FDA approvals help companies offset revenue losses from patent expirations."
    ]
    
    for insight in insights:
        st.markdown(f"• {insight}")
    
    # FDA approval success rates
    st.markdown("##### 📊 FDA Approval Context")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.info("""
        **FDA Approval Success Rates:**
        
        🔹 **Phase 3 to Approval**: ~58% overall  
        🔹 **Oncology**: ~48% success rate  
        🔹 **Rare Diseases**: ~72% success rate  
        🔹 **CNS/Neurology**: ~42% success rate  
        🔹 **Breakthrough Therapy**: ~85% success rate
        """)
    
    with col2:
        st.info("""
        **Average Timeline:**
        
        🔹 **Standard Review**: 10-12 months  
        🔹 **Priority Review**: 6-8 months  
        🔹 **Fast Track**: 6 months  
        🔹 **Breakthrough Therapy**: 6 months  
        🔹 **Accelerated Approval**: 6-8 months
        """)

if __name__ == "__main__":
    main()
