import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Add the parent directory to the path to import custom modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

try:
    from medequity_utils.dynamic_scraper import HealthcareScraper
    from medequity_utils.healthcare_classifier import classify_healthcare_company
    from medequity_utils.metrics_calculator import calculate_healthcare_metrics
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

# Page configuration
st.set_page_config(
    page_title="Clinical Pipeline - Healthcare Analyzer",
    page_icon="💊",
    layout="wide"
)

# Enhanced CSS
st.markdown("""
<style>
    .pipeline-header {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .phase-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 4px solid #1f77b4;
    }
    
    .pipeline-item {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin: 0.5rem 0;
        border-left: 4px solid #28a745;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .phase-preclinical { border-left-color: #6c757d; }
    .phase-1 { border-left-color: #17a2b8; }
    .phase-2 { border-left-color: #ffc107; }
    .phase-3 { border-left-color: #fd7e14; }
    .phase-approved { border-left-color: #28a745; }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'scraper' not in st.session_state:
    st.session_state.scraper = HealthcareScraper()

def main():
    st.markdown("""
    <div class="pipeline-header">
        <h1>💊 Clinical Pipeline Tracker</h1>
        <p style="font-size: 1.2rem;">Track drug development programs and clinical trials</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🔍 Company Pipeline", "📊 Pipeline Analysis", "📅 Trial Calendar"])
    
    with tab1:
        show_company_pipeline()
    
    with tab2:
        show_pipeline_analysis()
    
    with tab3:
        show_trial_calendar()

def show_company_pipeline():
    """Show individual company pipeline analysis"""
    st.markdown("### 🏢 Company Pipeline Analysis")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Healthcare Company Ticker:",
            placeholder="e.g., MRNA, PFE, REGN",
            help="Enter a healthcare company ticker to analyze its pipeline"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Analyze Pipeline", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        analyze_company_pipeline(ticker)
    elif ticker:
        st.info("👆 Click 'Analyze Pipeline' to get detailed pipeline information")
    else:
        show_pipeline_features()

def show_pipeline_features():
    """Show pipeline analysis features"""
    st.markdown("### 🌟 Pipeline Analysis Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="phase-card">
            <h3>🧪 Phase Tracking</h3>
            <ul>
                <li>Preclinical programs</li>
                <li>Phase I/II/III trials</li>
                <li>Regulatory submissions</li>
                <li>Commercial products</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="phase-card">
            <h3>📈 Value Assessment</h3>
            <ul>
                <li>Pipeline value scoring</li>
                <li>Risk-adjusted NPV</li>
                <li>Competitive landscape</li>
                <li>Market opportunity</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="phase-card">
            <h3>⏰ Timeline Analysis</h3>
            <ul>
                <li>Expected milestones</li>
                <li>Data readouts</li>
                <li>Regulatory timelines</li>
                <li>Launch projections</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def analyze_company_pipeline(ticker: str):
    """Analyze a company's clinical pipeline"""
    
    with st.spinner(f"🔬 Analyzing {ticker} pipeline..."):
        try:
            # Get company data
            company_data = st.session_state.scraper.fetch_company_data(ticker)
            
            if 'error' in company_data:
                st.error(f"❌ Error analyzing {ticker}: {company_data['error']}")
                return
            
            if not company_data.get('is_healthcare', False):
                st.warning(f"⚠️ {ticker} is not classified as a healthcare company.")
                return
            
            # Display pipeline analysis
            display_pipeline_results(company_data)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {str(e)}")

def display_pipeline_results(data: dict):
    """Display comprehensive pipeline analysis"""
    
    ticker = data.get('ticker', 'Unknown')
    name = data.get('name', ticker)
    pipeline = data.get('pipeline', [])
    
    # Header
    st.markdown(f"## 💊 {name} ({ticker}) Pipeline")
    
    if not pipeline:
        st.info("No pipeline data available for this company")
        return
    
    # Pipeline overview
    create_pipeline_overview(pipeline)
    
    # Phase distribution
    create_phase_distribution(pipeline)
    
    # Pipeline details
    create_pipeline_details(pipeline)
    
    # Value analysis
    create_value_analysis(pipeline, data)

def create_pipeline_overview(pipeline: list):
    """Create pipeline overview metrics"""
    st.markdown("### 📊 Pipeline Overview")
    
    # Calculate metrics
    total_programs = len(pipeline)
    
    # Phase counts
    phase_counts = {}
    for item in pipeline:
        if isinstance(item, dict) and 'phase' in item:
            phase = item['phase']
            phase_counts[phase] = phase_counts.get(phase, 0) + 1
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💊 Total Programs", total_programs)
    
    with col2:
        clinical_count = sum(phase_counts.get(phase, 0) for phase in ['Phase I', 'Phase II', 'Phase III'])
        st.metric("🧪 Clinical Trials", clinical_count)
    
    with col3:
        approved_count = phase_counts.get('Approved/Commercial', 0)
        st.metric("✅ Approved", approved_count)
    
    with col4:
        # Calculate pipeline value score
        phase_values = {
            'Preclinical': 1, 'Phase I': 2, 'Phase II': 4, 
            'Phase III': 8, 'Approved/Commercial': 15
        }
        total_value = sum(phase_values.get(phase, 1) * count for phase, count in phase_counts.items())
        st.metric("📈 Pipeline Score", total_value)

def create_phase_distribution(pipeline: list):
    """Create phase distribution visualization"""
    st.markdown("### 📊 Phase Distribution")
    
    # Calculate phase distribution
    phases = {}
    for item in pipeline:
        if isinstance(item, dict) and 'phase' in item:
            phase = item['phase']
            phases[phase] = phases.get(phase, 0) + 1
    
    if phases:
        col1, col2 = st.columns(2)
        
        with col1:
            # Pie chart
            fig_pie = px.pie(
                values=list(phases.values()),
                names=list(phases.keys()),
                title="Pipeline Distribution by Phase",
                color_discrete_sequence=px.colors.qualitative.Set3
            )
            fig_pie.update_layout(height=400)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        with col2:
            # Bar chart
            fig_bar = px.bar(
                x=list(phases.keys()),
                y=list(phases.values()),
                title="Programs by Development Phase",
                color=list(phases.values()),
                color_continuous_scale='Viridis'
            )
            fig_bar.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig_bar, use_container_width=True)

def create_pipeline_details(pipeline: list):
    """Create detailed pipeline listing"""
    st.markdown("### 💊 Pipeline Programs")
    
    # Group by phase
    phases_order = ['Approved/Commercial', 'Phase III', 'Phase II', 'Phase I', 'Preclinical', 'Unknown']
    
    for phase in phases_order:
        phase_items = [item for item in pipeline if isinstance(item, dict) and item.get('phase') == phase]
        
        if phase_items:
            st.markdown(f"#### {phase} ({len(phase_items)} programs)")
            
            for item in phase_items:
                indication = item.get('indication', 'Various')
                description = item.get('description', 'No description available')
                confidence = item.get('confidence', 'medium')
                
                # Determine phase styling
                phase_class = get_phase_class(phase)
                
                st.markdown(f"""
                <div class="pipeline-item {phase_class}">
                    <h4>{indication}</h4>
                    <p><strong>Phase:</strong> {phase}</p>
                    <p><strong>Description:</strong> {description[:200]}{'...' if len(description) > 200 else ''}</p>
                    <p><strong>Confidence:</strong> {confidence.title()}</p>
                </div>
                """, unsafe_allow_html=True)

def create_value_analysis(pipeline: list, data: dict):
    """Create pipeline value analysis"""
    st.markdown("### 💰 Pipeline Value Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Risk-Adjusted Value")
        
        # Calculate phase-weighted values
        phase_values = {
            'Preclinical': 1,
            'Phase I': 2,
            'Phase II': 4,
            'Phase III': 8,
            'Approved/Commercial': 15
        }
        
        phase_risks = {
            'Preclinical': 0.1,
            'Phase I': 0.2,
            'Phase II': 0.4,
            'Phase III': 0.7,
            'Approved/Commercial': 1.0
        }
        
        value_analysis = []
        for item in pipeline:
            if isinstance(item, dict) and 'phase' in item:
                phase = item['phase']
                base_value = phase_values.get(phase, 1)
                risk_factor = phase_risks.get(phase, 0.1)
                risk_adjusted_value = base_value * risk_factor
                
                value_analysis.append({
                    'Indication': item.get('indication', 'Unknown'),
                    'Phase': phase,
                    'Base Value': base_value,
                    'Risk Factor': f"{risk_factor:.0%}",
                    'Risk-Adjusted Value': f"{risk_adjusted_value:.1f}"
                })
        
        if value_analysis:
            df = pd.DataFrame(value_analysis)
            st.dataframe(df, use_container_width=True)
    
    with col2:
        st.markdown("#### 🎯 Key Insights")
        
        # Generate insights
        insights = generate_pipeline_insights(pipeline, data)
        for insight in insights:
            st.markdown(f"• {insight}")

def show_pipeline_analysis():
    """Show cross-company pipeline analysis"""
    st.markdown("### 📊 Cross-Company Pipeline Analysis")
    
    # Sample biotech companies for analysis
    biotech_companies = {
        "Moderna": "MRNA",
        "BioNTech": "BNTX", 
        "Regeneron": "REGN",
        "Vertex": "VRTX",
        "Biogen": "BIIB"
    }
    
    selected_companies = st.multiselect(
        "Select companies to compare:",
        list(biotech_companies.keys()),
        default=["Moderna", "Regeneron"]
    )
    
    if st.button("🔍 Compare Pipelines", type="primary"):
        compare_pipelines(selected_companies, biotech_companies)

def compare_pipelines(companies: list, ticker_map: dict):
    """Compare pipelines across multiple companies"""
    
    if not companies:
        st.warning("Please select at least one company to analyze")
        return
    
    with st.spinner(f"📊 Comparing pipelines for {len(companies)} companies..."):
        
        comparison_data = []
        
        for company in companies:
            ticker = ticker_map[company]
            try:
                company_data = st.session_state.scraper.fetch_company_data(ticker)
                pipeline = company_data.get('pipeline', [])
                
                # Calculate metrics
                total_programs = len(pipeline)
                clinical_programs = sum(1 for item in pipeline 
                                      if isinstance(item, dict) and 
                                      item.get('phase') in ['Phase I', 'Phase II', 'Phase III'])
                
                comparison_data.append({
                    'Company': company,
                    'Ticker': ticker,
                    'Total Programs': total_programs,
                    'Clinical Programs': clinical_programs,
                    'Pipeline Score': calculate_pipeline_score(pipeline)
                })
                
            except Exception as e:
                st.warning(f"Could not analyze {company}: {str(e)}")
        
        if comparison_data:
            # Display comparison
            df = pd.DataFrame(comparison_data)
            st.dataframe(df, use_container_width=True)
            
            # Create comparison chart
            fig = px.bar(
                df, 
                x='Company', 
                y=['Total Programs', 'Clinical Programs'],
                title="Pipeline Program Comparison",
                barmode='group'
            )
            st.plotly_chart(fig, use_container_width=True)

def show_trial_calendar():
    """Show upcoming trial milestones and events"""
    st.markdown("### 📅 Clinical Trial Calendar")
    
    st.info("🚧 Feature coming soon: Track upcoming trial readouts, FDA meetings, and regulatory milestones")
    
    # Demo calendar data
    demo_events = [
        {"Date": "2024-07-15", "Company": "Moderna", "Event": "Phase 3 data readout", "Indication": "RSV vaccine"},
        {"Date": "2024-08-20", "Company": "Vertex", "Event": "FDA PDUFA date", "Indication": "CRISPR therapy"},
        {"Date": "2024-09-10", "Company": "Regeneron", "Event": "Phase 2 results", "Indication": "Oncology program"},
        {"Date": "2024-10-05", "Company": "BioNTech", "Event": "Trial initiation", "Indication": "Cancer vaccine"},
    ]
    
    st.markdown("#### 📋 Upcoming Events (Demo)")
    df_events = pd.DataFrame(demo_events)
    st.dataframe(df_events, use_container_width=True)
    
    # Timeline visualization
    fig = px.timeline(
        df_events,
        x_start="Date",
        x_end="Date", 
        y="Company",
        color="Event",
        title="Upcoming Clinical Milestones"
    )
    st.plotly_chart(fig, use_container_width=True)

def get_phase_class(phase: str) -> str:
    """Get CSS class for phase styling"""
    phase_classes = {
        'Preclinical': 'phase-preclinical',
        'Phase I': 'phase-1',
        'Phase II': 'phase-2', 
        'Phase III': 'phase-3',
        'Approved/Commercial': 'phase-approved'
    }
    return phase_classes.get(phase, '')

def calculate_pipeline_score(pipeline: list) -> int:
    """Calculate pipeline value score"""
    phase_values = {
        'Preclinical': 1, 'Phase I': 2, 'Phase II': 4, 
        'Phase III': 8, 'Approved/Commercial': 15
    }
    
    total_score = 0
    for item in pipeline:
        if isinstance(item, dict) and 'phase' in item:
            phase = item['phase']
            total_score += phase_values.get(phase, 1)
    
    return total_score

def generate_pipeline_insights(pipeline: list, data: dict) -> list:
    """Generate key insights about the pipeline"""
    insights = []
    
    # Pipeline breadth
    unique_indications = set()
    for item in pipeline:
        if isinstance(item, dict) and 'indication' in item:
            unique_indications.add(item['indication'])
    
    if len(unique_indications) > 3:
        insights.append(f"Diversified pipeline across {len(unique_indications)} therapeutic areas")
    
    # Late-stage focus
    late_stage = sum(1 for item in pipeline 
                    if isinstance(item, dict) and 
                    item.get('phase') in ['Phase III', 'Approved/Commercial'])
    
    if late_stage > 0:
        insights.append(f"{late_stage} programs in late-stage development")
    
    # R&D intensity correlation
    financials = data.get('financials', {})
    rd_intensity = financials.get('rd_intensity', 0)
    
    if rd_intensity and rd_intensity > 0.3:
        insights.append(f"High R&D investment ({rd_intensity*100:.0f}% of revenue)")
    
    # Pipeline density
    market_cap = data.get('basic_info', {}).get('marketCap', 0)
    if market_cap > 0:
        programs_per_billion = len(pipeline) / (market_cap / 1e9)
        if programs_per_billion > 2:
            insights.append("High pipeline density relative to market cap")
    
    return insights[:4]  # Return top 4 insights

if __name__ == "__main__":
    main()
