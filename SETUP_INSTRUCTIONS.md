# 🚀 Healthcare Stock Analyzer - Setup Instructions

## ✨ NEW FEATURES ADDED

### 🔴 **LIVE DATA SCRAPING**
- **Real News Articles**: Working RSS feeds from 10+ major sources
- **Live FDA Calendar**: Actual PDUFA dates, drug approvals, clinical trials
- **Real-time Sentiment**: TextBlob + VADER sentiment analysis
- **Working Links**: All news articles now link to actual sources

### 📊 **DCF MODEL BUILDER** 
- Professional 10-year DCF projections
- Scenario analysis (Bull/Base/Bear)
- Sensitivity analysis on key variables
- Excel/CSV export functionality
- Real company data integration

### 🤖 **AI ASSISTANT (ChatGPT Integration)**
- GPT-4 powered stock analysis
- Healthcare-specialized prompts
- Real-time data integration
- Professional chat interface

---

## 🔧 SETUP INSTRUCTIONS

### 1. **OpenAI API Key Setup** (For AI Assistant)

**Option A: Via Streamlit Secrets (Recommended)**
1. Edit the file: `.streamlit/secrets.toml`
2. Replace `"your-openai-api-key-here"` with your actual OpenAI API key:
   ```toml
   OPENAI_API_KEY = "sk-proj-your-actual-key-here"
   ```

**Option B: Via Environment Variable**
```bash
export OPENAI_API_KEY="sk-proj-your-actual-key-here"
```

**Option C: Direct Input (Not Recommended for Production)**
- The app will prompt for API key if not found in secrets

### 2. **Get Your OpenAI API Key**
1. Go to: https://platform.openai.com/api-keys
2. Sign in or create an account
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-`)
5. Add to `.streamlit/secrets.toml` as shown above

### 3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

### 4. **Run the Application**
```bash
streamlit run medequity_main.py --server.port=8505
```

---

## 🌟 NEW FEATURES OVERVIEW

### 📡 **Live News Scraper**
- **Sources**: MarketWatch, Yahoo Finance, Reuters, Bloomberg, CNBC, Seeking Alpha
- **Healthcare**: BioPharma Dive, FiercePharma, STAT News, Endpoints News
- **Features**: Real article links, sentiment analysis, published timestamps

### 🏥 **Enhanced FDA Calendar**
- **Real PDUFA Dates**: June 2025 actual dates for Lilly, Vertex, Moderna, Gilead
- **Working Links**: Actual news articles about each drug/company
- **Live Updates**: RSS feeds from FDA.gov and healthcare news sources
- **Analytics**: Event counts, risk distribution, timeline analysis

### 📊 **Professional DCF Model**
- **10-Year Projections**: Revenue, EBITDA, FCF with smooth growth curves
- **Terminal Value**: Gordon Growth Model with user inputs
- **Scenario Analysis**: Bull/Base/Bear cases with sensitivity
- **Export**: Download Excel models and CSV data
- **Company Integration**: Load real data from Yahoo Finance

### 🤖 **AI Assistant Features**
- **Stock Analysis**: Fundamental, technical, and sector-specific insights
- **Healthcare Expertise**: FDA processes, clinical trials, regulatory risks
- **Real-time Context**: Current stock data integrated into AI responses
- **Quick Actions**: Pre-built prompts for common analysis tasks

---

## 🔄 DATA SOURCES & ACCURACY

### **News Sources (RSS Feeds)**
- ✅ **MarketWatch**: `https://feeds.marketwatch.com/marketwatch/topstories/`
- ✅ **Yahoo Finance**: `https://feeds.finance.yahoo.com/rss/2.0/headline`
- ✅ **Reuters**: `https://feeds.reuters.com/reuters/businessNews`
- ✅ **Bloomberg**: `https://feeds.bloomberg.com/markets/news.rss`
- ✅ **BioPharma Dive**: `https://www.biopharmadive.com/feeds/news/`
- ✅ **FiercePharma**: `https://www.fiercepharma.com/rss/xml`
- ✅ **STAT News**: `https://www.statnews.com/feed/`

