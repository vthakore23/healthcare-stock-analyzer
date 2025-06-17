import streamlit as st
import sys
import os
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random

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
    page_title="3D Pipeline Visualization",
    page_icon="🎨",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
.viz-header {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.pipeline-node {
    background: white;
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-left: 4px solid #3b82f6;
}

.phase-preclinical { border-left-color: #6b7280; }
.phase-1 { border-left-color: #3b82f6; }
.phase-2 { border-left-color: #f59e0b; }
.phase-3 { border-left-color: #ef4444; }
.phase-approved { border-left-color: #10b981; }

.control-panel {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.visualization-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    border-top: 4px solid #f093fb;
}
</style>
""", unsafe_allow_html=True)

# Initialize predictor
if 'trial_predictor' not in st.session_state:
    st.session_state.trial_predictor = ClinicalTrialPredictor()

def main():
    st.markdown("""
    <div class="viz-header">
        <h1>🎨 3D Pipeline Visualization</h1>
        <p>Interactive Clinical Pipeline • Therapeutic Area Clustering • Development Timeline</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🚀 3D Pipeline View", 
        "🏢 Company Pipeline", 
        "🌐 Therapeutic Clusters", 
        "📊 Timeline Analysis"
    ])
    
    with tab1:
        show_3d_pipeline_view()
    
    with tab2:
        show_company_pipeline()
    
    with tab3:
        show_therapeutic_clusters()
    
    with tab4:
        show_timeline_analysis()

def show_3d_pipeline_view():
    """Show 3D pipeline visualization"""
    st.markdown("### 🚀 Interactive 3D Pipeline Visualization")
    
    # Control panel
    show_control_panel()
    
    # Generate and display 3D visualization
    create_3d_pipeline_visualization()

def show_control_panel():
    """Show visualization control panel"""
    st.markdown("""
    <div class="control-panel">
        <h3>🎛️ Visualization Controls</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        companies = st.multiselect(
            "Select Companies:",
            ["MRNA", "PFE", "JNJ", "REGN", "VRTX", "BIIB", "AMGN", "GILD"],
            default=["MRNA", "PFE", "REGN"],
            key="viz_companies"
        )
    
    with col2:
        phases = st.multiselect(
            "Filter by Phase:",
            ["Preclinical", "Phase I", "Phase II", "Phase III", "Approved"],
            default=["Phase II", "Phase III"],
            key="viz_phases"
        )
    
    with col3:
        therapeutic_areas = st.multiselect(
            "Therapeutic Areas:",
            ["Oncology", "Immunology", "Neurology", "Cardiovascular", "Infectious Disease"],
            default=["Oncology", "Immunology"],
            key="viz_areas"
        )
    
    with col4:
        view_mode = st.selectbox(
            "View Mode:",
            ["Success Probability", "Market Size", "Timeline", "Risk Level"],
            key="viz_mode"
        )
    
    return companies, phases, therapeutic_areas, view_mode

def create_3d_pipeline_visualization():
    """Create 3D pipeline visualization"""
    
    companies, phases, therapeutic_areas, view_mode = st.session_state.viz_companies, st.session_state.viz_phases, st.session_state.viz_areas, st.session_state.viz_mode
    
    if not companies:
        st.info("Please select at least one company to visualize")
        return
    
    with st.spinner("Creating 3D visualization..."):
        try:
            # Generate mock pipeline data for visualization
            pipeline_data = generate_mock_pipeline_data(companies, phases, therapeutic_areas)
            
            if not pipeline_data:
                st.warning("No pipeline data matches your filters")
                return
            
            # Create 3D scatter plot
            fig = create_3d_scatter_plot(pipeline_data, view_mode)
            
            st.plotly_chart(fig, use_container_width=True, height=700)
            
            # Show pipeline summary
            show_pipeline_summary(pipeline_data)
            
        except Exception as e:
            st.error(f"Visualization failed: {str(e)}")

def generate_mock_pipeline_data(companies, phases, therapeutic_areas):
    """Generate mock pipeline data for visualization"""
    
    pipeline_data = []
    
    for company in companies:
        for phase in phases:
            for area in therapeutic_areas:
                # Generate random programs for each combination
                num_programs = random.randint(0, 3)
                
                for i in range(num_programs):
                    # Generate coordinates for 3D visualization
                    x_coord = get_phase_coordinate(phase) + random.uniform(-0.3, 0.3)
                    y_coord = get_area_coordinate(area) + random.uniform(-0.3, 0.3)
                    z_coord = random.uniform(0, 10)  # Timeline or other metric
                    
                    program = {
                        'company': company,
                        'phase': phase,
                        'therapeutic_area': area,
                        'program_name': f"{area} Program {i+1}",
                        'x': x_coord,
                        'y': y_coord,
                        'z': z_coord,
                        'success_probability': random.uniform(0.3, 0.9),
                        'market_size': random.uniform(1, 20),  # Billions
                        'timeline_months': random.randint(6, 48),
                        'risk_level': random.choice(['Low', 'Medium', 'High']),
                        'patient_count': random.randint(100, 1000),
                        'indication': f"{area} indication"
                    }
                    
                    pipeline_data.append(program)
    
    return pipeline_data

def get_phase_coordinate(phase):
    """Get X coordinate for phase"""
    phase_coords = {
        'Preclinical': 0,
        'Phase I': 1,
        'Phase II': 2,
        'Phase III': 3,
        'Approved': 4
    }
    return phase_coords.get(phase, 0)

def get_area_coordinate(area):
    """Get Y coordinate for therapeutic area"""
    area_coords = {
        'Oncology': 0,
        'Immunology': 1,
        'Neurology': 2,
        'Cardiovascular': 3,
        'Infectious Disease': 4
    }
    return area_coords.get(area, 0)

def create_3d_scatter_plot(pipeline_data, view_mode):
    """Create 3D scatter plot visualization"""
    
    df = pd.DataFrame(pipeline_data)
    
    # Determine size and color based on view mode
    if view_mode == "Success Probability":
        size = df['success_probability'] * 50
        color = df['success_probability']
        color_scale = 'Viridis'
        title = "3D Pipeline View - Success Probability"
    elif view_mode == "Market Size":
        size = df['market_size'] * 3
        color = df['market_size']
        color_scale = 'Blues'
        title = "3D Pipeline View - Market Size ($B)"
    elif view_mode == "Timeline":
        size = [30] * len(df)  # Fixed size
        color = df['timeline_months']
        color_scale = 'Reds'
        title = "3D Pipeline View - Development Timeline"
    else:  # Risk Level
        risk_map = {'Low': 1, 'Medium': 2, 'High': 3}
        size = [30] * len(df)
        color = [risk_map[risk] for risk in df['risk_level']]
        color_scale = 'RdYlGn_r'
        title = "3D Pipeline View - Risk Level"
    
    # Create hover text
    hover_text = []
    for _, row in df.iterrows():
        hover_text.append(
            f"<b>{row['company']}</b><br>" +
            f"Program: {row['program_name']}<br>" +
            f"Phase: {row['phase']}<br>" +
            f"Area: {row['therapeutic_area']}<br>" +
            f"Success Prob: {row['success_probability']:.0%}<br>" +
            f"Market Size: ${row['market_size']:.1f}B<br>" +
            f"Timeline: {row['timeline_months']} months"
        )
    
    # Create 3D scatter plot
    fig = go.Figure(data=go.Scatter3d(
        x=df['x'],
        y=df['y'],
        z=df['z'],
        mode='markers',
        marker=dict(
            size=size,
            color=color,
            colorscale=color_scale,
            opacity=0.8,
            colorbar=dict(title=view_mode),
            line=dict(width=1, color='white')
        ),
        text=hover_text,
        hovertemplate='%{text}<extra></extra>',
        name='Pipeline Programs'
    ))
    
    # Update layout
    fig.update_layout(
        title=title,
        scene=dict(
            xaxis_title='Development Phase',
            yaxis_title='Therapeutic Area',
            zaxis_title='Development Progress',
            xaxis=dict(
                tickmode='array',
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['Preclinical', 'Phase I', 'Phase II', 'Phase III', 'Approved']
            ),
            yaxis=dict(
                tickmode='array',
                tickvals=[0, 1, 2, 3, 4],
                ticktext=['Oncology', 'Immunology', 'Neurology', 'Cardiovascular', 'Infectious Disease']
            ),
            camera=dict(
                eye=dict(x=1.87, y=0.88, z=-0.64)
            )
        ),
        height=600,
        margin=dict(r=20, b=10, l=10, t=40)
    )
    
    return fig

def show_pipeline_summary(pipeline_data):
    """Show pipeline data summary"""
    
    st.markdown("### 📊 Pipeline Summary")
    
    df = pd.DataFrame(pipeline_data)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Programs", len(df))
    
    with col2:
        avg_success = df['success_probability'].mean()
        st.metric("Avg Success Probability", f"{avg_success:.0%}")
    
    with col3:
        total_market = df['market_size'].sum()
        st.metric("Total Market Size", f"${total_market:.1f}B")
    
    with col4:
        avg_timeline = df['timeline_months'].mean()
        st.metric("Avg Timeline", f"{avg_timeline:.0f} months")
    
    # Company breakdown
    company_summary = df.groupby('company').agg({
        'program_name': 'count',
        'success_probability': 'mean',
        'market_size': 'sum'
    }).round(2)
    
    company_summary.columns = ['Programs', 'Avg Success Prob', 'Total Market ($B)']
    company_summary['Avg Success Prob'] = company_summary['Avg Success Prob'].apply(lambda x: f"{x:.0%}")
    
    st.markdown("#### 🏢 Company Breakdown")
    st.dataframe(company_summary, use_container_width=True)

def show_company_pipeline():
    """Show individual company pipeline"""
    st.markdown("### 🏢 Company Pipeline Visualization")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        ticker = st.text_input(
            "Enter Company Ticker:",
            placeholder="e.g., MRNA, PFE, REGN",
            key="company_ticker"
        ).upper().strip()
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        analyze_btn = st.button("🔍 Visualize Pipeline", type="primary", use_container_width=True)
    
    if ticker and analyze_btn:
        visualize_company_pipeline(ticker)
    else:
        show_company_viz_examples()

def show_company_viz_examples():
    """Show company visualization examples"""
    st.markdown("### 🌟 Company Pipeline Features")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🎯 Pipeline Mapping:**
        - Phase progression visualization
        - Therapeutic area clustering
        - Success probability overlays
        - Timeline animations
        """)
    
    with col2:
        st.markdown("""
        **📊 Interactive Features:**
        - Hover for detailed information
        - Filter by development phase
        - Zoom and rotate views
        - Export visualizations
        """)
    
    with col3:
        st.markdown("""
        **🔄 Real-time Updates:**
        - Live clinical trial data
        - Success probability updates
        - Timeline adjustments
        - Risk factor changes
        """)

def visualize_company_pipeline(ticker):
    """Visualize individual company pipeline"""
    
    with st.spinner(f"Creating pipeline visualization for {ticker}..."):
        try:
            # Get company data
            stock = yf.Ticker(ticker)
            info = stock.info
            company_name = info.get('longName', ticker)
            
            # Generate company-specific pipeline data
            pipeline_data = generate_company_pipeline_data(ticker)
            
            if not pipeline_data:
                st.warning(f"No pipeline data found for {ticker}")
                return
            
            st.markdown(f"## 🏢 {company_name} ({ticker}) - Pipeline Visualization")
            
            # Create company-specific visualizations
            create_company_pipeline_charts(pipeline_data)
            
        except Exception as e:
            st.error(f"Pipeline visualization failed: {str(e)}")

def generate_company_pipeline_data(ticker):
    """Generate company-specific pipeline data"""
    
    therapeutic_areas = ["Oncology", "Immunology", "Neurology", "Cardiovascular", "Infectious Disease"]
    phases = ["Preclinical", "Phase I", "Phase II", "Phase III", "Approved"]
    
    pipeline_data = []
    
    # Generate 8-15 programs for the company
    num_programs = random.randint(8, 15)
    
    for i in range(num_programs):
        area = random.choice(therapeutic_areas)
        phase = random.choice(phases)
        
        program = {
            'company': ticker,
            'program_id': f"Program-{i+1:02d}",
            'program_name': f"{area} Therapeutic {i+1}",
            'phase': phase,
            'therapeutic_area': area,
            'indication': f"Treatment for {area.lower()} condition",
            'success_probability': random.uniform(0.2, 0.9),
            'market_size': random.uniform(0.5, 15),
            'timeline_months': random.randint(6, 60),
            'risk_level': random.choice(['Low', 'Medium', 'High']),
            'patient_count': random.randint(50, 2000),
            'start_date': datetime.now() - timedelta(days=random.randint(30, 1000)),
            'expected_completion': datetime.now() + timedelta(days=random.randint(30, 800))
        }
        
        pipeline_data.append(program)
    
    return pipeline_data

def create_company_pipeline_charts(pipeline_data):
    """Create multiple charts for company pipeline"""
    
    df = pd.DataFrame(pipeline_data)
    
    # Phase distribution
    col1, col2 = st.columns(2)
    
    with col1:
        phase_counts = df['phase'].value_counts()
        fig_pie = px.pie(
            values=phase_counts.values,
            names=phase_counts.index,
            title="Pipeline Distribution by Phase"
        )
        fig_pie.update_layout(height=400)
        st.plotly_chart(fig_pie, use_container_width=True)
    
    with col2:
        area_counts = df['therapeutic_area'].value_counts()
        fig_bar = px.bar(
            x=area_counts.index,
            y=area_counts.values,
            title="Programs by Therapeutic Area",
            color=area_counts.values,
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Success probability vs Market size scatter
    fig_scatter = px.scatter(
        df,
        x='success_probability',
        y='market_size',
        color='phase',
        size='timeline_months',
        hover_data=['program_name', 'therapeutic_area'],
        title="Success Probability vs Market Opportunity"
    )
    fig_scatter.update_layout(height=500)
    st.plotly_chart(fig_scatter, use_container_width=True)
    
    # Timeline analysis
    df['months_to_completion'] = (df['expected_completion'] - datetime.now()).dt.days / 30.44
    df['months_to_completion'] = df['months_to_completion'].clip(lower=0)
    
    fig_timeline = px.timeline(
        df,
        x_start='start_date',
        x_end='expected_completion',
        y='program_name',
        color='phase',
        title="Program Development Timeline"
    )
    fig_timeline.update_layout(height=max(400, len(df) * 30))
    st.plotly_chart(fig_timeline, use_container_width=True)
    
    # Individual program details
    show_program_details(df)

def show_program_details(df):
    """Show detailed program information"""
    
    st.markdown("### 💊 Program Details")
    
    for _, program in df.iterrows():
        phase = program['phase']
        
        # Determine phase styling
        phase_classes = {
            'Preclinical': 'phase-preclinical',
            'Phase I': 'phase-1',
            'Phase II': 'phase-2',
            'Phase III': 'phase-3',
            'Approved': 'phase-approved'
        }
        
        phase_class = phase_classes.get(phase, '')
        
        with st.expander(f"{program['program_name']} - {phase}"):
            st.markdown(f"""
            <div class="pipeline-node {phase_class}">
                <h4>{program['program_name']}</h4>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem;">
                    <div><strong>Therapeutic Area:</strong><br>{program['therapeutic_area']}</div>
                    <div><strong>Success Probability:</strong><br>{program['success_probability']:.0%}</div>
                    <div><strong>Market Size:</strong><br>${program['market_size']:.1f}B</div>
                </div>
                <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 1rem; margin-top: 1rem;">
                    <div><strong>Timeline:</strong><br>{program['timeline_months']} months</div>
                    <div><strong>Risk Level:</strong><br>{program['risk_level']}</div>
                    <div><strong>Patient Count:</strong><br>{program['patient_count']:,}</div>
                </div>
                <p style="margin-top: 1rem;"><strong>Indication:</strong> {program['indication']}</p>
            </div>
            """, unsafe_allow_html=True)

def show_therapeutic_clusters():
    """Show therapeutic area clustering"""
    st.markdown("### 🌐 Therapeutic Area Clustering")
    
    # Generate clustering visualization
    create_therapeutic_clustering()

def create_therapeutic_clustering():
    """Create therapeutic area clustering visualization"""
    
    # Generate mock clustering data
    companies = ["MRNA", "PFE", "JNJ", "REGN", "VRTX", "BIIB", "AMGN", "GILD"]
    areas = ["Oncology", "Immunology", "Neurology", "Cardiovascular", "Infectious Disease"]
    
    clustering_data = []
    
    for company in companies:
        x_base = random.uniform(-10, 10)
        y_base = random.uniform(-10, 10)
        
        for area in areas:
            # Generate some programs in each area
            num_programs = random.randint(0, 5)
            
            for i in range(num_programs):
                cluster_point = {
                    'company': company,
                    'therapeutic_area': area,
                    'x': x_base + random.uniform(-2, 2),
                    'y': y_base + random.uniform(-2, 2),
                    'program_count': num_programs,
                    'total_market_size': random.uniform(5, 50),
                    'avg_success_prob': random.uniform(0.3, 0.8)
                }
                clustering_data.append(cluster_point)
    
    df = pd.DataFrame(clustering_data)
    
    if not df.empty:
        # Create clustering scatter plot
        fig = px.scatter(
            df,
            x='x',
            y='y',
            color='therapeutic_area',
            size='total_market_size',
            hover_data=['company', 'program_count', 'avg_success_prob'],
            title="Therapeutic Area Clustering by Company",
            size_max=20
        )
        
        fig.update_layout(
            height=600,
            xaxis_title="Research Focus Dimension 1",
            yaxis_title="Research Focus Dimension 2"
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Show clustering insights
        show_clustering_insights(df)

def show_clustering_insights(df):
    """Show insights from clustering analysis"""
    
    st.markdown("### 🔍 Clustering Insights")
    
    # Area concentration analysis
    area_concentration = df.groupby('therapeutic_area').agg({
        'company': 'nunique',
        'total_market_size': 'mean',
        'avg_success_prob': 'mean'
    }).round(2)
    
    area_concentration.columns = ['Companies Active', 'Avg Market Size ($B)', 'Avg Success Prob']
    area_concentration['Avg Success Prob'] = area_concentration['Avg Success Prob'].apply(lambda x: f"{x:.0%}")
    
    st.dataframe(area_concentration, use_container_width=True)

def show_timeline_analysis():
    """Show timeline analysis"""
    st.markdown("### 📊 Development Timeline Analysis")
    
    # Generate timeline data
    create_timeline_analysis()

def create_timeline_analysis():
    """Create timeline analysis visualization"""
    
    # Generate mock timeline data
    phases = ["Preclinical", "Phase I", "Phase II", "Phase III", "Approved"]
    companies = ["MRNA", "PFE", "JNJ", "REGN", "VRTX"]
    
    timeline_data = []
    
    for company in companies:
        for phase in phases:
            # Generate programs in each phase
            num_programs = random.randint(1, 4)
            
            for i in range(num_programs):
                start_date = datetime.now() - timedelta(days=random.randint(0, 1000))
                duration = random.randint(180, 1095)  # 6 months to 3 years
                end_date = start_date + timedelta(days=duration)
                
                program = {
                    'company': company,
                    'phase': phase,
                    'program_name': f"{company} {phase} Program {i+1}",
                    'start_date': start_date,
                    'end_date': end_date,
                    'duration_months': duration / 30.44,
                    'progress': random.uniform(0.1, 0.9)
                }
                timeline_data.append(program)
    
    df = pd.DataFrame(timeline_data)
    
    # Create Gantt chart
    fig = px.timeline(
        df,
        x_start='start_date',
        x_end='end_date',
        y='company',
        color='phase',
        title="Development Timeline by Company",
        hover_data=['program_name', 'duration_months']
    )
    
    fig.update_layout(height=400)
    st.plotly_chart(fig, use_container_width=True)
    
    # Phase duration analysis
    col1, col2 = st.columns(2)
    
    with col1:
        avg_duration = df.groupby('phase')['duration_months'].mean().round(1)
        
        fig_duration = px.bar(
            x=avg_duration.index,
            y=avg_duration.values,
            title="Average Phase Duration (Months)",
            color=avg_duration.values,
            color_continuous_scale='Blues'
        )
        fig_duration.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig_duration, use_container_width=True)
    
    with col2:
        # Progress distribution
        fig_progress = px.histogram(
            df,
            x='progress',
            color='phase',
            title="Program Progress Distribution",
            nbins=20
        )
        fig_progress.update_layout(height=400)
        st.plotly_chart(fig_progress, use_container_width=True)

if __name__ == "__main__":
    main() 