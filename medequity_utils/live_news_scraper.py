import requests
import feedparser
import pandas as pd
from datetime import datetime, timedelta
import time
from urllib.parse import quote
import json
import re
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

class LiveNewsScaper:
    """Real-time news scraper for stock-related news with sentiment analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.analyzer = SentimentIntensityAnalyzer()
        
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
        """Search RSS feeds for ticker mentions"""
        
        articles = []
        
        for source_name, rss_url in sources.items():
            try:
                # Parse RSS feed
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:20]:  # Check recent entries
                    title = entry.get('title', '')
                    summary = entry.get('summary', '')
                    
                    # Check if ticker is mentioned
                    if self._contains_ticker(title + ' ' + summary, ticker):
                        
                        # Extract published date
                        published_date = self._parse_date(entry.get('published'))
                        
                        article = {
                            'title': title,
                            'summary': summary[:200] + '...' if len(summary) > 200 else summary,
                            'url': entry.get('link', '#'),
                            'source': source_name,
                            'published': self._format_time_ago(published_date),
                            'published_date': published_date,
                            'ticker': ticker
                        }
                        
                        articles.append(article)
                        
                        if len(articles) >= max_per_source:
                            break
                
            except Exception as e:
                print(f"Error fetching from {source_name}: {e}")
                continue
        
        return articles
    
    def _search_web_news(self, ticker: str, max_articles: int = 5):
        """Search web for additional news articles"""
        
        articles = []
        
        try:
            # Use Google News RSS (alternative approach)
            query = f"{ticker} stock news"
            google_news_url = f"https://news.google.com/rss/search?q={quote(query)}&hl=en-US&gl=US&ceid=US:en"
            
            feed = feedparser.parse(google_news_url)
            
            for entry in feed.entries[:max_articles]:
                
                published_date = self._parse_date(entry.get('published'))
                
                article = {
                    'title': entry.get('title', ''),
                    'summary': 'Google News aggregated content',
                    'url': entry.get('link', '#'),
                    'source': 'Google News',
                    'published': self._format_time_ago(published_date),
                    'published_date': published_date,
                    'ticker': ticker
                }
                
                articles.append(article)
        
        except Exception as e:
            print(f"Error fetching Google News: {e}")
        
        return articles
    
    def _contains_ticker(self, text: str, ticker: str) -> bool:
        """Check if text contains the ticker symbol"""
        
        # Clean ticker (remove common suffixes)
        clean_ticker = ticker.replace('-', '').replace('.', '')
        
        # Check for ticker mentions (case insensitive, word boundaries)
        pattern = r'\b' + re.escape(clean_ticker) + r'\b'
        
        return bool(re.search(pattern, text, re.IGNORECASE))
    
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
            # TextBlob analysis
            blob = TextBlob(text)
            textblob_polarity = blob.sentiment.polarity
            
            # VADER analysis
            vader_scores = self.analyzer.polarity_scores(text)
            vader_compound = vader_scores['compound']
            
            # Combine scores
            combined_score = (textblob_polarity + vader_compound) / 2
            
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
    
    def get_general_market_news(self, max_articles: int = 15):
        """Get general market news without ticker filtering"""
        
        articles = []
        
        # Get from major financial news sources
        for source_name, rss_url in list(self.news_sources.items())[:3]:
            try:
                feed = feedparser.parse(rss_url)
                
                for entry in feed.entries[:5]:
                    published_date = self._parse_date(entry.get('published'))
                    
                    article = {
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', '')[:200] + '...',
                        'url': entry.get('link', '#'),
                        'source': source_name,
                        'published': self._format_time_ago(published_date),
                        'published_date': published_date
                    }
                    
                    # Add sentiment analysis
                    article.update(self._analyze_sentiment(article['title']))
                    
                    articles.append(article)
                    
            except Exception as e:
                continue
        
        # Sort by date and return recent articles
        articles = sorted(articles, key=lambda x: x.get('published_date', datetime.now()), reverse=True)
        return articles[:max_articles] 