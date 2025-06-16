import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import yfinance as yf
from datetime import datetime, timedelta
import io
import base64

# Page configuration
st.set_page_config(
    page_title="DCF Model Builder - Healthcare Analyzer | June 2025",
    page_icon="📊",
    layout="wide"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .dcf-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .assumption-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .valuation-result {
        background: linear-gradient(135deg, #00C851 0%, #007E33 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1.5rem 0;
        font-family: 'Inter', sans-serif;
    }
    
    .scenario-analysis {
        background: #f8fafc;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        border: 1px solid #e2e8f0;
    }
    
    .metric-highlight {
        font-size: 2.5rem;
        font-weight: bold;
        color: white;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .assumption-input {
        background: #f8fafc;
        border: 2px solid #e2e8f0;
        border-radius: 8px;
        padding: 0.5rem;
        font-size: 1rem;
        width: 100%;
    }
    
    .sensitivity-grid {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
    }
</style>
""", unsafe_allow_html=True)

class DCFModel:
    """Comprehensive DCF (Discounted Cash Flow) Model Builder"""
    
    def __init__(self):
        self.projection_years = 10
        self.terminal_growth_rate = 2.5
        self.tax_rate = 21.0
        
    def calculate_dcf_valuation(self, assumptions):
        """Calculate DCF valuation based on user assumptions"""
        
        years = list(range(1, self.projection_years + 1))
        
        # Base year metrics
        base_revenue = assumptions['base_revenue']
        base_ebitda_margin = assumptions['base_ebitda_margin']
        
        # Growth rates
        revenue_growth_rates = self._generate_growth_rates(
            assumptions['revenue_growth_y1'],
            assumptions['revenue_growth_y5'],
            assumptions['revenue_growth_terminal']
        )
        
        # Build financial projections
        projections = self._build_projections(assumptions, revenue_growth_rates)
        
        # Calculate valuation
        valuation_results = self._calculate_valuation(projections, assumptions)
        
        return projections, valuation_results
    
    def _generate_growth_rates(self, y1_growth, y5_growth, terminal_growth):
        """Generate smooth revenue growth rates from Y1 to terminal"""
        
        growth_rates = []
        
        # Years 1-5: Linear decline from Y1 to Y5
        for year in range(1, 6):
            rate = y1_growth - (y1_growth - y5_growth) * ((year - 1) / 4)
            growth_rates.append(rate / 100)
        
        # Years 6-10: Linear decline from Y5 to terminal
        for year in range(6, 11):
            rate = y5_growth - (y5_growth - terminal_growth) * ((year - 5) / 5)
            growth_rates.append(rate / 100)
        
        return growth_rates
    
    def _build_projections(self, assumptions, growth_rates):
        """Build detailed financial projections"""
        
        projections = {
            'Year': list(range(1, self.projection_years + 1)),
            'Revenue': [],
            'Revenue_Growth': [],
            'EBITDA': [],
            'EBITDA_Margin': [],
            'EBIT': [],
            'Taxes': [],
            'NOPAT': [],
            'Capex': [],
            'Capex_Revenue': [],
            'Change_NWC': [],
            'FCFF': [],
            'Discount_Factor': [],
            'PV_FCFF': []
        }
        
        # Base year values
        current_revenue = assumptions['base_revenue']
        wacc = assumptions['wacc'] / 100
        
        for i, year in enumerate(range(1, self.projection_years + 1)):
            # Revenue
            growth_rate = growth_rates[i]
            revenue = current_revenue * (1 + growth_rate)
            projections['Revenue'].append(revenue)
            projections['Revenue_Growth'].append(growth_rate * 100)
            
            # EBITDA with margin improvement/decline
            ebitda_margin = assumptions['base_ebitda_margin'] + \
                           (assumptions['target_ebitda_margin'] - assumptions['base_ebitda_margin']) * \
                           min(year / 5, 1.0)  # Reach target by Year 5
            ebitda = revenue * (ebitda_margin / 100)
            projections['EBITDA'].append(ebitda)
            projections['EBITDA_Margin'].append(ebitda_margin)
            
            # Depreciation & Amortization
            da = revenue * (assumptions['da_revenue'] / 100)
            ebit = ebitda - da
            projections['EBIT'].append(ebit)
            
            # Taxes
            taxes = ebit * (self.tax_rate / 100) if ebit > 0 else 0
            projections['Taxes'].append(taxes)
            
            # NOPAT (Net Operating Profit After Tax)
            nopat = ebit - taxes
            projections['NOPAT'].append(nopat)
            
            # Capital Expenditures
            capex = revenue * (assumptions['capex_revenue'] / 100)
            projections['Capex'].append(capex)
            projections['Capex_Revenue'].append(assumptions['capex_revenue'])
            
            # Change in Net Working Capital
            nwc_change = (revenue - current_revenue) * (assumptions['nwc_revenue'] / 100)
            projections['Change_NWC'].append(nwc_change)
            
            # Free Cash Flow to the Firm
            fcff = nopat + da - capex - nwc_change
            projections['FCFF'].append(fcff)
            
            # Discount factors and present value
            discount_factor = 1 / ((1 + wacc) ** year)
            projections['Discount_Factor'].append(discount_factor)
            
            pv_fcff = fcff * discount_factor
            projections['PV_FCFF'].append(pv_fcff)
            
            # Update for next iteration
            current_revenue = revenue
        
        return pd.DataFrame(projections)
    
    def _calculate_valuation(self, projections, assumptions):
        """Calculate enterprise and equity valuation"""
        
        # Terminal value calculation
        terminal_fcff = projections['FCFF'].iloc[-1] * (1 + self.terminal_growth_rate / 100)
        terminal_value = terminal_fcff / (assumptions['wacc'] / 100 - self.terminal_growth_rate / 100)
        
        # Present value of terminal value
        pv_terminal_value = terminal_value / ((1 + assumptions['wacc'] / 100) ** self.projection_years)
        
        # Enterprise value
        pv_projection_period = projections['PV_FCFF'].sum()
        enterprise_value = pv_projection_period + pv_terminal_value
        
        # Equity value
        equity_value = enterprise_value - assumptions['net_debt']
        
        # Per share value
        value_per_share = equity_value / assumptions['shares_outstanding']
        
        # Current stock price comparison
        current_price = assumptions.get('current_stock_price', 0)
        upside_downside = ((value_per_share - current_price) / current_price * 100) if current_price > 0 else 0
        
        return {
            'pv_projection_period': pv_projection_period,
            'terminal_value': terminal_value,
            'pv_terminal_value': pv_terminal_value,
            'enterprise_value': enterprise_value,
            'equity_value': equity_value,
            'value_per_share': value_per_share,
            'current_price': current_price,
            'upside_downside': upside_downside,
            'implied_ev_revenue': enterprise_value / assumptions['base_revenue'],
            'implied_pe': equity_value / (projections['NOPAT'].iloc[0] * assumptions['shares_outstanding'] / equity_value) if projections['NOPAT'].iloc[0] > 0 else 0
        }
    
    def sensitivity_analysis(self, base_assumptions, sensitivity_vars):
        """Perform sensitivity analysis on key variables"""
        
        base_valuation = self.calculate_dcf_valuation(base_assumptions)[1]['value_per_share']
        
        sensitivity_results = {}
        
        for var_name, var_range in sensitivity_vars.items():
            results = []
            
            for var_value in var_range:
                # Create modified assumptions
                modified_assumptions = base_assumptions.copy()
                modified_assumptions[var_name] = var_value
                
                # Calculate valuation
                try:
                    _, valuation = self.calculate_dcf_valuation(modified_assumptions)
                    results.append({
                        'variable_value': var_value,
                        'value_per_share': valuation['value_per_share'],
                        'change_vs_base': (valuation['value_per_share'] - base_valuation) / base_valuation * 100
                    })
                except:
                    results.append({
                        'variable_value': var_value,
                        'value_per_share': 0,
                        'change_vs_base': -100
                    })
            
            sensitivity_results[var_name] = pd.DataFrame(results)
        
        return sensitivity_results
    
    def scenario_analysis(self, base_assumptions):
        """Perform scenario analysis (Bull, Base, Bear cases)"""
        
        scenarios = {
            'Bear Case': {
                'revenue_growth_y1': base_assumptions['revenue_growth_y1'] - 5,
                'revenue_growth_y5': base_assumptions['revenue_growth_y5'] - 3,
                'target_ebitda_margin': base_assumptions['target_ebitda_margin'] - 2,
                'wacc': base_assumptions['wacc'] + 1,
                'terminal_growth_rate': 1.5
            },
            'Base Case': base_assumptions.copy(),
            'Bull Case': {
                'revenue_growth_y1': base_assumptions['revenue_growth_y1'] + 5,
                'revenue_growth_y5': base_assumptions['revenue_growth_y5'] + 3,
                'target_ebitda_margin': base_assumptions['target_ebitda_margin'] + 2,
                'wacc': base_assumptions['wacc'] - 0.5,
                'terminal_growth_rate': 3.0
            }
        }
        
        scenario_results = {}
        
        for scenario_name, scenario_assumptions in scenarios.items():
            # Merge with base assumptions
            full_assumptions = base_assumptions.copy()
            full_assumptions.update(scenario_assumptions)
            
            try:
                projections, valuation = self.calculate_dcf_valuation(full_assumptions)
                scenario_results[scenario_name] = {
                    'projections': projections,
                    'valuation': valuation
                }
            except Exception as e:
                scenario_results[scenario_name] = {
                    'projections': None,
                    'valuation': {'value_per_share': 0, 'enterprise_value': 0}
                }
        
        return scenario_results

def main():
    st.markdown("""
    <div class="dcf-header">
        <h1>📊 DCF Model Builder</h1>
        <p style="font-size: 1.3rem;">Professional Discounted Cash Flow Valuation Model</p>
        <div style="color: #e0e7ff; font-weight: 500;">Build custom DCF models with scenario & sensitivity analysis</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize DCF model
    if 'dcf_model' not in st.session_state:
        st.session_state.dcf_model = DCFModel()
    
    # Sidebar for company selection
    with st.sidebar:
        st.markdown("### 🏢 Company Selection")
        
        # Option to pull data from a ticker
        ticker_input = st.text_input("Stock Ticker (optional):", placeholder="e.g., MRNA, PFE")
        
        if ticker_input and st.button("📊 Load Company Data"):
            load_company_data(ticker_input.upper())
        
        st.markdown("---")
        st.markdown("### 💡 DCF Best Practices")
        st.markdown("""
        - **Be Conservative**: Use realistic growth assumptions
        - **Sanity Check**: Compare to trading multiples
        - **Sensitivity**: Test key variable ranges
        - **Terminal Value**: Usually 60-80% of total value
        - **WACC**: Critical - small changes = big impact
        """)
    
    # Main DCF interface
    col1, col2 = st.columns([1, 1])
    
    with col1:
        show_assumptions_input()
    
    with col2:
        show_dcf_results()
    
    # Additional analysis sections
    st.markdown("---")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Scenario Analysis", "🎯 Sensitivity Analysis", "📊 Export Model", "📚 DCF Guide"])
    
    with tab1:
        show_scenario_analysis()
    
    with tab2:
        show_sensitivity_analysis()
    
    with tab3:
        show_export_options()
    
    with tab4:
        show_dcf_guide()

def load_company_data(ticker):
    """Load real company data from Yahoo Finance"""
    
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials
        
        if info:
            # Set session state with company data
            st.session_state.company_ticker = ticker
            st.session_state.company_name = info.get('longName', ticker)
            
            # Pre-populate some assumptions based on real data
            market_cap = info.get('marketCap', 0)
            enterprise_value = info.get('enterpriseValue', market_cap)
            
            if market_cap > 0:
                st.session_state.loaded_data = {
                    'market_cap': market_cap,
                    'enterprise_value': enterprise_value,
                    'current_price': info.get('regularMarketPrice', 0),
                    'shares_outstanding': info.get('sharesOutstanding', market_cap / info.get('regularMarketPrice', 1)),
                    'total_debt': info.get('totalDebt', 0),
                    'total_cash': info.get('totalCash', 0)
                }
                
                st.success(f"✅ Loaded data for {st.session_state.company_name}")
            else:
                st.error("❌ Could not load financial data for this ticker")
                
    except Exception as e:
        st.error(f"❌ Error loading data: {e}")

def show_assumptions_input():
    """Show DCF assumptions input interface"""
    
    st.markdown("### 📝 DCF Assumptions")
    
    # Company basics
    with st.expander("🏢 Company Information", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            company_name = st.text_input("Company Name", value=st.session_state.get('company_name', ''))
            base_revenue = st.number_input("Base Year Revenue ($M)", value=1000.0, step=50.0, format="%.1f")
        
        with col2:
            current_stock_price = st.number_input("Current Stock Price ($)", 
                                                value=st.session_state.get('loaded_data', {}).get('current_price', 100.0), 
                                                step=1.0, format="%.2f")
            shares_outstanding = st.number_input("Shares Outstanding (M)", 
                                               value=st.session_state.get('loaded_data', {}).get('shares_outstanding', 100.0)/1e6 if st.session_state.get('loaded_data', {}).get('shares_outstanding') else 100.0, 
                                               step=1.0, format="%.1f")
    
    # Growth assumptions
    with st.expander("📈 Growth Assumptions", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            revenue_growth_y1 = st.slider("Year 1 Revenue Growth (%)", -20, 50, 15)
        
        with col2:
            revenue_growth_y5 = st.slider("Year 5 Revenue Growth (%)", -10, 30, 8)
        
        with col3:
            revenue_growth_terminal = st.slider("Terminal Growth (%)", 0.0, 5.0, 2.5, step=0.5)
    
    # Profitability assumptions
    with st.expander("💰 Profitability Assumptions", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            base_ebitda_margin = st.slider("Base EBITDA Margin (%)", 0, 50, 20)
            target_ebitda_margin = st.slider("Target EBITDA Margin (%)", 0, 60, 25)
        
        with col2:
            da_revenue = st.slider("D&A as % of Revenue (%)", 0.0, 10.0, 3.0, step=0.5)
            tax_rate = st.slider("Tax Rate (%)", 0, 40, 21)
    
    # Investment assumptions
    with st.expander("🏗️ Investment Assumptions", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            capex_revenue = st.slider("Capex as % of Revenue (%)", 0.0, 15.0, 4.0, step=0.5)
        
        with col2:
            nwc_revenue = st.slider("NWC as % of Revenue (%)", -5.0, 15.0, 2.0, step=0.5)
    
    # Valuation assumptions
    with st.expander("🎯 Valuation Assumptions", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            wacc = st.slider("WACC (%)", 5.0, 20.0, 10.0, step=0.5)
        
        with col2:
            net_debt = st.number_input("Net Debt ($M)", 
                                     value=(st.session_state.get('loaded_data', {}).get('total_debt', 0) - 
                                           st.session_state.get('loaded_data', {}).get('total_cash', 0))/1e6 if st.session_state.get('loaded_data') else 0.0,
                                     step=50.0, format="%.1f")
    
    # Store assumptions in session state
    st.session_state.dcf_assumptions = {
        'company_name': company_name,
        'base_revenue': base_revenue,
        'current_stock_price': current_stock_price,
        'shares_outstanding': shares_outstanding,
        'revenue_growth_y1': revenue_growth_y1,
        'revenue_growth_y5': revenue_growth_y5,
        'revenue_growth_terminal': revenue_growth_terminal,
        'base_ebitda_margin': base_ebitda_margin,
        'target_ebitda_margin': target_ebitda_margin,
        'da_revenue': da_revenue,
        'tax_rate': tax_rate,
        'capex_revenue': capex_revenue,
        'nwc_revenue': nwc_revenue,
        'wacc': wacc,
        'net_debt': net_debt
    }

def show_dcf_results():
    """Show DCF calculation results"""
    
    st.markdown("### 🎯 Valuation Results")
    
    if 'dcf_assumptions' in st.session_state:
        assumptions = st.session_state.dcf_assumptions
        
        # Calculate DCF
        with st.spinner("📊 Running DCF calculations..."):
            projections, valuation = st.session_state.dcf_model.calculate_dcf_valuation(assumptions)
        
        # Display key results
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown(f"""
            <div class="valuation-result">
                <h3>💰 Intrinsic Value</h3>
                <div class="metric-highlight">${valuation['value_per_share']:.2f}</div>
                <p>per share</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            upside_color = "#00C851" if valuation['upside_downside'] > 0 else "#ff4444"
            upside_text = "Upside" if valuation['upside_downside'] > 0 else "Downside"
            
            st.markdown(f"""
            <div class="valuation-result" style="background: linear-gradient(135deg, {upside_color} 0%, {upside_color}CC 100%);">
                <h3>📈 {upside_text}</h3>
                <div class="metric-highlight">{valuation['upside_downside']:+.1f}%</div>
                <p>vs current price ${assumptions['current_stock_price']:.2f}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Valuation breakdown
        st.markdown("#### 📊 Valuation Breakdown")
        
        breakdown_data = {
            'Component': ['PV of Projection Period', 'PV of Terminal Value', 'Enterprise Value', 'Less: Net Debt', 'Equity Value'],
            'Value ($M)': [
                valuation['pv_projection_period'],
                valuation['pv_terminal_value'],
                valuation['enterprise_value'],
                -assumptions['net_debt'],
                valuation['equity_value']
            ],
            '% of EV': [
                valuation['pv_projection_period'] / valuation['enterprise_value'] * 100,
                valuation['pv_terminal_value'] / valuation['enterprise_value'] * 100,
                100,
                -assumptions['net_debt'] / valuation['enterprise_value'] * 100,
                valuation['equity_value'] / valuation['enterprise_value'] * 100
            ]
        }
        
        breakdown_df = pd.DataFrame(breakdown_data)
        st.dataframe(breakdown_df, use_container_width=True)
        
        # Key metrics
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("EV/Revenue (LTM)", f"{valuation['implied_ev_revenue']:.1f}x")
        
        with col2:
            st.metric("Terminal Value %", f"{valuation['pv_terminal_value']/valuation['enterprise_value']*100:.0f}%")
        
        with col3:
            st.metric("Enterprise Value", f"${valuation['enterprise_value']:.0f}M")
        
        # Store results for other tabs
        st.session_state.dcf_projections = projections
        st.session_state.dcf_valuation = valuation
        
        # Financial projections chart
        st.markdown("#### 📈 Financial Projections")
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=('Revenue & Growth', 'EBITDA & Margin', 'Free Cash Flow', 'Cumulative PV'),
            specs=[[{"secondary_y": True}, {"secondary_y": True}],
                   [{"secondary_y": False}, {"secondary_y": False}]]
        )
        
        # Revenue and growth
        fig.add_trace(go.Bar(x=projections['Year'], y=projections['Revenue'], name='Revenue ($M)', showlegend=False), row=1, col=1)
        fig.add_trace(go.Scatter(x=projections['Year'], y=projections['Revenue_Growth'], name='Growth %', mode='lines+markers', yaxis='y2', showlegend=False), row=1, col=1)
        
        # EBITDA and margin
        fig.add_trace(go.Bar(x=projections['Year'], y=projections['EBITDA'], name='EBITDA ($M)', showlegend=False), row=1, col=2)
        fig.add_trace(go.Scatter(x=projections['Year'], y=projections['EBITDA_Margin'], name='Margin %', mode='lines+markers', yaxis='y4', showlegend=False), row=1, col=2)
        
        # Free cash flow
        fig.add_trace(go.Bar(x=projections['Year'], y=projections['FCFF'], name='FCFF ($M)', showlegend=False), row=2, col=1)
        
        # Cumulative PV
        cumulative_pv = projections['PV_FCFF'].cumsum()
        fig.add_trace(go.Scatter(x=projections['Year'], y=cumulative_pv, name='Cumulative PV', mode='lines+markers', fill='tonexty', showlegend=False), row=2, col=2)
        
        fig.update_layout(height=600, title_text="DCF Model Projections")
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        st.info("👆 Please input your DCF assumptions to see valuation results")

def show_scenario_analysis():
    """Show scenario analysis results"""
    
    st.markdown("### 📈 Scenario Analysis")
    
    if 'dcf_assumptions' in st.session_state:
        assumptions = st.session_state.dcf_assumptions
        
        with st.spinner("🔄 Running scenario analysis..."):
            scenarios = st.session_state.dcf_model.scenario_analysis(assumptions)
        
        # Scenario results table
        scenario_data = {
            'Scenario': [],
            'Value per Share': [],
            'Enterprise Value': [],
            'Upside/Downside': []
        }
        
        base_value = scenarios['Base Case']['valuation']['value_per_share']
        
        for scenario_name, results in scenarios.items():
            scenario_data['Scenario'].append(scenario_name)
            scenario_data['Value per Share'].append(f"${results['valuation']['value_per_share']:.2f}")
            scenario_data['Enterprise Value'].append(f"${results['valuation']['enterprise_value']:.0f}M")
            
            upside = (results['valuation']['value_per_share'] - assumptions['current_stock_price']) / assumptions['current_stock_price'] * 100
            scenario_data['Upside/Downside'].append(f"{upside:+.1f}%")
        
        scenario_df = pd.DataFrame(scenario_data)
        st.dataframe(scenario_df, use_container_width=True)
        
        # Scenario chart
        values = [scenarios[s]['valuation']['value_per_share'] for s in ['Bear Case', 'Base Case', 'Bull Case']]
        colors = ['#ff4444', '#33b5e5', '#00C851']
        
        fig = go.Figure(data=[
            go.Bar(x=['Bear Case', 'Base Case', 'Bull Case'], y=values, marker_color=colors)
        ])
        
        # Add current price line
        fig.add_hline(y=assumptions['current_stock_price'], line_dash="dash", 
                      annotation_text=f"Current Price: ${assumptions['current_stock_price']:.2f}")
        
        fig.update_layout(
            title="Scenario Analysis - Value per Share",
            yaxis_title="Value per Share ($)",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("👆 Please complete DCF assumptions to run scenario analysis")

def show_sensitivity_analysis():
    """Show sensitivity analysis"""
    
    st.markdown("### 🎯 Sensitivity Analysis")
    
    if 'dcf_assumptions' in st.session_state:
        assumptions = st.session_state.dcf_assumptions
        
        # Sensitivity variable selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📊 Select Variables to Test")
            
            test_wacc = st.checkbox("WACC", value=True)
            test_terminal_growth = st.checkbox("Terminal Growth Rate", value=True)
            test_revenue_growth = st.checkbox("Year 1 Revenue Growth", value=True)
            test_ebitda_margin = st.checkbox("Target EBITDA Margin", value=False)
        
        with col2:
            st.markdown("#### ⚙️ Sensitivity Ranges")
            
            wacc_range = st.slider("WACC Range (+/-)", 0.5, 3.0, 1.5, step=0.5)
            terminal_range = st.slider("Terminal Growth Range (+/-)", 0.5, 2.0, 1.0, step=0.5)
            revenue_range = st.slider("Revenue Growth Range (+/-)", 2, 10, 5)
            ebitda_range = st.slider("EBITDA Margin Range (+/-)", 1, 5, 2)
        
        if st.button("🚀 Run Sensitivity Analysis"):
            
            # Build sensitivity variables
            sensitivity_vars = {}
            
            if test_wacc:
                base_wacc = assumptions['wacc']
                sensitivity_vars['wacc'] = np.arange(base_wacc - wacc_range, base_wacc + wacc_range + 0.1, 0.5)
            
            if test_terminal_growth:
                base_terminal = 2.5  # Default terminal growth
                sensitivity_vars['revenue_growth_terminal'] = np.arange(base_terminal - terminal_range, base_terminal + terminal_range + 0.1, 0.5)
            
            if test_revenue_growth:
                base_rev_growth = assumptions['revenue_growth_y1']
                sensitivity_vars['revenue_growth_y1'] = np.arange(base_rev_growth - revenue_range, base_rev_growth + revenue_range + 1, 2)
            
            if test_ebitda_margin:
                base_ebitda = assumptions['target_ebitda_margin']
                sensitivity_vars['target_ebitda_margin'] = np.arange(base_ebitda - ebitda_range, base_ebitda + ebitda_range + 1, 1)
            
            with st.spinner("🔄 Running sensitivity analysis..."):
                sensitivity_results = st.session_state.dcf_model.sensitivity_analysis(assumptions, sensitivity_vars)
            
            # Display results
            for var_name, results_df in sensitivity_results.items():
                st.markdown(f"#### {var_name.replace('_', ' ').title()}")
                
                # Chart
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=results_df['variable_value'],
                    y=results_df['value_per_share'],
                    mode='lines+markers',
                    name='Value per Share'
                ))
                
                # Add current price line
                fig.add_hline(y=assumptions['current_stock_price'], line_dash="dash",
                             annotation_text=f"Current Price: ${assumptions['current_stock_price']:.2f}")
                
                fig.update_layout(
                    xaxis_title=var_name.replace('_', ' ').title(),
                    yaxis_title="Value per Share ($)",
                    height=300
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                # Table
                st.dataframe(results_df, use_container_width=True)
    
    else:
        st.info("👆 Please complete DCF assumptions to run sensitivity analysis")

def show_export_options():
    """Show export options for the DCF model"""
    
    st.markdown("### 📊 Export DCF Model")
    
    if 'dcf_projections' in st.session_state and 'dcf_valuation' in st.session_state:
        projections = st.session_state.dcf_projections
        valuation = st.session_state.dcf_valuation
        assumptions = st.session_state.dcf_assumptions
        
        # Excel export option
        st.markdown("#### 📈 Download Excel Model")
        
        if st.button("🔽 Generate Excel DCF Model"):
            excel_buffer = create_excel_dcf_model(projections, valuation, assumptions)
            
            st.download_button(
                label="📊 Download DCF Model.xlsx",
                data=excel_buffer,
                file_name=f"DCF_Model_{assumptions.get('company_name', 'Company').replace(' ', '_')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        
        # CSV export
        st.markdown("#### 📋 Download CSV Data")
        
        col1, col2 = st.columns(2)
        
        with col1:
            csv_projections = projections.to_csv(index=False)
            st.download_button(
                label="📈 Download Projections CSV",
                data=csv_projections,
                file_name="dcf_projections.csv",
                mime="text/csv"
            )
        
        with col2:
            # Create valuation summary
            valuation_summary = pd.DataFrame([
                ['Enterprise Value', f"${valuation['enterprise_value']:.0f}M"],
                ['Equity Value', f"${valuation['equity_value']:.0f}M"],
                ['Value per Share', f"${valuation['value_per_share']:.2f}"],
                ['Current Price', f"${assumptions['current_stock_price']:.2f}"],
                ['Upside/Downside', f"{valuation['upside_downside']:+.1f}%"]
            ], columns=['Metric', 'Value'])
            
            csv_valuation = valuation_summary.to_csv(index=False)
            st.download_button(
                label="💰 Download Valuation CSV",
                data=csv_valuation,
                file_name="dcf_valuation.csv",
                mime="text/csv"
            )
        
        # Model summary
        st.markdown("#### 📋 Model Summary")
        
        summary_data = {
            'Parameter': ['Company', 'Base Revenue', 'WACC', 'Terminal Growth', 'Value per Share', 'Upside/Downside'],
            'Value': [
                assumptions.get('company_name', 'N/A'),
                f"${assumptions['base_revenue']:.0f}M",
                f"{assumptions['wacc']:.1f}%",
                f"{assumptions['revenue_growth_terminal']:.1f}%",
                f"${valuation['value_per_share']:.2f}",
                f"{valuation['upside_downside']:+.1f}%"
            ]
        }
        
        summary_df = pd.DataFrame(summary_data)
        st.dataframe(summary_df, use_container_width=True)
    
    else:
        st.info("👆 Please complete the DCF model to access export options")

def create_excel_dcf_model(projections, valuation, assumptions):
    """Create Excel DCF model for download"""
    
    from io import BytesIO
    
    output = BytesIO()
    
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        # Assumptions sheet
        assumptions_df = pd.DataFrame([
            ['Company Name', assumptions.get('company_name', 'N/A')],
            ['Base Revenue ($M)', assumptions['base_revenue']],
            ['Current Stock Price ($)', assumptions['current_stock_price']],
            ['Shares Outstanding (M)', assumptions['shares_outstanding']],
            ['Year 1 Revenue Growth (%)', assumptions['revenue_growth_y1']],
            ['Year 5 Revenue Growth (%)', assumptions['revenue_growth_y5']],
            ['Terminal Growth Rate (%)', assumptions['revenue_growth_terminal']],
            ['Base EBITDA Margin (%)', assumptions['base_ebitda_margin']],
            ['Target EBITDA Margin (%)', assumptions['target_ebitda_margin']],
            ['WACC (%)', assumptions['wacc']],
            ['Net Debt ($M)', assumptions['net_debt']]
        ], columns=['Parameter', 'Value'])
        
        assumptions_df.to_excel(writer, sheet_name='Assumptions', index=False)
        
        # Projections sheet
        projections.to_excel(writer, sheet_name='Projections', index=False)
        
        # Valuation sheet
        valuation_df = pd.DataFrame([
            ['PV of Projection Period ($M)', valuation['pv_projection_period']],
            ['Terminal Value ($M)', valuation['terminal_value']],
            ['PV of Terminal Value ($M)', valuation['pv_terminal_value']],
            ['Enterprise Value ($M)', valuation['enterprise_value']],
            ['Net Debt ($M)', assumptions['net_debt']],
            ['Equity Value ($M)', valuation['equity_value']],
            ['Shares Outstanding (M)', assumptions['shares_outstanding']],
            ['Value per Share ($)', valuation['value_per_share']],
            ['Current Stock Price ($)', assumptions['current_stock_price']],
            ['Upside/Downside (%)', valuation['upside_downside']]
        ], columns=['Item', 'Value'])
        
        valuation_df.to_excel(writer, sheet_name='Valuation', index=False)
    
    output.seek(0)
    return output.getvalue()

def show_dcf_guide():
    """Show DCF methodology guide"""
    
    st.markdown("### 📚 DCF Methodology Guide")
    
    with st.expander("🎯 What is DCF?", expanded=True):
        st.markdown("""
        **Discounted Cash Flow (DCF)** is a valuation method that estimates the value of a company based on its projected future cash flows, discounted back to present value.
        
        **Key Formula**: `Enterprise Value = Σ(FCF / (1 + WACC)^t) + Terminal Value / (1 + WACC)^n`
        
        **Why DCF?**
        - **Intrinsic Value**: Based on fundamental business performance
        - **Forward-Looking**: Uses future projections, not just historical data
        - **Comprehensive**: Considers all aspects of business performance
        - **Flexible**: Can model different scenarios and assumptions
        """)
    
    with st.expander("📊 Key Components"):
        st.markdown("""
        **1. Free Cash Flow to the Firm (FCFF)**
        ```
        FCFF = EBIT × (1 - Tax Rate) + Depreciation - CapEx - Change in NWC
        ```
        
        **2. Weighted Average Cost of Capital (WACC)**
        ```
        WACC = (E/V × Re) + (D/V × Rd × (1 - Tax Rate))
        ```
        
        **3. Terminal Value**
        ```
        Terminal Value = FCF(final year) × (1 + g) / (WACC - g)
        ```
        
        **4. Enterprise to Equity Value**
        ```
        Equity Value = Enterprise Value - Net Debt
        Value per Share = Equity Value / Shares Outstanding
        ```
        """)
    
    with st.expander("⚖️ Key Assumptions"):
        st.markdown("""
        **Revenue Growth**: 
        - Year 1-5: Based on market size, competition, product lifecycle
        - Terminal: Usually 2-4%, not exceeding long-term GDP growth
        
        **Margins**:
        - Consider operating leverage, competition, industry dynamics
        - Healthcare companies often have high R&D costs but strong margins
        
        **WACC**:
        - Risk-free rate + equity risk premium × beta + debt costs
        - Healthcare: typically 8-12% depending on company stage/risk
        
        **Terminal Growth**:
        - Conservative: 2-3% (long-term GDP/inflation)
        - Should not exceed long-term economic growth
        """)
    
    with st.expander("🎯 Healthcare-Specific Considerations"):
        st.markdown("""
        **Biotech & Pharma Valuation**:
        - **Pipeline Risk**: Weight by probability of success
        - **Patent Cliffs**: Model revenue decline when patents expire
        - **R&D Intensity**: High upfront costs, long development cycles
        - **Regulatory Risk**: FDA approval uncertainty
        
        **Key Metrics**:
        - **Risk-Adjusted NPV**: Probability-weight pipeline assets
        - **Peak Sales**: Estimate maximum drug revenue potential
        - **Time to Market**: Consider development timelines
        - **Competition**: Model market share erosion
        
        **Typical Ranges**:
        - **WACC**: 9-15% (higher for early-stage biotech)
        - **Terminal Growth**: 2-4%
        - **EBITDA Margins**: 20-40% for mature pharma, negative for early biotech
        """)
    
    with st.expander("⚠️ Common Pitfalls"):
        st.markdown("""
        **1. Over-Optimistic Growth**
        - Reality check against industry/market size
        - Consider competitive dynamics
        
        **2. Terminal Value Dominance**
        - Should be 60-80% of total value
        - If >90%, projections may be too conservative
        
        **3. Ignoring Cyclicality**
        - Normalize for economic cycles
        - Use multiple scenarios
        
        **4. WACC Assumptions**
        - Small changes have huge impact
        - Regularly update based on market conditions
        
        **5. Working Capital**
        - Don't forget seasonal effects
        - Model realistic collection/payment cycles
        """)

if __name__ == "__main__":
    main() 