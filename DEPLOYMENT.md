# 🚀 Deployment Guide - Healthcare Stock Analyzer

This guide will help you deploy the Healthcare Stock Analyzer to GitHub and Streamlit Cloud.

## 📋 Prerequisites

- GitHub account
- Git installed on your local machine
- Python 3.8+ (for local testing)

## 🗂️ Step 1: Prepare for GitHub

### 1.1 Initialize Git Repository (if not already done)

```bash
cd /path/to/healthcare-stock-analyzer
git init
git add .
git commit -m "Initial commit: Healthcare Stock Analyzer v2025.6"
```

### 1.2 Create GitHub Repository

1. Go to [GitHub.com](https://github.com)
2. Click "New repository"
3. Name it: `healthcare-stock-analyzer`
4. Description: "AI-powered healthcare investment intelligence platform"
5. Make it **Public** (required for free Streamlit Cloud)
6. Don't initialize with README (we already have one)
7. Click "Create repository"

### 1.3 Connect Local Repository to GitHub

```bash
git remote add origin https://github.com/YOUR_USERNAME/healthcare-stock-analyzer.git
git branch -M main
git push -u origin main
```

Replace `YOUR_USERNAME` with your actual GitHub username.

## 🌐 Step 2: Deploy to Streamlit Cloud

### 2.1 Access Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Sign in with your GitHub account
3. Click "New app"

### 2.2 Configure Deployment

**Repository Settings:**
- **Repository:** `YOUR_USERNAME/healthcare-stock-analyzer`
- **Branch:** `main`
- **Main file path:** `medequity_main.py`

**Advanced Settings (Optional):**
- **Python version:** `3.9`
- **App URL:** `healthcare-analyzer-YOUR_USERNAME` (customize as desired)

### 2.3 Deploy

1. Click "Deploy!"
2. Wait for the build process (usually 2-5 minutes)
3. Your app will be live at: `https://healthcare-analyzer-YOUR_USERNAME.streamlit.app`

## ✅ Step 3: Verification

### 3.1 Test Core Functionality

Visit your deployed app and test:

- [ ] Home page loads correctly
- [ ] Enter a ticker symbol (e.g., "PFE")
- [ ] Click "Analyze Now"
- [ ] Verify all 6 pages are accessible:
  - [ ] 📊 Company Deep Dive
  - [ ] 🔍 Healthcare Screener
  - [ ] 💊 Clinical Pipeline
  - [ ] 📈 Portfolio Tracker
  - [ ] 🏥 FDA Calendar
  - [ ] 💰 M&A Comparisons

### 3.2 Performance Check

- Page load time < 5 seconds
- Charts render properly
- No error messages in the interface
- Mobile responsiveness

## 🔧 Step 4: Custom Domain (Optional)

### 4.1 Streamlit Cloud Custom Domain

1. Go to your app dashboard
2. Click "Settings"
3. In "General" tab, find "Custom domain"
4. Enter your domain (e.g., `healthcareanalyzer.com`)
5. Follow DNS configuration instructions

### 4.2 DNS Configuration

Add a CNAME record:
```
Type: CNAME
Name: www (or your subdomain)
Value: your-app-name.streamlit.app
```

## 🚀 Step 5: Production Optimization

### 5.1 Environment Variables

If you need to add API keys or secrets:

1. In Streamlit Cloud dashboard, go to "Settings"
2. Click "Secrets"
3. Add your secrets in TOML format:

```toml
[api_keys]
news_api = "your_api_key_here"
alpha_vantage = "your_api_key_here"
```

### 5.2 Performance Monitoring

- Monitor app usage in Streamlit Cloud dashboard
- Check logs for any errors
- Review resource usage

## 🔄 Step 6: Continuous Deployment

### 6.1 Automatic Updates

Once connected, any push to your main branch will automatically trigger a redeployment:

```bash
# Make changes to your code
git add .
git commit -m "Feature: Added new analysis metrics"
git push origin main
```

The app will automatically update within 2-3 minutes.

### 6.2 Version Management

Use semantic versioning for releases:

```bash
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin v1.0.0
```

## 📊 Step 7: Analytics & Monitoring

### 7.1 Streamlit Cloud Analytics

- View app usage statistics
- Monitor performance metrics
- Track user engagement

### 7.2 Google Analytics (Optional)

Add to your `medequity_main.py`:

```python
# Add to the main page
st.markdown("""
<script async src="https://www.googletagmanager.com/gtag/js?id=GA_MEASUREMENT_ID"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());
  gtag('config', 'GA_MEASUREMENT_ID');
</script>
""", unsafe_allow_html=True)
```

## 🛠️ Troubleshooting

### Common Issues & Solutions

**Issue 1: Import Errors**
```
Solution: Ensure all dependencies are in requirements.txt with correct versions
```

**Issue 2: Memory Errors**
```
Solution: Optimize data loading, use caching, reduce concurrent operations
```

**Issue 3: Slow Loading**
```
Solution: Implement st.cache_data for expensive operations
```

**Issue 4: API Rate Limits**
```
Solution: Add error handling, implement retry logic with exponential backoff
```

### Debug Mode

Run locally with debug info:
```bash
streamlit run medequity_main.py --logger.level=debug
```

## 📞 Support

### Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [Streamlit Community Forum](https://discuss.streamlit.io)
- [GitHub Issues](https://github.com/YOUR_USERNAME/healthcare-stock-analyzer/issues)

### Contact

- 📧 Support: Create an issue on GitHub
- 💬 Community: Join Streamlit forums
- 📖 Docs: Check README.md for detailed information

---

## 🎉 Congratulations!

Your Healthcare Stock Analyzer is now live and accessible worldwide! 

**🔗 Share your app:**
- Direct link: `https://your-app-name.streamlit.app`
- Social media: Use the built-in share button
- Professional networks: Include in your portfolio

**⭐ Don't forget to:**
- Star the repository if you found it useful
- Share with the community
- Contribute improvements via pull requests

---

*Happy analyzing! 📊💊🏥* 