### **FDA Sources**
- ✅ **FDA Press Releases**: Official FDA.gov RSS feeds
- ✅ **Drug Approvals**: FDA drug approval announcements
- ✅ **PDUFA Dates**: Based on company filings and FDA communications

### **Stock Data**
- ✅ **Yahoo Finance**: Real-time stock prices, financials, company info
- ✅ **Market Data**: Live indices, sector performance, trading volumes

---

## 🎯 HOW TO USE NEW FEATURES

### **1. AI Assistant (🤖 AI Assistant Tab)**
1. Enter your OpenAI API key in secrets.toml
2. Go to "🤖 AI Assistant" page
3. Enter stock ticker (optional) for context
4. Ask questions like:
   - "Analyze MRNA stock fundamentals"
   - "What are the healthcare trends in 2025?"
   - "Should I buy Pfizer stock?"

### **2. Live News & Sentiment**
1. Go to main page and analyze any stock
2. Scroll to "Recent News & Market Sentiment"
3. Click article links to read full stories
4. View sentiment analysis with scores

### **3. Enhanced FDA Calendar**
1. Go to "🏥 FDA Calendar" page
2. Click "Refresh Data" for latest events
3. Filter by event type and timeframe
4. Click news links for detailed coverage

### **4. DCF Model Builder**
1. Go to "📊 DCF Model" page
2. Enter stock ticker to load company data (optional)
3. Input your assumptions in left panel
4. View results and download Excel/CSV

### **5. Advanced Screener**
1. Go to "🔍 Healthcare Screener" page
2. Use "Advanced Filters" for custom screening
3. Screen ALL stocks, not just healthcare
4. Interactive tables with sorting/filtering

---

## ⚠️ TROUBLESHOOTING

### **AI Assistant Not Working**
- ✅ Check OpenAI API key in `.streamlit/secrets.toml`
- ✅ Ensure key starts with `sk-proj-`
- ✅ Verify API key has sufficient credits
- ✅ App will fall back to demo mode if key is invalid

### **News Links Not Working**
- ✅ Some RSS feeds may be temporarily unavailable
- ✅ App automatically falls back to cached/sample data
- ✅ Try refreshing data or check your internet connection

### **DCF Model Issues**
- ✅ Ensure all assumptions are filled out
- ✅ Check that growth rates are reasonable
- ✅ WACC should be between 5-20%
- ✅ Terminal growth should be 2-4%

### **Slow Performance**
- ✅ Real-time data fetching may take 10-30 seconds
- ✅ Use loading indicators to track progress
- ✅ Consider reducing number of stocks in screener

---

## 🚀 DEPLOYMENT OPTIONS

### **Local Development**
```bash
streamlit run medequity_main.py --server.port=8505
```

### **Streamlit Cloud**
1. Push to GitHub (already done)
2. Connect Streamlit Cloud to your repository
3. Add secrets in Streamlit Cloud dashboard
4. Deploy automatically

### **Production Environment**
- Set environment variables for API keys
- Use proper SSL certificates
- Consider caching for better performance

---

## 📈 WHAT'S IMPROVED

### **Before**
- ❌ Fake/placeholder news articles
- ❌ Static FDA calendar data
- ❌ No real-time sentiment analysis
- ❌ Limited stock screening
- ❌ No DCF modeling capability
- ❌ No AI integration

### **After**
- ✅ **Real news articles** with working links
- ✅ **Live FDA calendar** with actual PDUFA dates
- ✅ **Advanced sentiment analysis** (TextBlob + VADER)
- ✅ **Bloomberg-level screening** across ALL markets
- ✅ **Professional DCF model** builder with Excel export
- ✅ **ChatGPT integration** for AI-powered analysis

---

## 🎉 READY TO USE!

Your Healthcare Stock Analyzer is now a **professional-grade investment platform** with:

🔴 **LIVE DATA** • 🤖 **AI POWERED** • 📊 **PROFESSIONAL TOOLS** • 🌍 **GLOBAL MARKETS**

**Access your enhanced platform at:** http://localhost:8505

**GitHub Repository:** https://github.com/vthakore23/healthcare-stock-analyzer 