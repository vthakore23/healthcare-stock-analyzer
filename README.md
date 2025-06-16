# 🏥 Healthcare Stock Analyzer

A powerful AI-driven healthcare investment intelligence platform built with Streamlit, featuring real-time data analysis, clinical pipeline tracking, and comprehensive M&A comparisons.

## 🌟 Features

### 📊 Company Deep Dive
- Comprehensive financial analysis and metrics
- Real-time stock data and charts
- Healthcare Investment Score calculation
- Business description and competitive analysis

### 🔍 Healthcare Screener
- Multi-criteria stock screening
- Customizable filters and metrics
- Real-time market data integration
- Export capabilities

### 💊 Clinical Pipeline Analysis
- Real-time pipeline data scraping
- Phase-by-phase drug analysis
- Therapeutic area breakdown
- R&D intensity calculations

### 📈 Portfolio Tracker
- Track multiple healthcare stocks
- Performance analytics
- Risk assessment tools
- Portfolio optimization insights

### 🏥 FDA Calendar
- Drug approval timelines
- FDA meeting schedules
- Regulatory milestone tracking
- Interactive timeline visualization

### 💰 M&A Comparisons
- Recent healthcare M&A deals (updated June 2025)
- Premium analysis and benchmarking
- Deal valuation metrics
- Market trend analysis

## 🚀 Live Demo

**🔗 [View Live Application](https://healthcare-stock-analyzer.streamlit.app/)**

## 📋 Requirements

- Python 3.8+
- Streamlit 1.28+
- See `requirements.txt` for complete dependencies

## 🛠️ Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/healthcare-stock-analyzer.git
   cd healthcare-stock-analyzer
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   streamlit run medequity_main.py
   ```

## 🌐 Deployment

### Streamlit Cloud
1. Fork this repository
2. Connect your GitHub account to [Streamlit Cloud](https://share.streamlit.io/)
3. Deploy directly from your GitHub repository
4. The app will be live at `https://yourapp.streamlit.app/`

### Local Development
```bash
# Clone and setup
git clone https://github.com/yourusername/healthcare-stock-analyzer.git
cd healthcare-stock-analyzer
pip install -r requirements.txt

# Run locally
streamlit run medequity_main.py --server.port=8501
```

## 🎨 UI Features

- **Modern Glassmorphism Design**: Beautiful, translucent UI elements
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Interactive Charts**: Powered by Plotly for rich visualizations
- **Real-time Updates**: Live data feeds and automatic refreshing
- **Professional Color Scheme**: Healthcare-focused design language

## 📊 Data Sources

- **Yahoo Finance**: Real-time stock data and financials
- **SEC Filings**: Company business descriptions and R&D data
- **Market Data**: Live trading information and metrics
- **Healthcare Databases**: Pipeline and clinical trial information

## 🔧 Architecture

```
healthcare-stock-analyzer/
├── medequity_main.py           # Main application entry point
├── pages/                      # Streamlit pages
│   ├── 1_📊_Company_Deep_Dive.py
│   ├── 2_🔍_Healthcare_Screener.py
│   ├── 3_💊_Clinical_Pipeline.py
│   ├── 4_📈_Portfolio_Tracker.py
│   ├── 5_🏥_FDA_Calendar.py
│   └── 6_💰_MA_Comps.py
├── medequity_utils/           # Utility modules
│   └── dynamic_scraper.py     # Data scraping utilities
├── .streamlit/                # Streamlit configuration
│   └── config.toml
├── requirements.txt           # Python dependencies
└── README.md                 # Project documentation
```

## 📈 Data Currency

All data is current as of **June 2025**, including:
- ✅ Latest M&A deals and valuations
- ✅ Current market metrics and benchmarks
- ✅ Real-time stock prices and fundamentals
- ✅ Updated regulatory calendars and timelines

## 🔒 Security & Privacy

- No user data collection
- All data sourced from public APIs
- Secure HTTPS connections
- No sensitive information stored

## 📱 Mobile Responsive

The application is fully responsive and optimized for:
- 📱 Mobile devices (iOS/Android)
- 💻 Desktop computers
- 📟 Tablet devices
- 🖥️ Large displays

