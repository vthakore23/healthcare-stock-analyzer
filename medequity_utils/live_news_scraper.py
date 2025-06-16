import requests
import feedparser
import pandas as pd
from datetime import datetime, timedelta
import time
from urllib.parse import quote
import json
import re

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = True
except ImportError:
    VADER_AVAILABLE = False

class LiveNewsScaper:
    """Real-time news scraper for stock-related news with sentiment analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Initialize sentiment analyzer if available
        if VADER_AVAILABLE:
            self.analyzer = SentimentIntensityAnalyzer()
        else:
            self.analyzer = None
        
        # News source RSS feeds
        self.news_sources = {
            'MarketWatch': 'https://feeds.marketwatch.com/marketwatch/topstories/',
            'Yahoo Finance': 'https://feeds.finance.yahoo.com/rss/2.0/headline',
            'Reuters Business': 'https://feeds.reuters.com/reuters/businessNews',
            'Bloomberg': 'https://feeds.bloomberg.com/markets/news.rss',
            'CNBC': 'https://search.cnbc.com/rs/search/combinedcms/view.xml?partnerId=wrss01&id=10000664',
            'Seeking Alpha': 'https://seekingalpha.com/feed.xml'
        }
        
        # Healthcare specific sources
        self.healthcare_sources = {
            'BioPharma Dive': 'https://www.biopharmadive.com/feeds/news/',
            'FiercePharma': 'https://www.fiercepharma.com/rss/xml',
            'STAT News': 'https://www.statnews.com/feed/',
            'Endpoints News': 'https://endpts.com/feed/',
            'Pharmaceutical Executive': 'https://www.pharmexec.com/rss/all'
        }
    
    def get_stock_news(self, ticker: str, max_articles: int = 10):
        """Get real-time news for a specific stock ticker"""
        
        all_articles = []
        
        # Search general financial news
        general_articles = self._search_rss_feeds(ticker, self.news_sources, max_articles//2)
        all_articles.extend(general_articles)
        
        # Search healthcare-specific news if healthcare stock
        healthcare_articles = self._search_rss_feeds(ticker, self.healthcare_sources, max_articles//2)
        all_articles.extend(healthcare_articles)
        
        # Get additional news from web search
        web_articles = self._search_web_news(ticker, max_articles//3)
        all_articles.extend(web_articles)
        
        # Sort by date and limit results
        all_articles = sorted(all_articles, key=lambda x: x.get('published_date', datetime.now()), reverse=True)
        all_articles = all_articles[:max_articles]
        
        # Analyze sentiment for each article
        for article in all_articles:
            article.update(self._analyze_sentiment(article.get('title', '')))
        
        return all_articles
    
    def _search_rss_feeds(self, ticker: str, sources: dict, max_per_source: int = 3):
        """Search RSS feeds for ticker mentions with improved error handling"""
        
        articles = []
        
        for source_name, rss_url in sources.items():
            try:
                # Add timeout and proper headers for RSS parsing
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/rss+xml, application/xml, text/xml'
                }
                
                # Parse RSS feed with timeout
                response = requests.get(rss_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                else:
                    # Skip this source if we get errors
                    continue
                
                if not hasattr(feed, 'entries') or len(feed.entries) == 0:
                    continue
                
                for entry in feed.entries[:20]:  # Check recent entries
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    
                    # Check if ticker is mentioned (case insensitive, broader matching)
                    if self._contains_ticker(title + ' ' + summary, ticker):
                        
                        # Extract published date
                        published_date = self._parse_date(entry.get('published'))
                        
                        # Clean up the URL
                        article_url = entry.get('link', '#')
                        if article_url.startswith('http'):
                            # URL is valid
                            pass
                        else:
                            # Create a fallback URL
                            article_url = f"https://www.google.com/search?q={quote(ticker + ' ' + title)}"
                        
                        article = {
                            'title': title,
                            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                            'url': article_url,
                            'source': source_name,
                            'published': self._format_time_ago(published_date),
                            'published_date': published_date,
                            'ticker': ticker
                        }
                        
                        articles.append(article)
                        
                        if len(articles) >= max_per_source:
                            break
                
            except Exception as e:
                # If RSS feed fails, create a fallback search link
                fallback_url = f"https://www.google.com/search?q={quote(ticker + ' stock news ' + source_name)}"
                fallback_article = {
                    'title': f"Search {ticker} news on {source_name}",
                    'summary': f"Click to search for latest {ticker} news on {source_name}",
                    'url': fallback_url,
                    'source': source_name,
                    'published': 'Recently',
                    'published_date': datetime.now(),
                    'ticker': ticker
                }
                articles.append(fallback_article)
                continue
        
        return articles
    
    def _search_web_news(self, ticker: str, max_articles: int = 5):
        """Search web for additional news articles with fallback options"""
        
        articles = []
        
        # Create reliable fallback articles with working search links
        fallback_articles = [
            {
                'title': f'{ticker} Latest Financial News',
                'summary': f'Search for the latest financial news and analysis for {ticker}',
                'url': f'https://www.google.com/search?q={quote(ticker + " stock news financial")}',
                'source': 'Financial Search',
                'published': 'Available',
                'published_date': datetime.now(),
                'ticker': ticker
            },
            {
                'title': f'{ticker} Earnings and Analysis',
                'summary': f'Find earnings reports, analyst ratings and market analysis for {ticker}',
                'url': f'https://www.google.com/search?q={quote(ticker + " earnings analysis")}',
                'source': 'Market Analysis',
                'published': 'Available',
                'published_date': datetime.now(),
                'ticker': ticker
            },
            {
                'title': f'{ticker} News on Yahoo Finance',
                'summary': f'View the latest news and updates for {ticker} on Yahoo Finance',
                'url': f'https://finance.yahoo.com/quote/{ticker}/news',
                'source': 'Yahoo Finance',
                'published': 'Available',
                'published_date': datetime.now(),
                'ticker': ticker
            },
            {
                'title': f'{ticker} MarketWatch Coverage',
                'summary': f'Read MarketWatch coverage and analysis for {ticker}',
                'url': f'https://www.marketwatch.com/investing/stock/{ticker}',
                'source': 'MarketWatch',
                'published': 'Available',
                'published_date': datetime.now(),
                'ticker': ticker
            }
        ]
        
        try:
            # Try Google News RSS first
            query = f"{ticker} stock news"
            google_news_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
            
            response = requests.get(google_news_url, timeout=10)
            if response.status_code == 200:
                feed = feedparser.parse(response.content)
                
                for entry in feed.entries[:max_articles]:
                    published_date = self._parse_date(entry.get('published'))
                    
                    article = {
                        'title': entry.get('title', ''),
                        'summary': 'Google News aggregated content',
                        'url': entry.get('link', f'https://www.google.com/search?q={quote(ticker + " news")}'),
                        'source': 'Google News',
                        'published': self._format_time_ago(published_date),
                        'published_date': published_date,
                        'ticker': ticker
                    }
                    
                    articles.append(article)
            
            # If we got articles from Google News, return them
            if articles:
                return articles
        
        except Exception as e:
            pass  # Fall through to fallback
        
        # Return fallback articles with working links
        return fallback_articles[:max_articles]
    
    def _contains_ticker(self, text: str, ticker: str) -> bool:
        """Check if text contains the ticker symbol with broader matching"""
        
        text = text.lower()
        ticker_lower = ticker.lower()
        
        # Direct ticker match
        if ticker_lower in text:
            return True
        
        # Clean ticker (remove common suffixes)
        clean_ticker = ticker.replace('-', '').replace('.', '').lower()
        
        # Check for ticker mentions (case insensitive, word boundaries)
        pattern = r'\b' + re.escape(clean_ticker) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            return True
        
        # Company name mapping for common tickers
        company_names = {
            'mrna': ['moderna'],
            'pfe': ['pfizer'],
            'jnj': ['johnson', 'j&j'],
            'lly': ['lilly', 'eli lilly'],
            'abbv': ['abbvie'],
            'regn': ['regeneron'],
            'vrtx': ['vertex'],
            'gild': ['gilead'],
            'biib': ['biogen'],
            'amgn': ['amgen'],
            'bntx': ['biontech'],
            'nvda': ['nvidia'],
            'tsla': ['tesla'],
            'aapl': ['apple'],
            'msft': ['microsoft'],
            'googl': ['google', 'alphabet'],
            'amzn': ['amazon'],
            'meta': ['facebook', 'meta']
        }
        
        # Check company name matches
        if ticker_lower in company_names:
            for company_name in company_names[ticker_lower]:
                if company_name in text:
                    return True
        
        return False
    
    def _parse_date(self, date_str):
        """Parse various date formats to datetime"""
        
        if not date_str:
            return datetime.now()
        
        try:
            # Try different date formats
            formats = [
                "%a, %d %b %Y %H:%M:%S %Z",
                "%a, %d %b %Y %H:%M:%S %z",
                "%Y-%m-%dT%H:%M:%S%z",
                "%Y-%m-%d %H:%M:%S",
                "%a, %d %b %Y %H:%M:%S"
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # If all else fails, return current time
            return datetime.now()
            
        except Exception:
            return datetime.now()
    
    def _format_time_ago(self, published_date):
        """Format time difference as human readable"""
        
        try:
            now = datetime.now()
            if published_date.tzinfo:
                # Handle timezone-aware dates
                published_date = published_date.replace(tzinfo=None)
            
            diff = now - published_date
            
            if diff.days > 0:
                return f"{diff.days} day{'s' if diff.days > 1 else ''} ago"
            elif diff.seconds > 3600:
                hours = diff.seconds // 3600
                return f"{hours} hour{'s' if hours > 1 else ''} ago"
            elif diff.seconds > 60:
                minutes = diff.seconds // 60
                return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
            else:
                return "Just now"
                
        except Exception:
            return "Recently"
    
    def _analyze_sentiment(self, text: str):
        """Analyze sentiment of text using multiple methods"""
        
        try:
            textblob_polarity = 0.0
            vader_compound = 0.0
            
            # TextBlob analysis
            if TEXTBLOB_AVAILABLE:
                try:
                    blob = TextBlob(text)
                    textblob_polarity = blob.sentiment.polarity
                except Exception:
                    textblob_polarity = 0.0
            
            # VADER analysis
            if VADER_AVAILABLE and self.analyzer:
                try:
                    vader_scores = self.analyzer.polarity_scores(text)
                    vader_compound = vader_scores['compound']
                except Exception:
                    vader_compound = 0.0
            
            # Combine scores or use basic keyword analysis
            if TEXTBLOB_AVAILABLE or VADER_AVAILABLE:
                combined_score = (textblob_polarity + vader_compound) / 2
            else:
                # Basic keyword-based sentiment analysis
                combined_score = self._basic_sentiment_analysis(text)
            
            # Classify sentiment
            if combined_score > 0.1:
                sentiment_label = 'Positive'
            elif combined_score < -0.1:
                sentiment_label = 'Negative'
            else:
                sentiment_label = 'Neutral'
            
            return {
                'sentiment_score': combined_score,
                'sentiment_label': sentiment_label,
                'textblob_polarity': textblob_polarity,
                'vader_compound': vader_compound
            }
            
        except Exception as e:
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'Neutral',
                'textblob_polarity': 0.0,
                'vader_compound': 0.0
            }
    
    def _basic_sentiment_analysis(self, text: str):
        """Basic sentiment analysis using keyword matching"""
        
        text = text.lower()
        
        positive_words = [
            'approval', 'approved', 'breakthrough', 'positive', 'success', 'successful', 
            'growth', 'profit', 'gains', 'rise', 'soar', 'beat', 'exceeds', 'strong',
            'upgrade', 'bullish', 'optimistic', 'innovation', 'advance', 'promising'
        ]
        
        negative_words = [
            'rejection', 'rejected', 'decline', 'fall', 'drop', 'loss', 'loses',
            'weak', 'concern', 'worry', 'risk', 'warning', 'alert', 'downgrade',
            'bearish', 'pessimistic', 'failure', 'delay', 'suspended', 'halt'
        ]
        
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        if positive_count > negative_count:
            return 0.3  # Positive
        elif negative_count > positive_count:
            return -0.3  # Negative
        else:
            return 0.0  # Neutral
    
    def get_general_market_news(self, max_articles: int = 15):
        """Get general market news without ticker filtering"""
        
        articles = []
        
        # Get from major financial news sources with better error handling
        for source_name, rss_url in list(self.news_sources.items())[:3]:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/rss+xml, application/xml, text/xml'
                }
                
                response = requests.get(rss_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    feed = feedparser.parse(response.content)
                    
                    if hasattr(feed, 'entries') and len(feed.entries) > 0:
                        for entry in feed.entries[:5]:
                            published_date = self._parse_date(entry.get('published'))
                            
                            # Clean up the URL
                            article_url = entry.get('link', '#')
                            if not article_url.startswith('http'):
                                article_url = f"https://www.google.com/search?q={quote(entry.get('title', ''))}"
                            
                            article = {
                                'title': entry.get('title', ''),
                                'summary': entry.get('summary', '')[:200] + '...',
                                'url': article_url,
                                'source': source_name,
                                'published': self._format_time_ago(published_date),
                                'published_date': published_date
                            }
                            
                            # Add sentiment analysis
                            article.update(self._analyze_sentiment(article['title']))
                            
                            articles.append(article)
                    
            except Exception as e:
                continue
        
        # If we don't have enough articles, add fallback articles
        if len(articles) < 5:
            fallback_articles = self._get_fallback_general_news()
            articles.extend(fallback_articles)
        
        # Sort by date and return recent articles
        articles = sorted(articles, key=lambda x: x.get('published_date', datetime.now()), reverse=True)
        return articles[:max_articles]
    
    def _get_fallback_general_news(self):
        """Get fallback general market news articles with working links"""
        
        fallback_articles = []
        
        news_items = [
            {
                'title': 'Market Overview - Real-time Financial Data',
                'summary': 'Get comprehensive market overview including stock prices, indices, and market trends',
                'url': 'https://finance.yahoo.com/markets/',
                'source': 'Yahoo Finance'
            },
            {
                'title': 'Healthcare Sector News & Analysis',
                'summary': 'Latest news and analysis covering the healthcare and biotech sectors',
                'url': 'https://www.google.com/search?q=healthcare+biotech+stock+news',
                'source': 'Healthcare News'
            },
            {
                'title': 'Pharmaceutical Industry Updates',
                'summary': 'Breaking news on drug approvals, clinical trials, and pharmaceutical companies',
                'url': 'https://www.biopharmadive.com/',
                'source': 'BioPharma Dive'
            },
            {
                'title': 'FDA Drug Approvals & Regulatory News',
                'summary': 'Latest FDA announcements, drug approvals, and regulatory developments',
                'url': 'https://www.fda.gov/news-events/newsroom/press-announcements',
                'source': 'FDA Newsroom'
            },
            {
                'title': 'Biotech Stock Market Analysis',
                'summary': 'Professional analysis and insights on biotech stock performance and trends',
                'url': 'https://www.nasdaq.com/market-activity/stocks/screener',
                'source': 'NASDAQ'
            }
        ]
        
        for item in news_items:
            article = {
                'title': item['title'],
                'summary': item['summary'],
                'url': item['url'],
                'source': item['source'],
                'published': 'Live',
                'published_date': datetime.now()
            }
            
            # Add sentiment analysis
            article.update(self._analyze_sentiment(article['title']))
            
            fallback_articles.append(article)
        
        return fallback_articles 