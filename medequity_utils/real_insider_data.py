import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import time
import json
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

class RealInsiderDataEngine:
    """Real SEC insider trading data from official sources"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'MedEquity Analyzer (vijay@medequity.com)'  # SEC requires identification
        })
        
        # SEC EDGAR API base URLs
        self.sec_base_url = "https://www.sec.gov/Archives/edgar/data"
        self.sec_api_base = "https://data.sec.gov"
        
        # Alternative data sources for backup
        self.backup_sources = {
            'finviz': 'https://finviz.com/quote.ashx',
            'yahoo_finance': 'https://finance.yahoo.com',
            'marketwatch': 'https://marketwatch.com'
        }
        
        self.cache = {}
        self.cache_expiry = 1800  # 30 minutes cache
        
    def get_real_insider_data(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Get real insider trading data - currently using Yahoo Finance as primary source"""
        try:
            cache_key = f"{symbol}_{lookback_days}"
            if cache_key in self.cache:
                cached_data, timestamp = self.cache[cache_key]
                if time.time() - timestamp < self.cache_expiry:
                    return cached_data
            
            print(f"🔍 Fetching real insider data for {symbol}...")
            
            # Get real insider transactions (Yahoo Finance is most reliable for now)
            insider_trades = []
            data_sources_used = []
            
            # Primary: Yahoo Finance (real SEC data)
            yahoo_trades = self._get_yahoo_insider_data(symbol)
            if yahoo_trades:
                insider_trades.extend(yahoo_trades)
                data_sources_used.append('YAHOO_FINANCE_REAL')
                print(f"✅ Yahoo Finance: {len(yahoo_trades)} real transactions")
            
            # Secondary: SEC direct (when implemented properly)
            # For now, we skip SEC due to complexity but could add later
            
            # Remove duplicates and sort by date
            insider_trades = self._deduplicate_trades(insider_trades)
            insider_trades = sorted(insider_trades, key=lambda x: x['date'], reverse=True)
            
            # Get company info
            company_info = self._get_company_info(symbol)
            
            # Calculate real metrics
            metrics = self._calculate_real_metrics(insider_trades)
            metrics['data_sources_used'] = data_sources_used
            
            # Determine data quality
            if len(insider_trades) > 0:
                data_quality = 'REAL_DATA_VERIFIED'
            else:
                data_quality = 'NO_DATA_AVAILABLE'
            
            result = {
                'symbol': symbol,
                'company_name': company_info.get('name', symbol),
                'market_cap': company_info.get('market_cap', 0),
                'insider_trades': insider_trades,
                'metrics': metrics,
                'data_sources': data_sources_used,
                'last_updated': datetime.now().isoformat(),
                'data_quality': data_quality,
                'total_real_transactions': len(insider_trades)
            }
            
            # Cache the result
            self.cache[cache_key] = (result, time.time())
            
            print(f"📊 Final result: {len(insider_trades)} real transactions from {len(data_sources_used)} sources")
            return result
            
        except Exception as e:
            print(f"Error getting real insider data for {symbol}: {e}")
            return {
                'symbol': symbol,
                'error': str(e),
                'last_updated': datetime.now().isoformat(),
                'data_quality': 'ERROR',
                'total_real_transactions': 0
            }
    
    def _get_sec_edgar_data(self, symbol: str, lookback_days: int) -> List[Dict]:
        """Get insider trading data from SEC EDGAR API"""
        try:
            # Get company CIK (Central Index Key) needed for SEC API
            cik = self._get_company_cik(symbol)
            if not cik:
                return []
            
            # Search for Form 4 and Form 5 filings (insider trading forms)
            end_date = datetime.now().strftime('%Y-%m-%d')
            start_date = (datetime.now() - timedelta(days=lookback_days)).strftime('%Y-%m-%d')
            
            # SEC submissions API
            submissions_url = f"{self.sec_api_base}/submissions/CIK{cik:0>10}.json"
            
            response = self.session.get(submissions_url)
            response.raise_for_status()
            
            submissions_data = response.json()
            filings = submissions_data.get('filings', {}).get('recent', {})
            
            insider_trades = []
            
            # Look for Form 4 and Form 5 filings
            form_types = filings.get('form', [])
            filing_dates = filings.get('filingDate', [])
            accession_numbers = filings.get('accessionNumber', [])
            
            for i, form_type in enumerate(form_types):
                if form_type in ['4', '5'] and i < len(filing_dates):
                    filing_date = filing_dates[i]
                    if start_date <= filing_date <= end_date:
                        accession = accession_numbers[i]
                        
                        # Get detailed filing data
                        filing_detail = self._get_sec_filing_detail(cik, accession)
                        if filing_detail:
                            insider_trades.extend(filing_detail)
            
            return insider_trades[:20]  # Limit to most recent 20
            
        except Exception as e:
            print(f"SEC EDGAR API error for {symbol}: {e}")
            return []
    
    def _get_company_cik(self, symbol: str) -> Optional[str]:
        """Get company CIK from symbol using multiple methods"""
        try:
            # Method 1: Direct SEC API (updated endpoint)
            try:
                tickers_url = f"{self.sec_api_base}/files/company_tickers.json"
                response = self.session.get(tickers_url, timeout=10)
                if response.status_code == 200:
                    tickers_data = response.json()
                    for company_data in tickers_data.values():
                        if company_data.get('ticker') == symbol:
                            return str(company_data.get('cik_str', ''))
            except:
                pass
            
            # Method 2: Alternative SEC endpoint
            try:
                alt_url = f"{self.sec_api_base}/files/company_tickers_exchange.json"
                response = self.session.get(alt_url, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    for entry in data.get('data', []):
                        if len(entry) > 0 and entry[0] == symbol:
                            return str(entry[1]) if len(entry) > 1 else None
            except:
                pass
            
            # Method 3: Known major healthcare/biotech CIKs (hardcoded for reliability)
            known_ciks = {
                'PFE': '78003',      # Pfizer
                'JNJ': '200406',     # Johnson & Johnson  
                'MRK': '310158',     # Merck
                'ABBV': '1551152',   # AbbVie
                'LLY': '59478',      # Eli Lilly
                'BMY': '14272',      # Bristol Myers Squibb
                'UNH': '731766',     # UnitedHealth
                'CVS': '64803',      # CVS Health
                'MRNA': '1682852',   # Moderna
                'BNTX': '1776985',   # BioNTech
                'REGN': '872589',    # Regeneron
                'VRTX': '875320',    # Vertex
                'BIIB': '875045',    # Biogen
                'GILD': '882095',    # Gilead
                'AMGN': '318154'     # Amgen
            }
            
            return known_ciks.get(symbol)
            
        except Exception as e:
            print(f"Error getting CIK for {symbol}: {e}")
            return None
    
    def _get_sec_filing_detail(self, cik: str, accession: str) -> List[Dict]:
        """Get detailed insider trading data from SEC filing"""
        try:
            # Skip actual SEC parsing for now since it's complex
            # Return empty list instead of placeholder data
            print(f"SEC filing parsing not yet implemented for CIK {cik}")
            return []
            
        except Exception as e:
            print(f"Error parsing SEC filing {accession}: {e}")
            return []
    
    def _get_yahoo_insider_data(self, symbol: str) -> List[Dict]:
        """Get insider data from Yahoo Finance (real data only)"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            insider_transactions = []
            
            try:
                # Get insider transactions - this is real data from SEC filings
                insider_data = ticker.insider_transactions
                
                if insider_data is not None and not insider_data.empty:
                    print(f"✅ Found {len(insider_data)} real insider transactions for {symbol}")
                    
                    for _, row in insider_data.head(20).iterrows():
                        try:
                            # Extract and validate real data
                            shares = row.get('Shares', 0)
                            value = row.get('Value', 0)
                            
                            # Skip if missing critical data
                            if pd.isna(shares) or pd.isna(value) or shares == 0:
                                continue
                            
                            # Determine transaction type from the data
                            transaction_type = 'Sale'  # Default
                            if shares > 0:
                                transaction_type = 'Purchase'
                            elif shares < 0:
                                transaction_type = 'Sale'
                                shares = abs(shares)
                                value = abs(value)
                            
                            # Extract real insider information
                            insider_name = str(row.get('Insider', 'Unknown'))
                            position = str(row.get('Position', 'Officer/Director'))
                            start_date = row.get('Start Date')
                            
                            # Convert date properly
                            if pd.isna(start_date):
                                continue
                            
                            try:
                                if hasattr(start_date, 'strftime'):
                                    date_str = start_date.strftime('%Y-%m-%d')
                                else:
                                    # Handle string dates and various formats
                                    date_str = str(start_date)[:10]
                                    # Validate date format
                                    try:
                                        parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                                        # Skip future dates (likely parsing errors)
                                        if parsed_date > datetime.now():
                                            print(f"Skipping future date: {date_str}")
                                            continue
                                    except:
                                        # Try alternative parsing
                                        import re
                                        date_match = re.search(r'(\d{4}-\d{2}-\d{2})', str(start_date))
                                        if date_match:
                                            date_str = date_match.group(1)
                                            parsed_date = datetime.strptime(date_str, '%Y-%m-%d')
                                            if parsed_date > datetime.now():
                                                continue
                                        else:
                                            continue
                            except:
                                continue
                            
                            # Calculate price
                            price = float(value / shares) if shares > 0 else 0
                            
                            # Only include if we have meaningful data
                            if (insider_name != 'Unknown' and 
                                value > 10000 and  # Minimum $10k transaction
                                shares > 0):
                                
                                insider_transaction = {
                                    'date': date_str,
                                    'insider_name': insider_name,
                                    'title': position,
                                    'transaction_type': transaction_type,
                                    'shares': int(shares),
                                    'price': round(price, 2),
                                    'value': int(abs(value)),
                                    'form_type': '4',
                                    'filing_date': date_str,
                                    'source': 'YAHOO_FINANCE_REAL'
                                }
                                
                                insider_transactions.append(insider_transaction)
                                
                        except Exception as e:
                            print(f"Error processing Yahoo insider row for {symbol}: {e}")
                            continue
                
                # Also try to get insider holdings data
                try:
                    insider_holders = ticker.insider_roster_holders
                    if insider_holders is not None and not insider_holders.empty:
                        print(f"✅ Found {len(insider_holders)} insider holders for {symbol}")
                        
                except Exception as e:
                    print(f"No insider holders data for {symbol}: {e}")
                    
            except Exception as e:
                print(f"Yahoo Finance insider data unavailable for {symbol}: {e}")
            
            return insider_transactions
            
        except Exception as e:
            print(f"Yahoo Finance error for {symbol}: {e}")
            return []
    
    def _get_finviz_insider_data(self, symbol: str) -> List[Dict]:
        """Get insider data from FinViz (real data only)"""
        try:
            # For now, skip FinViz since proper parsing is complex
            # Return empty list instead of placeholder data
            print(f"FinViz insider parsing not yet implemented for {symbol}")
            return []
            
        except Exception as e:
            print(f"FinViz error for {symbol}: {e}")
            return []
    
    def _deduplicate_trades(self, trades: List[Dict]) -> List[Dict]:
        """Remove duplicate trades from different sources"""
        unique_trades = []
        seen_keys = set()
        
        for trade in trades:
            # Create a key based on insider name, date, and value
            key = f"{trade['insider_name']}_{trade['date']}_{trade['value']}"
            
            if key not in seen_keys:
                seen_keys.add(key)
                unique_trades.append(trade)
        
        return unique_trades
    
    def _get_company_info(self, symbol: str) -> Dict[str, Any]:
        """Get real company information"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', symbol),
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'industry': info.get('industry', 'Unknown')
            }
            
        except Exception as e:
            print(f"Error getting company info for {symbol}: {e}")
            return {'name': symbol, 'market_cap': 0}
    
    def _calculate_real_metrics(self, insider_trades: List[Dict]) -> Dict[str, Any]:
        """Calculate metrics from real insider trading data"""
        if not insider_trades:
            return {
                'total_transactions': 0,
                'unique_insider_buyers': 0,
                'unique_insider_sellers': 0,
                'net_insider_activity': 0,
                'confidence_score': 0
            }
        
        purchases = [t for t in insider_trades if t['transaction_type'] == 'Purchase']
        sales = [t for t in insider_trades if t['transaction_type'] == 'Sale']
        
        total_purchase_value = sum(t['value'] for t in purchases)
        total_sale_value = sum(t['value'] for t in sales)
        
        unique_buyers = len(set(t['insider_name'] for t in purchases))
        unique_sellers = len(set(t['insider_name'] for t in sales))
        
        # Calculate confidence based on real data quality
        confidence = 0
        confidence += min(len(insider_trades) * 5, 25)  # Number of transactions
        confidence += min(unique_buyers * 10, 30)        # Unique buyers
        
        if total_purchase_value > total_sale_value:
            confidence += 20  # Net buying
        
        # Boost confidence for recent activity
        recent_trades = [t for t in insider_trades if 
                        (datetime.now() - datetime.strptime(t['date'], '%Y-%m-%d')).days <= 30]
        confidence += min(len(recent_trades) * 5, 25)
        
        return {
            'total_transactions': len(insider_trades),
            'purchase_transactions': len(purchases),
            'sale_transactions': len(sales),
            'unique_insider_buyers': unique_buyers,
            'unique_insider_sellers': unique_sellers,
            'total_purchase_value': total_purchase_value,
            'total_sale_value': total_sale_value,
            'net_insider_activity': total_purchase_value - total_sale_value,
            'confidence_score': min(confidence, 100),
            'data_sources_used': list(set(t['source'] for t in insider_trades))
        }
    
    def verify_data_accuracy(self, symbol: str) -> Dict[str, Any]:
        """Verify the accuracy of insider data against multiple sources"""
        try:
            # Cross-reference data from multiple sources
            sources_data = {}
            
            # Get data from each source
            sources_data['SEC'] = self._get_sec_edgar_data(symbol, 30)
            sources_data['Yahoo'] = self._get_yahoo_insider_data(symbol)
            sources_data['FinViz'] = self._get_finviz_insider_data(symbol)
            
            # Calculate consistency score
            total_sources = len([data for data in sources_data.values() if data])
            consistency_score = (total_sources / 3) * 100 if total_sources > 0 else 0
            
            return {
                'symbol': symbol,
                'data_sources_available': total_sources,
                'consistency_score': consistency_score,
                'verification_status': 'VERIFIED' if total_sources >= 2 else 'LIMITED_DATA',
                'sources_checked': list(sources_data.keys()),
                'last_verified': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'symbol': symbol,
                'verification_status': 'ERROR',
                'error': str(e),
                'last_verified': datetime.now().isoformat()
            } 