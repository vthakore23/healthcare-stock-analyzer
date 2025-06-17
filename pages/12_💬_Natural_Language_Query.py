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
    from medequity_utils.natural_language_query import NaturalLanguageQueryEngine
    import yfinance as yf
except ImportError as e:
    st.error(f"Import error: {e}")

# Page configuration
st.set_page_config(
    page_title="Natural Language Query Engine",
    page_icon="💬",
    layout="wide"
)

# CSS styling
st.markdown("""
<style>
.query-header {
    background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
    color: white;
    padding: 2rem;
    border-radius: 15px;
    text-align: center;
    margin-bottom: 2rem;
}

.query-result-card {
    background: white;
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #8b5cf6;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.company-result {
    background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid #3b82f6;
}

.query-suggestion {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    cursor: pointer;
    transition: all 0.3s ease;
}

.query-suggestion:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.chat-input {
    font-size: 1.1rem;
    padding: 1rem;
    border-radius: 8px;
    border: 2px solid #e2e8f0;
    width: 100%;
}

.summary-box {
    background: linear-gradient(135deg, #ddd6fe 0%, #c4b5fd 100%);
    padding: 1.5rem;
    border-radius: 12px;
    margin: 1rem 0;
    border-left: 4px solid #8b5cf6;
}

.recommendation-box {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    padding: 1rem;
    border-radius: 8px;
    margin: 0.5rem 0;
    border-left: 4px solid #10b981;
}
</style>
""", unsafe_allow_html=True)

# Initialize query engine
if 'query_engine' not in st.session_state:
    st.session_state.query_engine = NaturalLanguageQueryEngine()

# Query history
if 'query_history' not in st.session_state:
    st.session_state.query_history = []

