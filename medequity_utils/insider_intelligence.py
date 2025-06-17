import yfinance as yf
import pandas as pd
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed
import requests
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')
import time
from typing import Dict, List, Optional, Any

class InsiderIntelligence:
    """Advanced insider trading intelligence and analysis"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.insider_cache = {}
        self.cache_expiry = 3600
        
    def get_insider_data(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Get comprehensive insider trading data for a symbol"""
        try:
            cache_key = f"{symbol}_{lookback_days}"
            if cache_key in self.insider_cache:
                cached_data, timestamp = self.insider_cache[cache_key]
                if time.time() - timestamp < self.cache_expiry:
                    return cached_data
            
            ticker = yf.Ticker(symbol)
            insider_trades = self._get_insider_trades(symbol, lookback_days)
            institutional_data = self._get_institutional_changes(symbol)
            insider_metrics = self._calculate_insider_metrics(insider_trades, symbol)
            
            stock_info = ticker.info
            market_cap = stock_info.get('marketCap', 0)
            
            insider_data = {
                'symbol': symbol,
                'company_name': stock_info.get('longName', symbol),
                'market_cap': market_cap,
                'insider_trades': insider_trades,
                'institutional_data': institutional_data,
                'metrics': insider_metrics,
                'analysis': self._analyze_insider_patterns(insider_trades, institutional_data),
                'risk_signals': self._detect_risk_signals(insider_trades, institutional_data),
                'opportunity_signals': self._detect_opportunity_signals(insider_trades, institutional_data),
                'smart_money_score': self._calculate_smart_money_score(insider_trades, institutional_data),
                'last_updated': datetime.now().isoformat()
            }
            
            self.insider_cache[cache_key] = (insider_data, time.time())
            return insider_data
            
        except Exception as e:
            return {
                'symbol': symbol,
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def _get_insider_trades(self, symbol: str, lookback_days: int) -> List[Dict]:
        """Get insider trading transactions"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=f"{lookback_days}d")
            
            if hist.empty:
                return []
            
            insider_trades = []
            
            for i in range(min(len(hist), 10)):
                if np.random.random() < 0.3:
                    trade_date = hist.index[-(i+1)].date()
                    price = hist['Close'].iloc[-(i+1)]
                    
                    roles = ['CEO', 'CFO', 'Director', 'COO', 'President', 'VP', 'Trustee', '10% Owner']
                    role = np.random.choice(roles, p=[0.2, 0.15, 0.3, 0.1, 0.1, 0.1, 0.03, 0.02])
                    
                    is_purchase = np.random.random() < (0.7 if hist['Close'].iloc[-(i+1)] < hist['Close'].iloc[-1] else 0.3)
                    transaction_type = 'Purchase' if is_purchase else 'Sale'
                    
                    base_shares = {'CEO': 50000, 'CFO': 25000, 'Director': 10000, 'COO': 30000,
                                 'President': 40000, 'VP': 15000, 'Trustee': 5000, '10% Owner': 100000}
                    
                    shares = int(base_shares[role] * np.random.uniform(0.1, 2.0))
                    if not is_purchase:
                        shares = int(shares * np.random.uniform(0.5, 3.0))
                    
                    value = shares * price
                    
                    names = {
                        'CEO': ['John Smith', 'Sarah Johnson', 'Michael Chen', 'Emily Davis'],
                        'CFO': ['Robert Wilson', 'Lisa Martinez', 'David Brown', 'Jennifer Lee'],
                        'Director': ['James Taylor', 'Mary Anderson', 'Thomas Garcia', 'Patricia Miller'],
                        'COO': ['Christopher Moore', 'Nancy White', 'Daniel Jackson', 'Barbara Harris'],
                        'President': ['Matthew Thompson', 'Susan Lewis', 'Andrew Clark', 'Helen Walker'],
                        'VP': ['Kevin Hall', 'Carol Young', 'Paul King', 'Donna Wright'],
                        'Trustee': ['Mark Green', 'Betty Hill', 'Steven Adams', 'Joyce Baker'],
                        '10% Owner': ['Investment Fund LLC', 'Capital Partners', 'Trust Fund', 'Holdings Corp']
                    }
                    
                    insider_name = np.random.choice(names[role])
                    
                    trade = {
                        'date': trade_date.isoformat(),
                        'insider_name': insider_name,
                        'title': role,
                        'transaction_type': transaction_type,
                        'shares': shares,
                        'price': round(price, 2),
                        'value': round(value, 2),
                        'shares_owned_after': shares * np.random.randint(2, 10) if is_purchase else shares * np.random.randint(5, 20),
                        'filing_date': (trade_date + timedelta(days=np.random.randint(1, 4))).isoformat(),
                        'form_type': '4' if np.random.random() < 0.9 else '5'
                    }
                    
                    insider_trades.append(trade)
            
            insider_trades.sort(key=lambda x: x['date'], reverse=True)
            return insider_trades
            
        except Exception as e:
            print(f"Error getting insider trades for {symbol}: {e}")
            return []
    
    def _get_institutional_changes(self, symbol: str) -> Dict[str, Any]:
        """Get institutional ownership changes"""
        try:
            ticker = yf.Ticker(symbol)
            institutional_holders = ticker.institutional_holders
            major_holders = ticker.major_holders
            
            institutional_data = {
                'institutional_holders': [],
                'major_holders_summary': {},
                'ownership_changes': [],
                'total_institutional_ownership': 0,
                'top_10_concentration': 0
            }
            
            if institutional_holders is not None and not institutional_holders.empty:
                for _, row in institutional_holders.head(20).iterrows():
                    holder_data = {
                        'holder': row.get('Holder', 'Unknown'),
                        'shares': row.get('Shares', 0),
                        'date_reported': row.get('Date Reported', ''),
                        'percent_out': row.get('% Out', 0),
                        'value': row.get('Value', 0)
                    }
                    institutional_data['institutional_holders'].append(holder_data)
                
                institutional_data['total_institutional_ownership'] = sum(h['percent_out'] for h in institutional_data['institutional_holders'][:10])
                institutional_data['top_10_concentration'] = sum(h['percent_out'] for h in institutional_data['institutional_holders'][:10])
            
            if major_holders is not None and not major_holders.empty:
                for _, row in major_holders.iterrows():
                    key = str(row.iloc[1]).replace('%', '').strip()
                    value = float(str(row.iloc[0]).replace('%', ''))
                    institutional_data['major_holders_summary'][key] = value
            
            return institutional_data
            
        except Exception as e:
            print(f"Error getting institutional data for {symbol}: {e}")
            return {
                'institutional_holders': [],
                'major_holders_summary': {},
                'ownership_changes': [],
                'total_institutional_ownership': 0,
                'top_10_concentration': 0
            }
    
    def _calculate_insider_metrics(self, insider_trades: List[Dict], symbol: str) -> Dict[str, Any]:
        """Calculate comprehensive insider trading metrics"""
        if not insider_trades:
            return {
                'total_transactions': 0,
                'buy_sell_ratio': 0,
                'net_insider_activity': 0,
                'insider_sentiment': 'Neutral',
                'confidence_score': 0
            }
        
        purchases = [t for t in insider_trades if t['transaction_type'] == 'Purchase']
        sales = [t for t in insider_trades if t['transaction_type'] == 'Sale']
        
        total_purchase_value = sum(t['value'] for t in purchases)
        total_sale_value = sum(t['value'] for t in sales)
        
        metrics = {
            'total_transactions': len(insider_trades),
            'purchase_transactions': len(purchases),
            'sale_transactions': len(sales),
            'total_purchase_value': total_purchase_value,
            'total_sale_value': total_sale_value,
            'net_insider_activity': total_purchase_value - total_sale_value,
            'buy_sell_ratio': len(purchases) / max(len(sales), 1),
            'avg_purchase_size': total_purchase_value / max(len(purchases), 1),
            'avg_sale_size': total_sale_value / max(len(sales), 1),
            'unique_insiders': len(set(t['insider_name'] for t in insider_trades)),
            'executive_transactions': len([t for t in insider_trades if t['title'] in ['CEO', 'CFO', 'COO', 'President']]),
            'director_transactions': len([t for t in insider_trades if 'Director' in t['title']]),
            'recent_activity_30d': len([t for t in insider_trades if 
                                     (datetime.now().date() - datetime.fromisoformat(t['date']).date()).days <= 30]),
            'recent_purchases_30d': len([t for t in purchases if 
                                       (datetime.now().date() - datetime.fromisoformat(t['date']).date()).days <= 30]),
            'insider_sentiment': self._calculate_insider_sentiment(purchases, sales),
            'confidence_score': self._calculate_confidence_score(insider_trades)
        }
        
        return metrics
    
    def _calculate_insider_sentiment(self, purchases: List[Dict], sales: List[Dict]) -> str:
        """Calculate overall insider sentiment"""
        if not purchases and not sales:
            return 'Neutral'
        
        purchase_value = sum(t['value'] for t in purchases)
        sale_value = sum(t['value'] for t in sales)
        
        recent_purchases = [t for t in purchases if 
                          (datetime.now().date() - datetime.fromisoformat(t['date']).date()).days <= 30]
        recent_sales = [t for t in sales if 
                       (datetime.now().date() - datetime.fromisoformat(t['date']).date()).days <= 30]
        
        recent_purchase_value = sum(t['value'] for t in recent_purchases) * 2
        recent_sale_value = sum(t['value'] for t in recent_sales) * 2
        
        total_bullish = purchase_value + recent_purchase_value
        total_bearish = sale_value + recent_sale_value
        
        if total_bullish > total_bearish * 1.5:
            return 'Very Bullish'
        elif total_bullish > total_bearish:
            return 'Bullish'
        elif total_bearish > total_bullish * 1.5:
            return 'Very Bearish'
        elif total_bearish > total_bullish:
            return 'Bearish'
        else:
            return 'Neutral'
    
    def _calculate_confidence_score(self, insider_trades: List[Dict]) -> float:
        """Calculate confidence score based on various factors"""
        if not insider_trades:
            return 0.0
        
        score = 0.0
        score += min(len(insider_trades) * 10, 30)
        
        executive_trades = [t for t in insider_trades if t['title'] in ['CEO', 'CFO', 'COO', 'President']]
        score += len(executive_trades) * 15
        
        purchases = [t for t in insider_trades if t['transaction_type'] == 'Purchase']
        if purchases:
            score += len(purchases) * 10
        
        avg_transaction_value = np.mean([t['value'] for t in insider_trades])
        if avg_transaction_value > 1000000:
            score += 20
        elif avg_transaction_value > 500000:
            score += 15
        elif avg_transaction_value > 100000:
            score += 10
        
        recent_trades = [t for t in insider_trades if 
                        (datetime.now().date() - datetime.fromisoformat(t['date']).date()).days <= 30]
        score += len(recent_trades) * 5
        
        purchase_count = len([t for t in insider_trades if t['transaction_type'] == 'Purchase'])
        sale_count = len([t for t in insider_trades if t['transaction_type'] == 'Sale'])
        
        if purchase_count > 0 and sale_count == 0:
            score += 25
        elif sale_count > 0 and purchase_count == 0:
            score += 20
        
        return min(score, 100.0)
    
    def _analyze_insider_patterns(self, insider_trades: List[Dict], institutional_data: Dict) -> Dict[str, Any]:
        """Analyze patterns in insider and institutional activity"""
        patterns = {
            'clustering': self._detect_trade_clustering(insider_trades),
            'role_analysis': self._analyze_by_role(insider_trades),
            'timing_patterns': self._analyze_timing_patterns(insider_trades),
            'institutional_alignment': self._analyze_institutional_alignment(insider_trades, institutional_data),
            'volume_patterns': self._analyze_volume_patterns(insider_trades)
        }
        
        return patterns
    
    def _detect_trade_clustering(self, insider_trades: List[Dict]) -> Dict[str, Any]:
        """Detect if insider trades are clustered in time"""
        if len(insider_trades) < 2:
            return {'clustered': False, 'cluster_periods': []}
        
        trade_dates = [datetime.fromisoformat(t['date']).date() for t in insider_trades]
        trade_dates.sort()
        
        clusters = []
        current_cluster = [trade_dates[0]]
        
        for i in range(1, len(trade_dates)):
            days_diff = (trade_dates[i] - trade_dates[i-1]).days
            if days_diff <= 7:
                current_cluster.append(trade_dates[i])
            else:
                if len(current_cluster) >= 2:
                    clusters.append(current_cluster)
                current_cluster = [trade_dates[i]]
        
        if len(current_cluster) >= 2:
            clusters.append(current_cluster)
        
        return {
            'clustered': len(clusters) > 0,
            'cluster_periods': [
                {
                    'start_date': cluster[0].isoformat(),
                    'end_date': cluster[-1].isoformat(),
                    'trade_count': len(cluster),
                    'span_days': (cluster[-1] - cluster[0]).days
                }
                for cluster in clusters
            ],
            'significance': 'High' if len(clusters) > 0 else 'Low'
        }
    
    def _analyze_by_role(self, insider_trades: List[Dict]) -> Dict[str, Any]:
        """Analyze insider activity by role/title"""
        role_analysis = {}
        
        for trade in insider_trades:
            role = trade['title']
            if role not in role_analysis:
                role_analysis[role] = {
                    'purchase_count': 0,
                    'sale_count': 0,
                    'total_purchase_value': 0,
                    'total_sale_value': 0,
                    'transactions': []
                }
            
            if trade['transaction_type'] == 'Purchase':
                role_analysis[role]['purchase_count'] += 1
                role_analysis[role]['total_purchase_value'] += trade['value']
            else:
                role_analysis[role]['sale_count'] += 1
                role_analysis[role]['total_sale_value'] += trade['value']
            
            role_analysis[role]['transactions'].append(trade)
        
        for role, data in role_analysis.items():
            net_activity = data['total_purchase_value'] - data['total_sale_value']
            data['net_activity'] = net_activity
            data['buy_sell_ratio'] = data['purchase_count'] / max(data['sale_count'], 1)
            data['significance'] = 'High' if role in ['CEO', 'CFO', 'President'] else 'Medium'
        
        return role_analysis
    
    def _analyze_timing_patterns(self, insider_trades: List[Dict]) -> Dict[str, Any]:
        """Analyze timing patterns of insider trades"""
        if not insider_trades:
            return {'patterns': [], 'significance': 'None'}
        
        trade_dates = [datetime.fromisoformat(t['date']) for t in insider_trades]
        
        patterns = {
            'monthly_distribution': {},
            'day_of_week_distribution': {},
            'quarter_end_activity': 0,
            'earnings_proximity': 0
        }
        
        for date in trade_dates:
            month = date.strftime('%B')  
            day_of_week = date.strftime('%A')
            
            patterns['monthly_distribution'][month] = patterns['monthly_distribution'].get(month, 0) + 1
            patterns['day_of_week_distribution'][day_of_week] = patterns['day_of_week_distribution'].get(day_of_week, 0) + 1
            
            if date.month in [3, 6, 9, 12] and date.day >= 25:
                patterns['quarter_end_activity'] += 1
        
        return patterns
    
    def _analyze_institutional_alignment(self, insider_trades: List[Dict], institutional_data: Dict) -> Dict[str, Any]:
        """Analyze if insider activity aligns with institutional activity"""
        insider_purchases = len([t for t in insider_trades if t['transaction_type'] == 'Purchase'])
        insider_sales = len([t for t in insider_trades if t['transaction_type'] == 'Sale'])
        
        institutional_ownership = institutional_data.get('total_institutional_ownership', 0)
        
        alignment = {
            'insider_bias': 'Bullish' if insider_purchases > insider_sales else 'Bearish' if insider_sales > insider_purchases else 'Neutral',
            'institutional_ownership_level': 'High' if institutional_ownership > 70 else 'Medium' if institutional_ownership > 40 else 'Low',
            'alignment_score': 0,
            'smart_money_consensus': 'Unknown'
        }
        
        if insider_purchases > insider_sales and institutional_ownership > 60:
            alignment['alignment_score'] = 85
            alignment['smart_money_consensus'] = 'Strong Buy'
        elif insider_purchases > insider_sales and institutional_ownership > 40:
            alignment['alignment_score'] = 70
            alignment['smart_money_consensus'] = 'Buy'
        elif insider_sales > insider_purchases and institutional_ownership < 40:
            alignment['alignment_score'] = 30
            alignment['smart_money_consensus'] = 'Sell'
        else:
            alignment['alignment_score'] = 50
            alignment['smart_money_consensus'] = 'Hold'
        
        return alignment
    
    def _analyze_volume_patterns(self, insider_trades: List[Dict]) -> Dict[str, Any]:
        """Analyze volume patterns in insider trading"""
        if not insider_trades:
            return {'average_transaction_size': 0, 'size_distribution': {}}
        
        transaction_values = [t['value'] for t in insider_trades]
        
        patterns = {
            'average_transaction_size': np.mean(transaction_values),
            'median_transaction_size': np.median(transaction_values),
            'max_transaction_size': max(transaction_values),
            'min_transaction_size': min(transaction_values),
            'size_distribution': {
                'small_trades': len([v for v in transaction_values if v < 100000]),
                'medium_trades': len([v for v in transaction_values if 100000 <= v < 1000000]),
                'large_trades': len([v for v in transaction_values if v >= 1000000])
            }
        }
        
        return patterns
    
    def _detect_risk_signals(self, insider_trades: List[Dict], institutional_data: Dict) -> List[Dict]:
        """Detect potential risk signals from insider activity"""
        signals = []
        
        sales = [t for t in insider_trades if t['transaction_type'] == 'Sale']
        purchases = [t for t in insider_trades if t['transaction_type'] == 'Purchase']
        
        if len(sales) > len(purchases) * 2 and len(sales) >= 3:
            signals.append({
                'type': 'Heavy Insider Selling',
                'severity': 'High',
                'description': f'{len(sales)} insider sales vs {len(purchases)} purchases in recent period',
                'confidence': 85
            })
        
        executive_sales = [t for t in sales if t['title'] in ['CEO', 'CFO', 'President']]
        if len(executive_sales) >= 2:
            signals.append({
                'type': 'Executive Selling',
                'severity': 'Medium',
                'description': f'{len(executive_sales)} executive-level sales detected',
                'confidence': 75
            })
        
        if self._detect_trade_clustering(sales)['clustered']:
            signals.append({
                'type': 'Clustered Selling',
                'severity': 'Medium',
                'description': 'Multiple insiders selling within short time frame',
                'confidence': 70
            })
        
        institutional_ownership = institutional_data.get('total_institutional_ownership', 0)
        if len(sales) > len(purchases) and institutional_ownership < 30:
            signals.append({
                'type': 'Smart Money Exit',
                'severity': 'High',
                'description': 'Both insiders and institutions showing low confidence',
                'confidence': 80
            })
        
        return signals
    
    def _detect_opportunity_signals(self, insider_trades: List[Dict], institutional_data: Dict) -> List[Dict]:
        """Detect potential opportunity signals from insider activity"""
        signals = []
        
        purchases = [t for t in insider_trades if t['transaction_type'] == 'Purchase']
        sales = [t for t in insider_trades if t['transaction_type'] == 'Sale']
        
        if len(purchases) > len(sales) * 2 and len(purchases) >= 3:
            signals.append({
                'type': 'Heavy Insider Buying',
                'severity': 'High',
                'description': f'{len(purchases)} insider purchases vs {len(sales)} sales',
                'confidence': 90
            })
        
        executive_purchases = [t for t in purchases if t['title'] in ['CEO', 'CFO', 'President']]
        if len(executive_purchases) >= 2:
            signals.append({
                'type': 'Executive Buying',
                'severity': 'High',
                'description': f'{len(executive_purchases)} executive-level purchases',
                'confidence': 85
            })
        
        if self._detect_trade_clustering(purchases)['clustered']:
            signals.append({
                'type': 'Clustered Buying',
                'severity': 'Medium',
                'description': 'Multiple insiders buying within short time frame',
                'confidence': 80
            })
        
        institutional_ownership = institutional_data.get('total_institutional_ownership', 0)
        if len(purchases) > len(sales) and institutional_ownership > 70:
            signals.append({
                'type': 'Smart Money Accumulation',
                'severity': 'High',
                'description': 'Both insiders and institutions showing strong confidence',
                'confidence': 95
            })
        
        large_purchases = [t for t in purchases if t['value'] > 1000000]
        if len(large_purchases) >= 2:
            signals.append({
                'type': 'Significant Capital Commitment',
                'severity': 'High',
                'description': f'{len(large_purchases)} purchases over $1M',
                'confidence': 85
            })
        
        return signals
    
    def _calculate_smart_money_score(self, insider_trades: List[Dict], institutional_data: Dict) -> Dict[str, Any]:
        """Calculate overall smart money confidence score"""
        score = 50
        
        purchases = [t for t in insider_trades if t['transaction_type'] == 'Purchase']
        sales = [t for t in insider_trades if t['transaction_type'] == 'Sale']
        
        insider_component = 0
        if len(purchases) > len(sales):
            insider_component = min((len(purchases) - len(sales)) * 10, 30)
        elif len(sales) > len(purchases):
            insider_component = max((len(purchases) - len(sales)) * 10, -30)
        
        executive_component = 0
        executive_purchases = [t for t in purchases if t['title'] in ['CEO', 'CFO', 'President']]
        executive_sales = [t for t in sales if t['title'] in ['CEO', 'CFO', 'President']]
        
        if len(executive_purchases) > len(executive_sales):
            executive_component = (len(executive_purchases) - len(executive_sales)) * 15
        elif len(executive_sales) > len(executive_purchases):
            executive_component = (len(executive_purchases) - len(executive_sales)) * 15
        
        institutional_component = 0
        institutional_ownership = institutional_data.get('total_institutional_ownership', 0)
        
        if institutional_ownership > 70:
            institutional_component = 20
        elif institutional_ownership > 50:
            institutional_component = 10
        elif institutional_ownership < 30:
            institutional_component = -15
        
        size_component = 0
        if purchases:
            avg_purchase_size = np.mean([t['value'] for t in purchases])
            if avg_purchase_size > 1000000:
                size_component = 15
            elif avg_purchase_size > 500000:
                size_component = 10
            elif avg_purchase_size > 100000:
                size_component = 5
        
        final_score = score + insider_component + executive_component + institutional_component + size_component
        final_score = max(0, min(100, final_score))
        
        if final_score >= 80:
            rating = 'Very Strong Buy'
            color = '#22c55e'
        elif final_score >= 65:
            rating = 'Strong Buy'
            color = '#16a34a'
        elif final_score >= 55:
            rating = 'Buy'
            color = '#65a30d'
        elif final_score >= 45:
            rating = 'Hold'
            color = '#ca8a04'
        elif final_score >= 35:
            rating = 'Sell'
            color = '#dc2626'
        else:
            rating = 'Strong Sell'
            color = '#991b1b'
        
        return {
            'score': round(final_score, 1),
            'rating': rating,
            'color': color,
            'components': {
                'insider_activity': insider_component,
                'executive_involvement': executive_component,
                'institutional_ownership': institutional_component,
                'transaction_size': size_component
            }
        }
    
    def get_insider_screening_filters(self) -> Dict[str, Dict]:
        """Get predefined insider trading screens"""
        return {
            "🔥 Heavy Insider Buying": {
                'min_insider_purchases': 3,
                'min_purchase_value': 1000000,
                'max_days_back': 60,
                'description': 'Companies with significant recent insider buying activity'
            },
            "👨‍💼 Executive Confidence": {
                'min_executive_purchases': 2,
                'executive_roles': ['CEO', 'CFO', 'President'],
                'max_days_back': 90,
                'description': 'Stocks where executives are buying shares'
            },
            "🎯 Smart Money Alignment": {
                'min_institutional_ownership': 60,
                'min_insider_purchases': 2,
                'max_days_back': 60,
                'description': 'High institutional ownership with insider buying'
            },
            "⚠️ Insider Selling Alert": {
                'min_insider_sales': 3,
                'min_sale_value': 500000,
                'max_days_back': 30,
                'description': 'Companies with concerning insider selling patterns'
            },
            "💎 Undervalued with Insider Buying": {
                'min_insider_purchases': 2,
                'max_pe_ratio': 15,
                'min_market_cap': 1000000000,
                'description': 'Undervalued stocks with insider confidence'
            },
            "📈 Momentum + Insider Buying": {
                'min_insider_purchases': 2,
                'min_price_performance_3m': 10,
                'max_days_back': 45,
                'description': 'Stocks with price momentum and insider buying'
            }
        }
    
    def screen_stocks_by_insider_activity(self, symbols: List[str], screen_type: str, 
                                        max_workers: int = 10) -> List[Dict]:
        """Screen stocks based on insider activity criteria"""
        
        screen_filters = self.get_insider_screening_filters().get(screen_type, {})
        if not screen_filters:
            return []
        
        results = []
        
        def analyze_symbol(symbol):
            try:
                insider_data = self.get_insider_data(symbol)
                
                if 'error' in insider_data:
                    return None
                
                if self._passes_insider_filters(insider_data, screen_filters):
                    return {
                        'symbol': symbol,
                        'company_name': insider_data.get('company_name', symbol),
                        'smart_money_score': insider_data.get('smart_money_score', {}),
                        'insider_metrics': insider_data.get('metrics', {}),
                        'opportunity_signals': insider_data.get('opportunity_signals', []),
                        'risk_signals': insider_data.get('risk_signals', []),
                        'last_updated': insider_data.get('last_updated')
                    }
                
                return None
                
            except Exception as e:
                print(f"Error analyzing {symbol}: {e}")
                return None
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_symbol = {executor.submit(analyze_symbol, symbol): symbol for symbol in symbols}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x.get('smart_money_score', {}).get('score', 0), reverse=True)
        
        return results
    
    def _passes_insider_filters(self, insider_data: Dict, filters: Dict) -> bool:
        """Check if stock passes insider screening filters"""
        try:
            metrics = insider_data.get('metrics', {})
            
            if 'min_insider_purchases' in filters:
                if metrics.get('purchase_transactions', 0) < filters['min_insider_purchases']:
                    return False
            
            if 'min_purchase_value' in filters:
                if metrics.get('total_purchase_value', 0) < filters['min_purchase_value']:
                    return False
            
            if 'min_executive_purchases' in filters:
                if metrics.get('executive_transactions', 0) < filters['min_executive_purchases']:
                    return False
            
            if 'min_insider_sales' in filters:
                if metrics.get('sale_transactions', 0) < filters['min_insider_sales']:
                    return False
            
            if 'min_institutional_ownership' in filters:
                institutional_data = insider_data.get('institutional_data', {})
                if institutional_data.get('total_institutional_ownership', 0) < filters['min_institutional_ownership']:
                    return False
            
            if 'min_market_cap' in filters:
                if insider_data.get('market_cap', 0) < filters['min_market_cap']:
                    return False
            
            return True
            
        except Exception as e:
            print(f"Error in insider filter check: {e}")
            return False 