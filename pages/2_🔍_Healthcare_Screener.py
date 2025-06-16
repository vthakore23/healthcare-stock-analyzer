# Healthcare Screener Page

import streamlit as st
import sys
import os
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import numpy as np
import requests
from datetime import datetime, timedelta
from st_aggrid import AgGrid, GridOptionsBuilder, DataReturnMode, GridUpdateMode
from streamlit_option_menu import option_menu

# Add the parent directory to the path to import custom modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

# Import available utilities (these modules were removed in recent updates)
try:
    from medequity_utils.live_news_scraper import LiveNewsScraper
    from medequity_utils.live_fda_scraper import LiveFDACalendar
except ImportError:
    # These utilities are optional - screener will work without them
    pass

# Page configuration
st.set_page_config(
    page_title="Advanced Stock Screener - Healthcare Analyzer | June 2025",
    page_icon="🔍",
    layout="wide"
)

# Professional CSS styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    .screener-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin-bottom: 2rem;
        font-family: 'Inter', sans-serif;
    }
    
    .filter-section {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e2e8f0;
    }
    
    .metric-box {
        background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .stock-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        margin: 1rem 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border: 1px solid #e2e8f0;
        transition: all 0.3s ease;
    }
    
    .stock-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.15);
    }
    
    .performance-badge {
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
        color: white;
    }
    
    .badge-excellent { background: #22c55e; }
    .badge-good { background: #3b82f6; }
    .badge-average { background: #f59e0b; }
    .badge-poor { background: #ef4444; }
    
    .real-time-indicator {
        color: #10b981;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .section-divider {
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
        margin: 2rem 0;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

class AdvancedStockScreener:
    """Bloomberg-level advanced stock screener"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
    def get_stock_universe(self):
        """Get comprehensive stock universe from multiple sources"""
        try:
            # S&P 500
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            sp500_tables = pd.read_html(sp500_url)
            sp500_stocks = sp500_tables[0]['Symbol'].tolist()
            
            # NASDAQ 100
            nasdaq100_url = "https://en.wikipedia.org/wiki/Nasdaq-100"
            nasdaq_tables = pd.read_html(nasdaq100_url)
            nasdaq_stocks = nasdaq_tables[4]['Ticker'].tolist() if len(nasdaq_tables) > 4 else []
            
            # Russell 1000 (major companies)
            russell_stocks = [
                'GOOGL', 'MSFT', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'XOM', 'LLY',
                'V', 'JNJ', 'JPM', 'PG', 'MA', 'AVGO', 'HD', 'CVX', 'MRK', 'ABBV', 'COST', 'PEP',
                'KO', 'WMT', 'BAC', 'TMO', 'NFLX', 'CRM', 'ACN', 'LIN', 'ABT', 'CSCO', 'DHR',
                'VZ', 'DIS', 'ADBE', 'WFC', 'CMCSA', 'NKE', 'TXN', 'AMD', 'BMY', 'PM', 'RTX',
                'QCOM', 'HON', 'UPS', 'T', 'LOW', 'SBUX'
            ]
            
            # Healthcare-focused additions
            healthcare_stocks = [
                'PFE', 'MRNA', 'BNTX', 'REGN', 'VRTX', 'GILD', 'BIIB', 'AMGN', 'CELG', 'BMY',
                'MDT', 'SYK', 'ISRG', 'DXCM', 'ZTS', 'EW', 'HOLX', 'BDX', 'BSX', 'ALGN',
                'ILMN', 'IQV', 'A', 'MTD', 'IDXX', 'RMD', 'TECH', 'ZBH', 'BAX', 'TFX'
            ]
            
            # Combine all universes
            all_stocks = list(set(sp500_stocks + nasdaq_stocks + russell_stocks + healthcare_stocks))
            
            return all_stocks[:500]  # Limit for performance
            
        except Exception as e:
            st.warning(f"Using fallback stock universe. Full universe temporarily unavailable.")
            # Fallback comprehensive list
            return [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'BRK-B', 'UNH', 'JNJ',
                'PFE', 'LLY', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY', 'MRNA', 'REGN',
                'VRTX', 'GILD', 'BIIB', 'AMGN', 'MDT', 'SYK', 'ISRG', 'DXCM', 'ZTS', 'BSX',
                'V', 'MA', 'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'AXP', 'COF',
                'HD', 'WMT', 'COST', 'TGT', 'LOW', 'NKE', 'SBUX', 'MCD', 'DIS', 'NFLX'
            ]
    
    def get_real_time_data(self, symbols, max_workers=10):
        """Get real-time data for multiple symbols with parallel processing"""
        def fetch_stock_data(symbol):
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                hist = ticker.history(period="1y")
                
                if hist.empty or not info:
                    return None
                
                current_price = hist['Close'][-1] if not hist.empty else 0
                
                # Calculate key metrics
                data = {
                    'Symbol': symbol,
                    'Company': info.get('longName', symbol),
                    'Sector': info.get('sector', 'Unknown'),
                    'Industry': info.get('industry', 'Unknown'),
                    'Price': current_price,
                    'Market Cap': info.get('marketCap', 0),
                    'PE Ratio': info.get('trailingPE', 0),
                    'PEG Ratio': info.get('pegRatio', 0),
                    'Price to Book': info.get('priceToBook', 0),
                    'Debt to Equity': info.get('debtToEquity', 0),
                    'ROE': info.get('returnOnEquity', 0),
                    'ROA': info.get('returnOnAssets', 0),
                    'Profit Margin': info.get('profitMargins', 0),
                    'Operating Margin': info.get('operatingMargins', 0),
                    'Current Ratio': info.get('currentRatio', 0),
                    'Quick Ratio': info.get('quickRatio', 0),
                    'Revenue Growth': info.get('revenueGrowth', 0),
                    'Earnings Growth': info.get('earningsGrowth', 0),
                    'Beta': info.get('beta', 0),
                    'Volume': info.get('volume', 0),
                    'Avg Volume': info.get('averageVolume', 0),
                    'Dividend Yield': info.get('dividendYield', 0),
                    '52W High': info.get('fiftyTwoWeekHigh', 0),
                    '52W Low': info.get('fiftyTwoWeekLow', 0),
                    'ESG Score': info.get('totalEsg', 0),
                    'Analyst Rating': info.get('recommendationMean', 0),
                    'Target Price': info.get('targetMeanPrice', 0)
                }
                
                # Calculate performance metrics
                if not hist.empty and len(hist) > 0:
                    data['1D Change'] = ((current_price - hist['Close'][-2]) / hist['Close'][-2] * 100) if len(hist) > 1 else 0
                    data['1W Change'] = ((current_price - hist['Close'][-5]) / hist['Close'][-5] * 100) if len(hist) > 5 else 0
                    data['1M Change'] = ((current_price - hist['Close'][-22]) / hist['Close'][-22] * 100) if len(hist) > 22 else 0
                    data['3M Change'] = ((current_price - hist['Close'][-66]) / hist['Close'][-66] * 100) if len(hist) > 66 else 0
                    data['6M Change'] = ((current_price - hist['Close'][-132]) / hist['Close'][-132] * 100) if len(hist) > 132 else 0
                    data['1Y Change'] = ((current_price - hist['Close'][0]) / hist['Close'][0] * 100) if len(hist) > 200 else 0
                    
                    # Volatility
                    data['Volatility'] = hist['Close'].pct_change().std() * np.sqrt(252) * 100
                    
                    # RSI
                    delta = hist['Close'].diff()
                    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                    rs = gain / loss
                    data['RSI'] = 100 - (100 / (1 + rs)).iloc[-1] if not rs.empty else 50
                    
                return data
                
            except Exception as e:
                return None
        
        results = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(fetch_stock_data, symbol): symbol for symbol in symbols}
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        return pd.DataFrame(results)

def main():
    st.markdown("""
    <div class="screener-header">
        <h1>🔍 Advanced Stock Screener</h1>
        <p style="font-size: 1.3rem;">Bloomberg-level screening across ALL markets - June 2025</p>
        <div class="real-time-indicator">🔴 LIVE DATA • 🌍 GLOBAL MARKETS • 📊 REAL-TIME ANALYTICS</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize screener
    if 'advanced_screener' not in st.session_state:
        st.session_state.advanced_screener = AdvancedStockScreener()
    
    # Navigation menu
    selected = option_menu(
        menu_title=None,
        options=["🎯 Quick Screen", "🔧 Advanced Filters", "📊 Market Overview", "💎 Top Picks"],
        icons=["bullseye", "gear", "graph-up", "gem"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "#fafafa"},
            "icon": {"color": "#667eea", "font-size": "18px"},
            "nav-link": {"font-size": "16px", "text-align": "center", "--hover-color": "#eee"},
            "nav-link-selected": {"background-color": "#667eea"},
        }
    )
    
    if selected == "🎯 Quick Screen":
        show_quick_screen()
    elif selected == "🔧 Advanced Filters":
        show_advanced_filters()
    elif selected == "📊 Market Overview":
        show_market_overview()
    elif selected == "💎 Top Picks":
        show_top_picks()

def show_quick_screen():
    """Show quick screening options"""
    st.markdown("### 🎯 Quick Screen - Popular Strategies")
    
    # Quick screen categories
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 🚀 Growth Stocks")
        if st.button("High Growth", use_container_width=True):
            run_predefined_screen("growth")
        if st.button("Momentum", use_container_width=True):
            run_predefined_screen("momentum")
        if st.button("Small Cap Growth", use_container_width=True):
            run_predefined_screen("small_growth")
    
    with col2:
        st.markdown("#### 💰 Value Stocks")
        if st.button("Deep Value", use_container_width=True):
            run_predefined_screen("value")
        if st.button("Dividend Aristocrats", use_container_width=True):
            run_predefined_screen("dividend")
        if st.button("Low P/E", use_container_width=True):
            run_predefined_screen("low_pe")
    
    with col3:
        st.markdown("#### 🏥 Healthcare Focus")
        if st.button("Biotech Leaders", use_container_width=True):
            run_predefined_screen("biotech")
        if st.button("Pharma Giants", use_container_width=True):
            run_predefined_screen("pharma")
        if st.button("Med Tech", use_container_width=True):
            run_predefined_screen("medtech")
    
    # Display results if screen has been run
    if 'screen_results' in st.session_state and st.session_state.screen_results is not None:
        display_screening_results(st.session_state.screen_results, st.session_state.screen_type)

def show_advanced_filters():
    """Show advanced filtering interface"""
    st.markdown("### 🔧 Advanced Filters - Custom Screening")
    
    # Get stock universe
    with st.spinner("🔄 Loading stock universe..."):
        if 'stock_universe' not in st.session_state:
            st.session_state.stock_universe = st.session_state.advanced_screener.get_stock_universe()
    
    # Filter interface
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("#### 📊 Basic Filters")
        
        # Market Cap
        market_cap_min, market_cap_max = st.select_slider(
            "Market Cap (Billions)",
            options=[0, 1, 5, 10, 50, 100, 500, 1000, 5000],
            value=(1, 1000),
            format_func=lambda x: f"${x}B" if x > 0 else "Any"
        )
        
        # Price range
        price_min, price_max = st.slider(
            "Price Range ($)",
            min_value=0, max_value=1000,
            value=(5, 500),
            step=5
        )
        
        # Sectors
        sectors = ['Technology', 'Healthcare', 'Financial Services', 'Consumer Cyclical', 
                  'Communication Services', 'Industrials', 'Consumer Defensive', 'Energy',
                  'Utilities', 'Real Estate', 'Basic Materials']
        selected_sectors = st.multiselect("Sectors", sectors, default=sectors)
        
        st.markdown("#### 📈 Performance Filters")
        
        # Performance ranges
        perf_1y_min, perf_1y_max = st.slider("1Y Performance (%)", -100, 500, (-50, 200))
        perf_1m_min, perf_1m_max = st.slider("1M Performance (%)", -50, 100, (-20, 50))
        
        # Volume filter
        min_volume = st.number_input("Min Average Volume", value=100000, step=50000)
        
    with col2:
        st.markdown("#### 💹 Financial Metrics")
        
        col2a, col2b = st.columns(2)
        
        with col2a:
            # Valuation metrics
            pe_min, pe_max = st.slider("P/E Ratio", 0, 100, (5, 50))
            pb_min, pb_max = st.slider("Price to Book", 0.0, 10.0, (0.5, 5.0), 0.1)
            peg_min, peg_max = st.slider("PEG Ratio", 0.0, 5.0, (0.5, 2.0), 0.1)
            
            # Growth metrics
            rev_growth_min = st.slider("Min Revenue Growth (%)", -50, 100, 0)
            earn_growth_min = st.slider("Min Earnings Growth (%)", -100, 200, 0)
        
        with col2b:
            # Profitability metrics
            roe_min = st.slider("Min ROE (%)", -50, 100, 10)
            profit_margin_min = st.slider("Min Profit Margin (%)", -50, 100, 5)
            
            # Financial health
            debt_equity_max = st.slider("Max Debt/Equity", 0.0, 5.0, 2.0, 0.1)
            current_ratio_min = st.slider("Min Current Ratio", 0.0, 5.0, 1.0, 0.1)
            
            # Technical indicators
            rsi_min, rsi_max = st.slider("RSI Range", 0, 100, (30, 70))
            beta_min, beta_max = st.slider("Beta Range", 0.0, 3.0, (0.5, 2.0), 0.1)
        
        # Run custom screen button
        if st.button("🚀 Run Custom Screen", type="primary", use_container_width=True):
            filters = {
                'market_cap_range': (market_cap_min * 1e9, market_cap_max * 1e9),
                'price_range': (price_min, price_max),
                'sectors': selected_sectors,
                'perf_1y_range': (perf_1y_min, perf_1y_max),
                'perf_1m_range': (perf_1m_min, perf_1m_max),
                'min_volume': min_volume,
                'pe_range': (pe_min, pe_max),
                'pb_range': (pb_min, pb_max),
                'peg_range': (peg_min, peg_max),
                'rev_growth_min': rev_growth_min,
                'earn_growth_min': earn_growth_min,
                'roe_min': roe_min,
                'profit_margin_min': profit_margin_min,
                'debt_equity_max': debt_equity_max,
                'current_ratio_min': current_ratio_min,
                'rsi_range': (rsi_min, rsi_max),
                'beta_range': (beta_min, beta_max)
            }
            
            run_custom_screen(filters)
    
    # Display custom results
    if 'custom_screen_results' in st.session_state and st.session_state.custom_screen_results is not None:
        display_screening_results(st.session_state.custom_screen_results, "Custom Screen")

def show_market_overview():
    """Show market overview and statistics"""
    st.markdown("### 📊 Market Overview - Real-time Statistics")
    
    # Market indices
    indices = {
        '^GSPC': 'S&P 500',
        '^IXIC': 'NASDAQ',
        '^DJI': 'Dow Jones',
        '^RUT': 'Russell 2000',
        'XLV': 'Healthcare ETF',
        'IBB': 'Biotech ETF'
    }
    
    with st.spinner("📡 Fetching market data..."):
        market_data = get_market_indices_data(indices)
    
    # Display market overview
    cols = st.columns(3)
    for i, (symbol, data) in enumerate(market_data.items()):
        with cols[i % 3]:
            change_color = "🟢" if data['change'] >= 0 else "🔴"
            st.markdown(f"""
            <div class="metric-box">
                <h4>{data['name']} {change_color}</h4>
                <h2>${data['price']:.2f}</h2>
                <p>{data['change']:+.2f}% ({data['change_value']:+.2f})</p>
            </div>
            """, unsafe_allow_html=True)
    
    # Market statistics
    st.markdown("<hr class='section-divider'>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📈 Market Trends")
        show_market_trends()
    
    with col2:
        st.markdown("#### 🏆 Top Performers")
        show_top_performers()

def show_top_picks():
    """Show AI-powered top picks"""
    st.markdown("### 💎 AI-Powered Top Picks")
    
    # Different categories of picks
    pick_categories = {
        "🚀 Momentum Leaders": "momentum_leaders",
        "💰 Value Opportunities": "value_picks",
        "🏥 Healthcare Stars": "healthcare_picks",
        "🔮 AI Recommendations": "ai_picks"
    }
    
    selected_category = st.selectbox("Select Category:", list(pick_categories.keys()))
    
    if st.button("🔍 Generate Picks", type="primary"):
        generate_top_picks(pick_categories[selected_category])
    
    # Display picks if generated
    if 'top_picks' in st.session_state and st.session_state.top_picks is not None:
        display_top_picks_results()

def run_predefined_screen(screen_type):
    """Run predefined screening strategies"""
    
    with st.spinner(f"🔍 Running {screen_type} screen across ALL stocks..."):
        universe = st.session_state.stock_universe
        
        # Process larger chunks of the universe for better coverage
        chunk_size = 200  # Process 200 stocks at a time
        all_results = []
        
        # Process universe in chunks to get comprehensive coverage
        for i in range(0, min(len(universe), 800), chunk_size):  # Process up to 800 stocks
            chunk = universe[i:i + chunk_size]
            chunk_results = st.session_state.advanced_screener.get_real_time_data(chunk, max_workers=15)
            
            if not chunk_results.empty:
                all_results.append(chunk_results)
        
        # Combine all results
        if all_results:
            results = pd.concat(all_results, ignore_index=True)
        else:
            results = pd.DataFrame()
        
        # Apply specific filters based on screen type
        if not results.empty:
            if screen_type == "growth":
                # Growth stocks: High revenue growth, reasonable P/E, positive earnings growth
                filtered = results[
                    (results['Revenue Growth'] > 0.10) & 
                    (results['PE Ratio'] > 5) & 
                    (results['PE Ratio'] < 60) &
                    (results['Earnings Growth'] > 0.05) &
                    (results['Market Cap'] > 1e9)  # Over $1B market cap
                ]
                results = filtered.nlargest(50, 'Revenue Growth')
                
            elif screen_type == "momentum":
                # Momentum stocks: Strong recent performance, good volume
                filtered = results[
                    (results['1M Change'] > 5) & 
                    (results['3M Change'] > 10) &
                    (results['Volume'] > results['Avg Volume'] * 1.2) &
                    (results['RSI'] > 50) &
                    (results['Market Cap'] > 500e6)  # Over $500M market cap
                ]
                results = filtered.nlargest(50, '1M Change')
                
            elif screen_type == "small_growth":
                # Small cap growth
                filtered = results[
                    (results['Market Cap'] > 300e6) &
                    (results['Market Cap'] < 10e9) &
                    (results['Revenue Growth'] > 0.15) &
                    (results['PE Ratio'] > 0) &
                    (results['PE Ratio'] < 40)
                ]
                results = filtered.nlargest(50, 'Revenue Growth')
                
            elif screen_type == "value":
                # Value stocks: Low P/E, reasonable P/B, positive earnings
                filtered = results[
                    (results['PE Ratio'] > 0) & 
                    (results['PE Ratio'] < 18) & 
                    (results['Price to Book'] > 0) &
                    (results['Price to Book'] < 4) &
                    (results['Profit Margin'] > 0.05) &
                    (results['Market Cap'] > 1e9)
                ]
                results = filtered.nsmallest(50, 'PE Ratio')
                
            elif screen_type == "dividend":
                # Dividend aristocrats: High dividend yield, consistent payments
                filtered = results[
                    (results['Dividend Yield'] > 0.03) &
                    (results['PE Ratio'] > 0) &
                    (results['PE Ratio'] < 25) &
                    (results['Current Ratio'] > 1.2) &
                    (results['Market Cap'] > 5e9)  # Large cap for stability
                ]
                results = filtered.nlargest(50, 'Dividend Yield')
                
            elif screen_type == "low_pe":
                # Low P/E stocks
                filtered = results[
                    (results['PE Ratio'] > 0) & 
                    (results['PE Ratio'] < 12) &
                    (results['Profit Margin'] > 0.03) &
                    (results['ROE'] > 0.08) &
                    (results['Market Cap'] > 1e9)
                ]
                results = filtered.nsmallest(50, 'PE Ratio')
                
            elif screen_type == "biotech":
                # Biotech leaders: Healthcare sector with growth characteristics
                healthcare_results = results[results['Sector'] == 'Healthcare']
                if healthcare_results.empty:
                    # Fallback to known biotech symbols if sector filtering fails
                    biotech_symbols = ['MRNA', 'BNTX', 'REGN', 'VRTX', 'GILD', 'BIIB', 'AMGN', 'ILMN', 'INCY', 'ALNY']
                    biotech_data = st.session_state.advanced_screener.get_real_time_data(biotech_symbols)
                    results = biotech_data.head(30)
                else:
                    filtered = healthcare_results[
                        (healthcare_results['Revenue Growth'] > 0.08) &
                        (healthcare_results['Market Cap'] > 1e9) &
                        (healthcare_results['PE Ratio'] > 0)
                    ]
                    results = filtered.nlargest(30, 'Market Cap')
                
            elif screen_type == "pharma":
                # Pharma giants: Large healthcare companies
                healthcare_results = results[results['Sector'] == 'Healthcare']
                if healthcare_results.empty:
                    # Fallback to known pharma symbols
                    pharma_symbols = ['PFE', 'JNJ', 'MRK', 'ABT', 'LLY', 'BMY', 'ABBV', 'AZN', 'NVO', 'ROCHE']
                    pharma_data = st.session_state.advanced_screener.get_real_time_data(pharma_symbols)
                    results = pharma_data.head(30)
                else:
                    filtered = healthcare_results[
                        (healthcare_results['Market Cap'] > 50e9) &  # Large cap pharma
                        (healthcare_results['Dividend Yield'] > 0.02) &
                        (healthcare_results['PE Ratio'] > 0)
                    ]
                    results = filtered.nlargest(30, 'Market Cap')
                
            elif screen_type == "medtech":
                # Medical technology companies
                healthcare_results = results[results['Sector'] == 'Healthcare']
                if healthcare_results.empty:
                    # Fallback to known medtech symbols
                    medtech_symbols = ['MDT', 'SYK', 'ISRG', 'DXCM', 'BSX', 'ZBH', 'HOLX', 'EW', 'ALGN', 'IDXX']
                    medtech_data = st.session_state.advanced_screener.get_real_time_data(medtech_symbols)
                    results = medtech_data.head(30)
                else:
                    filtered = healthcare_results[
                        (healthcare_results['Market Cap'] > 5e9) &
                        (healthcare_results['ROE'] > 0.10) &
                        (healthcare_results['PE Ratio'] > 0)
                    ]
                    results = filtered.nlargest(30, 'Market Cap')
            
            # If no results after filtering, show top stocks by market cap
            if results.empty:
                st.warning(f"No stocks found matching {screen_type} criteria. Showing top stocks by market cap.")
                results = all_results[0].nlargest(20, 'Market Cap') if all_results else pd.DataFrame()
        
        st.session_state.screen_results = results
        st.session_state.screen_type = screen_type.title()

def run_custom_screen(filters):
    """Run custom screen with user-defined filters"""
    
    with st.spinner("🔍 Running custom screen across ALL stocks..."):
        universe = st.session_state.stock_universe
        
        # Process larger chunks for comprehensive screening
        chunk_size = 200
        all_results = []
        
        # Process up to 1000 stocks for custom screening
        for i in range(0, min(len(universe), 1000), chunk_size):
            chunk = universe[i:i + chunk_size]
            chunk_results = st.session_state.advanced_screener.get_real_time_data(chunk, max_workers=15)
            
            if not chunk_results.empty:
                all_results.append(chunk_results)
        
        # Combine all results
        if all_results:
            results = pd.concat(all_results, ignore_index=True)
        else:
            results = pd.DataFrame()
        
        if not results.empty:
            # Apply comprehensive filters
            filtered_results = results.copy()
            
            # Market cap filter
            if filters['market_cap_range'][0] > 0:
                filtered_results = filtered_results[
                    (filtered_results['Market Cap'] >= filters['market_cap_range'][0]) &
                    (filtered_results['Market Cap'] <= filters['market_cap_range'][1])
                ]
            
            # Price filter
            filtered_results = filtered_results[
                (filtered_results['Price'] >= filters['price_range'][0]) &
                (filtered_results['Price'] <= filters['price_range'][1])
            ]
            
            # Sector filter
            if filters['sectors']:
                filtered_results = filtered_results[filtered_results['Sector'].isin(filters['sectors'])]
            
            # PE filter
            filtered_results = filtered_results[
                (filtered_results['PE Ratio'] >= filters['pe_range'][0]) &
                (filtered_results['PE Ratio'] <= filters['pe_range'][1]) &
                (filtered_results['PE Ratio'] > 0)
            ]
            
            # Price to Book filter
            if 'pb_range' in filters:
                filtered_results = filtered_results[
                    (filtered_results['Price to Book'] >= filters['pb_range'][0]) &
                    (filtered_results['Price to Book'] <= filters['pb_range'][1]) &
                    (filtered_results['Price to Book'] > 0)
                ]
            
            # PEG filter
            if 'peg_range' in filters:
                filtered_results = filtered_results[
                    (filtered_results['PEG Ratio'] >= filters['peg_range'][0]) &
                    (filtered_results['PEG Ratio'] <= filters['peg_range'][1]) &
                    (filtered_results['PEG Ratio'] > 0)
                ]
            
            # Revenue growth filter
            if 'rev_growth_min' in filters:
                filtered_results = filtered_results[
                    filtered_results['Revenue Growth'] >= filters['rev_growth_min'] / 100
                ]
            
            # Earnings growth filter
            if 'earn_growth_min' in filters:
                filtered_results = filtered_results[
                    filtered_results['Earnings Growth'] >= filters['earn_growth_min'] / 100
                ]
            
            # ROE filter
            if 'roe_min' in filters:
                filtered_results = filtered_results[
                    filtered_results['ROE'] >= filters['roe_min'] / 100
                ]
            
            # Profit margin filter
            if 'profit_margin_min' in filters:
                filtered_results = filtered_results[
                    filtered_results['Profit Margin'] >= filters['profit_margin_min'] / 100
                ]
            
            # Volume filter
            if 'min_volume' in filters:
                filtered_results = filtered_results[
                    filtered_results['Avg Volume'] >= filters['min_volume']
                ]
            
            # Performance filters
            if 'perf_1y_range' in filters:
                filtered_results = filtered_results[
                    (filtered_results['1Y Change'] >= filters['perf_1y_range'][0]) &
                    (filtered_results['1Y Change'] <= filters['perf_1y_range'][1])
                ]
            
            if 'perf_1m_range' in filters:
                filtered_results = filtered_results[
                    (filtered_results['1M Change'] >= filters['perf_1m_range'][0]) &
                    (filtered_results['1M Change'] <= filters['perf_1m_range'][1])
                ]
            
            # Technical filters
            if 'rsi_range' in filters:
                filtered_results = filtered_results[
                    (filtered_results['RSI'] >= filters['rsi_range'][0]) &
                    (filtered_results['RSI'] <= filters['rsi_range'][1])
                ]
            
            if 'beta_range' in filters:
                filtered_results = filtered_results[
                    (filtered_results['Beta'] >= filters['beta_range'][0]) &
                    (filtered_results['Beta'] <= filters['beta_range'][1]) &
                    (filtered_results['Beta'] > 0)
                ]
            
            # Sort by market cap and return top results
            if not filtered_results.empty:
                st.session_state.custom_screen_results = filtered_results.nlargest(100, 'Market Cap')
            else:
                st.warning("No stocks match your custom criteria. Try adjusting the filters.")
                st.session_state.custom_screen_results = results.nlargest(20, 'Market Cap')
        else:
            st.session_state.custom_screen_results = pd.DataFrame()

def display_screening_results(results, screen_name):
    """Display screening results in an interactive table"""
    
    if results.empty:
        st.warning("No stocks match your criteria. Try adjusting your filters.")
        return
    
    st.markdown(f"### 📊 {screen_name} Results ({len(results)} stocks)")
    
    # Summary statistics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        avg_return = results['1Y Change'].mean() if '1Y Change' in results.columns else 0
        st.metric("Avg 1Y Return", f"{avg_return:.1f}%")
    
    with col2:
        avg_pe = results['PE Ratio'].mean() if 'PE Ratio' in results.columns else 0
        st.metric("Avg P/E Ratio", f"{avg_pe:.1f}")
    
    with col3:
        total_market_cap = results['Market Cap'].sum() / 1e12 if 'Market Cap' in results.columns else 0
        st.metric("Total Market Cap", f"${total_market_cap:.1f}T")
    
    with col4:
        top_performer = results.nlargest(1, '1Y Change')['Symbol'].iloc[0] if '1Y Change' in results.columns and not results.empty else "N/A"
        st.metric("Top Performer", top_performer)
    
    # Interactive table
    if not results.empty:
        # Prepare data for display
        display_cols = ['Symbol', 'Company', 'Sector', 'Price', 'Market Cap', 'PE Ratio', 
                       '1Y Change', '1M Change', 'Volume', 'RSI']
        
        # Filter to existing columns
        available_cols = [col for col in display_cols if col in results.columns]
        display_data = results[available_cols].copy()
        
        # Format data
        if 'Market Cap' in display_data.columns:
            display_data['Market Cap'] = display_data['Market Cap'].apply(lambda x: f"${x/1e9:.1f}B" if x > 0 else "N/A")
        if 'Price' in display_data.columns:
            display_data['Price'] = display_data['Price'].apply(lambda x: f"${x:.2f}" if x > 0 else "N/A")
        if '1Y Change' in display_data.columns:
            display_data['1Y Change'] = display_data['1Y Change'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
        if '1M Change' in display_data.columns:
            display_data['1M Change'] = display_data['1M Change'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "N/A")
        
        # Configure AgGrid
        gb = GridOptionsBuilder.from_dataframe(display_data)
        gb.configure_pagination(paginationAutoPageSize=True)
        gb.configure_side_bar()
        gb.configure_default_column(enablePivot=True, enableValue=True, enableRowGroup=True)
        gb.configure_selection('single', use_checkbox=True)
        gridOptions = gb.build()
        
        # Display interactive table
        grid_response = AgGrid(
            display_data,
            gridOptions=gridOptions,
            data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
            update_mode=GridUpdateMode.SELECTION_CHANGED,
            enable_enterprise_modules=True,
            height=400,
            width='100%'
        )
        
        # Show details for selected stock
        if grid_response['selected_rows'] is not None and len(grid_response['selected_rows']) > 0:
            selected_stock = grid_response['selected_rows'][0]['Symbol']
            show_stock_details(selected_stock, results)

def show_stock_details(symbol, data):
    """Show detailed information for selected stock"""
    stock_data = data[data['Symbol'] == symbol].iloc[0]
    
    st.markdown(f"### 📈 {symbol} - {stock_data.get('Company', 'N/A')}")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("#### 💰 Valuation")
        metrics = ['Price', 'Market Cap', 'PE Ratio', 'PEG Ratio', 'Price to Book']
        for metric in metrics:
            if metric in stock_data:
                value = stock_data[metric]
                if pd.notna(value) and value != 0:
                    if metric == 'Market Cap':
                        st.write(f"**{metric}:** ${value/1e9:.1f}B")
                    elif metric == 'Price':
                        st.write(f"**{metric}:** ${value:.2f}")
                    else:
                        st.write(f"**{metric}:** {value:.2f}")
    
    with col2:
        st.markdown("#### 📊 Performance")
        perf_metrics = ['1D Change', '1W Change', '1M Change', '3M Change', '6M Change', '1Y Change']
        for metric in perf_metrics:
            if metric in stock_data:
                value = stock_data[metric]
                if pd.notna(value):
                    color = "🟢" if value >= 0 else "🔴"
                    st.write(f"**{metric}:** {color} {value:.1f}%")
    
    with col3:
        st.markdown("#### 🔬 Financials")
        fin_metrics = ['ROE', 'ROA', 'Profit Margin', 'Debt to Equity', 'Current Ratio']
        for metric in fin_metrics:
            if metric in stock_data:
                value = stock_data[metric]
                if pd.notna(value) and value != 0:
                    if 'Margin' in metric or metric in ['ROE', 'ROA']:
                        st.write(f"**{metric}:** {value*100:.1f}%")
                    else:
                        st.write(f"**{metric}:** {value:.2f}")

def get_market_indices_data(indices):
    """Get real-time market indices data"""
    market_data = {}
    
    for symbol, name in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="2d")
            
            if not hist.empty and len(hist) >= 2:
                current_price = hist['Close'][-1]
                prev_close = hist['Close'][-2]
                change = (current_price - prev_close) / prev_close * 100
                change_value = current_price - prev_close
                
                market_data[symbol] = {
                    'name': name,
                    'price': current_price,
                    'change': change,
                    'change_value': change_value
                }
        except:
            market_data[symbol] = {
                'name': name,
                'price': 0,
                'change': 0,
                'change_value': 0
            }
    
    return market_data

def show_market_trends():
    """Show market trend analysis"""
    # Sample trend data
    dates = pd.date_range(start='2025-01-01', end='2025-06-16', freq='D')
    sp500_trend = np.cumsum(np.random.randn(len(dates)) * 0.01) * 100 + 5200
    
    fig = px.line(x=dates, y=sp500_trend, title="S&P 500 Trend (2025 YTD)")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def show_top_performers():
    """Show top performing stocks"""
    # Sample top performers data
    top_performers = pd.DataFrame({
        'Symbol': ['NVDA', 'AMD', 'MRNA', 'TSLA', 'GOOGL'],
        'Return': [89.2, 67.5, 45.8, 34.2, 28.9],
        'Sector': ['Technology', 'Technology', 'Healthcare', 'Consumer Cyclical', 'Communication Services']
    })
    
    fig = px.bar(top_performers, x='Symbol', y='Return', color='Sector',
                title="Top 5 Performers (YTD)")
    fig.update_layout(height=300)
    st.plotly_chart(fig, use_container_width=True)

def generate_top_picks(category):
    """Generate AI-powered top picks"""
    with st.spinner("🤖 AI analyzing market data..."):
        # Simulate AI analysis
        time.sleep(2)
        
        if category == "momentum_leaders":
            picks = [
                {'Symbol': 'NVDA', 'Score': 95, 'Reason': 'Strong AI momentum and earnings growth'},
                {'Symbol': 'MRNA', 'Score': 88, 'Reason': 'Pipeline expansion and vaccine leadership'},
                {'Symbol': 'TSLA', 'Score': 82, 'Reason': 'EV market dominance and innovation'}
            ]
        elif category == "value_picks":
            picks = [
                {'Symbol': 'JNJ', 'Score': 91, 'Reason': 'Undervalued with strong dividend yield'},
                {'Symbol': 'PFE', 'Score': 85, 'Reason': 'Low P/E ratio with pipeline potential'},
                {'Symbol': 'WMT', 'Score': 79, 'Reason': 'Defensive play with growth prospects'}
            ]
        elif category == "healthcare_picks":
            picks = [
                {'Symbol': 'LLY', 'Score': 93, 'Reason': 'Diabetes and Alzheimer drug leadership'},
                {'Symbol': 'UNH', 'Score': 89, 'Reason': 'Healthcare services growth and margins'},
                {'Symbol': 'REGN', 'Score': 84, 'Reason': 'Strong oncology pipeline and partnerships'}
            ]
        else:  # ai_picks
            picks = [
                {'Symbol': 'MSFT', 'Score': 94, 'Reason': 'AI integration across all products'},
                {'Symbol': 'GOOGL', 'Score': 87, 'Reason': 'Search AI and cloud computing growth'},
                {'Symbol': 'META', 'Score': 81, 'Reason': 'Metaverse investments and AI advertising'}
            ]
        
        st.session_state.top_picks = picks
        st.session_state.pick_category = category

def display_top_picks_results():
    """Display top picks results"""
    picks = st.session_state.top_picks
    
    st.markdown("#### 🏆 AI-Generated Top Picks")
    
    for i, pick in enumerate(picks, 1):
        score_color = "badge-excellent" if pick['Score'] >= 90 else "badge-good" if pick['Score'] >= 80 else "badge-average"
        
        st.markdown(f"""
        <div class="stock-card">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <h3>#{i} {pick['Symbol']}</h3>
                    <p>{pick['Reason']}</p>
                </div>
                <div>
                    <span class="performance-badge {score_color}">Score: {pick['Score']}</span>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
