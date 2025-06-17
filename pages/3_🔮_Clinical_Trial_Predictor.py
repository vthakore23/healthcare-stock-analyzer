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
    from medequity_utils.clinical_trial_predictor import ClinicalTrialPredictor
    import yfinance as yf
except ImportError as e:
    st.error(f"Import error: {e}")

# Page configuration
st.set_page_config(
    page_title="Clinical Trial Event Predictor",
    page_icon="🔮",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
.predictor-header {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.trial-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #3b82f6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.success-high { border-left-color: #10b981; }
.success-medium { border-left-color: #f59e0b; }
.success-low { border-left-color: #ef4444; }
</style>
""", unsafe_allow_html=True)

# Initialize predictor
if 'trial_predictor' not in st.session_state:
    st.session_state.trial_predictor = ClinicalTrialPredictor()

def main():
    st.markdown("""
    <div class="predictor-header">
        <h1>🔮 Clinical Trial Event Predictor</h1>
        <p>AI-Powered Trial Success Prediction & Stock Impact Analysis</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Healthcare Company Ticker:",
            placeholder="e.g., MRNA, PFE, REGN",
            help="Enter a healthcare company ticker to analyze clinical trials"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔮 Analyze Trials", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        analyze_trials(ticker)
    else:
        show_features()

def show_features():
    """Show feature overview"""
    st.markdown("### 🌟 Advanced Trial Prediction Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🤖 ML Predictions**
        - Success probability scoring
        - Company track record analysis  
        - Therapeutic area risk assessment
        - Trial design quality metrics
        """)
    
    with col2:
        st.markdown("""
        **📊 Real-Time Data**
        - Live ClinicalTrials.gov integration
        - FDA database monitoring
        - Regulatory milestone tracking
        - Competitive landscape analysis
        """)
    
    with col3:
        st.markdown("""
        **💰 Financial Impact**
        - Stock price impact scenarios
        - Revenue at risk calculations
        - Market opportunity sizing
        - Timeline-based projections
        """)

def analyze_trials(ticker: str):
    """Analyze company trials"""
    with st.spinner(f"Analyzing {ticker} clinical trials..."):
        try:
            # Fetch trials data
            trials_data = st.session_state.trial_predictor.fetch_clinicaltrials_data(ticker)
            
            if 'error' in trials_data:
                st.error(f"Error: {trials_data['error']}")
                return
            
            if not trials_data['trials']:
                st.warning(f"No clinical trials found for {ticker}")
                return
            
            display_results(trials_data)
            
        except Exception as e:
            st.error(f"Analysis failed: {str(e)}")

def display_results(trials_data):
    """Display trial analysis results"""
    ticker = trials_data['ticker']
    company_name = trials_data['company_name'] 
    trials = trials_data['trials']
    
    st.markdown(f"## 🔬 {company_name} ({ticker}) - Trial Analysis")
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Trials", len(trials))
    
    with col2:
        active = sum(1 for t in trials if 'active' in t.get('status', '').lower())
        st.metric("Active Trials", active)
    
    with col3:
        phase3 = sum(1 for t in trials if 'phase 3' in t.get('phase', '').lower())
        st.metric("Phase III", phase3)
    
    with col4:
        # Calculate average success probability
        predictions = []
        for trial in trials[:5]:
            try:
                pred = st.session_state.trial_predictor.predict_trial_success(trial)
                predictions.append(pred['success_probability'])
            except:
                continue
        
        avg_success = np.mean(predictions) if predictions else 0.5
        st.metric("Avg Success", f"{avg_success:.0%}")
    
    # Individual trial predictions
    st.markdown("### 🔮 Trial Predictions")
    
    for i, trial in enumerate(trials[:6]):
        with st.expander(f"Trial {i+1}: {trial.get('title', 'Unknown')[:80]}...", expanded=i<2):
            show_trial_prediction(trial)

def show_trial_prediction(trial):
    """Show individual trial prediction"""
    try:
        prediction = st.session_state.trial_predictor.predict_trial_success(trial)
        
        success_prob = prediction['success_probability']
        confidence = prediction['confidence']
        factors = prediction['factors']
        risk_level = prediction['risk_level']
        
        # Styling based on probability
        if success_prob > 0.7:
            card_class = "success-high"
        elif success_prob > 0.4:
            card_class = "success-medium"
        else:
            card_class = "success-low"
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown(f"""
            <div class="trial-card {card_class}">
                <h4>Trial Details</h4>
                <p><strong>Phase:</strong> {trial.get('phase', 'Unknown')}</p>
                <p><strong>Condition:</strong> {trial.get('condition', 'Unknown')}</p>
                <p><strong>Status:</strong> {trial.get('status', 'Unknown')}</p>
                <p><strong>NCT ID:</strong> {trial.get('nct_id', 'Unknown')}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            **Success Probability:**  
            # {success_prob:.0%}
            **Confidence:** {confidence.title()}  
            **Risk Level:** {risk_level}
            """)
        
        if factors:
            st.markdown("**Key Factors:**")
            for factor in factors:
                st.markdown(f"• {factor}")
                
    except Exception as e:
        st.error(f"Prediction failed: {str(e)}")

if __name__ == "__main__":
    main() 