import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
import time
from typing import Dict, List, Optional, Any, Tuple
import warnings
warnings.filterwarnings('ignore')

from .dynamic_scraper import HealthcareScraper
from .healthcare_classifier import HealthcareClassifier

class DynamicScreener:
    def __init__(self):
        self.scraper = HealthcareScraper()
        self.classifier = HealthcareClassifier()
        self.exchanges = ['NYSE', 'NASDAQ', 'AMEX']
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Common healthcare tickers to seed the screening
        self.known_healthcare_tickers = [
            # Large Pharma
            'PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'GSK', 'NVO', 'ROCHE',
            # Biotech
            'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD', 'AMGN', 'ILMN',
            # Medical Devices
            'MDT', 'ABT', 'SYK', 'BSX', 'EW', 'ISRG', 'DXCM', 'HOLX',
            # Healthcare Services
            'UNH', 'CVS', 'CI', 'HUM', 'ANTM', 'MOH', 'CNC',
            # Diagnostics
            'LH', 'DGX', 'QGEN', 'TMO', 'DHR', 'A', 'TECH',
            # Digital Health
            'TDOC', 'VEEV', 'DOCU', 'PTON', 'DOCS', 'HIMS'
        ]

    def get_all_healthcare_tickers(self, include_otc: bool = False, include_foreign: bool = True) -> List[str]:
        """Dynamically fetch all healthcare tickers from multiple sources"""
        all_tickers = set(self.known_healthcare_tickers)
        
        try:
            # Method 1: Get S&P 500 healthcare stocks
            sp500_healthcare = self._get_sp500_healthcare()
            all_tickers.update(sp500_healthcare)
        except Exception as e:
            print(f"Error fetching S&P 500 healthcare: {e}")
        
        try:
            # Method 2: Get NASDAQ healthcare stocks
            nasdaq_healthcare = self._get_nasdaq_healthcare()
            all_tickers.update(nasdaq_healthcare)
        except Exception as e:
            print(f"Error fetching NASDAQ healthcare: {e}")
        
        try:
            # Method 3: Get additional tickers from sector ETFs
            etf_healthcare = self._get_etf_holdings()
            all_tickers.update(etf_healthcare)
        except Exception as e:
            print(f"Error fetching ETF holdings: {e}")
        
        # Filter out invalid tickers
        valid_tickers = []
        for ticker in all_tickers:
            if self._is_valid_ticker_format(ticker):
                valid_tickers.append(ticker)
        
        return valid_tickers

    def _get_sp500_healthcare(self) -> List[str]:
        """Get healthcare stocks from S&P 500"""
        try:
            # Wikipedia S&P 500 list
            url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            tables = pd.read_html(url)
            sp500_table = tables[0]
            
            # Filter for healthcare sector
            healthcare_mask = sp500_table['GICS Sector'].str.contains('Health', case=False, na=False)
            healthcare_stocks = sp500_table[healthcare_mask]['Symbol'].tolist()
            
            return healthcare_stocks
        except Exception as e:
            print(f"Error fetching S&P 500 data: {e}")
            return []

    def _get_nasdaq_healthcare(self) -> List[str]:
        """Get healthcare stocks from NASDAQ"""
        try:
            # This would normally use NASDAQ API
            # For now, return common NASDAQ healthcare stocks
            nasdaq_healthcare = [
                'AMGN', 'GILD', 'REGN', 'VRTX', 'BIIB', 'ILMN', 'MRNA', 'BNTX',
                'SGEN', 'ALNY', 'BMRN', 'RARE', 'INCY', 'TECH', 'UTHR', 'IONS',
                'FOLD', 'ARWR', 'BLUE', 'CRSP', 'EDIT', 'NTLA', 'BEAM', 'SANA'
            ]
            return nasdaq_healthcare
        except Exception as e:
            print(f"Error fetching NASDAQ data: {e}")
            return []

    def _get_etf_holdings(self) -> List[str]:
        """Get holdings from healthcare ETFs"""
        try:
            # This would normally scrape ETF holdings
            # For now, return additional common healthcare stocks
            etf_holdings = [
                'TDOC', 'VEEV', 'DXCM', 'ISRG', 'HOLX', 'ALGN', 'PODD', 'TMDX',
                'NEOG', 'OMCL', 'NVTA', 'PACB', 'FATE', 'CRBU', 'VCEL', 'TCDA'
            ]
            return etf_holdings
        except Exception as e:
            print(f"Error fetching ETF holdings: {e}")
            return []

    def _is_valid_ticker_format(self, ticker: str) -> bool:
        """Check if ticker has valid format"""
        if not ticker or len(ticker) > 5:
            return False
        if not ticker.isalpha():
            return False
        return True

    def run_dynamic_screen(self, filters: Dict, include_otc: bool = False, 
                          include_foreign: bool = True, max_results: int = 100) -> pd.DataFrame:
        """Screen ALL healthcare stocks based on criteria"""
        
        print("🔍 Starting dynamic healthcare screening...")
        
        # Get universe of healthcare stocks
        tickers = self.get_all_healthcare_tickers(include_otc, include_foreign)
        print(f"📊 Analyzing {len(tickers)} healthcare tickers...")
        
        # Parallel processing for speed
        results = []
        processed_count = 0
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            # Submit all tickers for analysis
            future_to_ticker = {
                executor.submit(self._analyze_ticker, ticker, filters): ticker 
                for ticker in tickers
            }
            
            # Process results as they complete
            for future in as_completed(future_to_ticker):
                ticker = future_to_ticker[future]
                try:
                    result = future.result(timeout=30)
                    processed_count += 1
                    
                    if result and self._passes_filters(result, filters):
                        results.append(result)
                        print(f"✅ Found match: {ticker} - {result.get('name', 'Unknown')}")
                    
                    if processed_count % 10 == 0:
                        print(f"📈 Processed {processed_count}/{len(tickers)} tickers, found {len(results)} matches")
                    
                    # Limit results for performance
                    if len(results) >= max_results:
                        print(f"🛑 Reached maximum results limit ({max_results})")
                        break
                        
                except Exception as e:
                    print(f"❌ Error processing {ticker}: {str(e)}")
                    continue
        
        print(f"🎯 Screening complete! Found {len(results)} matches out of {processed_count} analyzed")
        
        if not results:
            return pd.DataFrame()
        
        # Convert to DataFrame and sort by market cap
        df = pd.DataFrame(results)
        df = df.sort_values('market_cap', ascending=False)
        
        return df

    def _analyze_ticker(self, ticker: str, filters: Dict) -> Optional[Dict]:
        """Analyze individual ticker with error handling"""
        try:
            # Basic validation first
            if not self.scraper.validate_ticker(ticker):
                return None
            
            # Get company data
            company_data = self.scraper.fetch_company_data(ticker)
            
            if 'error' in company_data:
                return None
            
            # Only proceed if healthcare company
            if not company_data.get('is_healthcare', False):
                return None
            
            # Extract key metrics for screening
            basic_info = company_data.get('basic_info', {})
            financials = company_data.get('financials', {})
            price_history = company_data.get('price_history', {})
            
            # Build screening data
            screening_data = {
                'ticker': ticker,
                'name': company_data.get('name', ticker),
                'sector': company_data.get('sector', 'Unknown'),
                'industry': company_data.get('industry', 'Unknown'),
                'subsector': company_data.get('subsector', 'Unknown'),
                'market_cap': basic_info.get('marketCap', 0),
                'current_price': price_history.get('current_price', 0),
                
                # Financial metrics
                'revenue': financials.get('revenue', 0),
                'gross_margins': financials.get('gross_margins', 0),
                'profit_margins': financials.get('profit_margins', 0),
                'pe_ratio': financials.get('pe_ratio', 0),
                'forward_pe': financials.get('forward_pe', 0),
                'peg_ratio': financials.get('peg_ratio', 0),
                'debt_to_equity': financials.get('debt_to_equity', 0),
                'return_on_equity': financials.get('return_on_equity', 0),
                'revenue_growth': financials.get('revenue_growth', 0),
                'earnings_growth': financials.get('earnings_growth', 0),
                'free_cash_flow': financials.get('free_cash_flow', 0),
                'total_cash': financials.get('total_cash', 0),
                'beta': financials.get('beta', 0),
                'dividend_yield': financials.get('dividend_yield', 0),
                
                # Price metrics
                'price_change_1d': price_history.get('price_changes', {}).get('1d', 0),
                'price_change_1w': price_history.get('price_changes', {}).get('1w', 0),
                'price_change_1m': price_history.get('price_changes', {}).get('1m', 0),
                'price_change_3m': price_history.get('price_changes', {}).get('3m', 0),
                'price_change_ytd': price_history.get('price_changes', {}).get('ytd', 0),
                'volume_avg_30d': price_history.get('volume_metrics', {}).get('avg_30d', 0),
                'volatility_30d': price_history.get('volatility', {}).get('30d_annualized', 0),
                
                # Healthcare-specific metrics
                'rd_intensity': financials.get('rd_intensity', 0),
                'pipeline_count': len(company_data.get('pipeline', [])),
                
                # Technical indicators
                'above_20d_ma': price_history.get('moving_averages', {}).get('above_20d', False),
                'above_50d_ma': price_history.get('moving_averages', {}).get('above_50d', False),
                'above_200d_ma': price_history.get('moving_averages', {}).get('above_200d', False),
                'distance_from_high': price_history.get('support_resistance', {}).get('distance_from_high', 0),
                'distance_from_low': price_history.get('support_resistance', {}).get('distance_from_low', 0),
                
                # News sentiment
                'news_sentiment': self._analyze_news_sentiment(company_data.get('news', [])),
                
                # Analyst data
                'analyst_rating': company_data.get('analyst_data', {}).get('recommendation_key', 'Unknown'),
                'target_price': company_data.get('analyst_data', {}).get('target_mean_price', 0),
                'num_analysts': company_data.get('analyst_data', {}).get('number_of_analyst_opinions', 0),
                
                # Additional data
                'last_updated': time.time()
            }
            
            # Calculate derived metrics
            if screening_data['current_price'] and screening_data['target_price']:
                screening_data['upside_potential'] = (
                    (screening_data['target_price'] / screening_data['current_price'] - 1) * 100
                )
            else:
                screening_data['upside_potential'] = 0
            
            return screening_data
            
        except Exception as e:
            print(f"Error analyzing {ticker}: {str(e)}")
            return None

    def _passes_filters(self, data: Dict, filters: Dict) -> bool:
        """Check if stock passes all filters"""
        try:
            # Market cap filters
            if 'min_market_cap' in filters:
                if not data.get('market_cap') or data['market_cap'] < filters['min_market_cap'] * 1e6:
                    return False
            
            if 'max_market_cap' in filters:
                if not data.get('market_cap') or data['market_cap'] > filters['max_market_cap'] * 1e6:
                    return False
            
            # P/E ratio filters
            if 'min_pe' in filters:
                pe = data.get('pe_ratio', 0)
                if not pe or pe < filters['min_pe']:
                    return False
            
            if 'max_pe' in filters:
                pe = data.get('pe_ratio', 0)
                if not pe or pe > filters['max_pe']:
                    return False
            
            # Revenue growth filter
            if 'min_revenue_growth' in filters:
                growth = data.get('revenue_growth', 0)
                if not growth or growth * 100 < filters['min_revenue_growth']:
                    return False
            
            # Profit margin filter
            if 'min_profit_margin' in filters:
                margin = data.get('profit_margins', 0)
                if not margin or margin * 100 < filters['min_profit_margin']:
                    return False
            
            # Gross margin filter
            if 'min_gross_margin' in filters:
                margin = data.get('gross_margins', 0)
                if not margin or margin * 100 < filters['min_gross_margin']:
                    return False
            
            # ROE filter
            if 'min_roe' in filters:
                roe = data.get('return_on_equity', 0)
                if not roe or roe * 100 < filters['min_roe']:
                    return False
            
            # Debt to equity filter
            if 'max_debt_to_equity' in filters:
                debt_equity = data.get('debt_to_equity', 0)
                if debt_equity and debt_equity > filters['max_debt_to_equity']:
                    return False
            
            # R&D intensity filter
            if 'min_rd_intensity' in filters:
                rd_intensity = data.get('rd_intensity', 0)
                if not rd_intensity or rd_intensity * 100 < filters['min_rd_intensity']:
                    return False
            
            # Pipeline filter
            if 'min_pipeline_count' in filters:
                pipeline_count = data.get('pipeline_count', 0)
                if pipeline_count < filters['min_pipeline_count']:
                    return False
            
            # Price momentum filters
            if 'min_price_change_1m' in filters:
                price_change = data.get('price_change_1m', 0)
                if price_change < filters['min_price_change_1m']:
                    return False
            
            if 'min_price_change_3m' in filters:
                price_change = data.get('price_change_3m', 0)
                if price_change < filters['min_price_change_3m']:
                    return False
            
            # Technical filters
            if filters.get('above_20d_ma', False):
                if not data.get('above_20d_ma', False):
                    return False
            
            if filters.get('above_50d_ma', False):
                if not data.get('above_50d_ma', False):
                    return False
            
            if filters.get('above_200d_ma', False):
                if not data.get('above_200d_ma', False):
                    return False
            
            # Subsector filter
            if 'subsectors' in filters and filters['subsectors']:
                if data.get('subsector', '') not in filters['subsectors']:
                    return False
            
            # Analyst rating filter
            if 'analyst_rating' in filters and filters['analyst_rating']:
                rating = data.get('analyst_rating', '').lower()
                target_rating = filters['analyst_rating'].lower()
                if target_rating not in rating:
                    return False
            
            # Minimum upside potential
            if 'min_upside_potential' in filters:
                upside = data.get('upside_potential', 0)
                if upside < filters['min_upside_potential']:
                    return False
            
            # News sentiment filter
            if 'news_sentiment' in filters and filters['news_sentiment']:
                sentiment = data.get('news_sentiment', 'neutral')
                if sentiment != filters['news_sentiment']:
                    return False
            
            # Dividend yield filter
            if 'min_dividend_yield' in filters:
                dividend_yield = data.get('dividend_yield', 0)
                if not dividend_yield or dividend_yield * 100 < filters['min_dividend_yield']:
                    return False
            
            # Beta filter
            if 'max_beta' in filters:
                beta = data.get('beta', 0)
                if beta and beta > filters['max_beta']:
                    return False
            
            # Volume filter
            if 'min_avg_volume' in filters:
                volume = data.get('volume_avg_30d', 0)
                if not volume or volume < filters['min_avg_volume']:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error in filter check: {e}")
            return False

    def _analyze_news_sentiment(self, news_list: List[Dict]) -> str:
        """Analyze overall news sentiment"""
        if not news_list or not isinstance(news_list, list):
            return 'neutral'
        
        sentiments = []
        for news_item in news_list:
            if isinstance(news_item, dict) and 'sentiment' in news_item:
                sentiments.append(news_item['sentiment'])
        
        if not sentiments:
            return 'neutral'
        
        # Count sentiment types
        positive_count = sentiments.count('positive')
        negative_count = sentiments.count('negative')
        neutral_count = sentiments.count('neutral')
        
        if positive_count > negative_count and positive_count > neutral_count:
            return 'positive'
        elif negative_count > positive_count and negative_count > neutral_count:
            return 'negative'
        else:
            return 'neutral'

    def get_quick_screens(self) -> Dict[str, Dict]:
        """Get predefined quick screening filters"""
        return {
            "🚀 High Growth Healthcare": {
                'min_revenue_growth': 25,
                'min_gross_margin': 60,
                'min_market_cap': 100,
                'description': 'Fast-growing healthcare companies with strong margins'
            },
            "💰 Profitable Biotechs": {
                'subsectors': ['Biotechnology'],
                'min_profit_margin': 5,
                'min_market_cap': 1000,
                'description': 'Profitable biotechnology companies'
            },
            "🔬 R&D Leaders": {
                'min_rd_intensity': 15,
                'min_market_cap': 500,
                'description': 'Companies with significant R&D investment'
            },
            "📈 Momentum Players": {
                'above_50d_ma': True,
                'min_price_change_3m': 10,
                'min_avg_volume': 100000,
                'description': 'Healthcare stocks with strong price momentum'
            },
            "🏥 Large Cap Healthcare": {
                'min_market_cap': 10000,
                'min_dividend_yield': 1,
                'max_beta': 1.2,
                'description': 'Large, stable healthcare companies with dividends'
            },
            "🧬 Emerging Biotechs": {
                'subsectors': ['Biotechnology'],
                'min_market_cap': 100,
                'max_market_cap': 5000,
                'min_pipeline_count': 1,
                'description': 'Mid-cap biotech companies with active pipelines'
            },
            "🎯 Analyst Favorites": {
                'min_upside_potential': 20,
                'analyst_rating': 'buy',
                'num_analysts': 3,
                'description': 'Healthcare stocks with strong analyst support'
            },
            "💊 Pharma Value Plays": {
                'subsectors': ['Pharmaceuticals'],
                'max_pe': 15,
                'min_dividend_yield': 2,
                'min_market_cap': 5000,
                'description': 'Undervalued pharmaceutical companies with dividends'
            },
            "🏗️ Medical Device Innovation": {
                'subsectors': ['Medical Devices'],
                'min_revenue_growth': 15,
                'min_gross_margin': 70,
                'description': 'Growing medical device companies with strong margins'
            },
            "📊 Healthcare REIT Income": {
                'min_dividend_yield': 4,
                'max_beta': 1.0,
                'min_market_cap': 1000,
                'description': 'Healthcare REITs with high dividend yields'
            }
        }

    def get_screening_suggestions(self, market_conditions: str = 'normal') -> List[str]:
        """Get screening suggestions based on market conditions"""
        if market_conditions == 'bull':
            return [
                "🚀 High Growth Healthcare",
                "📈 Momentum Players",
                "🧬 Emerging Biotechs",
                "🎯 Analyst Favorites"
            ]
        elif market_conditions == 'bear':
            return [
                "🏥 Large Cap Healthcare",
                "💊 Pharma Value Plays",
                "📊 Healthcare REIT Income",
                "💰 Profitable Biotechs"
            ]
        else:  # normal market
            return [
                "🔬 R&D Leaders",
                "🏗️ Medical Device Innovation",
                "🚀 High Growth Healthcare",
                "💰 Profitable Biotechs"
            ]

    def export_results(self, df: pd.DataFrame, filename: str = None) -> str:
        """Export screening results to CSV"""
        if filename is None:
            filename = f"healthcare_screen_{int(time.time())}.csv"
        
        # Select key columns for export
        export_columns = [
            'ticker', 'name', 'subsector', 'market_cap', 'current_price',
            'pe_ratio', 'revenue_growth', 'profit_margins', 'gross_margins',
            'price_change_1m', 'price_change_3m', 'analyst_rating',
            'upside_potential', 'pipeline_count', 'rd_intensity'
        ]
        
        available_columns = [col for col in export_columns if col in df.columns]
        export_df = df[available_columns].copy()
        
        # Format numeric columns
        numeric_columns = ['market_cap', 'current_price', 'pe_ratio', 'revenue_growth',
                          'profit_margins', 'gross_margins', 'upside_potential', 'rd_intensity']
        
        for col in numeric_columns:
            if col in export_df.columns:
                export_df[col] = pd.to_numeric(export_df[col], errors='coerce')
        
        export_df.to_csv(filename, index=False)
        return filename 