def main():
    st.markdown("""
    <div class="query-header">
        <h1>💬 Natural Language Query Engine</h1>
        <p>Ask complex questions about healthcare investments in plain English</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Main query interface
    show_query_interface()
    
    # Query suggestions
    show_query_suggestions()
    
    # Query history
    if st.session_state.query_history:
        show_query_history()

def show_query_interface():
    """Show main query interface"""
    st.markdown("### 🎯 Ask Your Investment Question")
    
    # Query input
    user_query = st.text_area(
        "Enter your question:",
        placeholder="Which biotech companies have Phase 3 oncology trials reading out in Q3?",
        height=100,
        help="Ask complex questions about healthcare investments, clinical trials, valuations, and more",
        key="query_input"
    )
    
    col1, col2 = st.columns([1, 4])
    
    with col1:
        query_btn = st.button("🔍 Search", type="primary", use_container_width=True)
    
    with col2:
        if st.button("🗑️ Clear History", use_container_width=True):
            st.session_state.query_history = []
            st.rerun()
    
    if user_query and query_btn:
        process_user_query(user_query)

def process_user_query(query: str):
    """Process user query and display results"""
    
    with st.spinner("🧠 Processing your query..."):
        try:
            # Process the query
            result = st.session_state.query_engine.process_query(query)
            
            # Add to history
            st.session_state.query_history.insert(0, {
                'query': query,
                'result': result,
                'timestamp': datetime.now()
            })
            
            # Keep only last 10 queries
            if len(st.session_state.query_history) > 10:
                st.session_state.query_history = st.session_state.query_history[:10]
            
            # Display results
            display_query_results(result)
            
        except Exception as e:
            st.error(f"Query processing failed: {str(e)}")

def display_query_results(result):
    """Display query results"""
    
    if 'error' in result:
        st.error(f"Query error: {result['error']}")
        
        suggestions = result.get('suggestions', [])
        if suggestions:
            st.markdown("### 💡 Try these example queries:")
            for suggestion in suggestions:
                if st.button(f"💭 {suggestion}", key=f"suggest_{hash(suggestion)}"):
                    st.session_state.query_input = suggestion
                    st.rerun()
        return
    
    query = result.get('query', '')
    parsed_intent = result.get('parsed_intent', {})
    results = result.get('results', {})
    result_count = result.get('result_count', 0)
    
    st.markdown(f"## 🔍 Query Results")
    st.markdown(f"**Original Query:** {query}")
    
    # Show summary
    summary = results.get('summary', '')
    if summary:
        st.markdown(f"""
        <div class="summary-box">
            <h3>📊 Summary</h3>
            <p>{summary}</p>
            <p><strong>Results Found:</strong> {result_count}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Show companies found
    companies = results.get('companies', [])
    if companies:
        show_company_results(companies, parsed_intent.get('intent', 'general'))
    
    # Show recommendations
    recommendations = results.get('recommendations', [])
    if recommendations:
        st.markdown("### 💡 Recommendations")
        for rec in recommendations:
            st.markdown(f"""
            <div class="recommendation-box">
                <p>• {rec}</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Show applied filters
    filters = results.get('filters_applied', {})
    if filters:
        st.markdown("### 🔧 Applied Filters")
        for filter_name, filter_value in filters.items():
            st.markdown(f"**{filter_name.replace('_', ' ').title()}:** {filter_value}")

def show_company_results(companies, query_type):
    """Show company results based on query type"""
    
    st.markdown("### 🏢 Companies Found")
    
    if query_type == 'phase_3_trials':
        show_phase3_results(companies)
    elif query_type == 'undervalued_companies':
        show_undervalued_results(companies)
    elif query_type == 'revenue_growth':
        show_growth_results(companies)
    else:
        show_general_results(companies)

def show_phase3_results(companies):
    """Show Phase 3 trial results"""
    
    for company in companies:
        ticker = company.get('ticker', 'Unknown')
        name = company.get('company_name', 'Unknown')
        market_cap = company.get('market_cap', 0)
        trials = company.get('phase3_trials', [])
        
        st.markdown(f"""
        <div class="company-result">
            <h4>{name} ({ticker})</h4>
            <p><strong>Market Cap:</strong> ${market_cap:.1f}B</p>
            <p><strong>Phase 3 Trials:</strong> {len(trials)}</p>
        </div>
        """, unsafe_allow_html=True)
        
        if trials:
            with st.expander(f"View {ticker} Phase 3 Trials"):
                for trial in trials:
                    st.markdown(f"""
                    **Indication:** {trial.get('indication', 'Unknown')}  
                    **Expected Completion:** {trial.get('expected_completion', 'Unknown')}  
                    **Patient Count:** {trial.get('patient_count', 0):,}  
                    **Primary Endpoint:** {trial.get('primary_endpoint', 'Unknown')}  
                    **Days to Completion:** {trial.get('days_to_completion', 0)}
                    
                    ---
                    """)

def show_undervalued_results(companies):
    """Show undervalued company results"""
    
    # Create DataFrame for better visualization
    company_data = []
    for company in companies:
        company_data.append({
            'Ticker': company.get('ticker', 'Unknown'),
            'Company': company.get('company_name', 'Unknown')[:30] + '...' if len(company.get('company_name', '')) > 30 else company.get('company_name', 'Unknown'),
            'Market Cap ($B)': company.get('market_cap', 0),
            'P/E Ratio': company.get('pe_ratio', 'N/A'),
            'PEG Ratio': company.get('peg_ratio', 'N/A'),
            'P/B Ratio': company.get('price_to_book', 'N/A'),
            'Valuation Score': company.get('valuation_score', 0),
            'Stock Price': f"${company.get('stock_price', 0):.2f}"
        })
    
    if company_data:
        df = pd.DataFrame(company_data)
        st.dataframe(df, use_container_width=True)
        
        # Valuation score chart
        if len(companies) > 1:
            tickers = [c.get('ticker', 'Unknown') for c in companies]
            scores = [c.get('valuation_score', 0) for c in companies]
            
            fig = px.bar(
                x=tickers,
                y=scores,
                title='Valuation Attractiveness Score',
                color=scores,
                color_continuous_scale='RdYlGn'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def show_growth_results(companies):
    """Show revenue growth results"""
    
    # Create DataFrame
    company_data = []
    for company in companies:
        company_data.append({
            'Ticker': company.get('ticker', 'Unknown'),
            'Company': company.get('company_name', 'Unknown')[:30] + '...' if len(company.get('company_name', '')) > 30 else company.get('company_name', 'Unknown'),
            'Revenue Growth (%)': company.get('revenue_growth', 0),
            'Revenue ($B)': company.get('total_revenue', 0),
            'Profit Margin (%)': company.get('profit_margin', 'N/A'),
            'Market Cap ($B)': company.get('market_cap', 0),
            'Stock Price': f"${company.get('stock_price', 0):.2f}"
        })
    
    if company_data:
        df = pd.DataFrame(company_data)
        st.dataframe(df, use_container_width=True)
        
        # Growth chart
        if len(companies) > 1:
            tickers = [c.get('ticker', 'Unknown') for c in companies]
            growth_rates = [c.get('revenue_growth', 0) for c in companies]
            
            fig = px.bar(
                x=tickers,
                y=growth_rates,
                title='Revenue Growth Rate (%)',
                color=growth_rates,
                color_continuous_scale='Greens'
            )
            fig.update_layout(height=400, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)

def show_general_results(companies):
    """Show general company results"""
    
    for company in companies:
        ticker = company.get('ticker', 'Unknown')
        name = company.get('company_name', 'Unknown')
        market_cap = company.get('market_cap', 0)
        stock_price = company.get('stock_price', 0)
        
        st.markdown(f"""
        <div class="company-result">
            <h4>{name} ({ticker})</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div><strong>Market Cap:</strong> ${market_cap:.1f}B</div>
                <div><strong>Stock Price:</strong> ${stock_price:.2f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

def show_query_suggestions():
    """Show query suggestions"""
    st.markdown("### 💡 Example Queries")
    
    suggestions = [
        "Which biotech companies have Phase 3 oncology trials reading out in Q3?",
        "Show me undervalued medical device companies with >20% revenue growth",
        "Find pharmaceutical companies with upcoming FDA approvals",
        "Which healthcare companies have strong institutional buying?",
        "List biotech companies with market cap under $5 billion",
        "Show me companies with high R&D spending in immunology"
    ]
    
    col1, col2 = st.columns(2)
    
    for i, suggestion in enumerate(suggestions):
        with col1 if i % 2 == 0 else col2:
            if st.button(f"💭 {suggestion}", key=f"suggestion_{i}", use_container_width=True):
                # Set the query in the text area and trigger processing
                st.session_state.query_input = suggestion
                process_user_query(suggestion)

def show_query_history():
    """Show query history"""
    st.markdown("### 📚 Query History")
    
    with st.expander("View Recent Queries", expanded=False):
        for i, item in enumerate(st.session_state.query_history[:5]):
            query = item['query']
            timestamp = item['timestamp']
            result = item['result']
            
            st.markdown(f"""
            <div class="query-result-card">
                <h4>Query {i+1} - {timestamp.strftime('%H:%M:%S')}</h4>
                <p><strong>Question:</strong> {query}</p>
                <p><strong>Results:</strong> {result.get('result_count', 0)} companies found</p>
            </div>
            """, unsafe_allow_html=True)
            
            if st.button(f"🔄 Rerun Query {i+1}", key=f"rerun_{i}"):
                process_user_query(query)

def show_query_features():
    """Show query engine features"""
    st.markdown("### 🌟 Query Engine Capabilities")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🎯 Query Types:**
        - Clinical trial searches
        - Valuation screening  
        - Growth analysis
        - Market cap filtering
        - Geographic analysis
        """)
    
    with col2:
        st.markdown("""
        **🧠 AI Understanding:**
        - Natural language parsing
        - Intent recognition
        - Parameter extraction
        - Context awareness
        - Query optimization
        """)
    
    with col3:
        st.markdown("""
        **📊 Result Features:**
        - Real-time data
        - Visual analytics
        - Comparative analysis
        - Actionable insights
        - Export capabilities
        """)

if __name__ == "__main__":
    main() 