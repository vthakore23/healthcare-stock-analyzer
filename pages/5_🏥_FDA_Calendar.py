import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Page configuration
st.set_page_config(
    page_title="FDA Calendar - Healthcare Analyzer",
    page_icon="🏥",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .fda-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .event-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .pdufa-date { border-left: 4px solid #ff6b6b; }
    .advisory-committee { border-left: 4px solid #4ecdc4; }
    .approval { border-left: 4px solid #45b7d1; }
    .rejection { border-left: 4px solid #96ceb4; }
    .clinical-hold { border-left: 4px solid #ffeaa7; }
</style>
""", unsafe_allow_html=True)

def main():
    st.markdown("""
    <div class="fda-header">
        <h1>🏥 FDA Regulatory Calendar</h1>
        <p style="font-size: 1.2rem;">Track FDA approvals, PDUFA dates, and regulatory milestones</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["📅 Upcoming Events", "📊 Event Analysis", "🔔 Alerts & Notifications"])
    
    with tab1:
        show_upcoming_events()
    
    with tab2:
        show_event_analysis()
    
    with tab3:
        show_alerts_notifications()

def show_upcoming_events():
    """Show upcoming FDA events and milestones"""
    st.markdown("### 📅 Upcoming FDA Events")
    
    # Filter options
    col1, col2, col3 = st.columns(3)
    
    with col1:
        event_type = st.selectbox("Event Type:", 
                                 ["All", "PDUFA Date", "Advisory Committee", "Clinical Hold", "Approval Decision"])
    
    with col2:
        time_frame = st.selectbox("Time Frame:", 
                                 ["Next 30 Days", "Next 90 Days", "Next 6 Months", "Next Year"])
    
    with col3:
        therapeutic_area = st.selectbox("Therapeutic Area:", 
                                       ["All", "Oncology", "CNS", "Cardiovascular", "Infectious Disease", "Rare Disease"])
    
    # Generate sample FDA events
    events = generate_sample_events()
    
    # Display events
    display_events_list(events, event_type, time_frame, therapeutic_area)
    
    # Timeline view
    create_events_timeline(events)

def show_event_analysis():
    """Show FDA event analysis and statistics"""
    st.markdown("### 📊 FDA Event Analysis")
    
    # Analysis metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📋 Total Events", "47")
        st.metric("📅 This Month", "8")
    
    with col2:
        st.metric("🎯 PDUFA Dates", "12")
        st.metric("🏛️ AdCom Meetings", "3")
    
    with col3:
        st.metric("✅ Approvals Expected", "15")
        st.metric("⏸️ Clinical Holds", "2")
    
    with col4:
        st.metric("🧬 Oncology Events", "18")
        st.metric("🧠 CNS Events", "7")
    
    # Analysis charts
    create_analysis_charts()

def show_alerts_notifications():
    """Show alerts and notification settings"""
    st.markdown("### 🔔 Alerts & Notifications")
    
    st.info("🚧 Feature coming soon: Set up personalized alerts for FDA events")
    
    # Demo notification settings
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### ⚙️ Alert Settings")
        
        st.checkbox("📧 Email notifications", value=True)
        st.checkbox("📱 Push notifications", value=False)
        st.checkbox("📅 Calendar integration", value=True)
        
        st.selectbox("Alert timing:", ["1 day before", "3 days before", "1 week before", "2 weeks before"])
        
        st.multiselect("Event types to track:", 
                      ["PDUFA Dates", "Advisory Committee", "Approvals", "Clinical Holds"],
                      default=["PDUFA Dates", "Approvals"])
    
    with col2:
        st.markdown("#### 📊 Recent Alerts")
        
        recent_alerts = [
            {"Date": "2024-06-10", "Event": "PDUFA Date Approaching", "Company": "Vertex", "Drug": "VX-548"},
            {"Date": "2024-06-08", "Event": "Advisory Committee", "Company": "Moderna", "Drug": "mRNA-1273"},
            {"Date": "2024-06-05", "Event": "Approval Decision", "Company": "Gilead", "Drug": "GS-441524"},
        ]
        
        for alert in recent_alerts:
            st.markdown(f"""
            <div class="event-card">
                <strong>{alert['Event']}</strong><br>
                {alert['Company']} - {alert['Drug']}<br>
                <small>{alert['Date']}</small>
            </div>
            """, unsafe_allow_html=True)

def generate_sample_events():
    """Generate sample FDA events"""
    base_date = datetime.now()
    
    events = [
        {
            "date": base_date + timedelta(days=7),
            "company": "Vertex Pharmaceuticals",
            "ticker": "VRTX",
            "drug": "VX-548",
            "indication": "Acute Pain",
            "event_type": "PDUFA Date",
            "therapeutic_area": "CNS",
            "probability": "High"
        },
        {
            "date": base_date + timedelta(days=14),
            "company": "Moderna",
            "ticker": "MRNA", 
            "drug": "mRNA-1273.222",
            "indication": "COVID-19 Variant",
            "event_type": "Advisory Committee",
            "therapeutic_area": "Infectious Disease",
            "probability": "Medium"
        },
        {
            "date": base_date + timedelta(days=21),
            "company": "Gilead Sciences",
            "ticker": "GILD",
            "drug": "GS-441524",
            "indication": "COVID-19",
            "event_type": "Approval Decision",
            "therapeutic_area": "Infectious Disease", 
            "probability": "High"
        },
        {
            "date": base_date + timedelta(days=28),
            "company": "Regeneron",
            "ticker": "REGN",
            "drug": "REGN-COV2",
            "indication": "COVID-19 Prevention",
            "event_type": "PDUFA Date",
            "therapeutic_area": "Infectious Disease",
            "probability": "Medium"
        },
        {
            "date": base_date + timedelta(days=35),
            "company": "BioNTech",
            "ticker": "BNTX",
            "drug": "BNT162b2",
            "indication": "Pediatric COVID-19",
            "event_type": "Advisory Committee",
            "therapeutic_area": "Infectious Disease",
            "probability": "High"
        },
        {
            "date": base_date + timedelta(days=42),
            "company": "Pfizer",
            "ticker": "PFE",
            "drug": "PF-07321332",
            "indication": "COVID-19 Treatment",
            "event_type": "PDUFA Date",
            "therapeutic_area": "Infectious Disease",
            "probability": "High"
        },
        {
            "date": base_date + timedelta(days=56),
            "company": "Bristol Myers Squibb",
            "ticker": "BMY",
            "drug": "Liso-cel",
            "indication": "B-cell Lymphoma",
            "event_type": "Approval Decision",
            "therapeutic_area": "Oncology",
            "probability": "Medium"
        },
        {
            "date": base_date + timedelta(days=63),
            "company": "Roche",
            "ticker": "RHHBY",
            "drug": "Tecentriq",
            "indication": "Bladder Cancer",
            "event_type": "Advisory Committee",
            "therapeutic_area": "Oncology",
            "probability": "Medium"
        }
    ]
    
    return events

def display_events_list(events, event_type_filter, time_frame_filter, therapeutic_area_filter):
    """Display filtered list of events"""
    
    # Apply filters
    filtered_events = events.copy()
    
    if event_type_filter != "All":
        filtered_events = [e for e in filtered_events if e['event_type'] == event_type_filter]
    
    if therapeutic_area_filter != "All":
        filtered_events = [e for e in filtered_events if e['therapeutic_area'] == therapeutic_area_filter]
    
    # Time frame filter
    cutoff_date = datetime.now()
    if time_frame_filter == "Next 30 Days":
        cutoff_date += timedelta(days=30)
    elif time_frame_filter == "Next 90 Days":
        cutoff_date += timedelta(days=90)
    elif time_frame_filter == "Next 6 Months":
        cutoff_date += timedelta(days=180)
    elif time_frame_filter == "Next Year":
        cutoff_date += timedelta(days=365)
    
    filtered_events = [e for e in filtered_events if e['date'] <= cutoff_date]
    
    st.markdown(f"### 📋 Events ({len(filtered_events)} found)")
    
    # Display events
    for event in sorted(filtered_events, key=lambda x: x['date']):
        event_class = get_event_class(event['event_type'])
        days_until = (event['date'] - datetime.now()).days
        
        st.markdown(f"""
        <div class="event-card {event_class}">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h4>{event['company']} ({event['ticker']})</h4>
                    <p><strong>{event['drug']}</strong> - {event['indication']}</p>
                    <p><strong>Event:</strong> {event['event_type']}</p>
                    <p><strong>Date:</strong> {event['date'].strftime('%Y-%m-%d')} ({days_until} days)</p>
                </div>
                <div style="text-align: right;">
                    <span style="background-color: {'#d4edda' if event['probability'] == 'High' else '#fff3cd' if event['probability'] == 'Medium' else '#f8d7da'}; 
                                 padding: 0.25rem 0.5rem; border-radius: 4px; font-size: 0.8rem;">
                        {event['probability']} Probability
                    </span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def create_events_timeline(events):
    """Create timeline visualization of events"""
    st.markdown("### 📊 Events Timeline")
    
    # Prepare data for timeline
    timeline_data = []
    for event in events:
        timeline_data.append({
            'Company': event['company'],
            'Drug': event['drug'],
            'Event': event['event_type'],
            'Date': event['date'],
            'Days Until': (event['date'] - datetime.now()).days,
            'Therapeutic Area': event['therapeutic_area']
        })
    
    df = pd.DataFrame(timeline_data)
    
    # Create timeline chart
    fig = px.scatter(
        df,
        x='Date',
        y='Company',
        color='Event',
        size='Days Until',
        hover_data=['Drug', 'Therapeutic Area'],
        title="FDA Events Timeline"
    )
    
    fig.update_layout(height=500)
    st.plotly_chart(fig, use_container_width=True)

def create_analysis_charts():
    """Create analysis charts"""
    col1, col2 = st.columns(2)
    
    with col1:
        # Events by type
        event_types = ['PDUFA Date', 'Advisory Committee', 'Approval Decision', 'Clinical Hold']
        event_counts = [12, 8, 15, 3]
        
        fig_types = px.pie(
            values=event_counts,
            names=event_types,
            title="Events by Type"
        )
        st.plotly_chart(fig_types, use_container_width=True)
    
    with col2:
        # Events by therapeutic area
        therapeutic_areas = ['Oncology', 'CNS', 'Cardiovascular', 'Infectious Disease', 'Rare Disease']
        area_counts = [18, 7, 5, 12, 6]
        
        fig_areas = px.bar(
            x=therapeutic_areas,
            y=area_counts,
            title="Events by Therapeutic Area"
        )
        st.plotly_chart(fig_areas, use_container_width=True)
    
    # Monthly distribution
    st.markdown("#### 📅 Monthly Distribution")
    
    months = ['Jun 2024', 'Jul 2024', 'Aug 2024', 'Sep 2024', 'Oct 2024', 'Nov 2024']
    monthly_counts = [8, 12, 9, 7, 6, 5]
    
    fig_monthly = px.line(
        x=months,
        y=monthly_counts,
        title="FDA Events by Month",
        markers=True
    )
    st.plotly_chart(fig_monthly, use_container_width=True)

def get_event_class(event_type):
    """Get CSS class for event type"""
    event_classes = {
        'PDUFA Date': 'pdufa-date',
        'Advisory Committee': 'advisory-committee',
        'Approval Decision': 'approval',
        'Clinical Hold': 'clinical-hold'
    }
    return event_classes.get(event_type, '')

if __name__ == "__main__":
    main()
