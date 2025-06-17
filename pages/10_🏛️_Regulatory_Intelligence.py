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
    from medequity_utils.regulatory_intelligence import RegulatoryIntelligence
    import yfinance as yf
except ImportError as e:
    st.error(f"Import error: {e}")

# Page configuration
st.set_page_config(
    page_title="Regulatory Intelligence Dashboard",
    page_icon="🏛️",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
.regulatory-header {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.regulatory-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #4f46e5;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.fda-card { border-left-color: #dc2626; }
.ema-card { border-left-color: #059669; }
.warning-card { border-left-color: #f59e0b; background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); }
.approval-card { border-left-color: #10b981; background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); }

.risk-score {
    text-align: center;
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

.risk-high { background: linear-gradient(135deg, #fef2f2 0%, #fecaca 100%); }
.risk-medium { background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%); }
.risk-low { background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); }

.pdufa-card {
    background: linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%);
    border-radius: 8px;
    padding: 1rem;
    margin: 0.5rem 0;
    border-left: 4px solid #0ea5e9;
}
</style>
""", unsafe_allow_html=True)

# Initialize regulatory intelligence
if 'regulatory_intel' not in st.session_state:
    st.session_state.regulatory_intel = RegulatoryIntelligence()

def main():
    st.markdown("""
    <div class="regulatory-header">
        <h1>🏛️ Regulatory Intelligence Dashboard</h1>
        <p>Real-time FDA & EMA Data • Approval Predictions • Risk Assessment</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Dashboard", 
        "🇺🇸 FDA Intelligence", 
        "🇪🇺 EMA Intelligence", 
        "🔔 Regulatory Alerts"
    ])
    
    with tab1:
        show_regulatory_dashboard()
    
    with tab2:
        show_fda_intelligence()
    
    with tab3:
        show_ema_intelligence()
    
    with tab4:
        show_regulatory_alerts()

def show_regulatory_dashboard():
    """Show main regulatory dashboard"""
    st.markdown("### 📊 Comprehensive Regulatory Overview")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Healthcare Company Ticker:",
            placeholder="e.g., PFE, JNJ, MRNA, REGN",
            help="Enter a healthcare company ticker for regulatory analysis",
            key="dashboard_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("📊 Analyze Regulatory", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        analyze_regulatory_dashboard(ticker)
    else:
        show_dashboard_features()

def show_dashboard_features():
    """Show dashboard features"""
    st.markdown("### 🌟 Regulatory Intelligence Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🇺🇸 FDA Intelligence**
        - Real-time drug approvals
        - Warning letters monitoring
        - Inspection outcomes tracking
        - PDUFA date calendar
        """)
    
    with col2:
        st.markdown("""
        **🤖 AI Predictions**
        - Approval likelihood scoring
        - Risk factor analysis
        - Timeline predictions
        - Success probability models
        """)
    
    with col3:
        st.markdown("""
        **🔔 Alert System**
        - Regulatory event notifications
        - Risk threshold monitoring
        - Timeline-based alerts
        - Competitive intelligence
        """)

def analyze_regulatory_dashboard(ticker: str):
    """Analyze regulatory dashboard for company"""
    with st.spinner(f"Analyzing regulatory status for {ticker}..."):
        try:
            dashboard_data = st.session_state.regulatory_intel.get_regulatory_dashboard(ticker)
            
            if 'error' in dashboard_data:
                st.error(f"Error: {dashboard_data['error']}")
                return
            
            display_dashboard_results(dashboard_data)
            
        except Exception as e:
            st.error(f"Regulatory analysis failed: {str(e)}")

def display_dashboard_results(dashboard_data):
    """Display regulatory dashboard results"""
    ticker = dashboard_data['ticker']
    company_name = dashboard_data['company_name']
    fda_data = dashboard_data.get('fda_intelligence', {})
    ema_data = dashboard_data.get('ema_intelligence', {})
    predictions = dashboard_data.get('approval_predictions', {})
    risk_score = dashboard_data.get('regulatory_risk_score', {})
    
    st.markdown(f"## 🏛️ {company_name} ({ticker}) - Regulatory Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        recent_approvals = len(fda_data.get('recent_approvals', []))
        st.metric("Recent FDA Approvals", recent_approvals)
    
    with col2:
        warning_letters = len(fda_data.get('warning_letters', []))
        st.metric("Warning Letters", warning_letters)
    
    with col3:
        pending_pdufa = len(fda_data.get('pdufa_dates', []))
        st.metric("Pending PDUFA", pending_pdufa)
    
    with col4:
        overall_risk = risk_score.get('overall_risk_score', 0)
        st.metric("Risk Score", f"{overall_risk:.0f}/100")
    
    # Risk assessment
    show_risk_assessment(risk_score)
    
    # Approval predictions
    show_approval_predictions(predictions)
    
    # Recent regulatory activities
    show_recent_activities(fda_data, ema_data)

def show_risk_assessment(risk_score):
    """Show regulatory risk assessment"""
    st.markdown("### ⚖️ Regulatory Risk Assessment")
    
    if 'error' in risk_score:
        st.error(f"Risk assessment error: {risk_score['error']}")
        return
    
    overall_risk = risk_score.get('overall_risk_score', 0)
    risk_level = risk_score.get('risk_level', 'Unknown')
    
    # Determine risk styling
    if risk_level == 'Very High' or risk_level == 'High':
        risk_class = "risk-high"
        risk_color = "#ef4444"
    elif risk_level == 'Medium':
        risk_class = "risk-medium"
        risk_color = "#f59e0b"
    else:
        risk_class = "risk-low"
        risk_color = "#10b981"
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown(f"""
        <div class="risk-score {risk_class}">
            <h3>Overall Risk Score</h3>
            <h1 style="color: {risk_color}; margin: 0.5rem 0;">{overall_risk:.0f}/100</h1>
            <p><strong>{risk_level}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Risk components
        risk_components = risk_score.get('risk_components', {})
        
        if risk_components:
            component_names = list(risk_components.keys())
            component_values = list(risk_components.values())
            
            fig = px.bar(
                x=component_values,
                y=component_names,
                orientation='h',
                title='Risk Components Breakdown',
                color=component_values,
                color_continuous_scale='Reds'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Key concerns and mitigation
    concerns = risk_score.get('key_concerns', [])
    suggestions = risk_score.get('mitigation_suggestions', [])
    
    if concerns or suggestions:
        col1, col2 = st.columns(2)
        
        with col1:
            if concerns:
                st.markdown("**🚨 Key Concerns:**")
                for concern in concerns:
                    st.markdown(f"• {concern}")
        
        with col2:
            if suggestions:
                st.markdown("**💡 Mitigation Suggestions:**")
                for suggestion in suggestions:
                    st.markdown(f"• {suggestion}")

def show_approval_predictions(predictions):
    """Show approval predictions"""
    st.markdown("### 🔮 Approval Predictions")
    
    if 'error' in predictions:
        st.error(f"Prediction error: {predictions['error']}")
        return
    
    prediction_list = predictions.get('predictions', [])
    
    if not prediction_list:
        st.info("No pending applications found for approval prediction")
        return
    
    avg_probability = predictions.get('average_approval_probability', 0)
    total_pending = predictions.get('total_pending_applications', 0)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.metric("Avg Approval Probability", f"{avg_probability:.0%}")
        st.metric("Total Pending Apps", total_pending)
    
    with col2:
        # Predictions chart
        if prediction_list:
            product_names = [pred['product_name'] for pred in prediction_list]
            probabilities = [pred['approval_probability'] for pred in prediction_list]
            
            fig = px.bar(
                x=probabilities,
                y=product_names,
                orientation='h',
                title='Approval Probability by Product',
                color=probabilities,
                color_continuous_scale='Viridis'
            )
            fig.update_layout(height=300, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    # Detailed predictions
    for prediction in prediction_list:
        show_individual_prediction(prediction)

def show_individual_prediction(prediction):
    """Show individual approval prediction"""
    product_name = prediction['product_name']
    pdufa_date = prediction['pdufa_date']
    probability = prediction['approval_probability']
    confidence = prediction['confidence_level']
    
    # Determine probability styling
    if probability > 0.7:
        prob_color = "#10b981"
    elif probability > 0.4:
        prob_color = "#f59e0b"
    else:
        prob_color = "#ef4444"
    
    st.markdown(f"""
    <div class="pdufa-card">
        <h4>{product_name}</h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
            <div><strong>PDUFA Date:</strong><br>{pdufa_date}</div>
            <div><strong>Approval Probability:</strong><br>
                <span style="color: {prob_color}; font-weight: bold;">{probability:.0%}</span>
            </div>
            <div><strong>Confidence:</strong><br>{confidence}</div>
        </div>
        
        <div style="margin-top: 1rem;">
            <strong>Risk Factors:</strong>
            <ul style="margin: 0.5rem 0;">
                {"".join(f"<li>{factor}</li>" for factor in prediction.get('risk_factors', []))}
            </ul>
        </div>
        
        <div style="margin-top: 0.5rem;">
            <strong>Positive Factors:</strong>
            <ul style="margin: 0.5rem 0;">
                {"".join(f"<li>{factor}</li>" for factor in prediction.get('positive_factors', []))}
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

def show_recent_activities(fda_data, ema_data):
    """Show recent regulatory activities"""
    st.markdown("### 📋 Recent Regulatory Activities")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🇺🇸 FDA Activities")
        
        # Recent approvals
        approvals = fda_data.get('recent_approvals', [])
        if approvals:
            st.markdown("**Recent Approvals:**")
            for approval in approvals[:3]:
                st.markdown(f"""
                <div class="regulatory-card approval-card">
                    <h5>{approval.get('product_name', 'Unknown Product')}</h5>
                    <p><strong>Approval Date:</strong> {approval.get('approval_date', 'Unknown')}</p>
                    <p><strong>Indication:</strong> {approval.get('indication', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
        
        # Warning letters
        warnings = fda_data.get('warning_letters', [])
        if warnings:
            st.markdown("**Warning Letters:**")
            for warning in warnings[:2]:
                st.markdown(f"""
                <div class="regulatory-card warning-card">
                    <h5>{warning.get('facility', 'Unknown Facility')}</h5>
                    <p><strong>Issue Date:</strong> {warning.get('issue_date', 'Unknown')}</p>
                    <p><strong>Violation:</strong> {warning.get('violation_type', 'Unknown')}</p>
                    <p><strong>Status:</strong> {warning.get('status', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("#### 🇪🇺 EMA Activities")
        
        # EMA approvals
        ema_approvals = ema_data.get('recent_approvals', [])
        if ema_approvals:
            st.markdown("**Recent EMA Approvals:**")
            for approval in ema_approvals[:3]:
                st.markdown(f"""
                <div class="regulatory-card ema-card">
                    <h5>{approval.get('product_name', 'Unknown Product')}</h5>
                    <p><strong>Approval Date:</strong> {approval.get('approval_date', 'Unknown')}</p>
                    <p><strong>Indication:</strong> {approval.get('indication', 'Unknown')}</p>
                    <p><strong>Type:</strong> {approval.get('approval_type', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No recent EMA approvals found")

def show_fda_intelligence():
    """Show detailed FDA intelligence"""
    st.markdown("### 🇺🇸 FDA Intelligence Center")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Company Ticker for FDA Analysis:",
            placeholder="e.g., PFE, JNJ, MRNA",
            key="fda_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        fda_btn = st.button("🇺🇸 Analyze FDA", type="primary", use_container_width=True)
    
    if ticker and fda_btn:
        analyze_fda_intelligence(ticker)
    else:
        show_fda_overview()

def show_fda_overview():
    """Show FDA intelligence overview"""
    st.markdown("### 🇺🇸 FDA Intelligence Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **📊 Available FDA Data:**
        - Recent drug approvals
        - Warning letters database
        - Inspection outcomes
        - PDUFA date tracking
        - Regulatory submissions
        """)
    
    with col2:
        st.markdown("""
        **🎯 Analysis Features:**
        - Approval timeline predictions
        - Risk factor identification
        - Competitive benchmarking
        - Regulatory pathway optimization
        - Success probability modeling
        """)

def analyze_fda_intelligence(ticker: str):
    """Analyze FDA intelligence for company"""
    with st.spinner(f"Analyzing FDA data for {ticker}..."):
        try:
            dashboard_data = st.session_state.regulatory_intel.get_regulatory_dashboard(ticker)
            
            if 'error' in dashboard_data:
                st.error(f"Error: {dashboard_data['error']}")
                return
            
            fda_data = dashboard_data.get('fda_intelligence', {})
            display_fda_details(fda_data, ticker)
            
        except Exception as e:
            st.error(f"FDA analysis failed: {str(e)}")

def display_fda_details(fda_data, ticker):
    """Display detailed FDA information"""
    st.markdown(f"## 🇺🇸 FDA Intelligence - {ticker}")
    
    # PDUFA dates
    pdufa_dates = fda_data.get('pdufa_dates', [])
    if pdufa_dates:
        st.markdown("### 📅 Upcoming PDUFA Dates")
        
        for pdufa in pdufa_dates:
            days_remaining = pdufa.get('days_remaining', 0)
            
            if days_remaining <= 30:
                urgency_color = "#ef4444"
                urgency_text = "🔴 Critical"
            elif days_remaining <= 90:
                urgency_color = "#f59e0b"
                urgency_text = "🟡 High Priority"
            else:
                urgency_color = "#10b981"
                urgency_text = "🟢 Monitor"
            
            st.markdown(f"""
            <div class="pdufa-card" style="border-left-color: {urgency_color};">
                <h4>{pdufa.get('product_name', 'Unknown Product')}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                    <div><strong>PDUFA Date:</strong><br>{pdufa.get('pdufa_date', 'Unknown')}</div>
                    <div><strong>Days Remaining:</strong><br>{days_remaining}</div>
                    <div><strong>Application Type:</strong><br>{pdufa.get('application_type', 'Unknown')}</div>
                    <div><strong>Priority Review:</strong><br>{'Yes' if pdufa.get('priority_review') else 'No'}</div>
                </div>
                <p style="margin-top: 1rem; color: {urgency_color}; font-weight: bold;">{urgency_text}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Inspection outcomes
    inspections = fda_data.get('inspection_outcomes', [])
    if inspections:
        st.markdown("### 🔍 Recent Inspection Outcomes")
        
        for inspection in inspections:
            classification = inspection.get('classification', 'Unknown')
            
            if classification == 'OAI':
                class_color = "#ef4444"
            elif classification == 'VAI':
                class_color = "#f59e0b"
            else:
                class_color = "#10b981"
            
            st.markdown(f"""
            <div class="regulatory-card" style="border-left-color: {class_color};">
                <h4>{inspection.get('facility', 'Unknown Facility')}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr 1fr; gap: 1rem;">
                    <div><strong>Date:</strong><br>{inspection.get('inspection_date', 'Unknown')}</div>
                    <div><strong>Type:</strong><br>{inspection.get('inspection_type', 'Unknown')}</div>
                    <div><strong>Classification:</strong><br>
                        <span style="color: {class_color}; font-weight: bold;">{classification}</span>
                    </div>
                    <div><strong>Observations:</strong><br>{inspection.get('observations', 0)}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_ema_intelligence():
    """Show EMA intelligence"""
    st.markdown("### 🇪🇺 EMA Intelligence Center")
    st.info("🚧 EMA intelligence features coming soon. Currently focused on FDA data.")

def show_regulatory_alerts():
    """Show regulatory alerts"""
    st.markdown("### 🔔 Regulatory Alert System")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        ticker = st.text_input(
            "Company Ticker for Alerts:",
            placeholder="e.g., PFE, JNJ, MRNA",
            key="alerts_ticker"
        ).upper().strip()
    
    with col2:
        alert_threshold = st.slider("Alert Threshold (days)", 7, 90, 30)
    
    if st.button("🔔 Get Alerts", type="primary", use_container_width=True) and ticker:
        get_regulatory_alerts(ticker, alert_threshold)
    else:
        show_alerts_demo()

def show_alerts_demo():
    """Show demo alerts"""
    st.markdown("### 🚨 Sample Regulatory Alerts")
    
    demo_alerts = [
        {
            'type': 'pdufa_date',
            'urgency': 'critical',
            'title': 'PDUFA date approaching in 5 days',
            'description': 'Alzheimer\'s Drug - Priority Review',
            'pdufa_date': '2024-07-20',
            'application_type': 'NDA'
        },
        {
            'type': 'warning_letter',
            'urgency': 'high',
            'title': 'Open FDA warning letter requires response',
            'description': 'Manufacturing Facility - GMP Violations',
            'issue_date': '2024-06-01',
            'severity': 'High'
        }
    ]
    
    for alert in demo_alerts:
        display_alert_card(alert)

def get_regulatory_alerts(ticker: str, threshold: int):
    """Get regulatory alerts for company"""
    with st.spinner(f"Getting regulatory alerts for {ticker}..."):
        try:
            alerts = st.session_state.regulatory_intel.get_regulatory_alerts(ticker, threshold)
            
            if not alerts:
                st.info(f"No regulatory alerts found for {ticker} within {threshold} days")
                return
            
            st.markdown(f"## 🔔 Regulatory Alerts - {ticker}")
            st.markdown(f"**Alerts within {threshold} days:** {len(alerts)}")
            
            for alert in alerts:
                display_alert_card(alert)
                
        except Exception as e:
            st.error(f"Failed to get alerts: {str(e)}")

def display_alert_card(alert):
    """Display individual alert card"""
    urgency = alert.get('urgency', 'medium')
    
    if urgency == 'critical':
        alert_color = "#ef4444"
        alert_icon = "🚨"
    elif urgency == 'high':
        alert_color = "#f59e0b"
        alert_icon = "⚠️"
    else:
        alert_color = "#10b981"
        alert_icon = "ℹ️"
    
    st.markdown(f"""
    <div class="regulatory-card" style="border-left-color: {alert_color}; background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(248,250,252,0.9) 100%);">
        <div style="display: flex; align-items: start; gap: 1rem;">
            <div style="font-size: 1.5rem;">{alert_icon}</div>
            <div style="flex: 1;">
                <h4 style="margin: 0; color: {alert_color};">{alert['title']}</h4>
                <p style="margin: 0.5rem 0;">{alert['description']}</p>
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-top: 1rem; font-size: 0.9rem;">
                    {"".join([
                        f"<p><strong>{key.replace('_', ' ').title()}:</strong> {value}</p>" 
                        for key, value in alert.items() 
                        if key not in ['type', 'urgency', 'title', 'description']
                    ])}
                </div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main() 