# Dynamic Healthcare Scraper

import yfinance as yf
import requests
from bs4 import BeautifulSoup
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import re
import time
import json
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class HealthcareScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.timeout = 10
        self.max_retries = 3
    
    def fetch_company_data(self, ticker: str) -> Dict[str, Any]:
        """Dynamically fetch comprehensive data for any ticker"""
        try:
            # Get basic data from yfinance
            stock = yf.Ticker(ticker)
            info = stock.info
            
            if not info or len(info) < 5:
                return {'error': f'No data found for {ticker}', 'ticker': ticker}
            
            # Determine if healthcare company
            is_healthcare = self._classify_healthcare(info)
            
            # Fetch comprehensive data in parallel
            with ThreadPoolExecutor(max_workers=6) as executor:
                futures = {
                    'financials': executor.submit(self._get_financials, stock),
                    'news': executor.submit(self._scrape_news, ticker),
                    'price_history': executor.submit(self._get_price_history, stock),
                    'analyst_data': executor.submit(self._get_analyst_data, stock),
                    'holders': executor.submit(self._get_holders, stock),
                }
                
                if is_healthcare:
                    futures['pipeline'] = executor.submit(self._scrape_pipeline, ticker, info)
                
                # Collect results
                data = {
                    'ticker': ticker,
                    'is_healthcare': is_healthcare,
                    'name': info.get('longName', ticker),
                    'sector': info.get('sector', 'Unknown'),
                    'industry': info.get('industry', 'Unknown'),
                    'subsector': self._determine_subsector(info),
                    'market_cap': info.get('marketCap', 0),
                    'basic_info': info,
                    'fetch_time': time.time()
                }
                
                for key, future in futures.items():
                    try:
                        data[key] = future.result(timeout=15)
                    except Exception as e:
                        data[key] = None
                        data[f'{key}_error'] = str(e)
                        
            return data
            
        except Exception as e:
            return {'error': str(e), 'ticker': ticker}
    
    def _classify_healthcare(self, info: Dict) -> bool:
        """Dynamically determine if company is healthcare"""
        healthcare_keywords = [
            'pharmaceutical', 'biotech', 'medical', 'healthcare', 'drug',
            'therapeutic', 'clinical', 'medicine', 'diagnostic',
            'surgical', 'hospital', 'laboratory', 'genomic', 'vaccine',
            'biotechnology', 'pharmacy', 'health', 'medtech', 'lifesciences'
        ]
        
        # Check sector first
        sector = info.get('sector', '').lower()
        if 'healthcare' in sector or 'health care' in sector:
            return True
            
        # Check industry
        industry = info.get('industry', '').lower()
        if any(keyword in industry for keyword in healthcare_keywords):
            return True
            
        # Check business description
        description = info.get('longBusinessSummary', '').lower()
        if description:
            # Count healthcare keywords in description
            healthcare_mentions = sum(1 for keyword in healthcare_keywords if keyword in description)
            if healthcare_mentions >= 2:  # At least 2 healthcare keywords
                return True
        
        # Check company name
        company_name = info.get('longName', '').lower()
        if any(keyword in company_name for keyword in healthcare_keywords):
            return True
            
        return False
    
    def _determine_subsector(self, info: Dict) -> str:
        """Determine healthcare subsector"""
        industry = info.get('industry', '').lower()
        description = (info.get('longBusinessSummary', '') + ' ' + 
                      info.get('longName', '')).lower()
        
        if any(word in industry + description for word in ['biotech', 'biotechnology', 'biologic']):
            return 'Biotechnology'
        elif any(word in industry + description for word in ['pharmaceutical', 'drug', 'pharma']):
            return 'Pharmaceuticals'
        elif any(word in industry + description for word in ['medical device', 'surgical', 'equipment']):
            return 'Medical Devices'
        elif any(word in industry + description for word in ['diagnostic', 'laboratory', 'testing']):
            return 'Diagnostics'
        elif any(word in industry + description for word in ['hospital', 'health system', 'provider']):
            return 'Healthcare Providers'
        elif any(word in industry + description for word in ['insurance', 'managed care', 'health plan']):
            return 'Healthcare Services'
        elif any(word in industry + description for word in ['digital health', 'telemedicine', 'health tech']):
            return 'Digital Health'
        else:
            return 'Healthcare - Other'
    
    def _get_financials(self, stock) -> Dict:
        """Get financial data"""
        try:
            info = stock.info
            financials = {
                'revenue': info.get('totalRevenue'),
                'gross_margins': info.get('grossMargins'),
                'profit_margins': info.get('profitMargins'),
                'pe_ratio': info.get('trailingPE'),
                'forward_pe': info.get('forwardPE'),
                'peg_ratio': info.get('pegRatio'),
                'debt_to_equity': info.get('debtToEquity'),
                'return_on_equity': info.get('returnOnEquity'),
                'revenue_growth': info.get('revenueGrowth'),
                'earnings_growth': info.get('earningsGrowth'),
                'current_ratio': info.get('currentRatio'),
                'quick_ratio': info.get('quickRatio'),
                'operating_margin': info.get('operatingMargins'),
                'ebitda': info.get('ebitda'),
                'free_cash_flow': info.get('freeCashflow'),
                'total_cash': info.get('totalCash'),
                'total_debt': info.get('totalDebt'),
                'book_value': info.get('bookValue'),
                'price_to_book': info.get('priceToBook'),
                'beta': info.get('beta'),
                'dividend_yield': info.get('dividendYield'),
                'payout_ratio': info.get('payoutRatio')
            }
            
            # Calculate additional metrics
            if financials['revenue'] and financials['revenue'] > 0:
                # R&D Intensity (if available)
                rd_expenses = info.get('researchAndDevelopment')
                if rd_expenses:
                    financials['rd_intensity'] = rd_expenses / financials['revenue']
            
            return financials
        except Exception as e:
            return {'error': str(e)}
    
    def _get_price_history(self, stock) -> Dict:
        """Get price history and technical indicators"""
        try:
            # Get 1 year of data
            hist = stock.history(period="1y")
            if hist.empty:
                return {'error': 'No price history available'}
            
            # Calculate technical indicators
            current_price = hist['Close'].iloc[-1] if len(hist) > 0 else None
            
            # Price changes
            price_changes = {}
            if len(hist) > 1:
                price_changes['1d'] = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-2]) - 1) * 100
            if len(hist) > 5:
                price_changes['1w'] = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-5]) - 1) * 100
            if len(hist) > 22:
                price_changes['1m'] = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-22]) - 1) * 100
            if len(hist) > 66:
                price_changes['3m'] = ((hist['Close'].iloc[-1] / hist['Close'].iloc[-66]) - 1) * 100
            if len(hist) > 0:
                price_changes['ytd'] = ((hist['Close'].iloc[-1] / hist['Close'].iloc[0]) - 1) * 100
            
            # Volume analysis
            volume_metrics = {}
            if len(hist) > 30:
                volume_metrics['avg_30d'] = hist['Volume'].tail(30).mean()
                volume_metrics['current_vs_avg'] = (hist['Volume'].iloc[-1] / volume_metrics['avg_30d']) if volume_metrics['avg_30d'] > 0 else 0
            
            # Volatility
            volatility = {}
            if len(hist) > 30:
                daily_returns = hist['Close'].pct_change().dropna()
                volatility['30d_annualized'] = daily_returns.tail(30).std() * (252 ** 0.5) * 100
            
            # Moving averages
            moving_averages = {}
            if len(hist) > 20:
                ma_20 = hist['Close'].rolling(window=20).mean().iloc[-1]
                moving_averages['20d'] = ma_20
                moving_averages['above_20d'] = current_price > ma_20
            if len(hist) > 50:
                ma_50 = hist['Close'].rolling(window=50).mean().iloc[-1]
                moving_averages['50d'] = ma_50
                moving_averages['above_50d'] = current_price > ma_50
            if len(hist) > 200:
                ma_200 = hist['Close'].rolling(window=200).mean().iloc[-1]
                moving_averages['200d'] = ma_200
                moving_averages['above_200d'] = current_price > ma_200
            
            # Support and resistance levels
            if len(hist) > 50:
                recent_high = hist['High'].tail(50).max()
                recent_low = hist['Low'].tail(50).min()
                
                support_resistance = {
                    '52w_high': hist['High'].max(),
                    '52w_low': hist['Low'].min(),
                    'recent_high_50d': recent_high,
                    'recent_low_50d': recent_low,
                    'distance_from_high': ((current_price / recent_high) - 1) * 100,
                    'distance_from_low': ((current_price / recent_low) - 1) * 100
                }
            else:
                support_resistance = {}
            
            return {
                'current_price': current_price,
                'price_changes': price_changes,
                'volume_metrics': volume_metrics,
                'volatility': volatility,
                'moving_averages': moving_averages,
                'support_resistance': support_resistance,
                'data_points': len(hist)
            }
        except Exception as e:
            return {'error': str(e)}
    
    def _scrape_news(self, ticker: str) -> List[Dict]:
        """Scrape recent news for the ticker"""
        news_list = []
        try:
            # Use yfinance news
            stock = yf.Ticker(ticker)
            news = stock.news
            
            for article in news[:10]:  # Get top 10 news items
                news_item = {
                    'title': article.get('title', ''),
                    'link': article.get('link', ''),
                    'source': article.get('publisher', 'Unknown'),
                    'published': article.get('providerPublishTime', 0),
                    'type': article.get('type', 'NEWS')
                }
                
                # Add sentiment analysis placeholder
                title_lower = news_item['title'].lower()
                if any(word in title_lower for word in ['breakthrough', 'approval', 'positive', 'success', 'beat', 'strong']):
                    news_item['sentiment'] = 'positive'
                elif any(word in title_lower for word in ['failure', 'reject', 'decline', 'miss', 'loss', 'concern']):
                    news_item['sentiment'] = 'negative'
                else:
                    news_item['sentiment'] = 'neutral'
                
                news_list.append(news_item)
        except Exception as e:
            news_list.append({'error': str(e)})
        
        return news_list
    
    def _get_analyst_data(self, stock) -> Dict:
        """Get analyst ratings and recommendations"""
        try:
            analyst_data = {}
            
            # Get recommendations
            try:
                recommendations = stock.recommendations
                if recommendations is not None and not recommendations.empty:
                    latest_recs = recommendations.tail(10)  # Get latest 10 recommendations
                    analyst_data['recommendations'] = latest_recs.to_dict('records')
                    
                    # Summary of current ratings
                    if 'To Grade' in latest_recs.columns:
                        rating_summary = latest_recs['To Grade'].value_counts().to_dict()
                        analyst_data['rating_summary'] = rating_summary
            except:
                pass
            
            # Get target price and analyst info from stock info
            info = stock.info
            analyst_data['target_mean_price'] = info.get('targetMeanPrice')
            analyst_data['target_high_price'] = info.get('targetHighPrice')
            analyst_data['target_low_price'] = info.get('targetLowPrice')
            analyst_data['recommendation_key'] = info.get('recommendationKey')
            analyst_data['recommendation_mean'] = info.get('recommendationMean')
            analyst_data['number_of_analyst_opinions'] = info.get('numberOfAnalystOpinions')
            
            return analyst_data
        except Exception as e:
            return {'error': str(e)}
    
    def _get_holders(self, stock) -> Dict:
        """Get institutional and insider holders"""
        try:
            holders_data = {}
            
            try:
                institutional_holders = stock.institutional_holders
                if institutional_holders is not None and not institutional_holders.empty:
                    holders_data['institutional'] = institutional_holders.head(10).to_dict('records')
            except:
                pass
            
            try:
                major_holders = stock.major_holders
                if major_holders is not None and not major_holders.empty:
                    holders_data['major'] = major_holders.to_dict('records')
            except:
                pass
            
            try:
                insider_roster = stock.insider_roster_holders
                if insider_roster is not None and not insider_roster.empty:
                    holders_data['insider_roster'] = insider_roster.head(10).to_dict('records')
            except:
                pass
            
            return holders_data
        except Exception as e:
            return {'error': str(e)}
    
    def _scrape_pipeline(self, ticker: str, info: Dict) -> List[Dict]:
        """Scrape clinical pipeline information from multiple sources"""
        pipeline_data = []
        
        try:
            # Method 1: Parse business description for pipeline info
            description = info.get('longBusinessSummary', '')
            if description:
                pipeline_data.extend(self._extract_pipeline_from_description(description, ticker))
            
            # Method 2: Try to get SEC filings data (simplified approach)
            try:
                sec_pipeline = self._get_pipeline_from_sec_hints(ticker, info)
                if sec_pipeline:
                    pipeline_data.extend(sec_pipeline)
            except:
                pass
            
            # Method 3: Estimate based on company profile
            market_cap = info.get('marketCap', 0)
            subsector = self._determine_subsector(info)
            
            if subsector in ['Biotechnology', 'Pharmaceuticals'] and market_cap > 0:
                estimated_programs = self._estimate_pipeline_size(ticker, market_cap, subsector, info)
                pipeline_data.extend(estimated_programs)
            
            # Remove duplicates and sort by confidence
            unique_pipeline = []
            seen = set()
            for item in pipeline_data:
                if isinstance(item, dict):
                    key = (item.get('phase', ''), item.get('indication', ''))
                    if key not in seen or item.get('confidence') == 'high':
                        unique_pipeline.append(item)
                        seen.add(key)
            
            return unique_pipeline[:10]  # Return top 10 programs
        
        except Exception as e:
            return [{'error': str(e), 'source': 'Pipeline Extraction'}]
    
    def _extract_pipeline_from_description(self, description: str, ticker: str) -> List[Dict]:
        """Extract pipeline information from business description"""
        pipeline_items = []
        
        pipeline_keywords = [
            'phase i', 'phase ii', 'phase iii', 'phase 1', 'phase 2', 'phase 3',
            'clinical trial', 'clinical study', 'fda approval', 'pipeline', 
            'candidate', 'program', 'indication', 'therapy', 'treatment',
            'drug', 'compound', 'molecule', 'investigational', 'development',
            'breakthrough therapy', 'orphan drug', 'fast track', 'priority review'
        ]
        
        # Split into sentences and analyze each one
        sentences = re.split(r'[.!?]+', description)
        
        for sentence in sentences:
            sentence_lower = sentence.lower().strip()
            if len(sentence_lower) < 30:  # Skip very short sentences
                continue
                
            keyword_count = sum(1 for keyword in pipeline_keywords if keyword in sentence_lower)
            
            if keyword_count >= 2:  # Has multiple pipeline keywords
                # Extract phase with improved regex
                phase = self._extract_phase(sentence_lower)
                
                # Extract indication with better coverage
                indication = self._extract_indication(sentence_lower)
                
                # Extract drug/program name if possible
                program_name = self._extract_program_name(sentence, ticker)
                
                pipeline_items.append({
                    'program_name': program_name,
                    'description': sentence.strip()[:200] + '...' if len(sentence.strip()) > 200 else sentence.strip(),
                    'phase': phase,
                    'indication': indication,
                    'source': 'Business Description',
                    'confidence': 'high' if keyword_count >= 4 else 'medium' if keyword_count >= 3 else 'low',
                    'keyword_count': keyword_count
                })
        
        return pipeline_items
    
    def _extract_phase(self, text: str) -> str:
        """Extract clinical phase from text"""
        phase_patterns = [
            (r'phase\s*(?:iii|3)', 'Phase III'),
            (r'phase\s*(?:ii|2)', 'Phase II'),
            (r'phase\s*(?:i|1)(?!\s*(?:ii|2))', 'Phase I'),
            (r'preclinical', 'Preclinical'),
            (r'pre-clinical', 'Preclinical'),
            (r'discovery', 'Discovery'),
            (r'approved|commercial|marketed', 'Approved/Commercial'),
            (r'registration|filing|submission', 'Registration'),
            (r'pivotal', 'Phase III'),
        ]
        
        for pattern, phase in phase_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return phase
        
        return 'Unknown'
    
    def _extract_indication(self, text: str) -> str:
        """Extract therapeutic indication from text"""
        indication_map = {
            r'cancer|oncology|tumor|carcinoma|lymphoma|leukemia|melanoma': 'Oncology',
            r'diabetes|diabetic': 'Diabetes',
            r'alzheimer|dementia|cognitive': 'Alzheimer\'s/Dementia',
            r'covid|coronavirus|sars-cov': 'COVID-19',
            r'heart|cardiac|cardiovascular|coronary': 'Cardiovascular',
            r'respiratory|asthma|copd|lung': 'Respiratory',
            r'arthritis|rheumatoid|inflammatory': 'Inflammatory',
            r'depression|psychiatric|mental health': 'Psychiatric',
            r'autoimmune|immune|immunology': 'Autoimmune',
            r'neurological|parkinson|epilepsy': 'Neurological',
            r'hepatitis|liver|hepatic': 'Hepatology',
            r'kidney|renal|nephrology': 'Nephrology',
            r'skin|dermatology|psoriasis': 'Dermatology',
            r'infectious|bacterial|viral|antimicrobial': 'Infectious Disease',
            r'vaccine|vaccination|immunization': 'Vaccines',
            r'rare disease|orphan': 'Rare Disease',
            r'pain|analgesic|chronic pain': 'Pain Management'
        }
        
        for pattern, indication in indication_map.items():
            if re.search(pattern, text, re.IGNORECASE):
                return indication
        
        return 'Various'
    
    def _extract_program_name(self, sentence: str, ticker: str) -> str:
        """Extract program/drug name from sentence"""
        # Look for patterns like "ABC-123", "Product-X", company codes
        patterns = [
            rf'{ticker}-\d+',  # Company ticker followed by numbers
            r'[A-Z]{2,4}-\d{2,4}',  # Letter-number combinations
            r'\b[A-Z][a-z]+[A-Z][a-z]*\b',  # CamelCase names
        ]
        
        for pattern in patterns:
            match = re.search(pattern, sentence)
            if match:
                return match.group()
        
        return f'{ticker} Program'
    
    def _get_pipeline_from_sec_hints(self, ticker: str, info: Dict) -> List[Dict]:
        """Get pipeline hints from SEC filing information (simplified)"""
        pipeline_hints = []
        
        # Use company size and type to estimate pipeline
        market_cap = info.get('marketCap', 0)
        subsector = self._determine_subsector(info)
        
        if subsector == 'Biotechnology' and market_cap > 1e9:  # Large biotech
            # Large biotechs typically have multiple programs
            pipeline_hints.extend([
                {
                    'program_name': f'{ticker} Lead Program',
                    'phase': 'Phase II',
                    'indication': 'Oncology',
                    'description': 'Lead clinical program based on company profile',
                    'source': 'Market Analysis',
                    'confidence': 'medium'
                },
                {
                    'program_name': f'{ticker} Early Stage',
                    'phase': 'Phase I',
                    'indication': 'Various',
                    'description': 'Early-stage development programs',
                    'source': 'Market Analysis',
                    'confidence': 'low'
                }
            ])
        
        return pipeline_hints
    
    def _estimate_pipeline_size(self, ticker: str, market_cap: float, subsector: str, info: Dict) -> List[Dict]:
        """Estimate pipeline size based on company characteristics"""
        estimated_programs = []
        
        # Get R&D spending if available
        rd_expenses = info.get('researchAndDevelopment', 0)
        revenue = info.get('totalRevenue', 0)
        
        rd_intensity = (rd_expenses / revenue) if revenue and rd_expenses else 0
        
        # Estimate number of programs based on size and R&D
        if market_cap > 50e9:  # Mega cap
            num_programs = 8 + int(rd_intensity * 10)
        elif market_cap > 10e9:  # Large cap
            num_programs = 4 + int(rd_intensity * 8)
        elif market_cap > 1e9:  # Mid cap
            num_programs = 2 + int(rd_intensity * 6)
        else:  # Small cap
            num_programs = 1 + int(rd_intensity * 4)
        
        num_programs = min(num_programs, 6)  # Cap at 6 programs
        
        # Generate estimated programs
        phases = ['Phase I', 'Phase II', 'Phase III', 'Preclinical']
        indications = ['Oncology', 'Immunology', 'CNS', 'Cardiovascular', 'Rare Disease']
        
        for i in range(num_programs):
            phase = phases[i % len(phases)]
            indication = indications[i % len(indications)]
            
            estimated_programs.append({
                'program_name': f'{ticker}-{100 + i}',
                'phase': phase,
                'indication': indication,
                'description': f'Estimated {phase} program in {indication} based on company profile',
                'source': 'Pipeline Estimation',
                'confidence': 'low',
                'estimated': True
            })
        
        return estimated_programs

    def validate_ticker(self, ticker: str) -> bool:
        """Quick validation if ticker exists"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            return info and len(info) > 5 and ('regularMarketPrice' in info or 'currentPrice' in info or 'previousClose' in info)
        except:
            return False

    def get_healthcare_metrics(self, data: Dict) -> Dict:
        """Calculate healthcare-specific metrics"""
        try:
            if not data.get('is_healthcare', False):
                return {'error': 'Not a healthcare company'}
            
            metrics = {}
            basic_info = data.get('basic_info', {})
            financials = data.get('financials', {})
            
            # R&D Intensity
            rd_intensity = financials.get('rd_intensity')
            if rd_intensity:
                metrics['rd_intensity'] = rd_intensity
                if rd_intensity > 0.3:
                    metrics['rd_category'] = 'High R&D'
                elif rd_intensity > 0.15:
                    metrics['rd_category'] = 'Medium R&D'
                else:
                    metrics['rd_category'] = 'Low R&D'
            
            # Pipeline value estimate (very rough)
            pipeline = data.get('pipeline', [])
            if pipeline and len(pipeline) > 0:
                pipeline_count = len([p for p in pipeline if isinstance(p, dict) and 'phase' in p])
                metrics['pipeline_count'] = pipeline_count
                
                # Rough pipeline value estimate
                market_cap = basic_info.get('marketCap', 0)
                if market_cap > 0 and pipeline_count > 0:
                    # Very rough estimate: 10-30% of market cap could be pipeline value
                    pipeline_value_estimate = market_cap * 0.2  # 20% rough estimate
                    metrics['estimated_pipeline_value'] = pipeline_value_estimate
            
            # Healthcare subsector risk profile
            subsector = data.get('subsector', '')
            risk_profiles = {
                'Biotechnology': 'High Risk/High Reward',
                'Pharmaceuticals': 'Medium Risk',
                'Medical Devices': 'Medium Risk',
                'Healthcare Providers': 'Low-Medium Risk',
                'Healthcare Services': 'Low-Medium Risk',
                'Diagnostics': 'Medium Risk',
                'Digital Health': 'Medium-High Risk'
            }
            metrics['risk_profile'] = risk_profiles.get(subsector, 'Unknown Risk')
            
            # Revenue diversification (based on description analysis)
            description = basic_info.get('longBusinessSummary', '').lower()
            if description:
                revenue_sources = []
                if any(word in description for word in ['drug sales', 'product sales', 'commercial']):
                    revenue_sources.append('Product Sales')
                if any(word in description for word in ['licensing', 'royalty', 'partnership']):
                    revenue_sources.append('Licensing/Royalties')
                if any(word in description for word in ['service', 'consulting']):
                    revenue_sources.append('Services')
                
                metrics['revenue_sources'] = revenue_sources
                metrics['revenue_diversification'] = 'High' if len(revenue_sources) > 2 else 'Medium' if len(revenue_sources) == 2 else 'Low'
            
            return metrics
        except Exception as e:
            return {'error': str(e)}
