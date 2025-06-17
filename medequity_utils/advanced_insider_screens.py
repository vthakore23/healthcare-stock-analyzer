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
from .insider_intelligence import InsiderIntelligence

class AdvancedInsiderScreens:
    """Advanced insider trading screens for generating investment edge"""
    
    def __init__(self):
        self.insider_intel = InsiderIntelligence()
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        self.stock_universe = [
            'PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'GSK', 'NVO', 'UNH', 'CVS',
            'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD', 'AMGN', 'ILMN', 'SGEN',
            'MDT', 'ABT', 'SYK', 'BSX', 'EW', 'ISRG', 'DXCM', 'HOLX', 'TMO', 'DHR',
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 'NFLX', 'CRM',
            'JPM', 'BAC', 'WFC', 'GS', 'MS', 'C', 'V', 'MA', 'AXP', 'COF',
            'WMT', 'COST', 'TGT', 'HD', 'LOW', 'NKE', 'SBUX', 'MCD', 'DIS'
        ]
    
    def get_comprehensive_insider_metrics(self, symbol: str, lookback_days: int = 90) -> Dict[str, Any]:
        """Get comprehensive insider metrics with market cap analysis"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period=f"{lookback_days}d")
            
            if hist.empty:
                return {'error': 'No price data available'}
            
            market_cap = info.get('marketCap', 0)
            shares_outstanding = info.get('sharesOutstanding', 0)
            current_price = hist['Close'][-1]
            
            insider_data = self.insider_intel.get_insider_data(symbol, lookback_days)
            if 'error' in insider_data:
                return insider_data
            
            insider_trades = insider_data.get('insider_trades', [])
            
            metrics = self._calculate_advanced_metrics(
                insider_trades, market_cap, shares_outstanding, current_price, hist
            )
            
            valuation_metrics = self._get_valuation_growth_metrics(info)
            
            comprehensive_metrics = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'market_cap': market_cap,
                'current_price': current_price,
                'insider_metrics': metrics,
                'valuation_metrics': valuation_metrics,
                'insider_data': insider_data,
                'price_history': hist,
                'last_updated': datetime.now().isoformat()
            }
            
            return comprehensive_metrics
            
        except Exception as e:
            return {'error': str(e), 'symbol': symbol}
    
    def _calculate_advanced_metrics(self, insider_trades: List[Dict], market_cap: float, 
                                  shares_outstanding: float, current_price: float, hist: pd.DataFrame) -> Dict[str, Any]:
        """Calculate advanced insider trading metrics"""
        if not insider_trades:
            return {
                'insider_buyer_count': 0,
                'insider_seller_count': 0,
                'unique_insider_buyers': 0,
                'unique_insider_sellers': 0,
                'total_shares_bought': 0,
                'total_shares_sold': 0,
                'percent_market_cap_bought': 0,
                'percent_market_cap_sold': 0,
                'avg_purchase_size_usd': 0,
                'avg_sale_size_usd': 0,
                'largest_purchase_usd': 0,
                'largest_sale_usd': 0,
                'insider_conviction_score': 0,
                'timing_score': 0,
                'executive_vs_director_ratio': 0
            }
        
        purchases = [t for t in insider_trades if t['transaction_type'] == 'Purchase']
        sales = [t for t in insider_trades if t['transaction_type'] == 'Sale']
        
        insider_buyer_count = len(purchases)
        insider_seller_count = len(sales)
        unique_insider_buyers = len(set(t['insider_name'] for t in purchases))
        unique_insider_sellers = len(set(t['insider_name'] for t in sales))
        
        total_shares_bought = sum(t['shares'] for t in purchases)
        total_shares_sold = sum(t['shares'] for t in sales)
        
        percent_market_cap_bought = 0
        percent_market_cap_sold = 0
        
        if shares_outstanding > 0:
            percent_market_cap_bought = (total_shares_bought / shares_outstanding) * 100
            percent_market_cap_sold = (total_shares_sold / shares_outstanding) * 100
        
        total_value_bought = sum(t['value'] for t in purchases)
        total_value_sold = sum(t['value'] for t in sales)
        
        avg_purchase_size_usd = total_value_bought / max(len(purchases), 1)
        avg_sale_size_usd = total_value_sold / max(len(sales), 1)
        
        largest_purchase_usd = max([t['value'] for t in purchases] + [0])
        largest_sale_usd = max([t['value'] for t in sales] + [0])
        
        insider_conviction_score = self._calculate_conviction_score(purchases, sales, market_cap)
        timing_score = self._calculate_timing_score(insider_trades, hist)
        
        executive_trades = [t for t in insider_trades if t['title'] in ['CEO', 'CFO', 'President', 'COO']]
        director_trades = [t for t in insider_trades if 'Director' in t['title']]
        
        executive_vs_director_ratio = len(executive_trades) / max(len(director_trades), 1)
        
        return {
            'insider_buyer_count': insider_buyer_count,
            'insider_seller_count': insider_seller_count,
            'unique_insider_buyers': unique_insider_buyers,
            'unique_insider_sellers': unique_insider_sellers,
            'total_shares_bought': total_shares_bought,
            'total_shares_sold': total_shares_sold,
            'percent_market_cap_bought': percent_market_cap_bought,
            'percent_market_cap_sold': percent_market_cap_sold,
            'net_insider_shares': total_shares_bought - total_shares_sold,
            'net_insider_value': total_value_bought - total_value_sold,
            'avg_purchase_size_usd': avg_purchase_size_usd,
            'avg_sale_size_usd': avg_sale_size_usd,
            'largest_purchase_usd': largest_purchase_usd,
            'largest_sale_usd': largest_sale_usd,
            'insider_conviction_score': insider_conviction_score,
            'timing_score': timing_score,
            'executive_vs_director_ratio': executive_vs_director_ratio,
            'buy_sell_value_ratio': total_value_bought / max(total_value_sold, 1),
            'buy_sell_count_ratio': insider_buyer_count / max(insider_seller_count, 1)
        }
    
    def _calculate_conviction_score(self, purchases: List[Dict], sales: List[Dict], market_cap: float) -> float:
        """Calculate insider conviction score based on transaction characteristics"""
        score = 50
        
        if len(purchases) > len(sales):
            score += min((len(purchases) - len(sales)) * 15, 30)
        elif len(sales) > len(purchases):
            score -= min((len(sales) - len(purchases)) * 10, 30)
        
        if purchases and market_cap > 0:
            total_purchase_value = sum(t['value'] for t in purchases)
            purchase_to_mcap_ratio = total_purchase_value / market_cap
            
            if purchase_to_mcap_ratio > 0.001:
                score += 20
            elif purchase_to_mcap_ratio > 0.0005:
                score += 10
        
        executive_purchases = [t for t in purchases if t['title'] in ['CEO', 'CFO', 'President']]
        if len(executive_purchases) >= 2:
            score += 15
        elif len(executive_purchases) == 1:
            score += 8
        
        if len(purchases) > 0 and len(sales) == 0:
            score += 10
        elif len(sales) > 0 and len(purchases) == 0:
            score -= 15
        
        return max(0, min(100, score))
    
    def _calculate_timing_score(self, insider_trades: List[Dict], hist: pd.DataFrame) -> float:
        """Calculate timing score based on price performance after insider activity"""
        if not insider_trades or hist.empty:
            return 50
        
        score = 50
        scored_trades = 0
        
        for trade in insider_trades:
            trade_date = pd.to_datetime(trade['date'])
            
            if trade_date in hist.index:
                trade_price = hist.loc[trade_date, 'Close']
                current_price = hist['Close'][-1]
                
                price_change = (current_price - trade_price) / trade_price * 100
                
                if trade['transaction_type'] == 'Purchase':
                    if price_change > 10:
                        score += 20
                    elif price_change > 5:
                        score += 10
                    elif price_change < -10:
                        score -= 15
                    elif price_change < -5:
                        score -= 8
                else:
                    if price_change < -10:
                        score += 15
                    elif price_change < -5:
                        score += 8
                    elif price_change > 10:
                        score -= 10
                    elif price_change > 5:
                        score -= 5
                
                scored_trades += 1
        
        if scored_trades > 0:
            score = score / max(scored_trades, 1) * len(insider_trades)
        
        return max(0, min(100, score))
    
    def _get_valuation_growth_metrics(self, info: Dict) -> Dict[str, Any]:
        """Get comprehensive valuation and growth metrics"""
        return {
            'pe_ratio': info.get('trailingPE', 0),
            'forward_pe': info.get('forwardPE', 0),
            'peg_ratio': info.get('pegRatio', 0),
            'price_to_book': info.get('priceToBook', 0),
            'price_to_sales': info.get('priceToSalesTrailing12Months', 0),
            'ev_to_revenue': info.get('enterpriseToRevenue', 0),
            'ev_to_ebitda': info.get('enterpriseToEbitda', 0),
            'debt_to_equity': info.get('debtToEquity', 0),
            'current_ratio': info.get('currentRatio', 0),
            'roe': info.get('returnOnEquity', 0),
            'roa': info.get('returnOnAssets', 0),
            'gross_margins': info.get('grossMargins', 0),
            'operating_margins': info.get('operatingMargins', 0),
            'profit_margins': info.get('profitMargins', 0),
            'revenue_growth': info.get('revenueGrowth', 0),
            'earnings_growth': info.get('earningsGrowth', 0),
            'dividend_yield': info.get('dividendYield', 0),
            'beta': info.get('beta', 0),
            'analyst_rating': info.get('recommendationMean', 0),
            'target_price': info.get('targetMeanPrice', 0)
        }
    
    def run_edge_generating_screens(self) -> Dict[str, List[Dict]]:
        """Run multiple edge-generating screens across all stocks"""
        
        screens = {
            "🔥 Heavy Insider Accumulation": self._screen_heavy_accumulation,
            "💎 Smart Money Convergence": self._screen_smart_money_convergence,
            "🎯 Undervalued with Insider Buying": self._screen_undervalued_with_buying,
            "⚡ Momentum + Insider Activity": self._screen_momentum_insider,
            "🏆 Executive Confidence Play": self._screen_executive_confidence,
            "🔍 Hidden Gem Discovery": self._screen_hidden_gems,
            "⚠️ Insider Selling Alerts": self._screen_insider_selling
        }
        
        results = {}
        
        for screen_name, screen_func in screens.items():
            print(f"Running {screen_name}...")
            try:
                screen_results = screen_func()
                results[screen_name] = screen_results
                print(f"✅ {screen_name}: Found {len(screen_results)} matches")
            except Exception as e:
                print(f"❌ {screen_name}: Error - {str(e)}")
                results[screen_name] = []
        
        return results
    
    def _screen_heavy_accumulation(self) -> List[Dict]:
        """Screen for stocks with heavy insider accumulation"""
        results = []
        
        def analyze_stock(symbol):
            try:
                metrics = self.get_comprehensive_insider_metrics(symbol, 90)
                if 'error' in metrics:
                    return None
                
                insider_metrics = metrics.get('insider_metrics', {})
                
                criteria = [
                    insider_metrics.get('unique_insider_buyers', 0) >= 3,
                    insider_metrics.get('percent_market_cap_bought', 0) >= 0.1,
                    insider_metrics.get('buy_sell_value_ratio', 0) >= 2.0,
                    insider_metrics.get('insider_conviction_score', 0) >= 70
                ]
                
                if sum(criteria) >= 3:
                    return {
                        'symbol': symbol,
                        'company_name': metrics.get('company_name', symbol),
                        'insider_buyers': insider_metrics.get('unique_insider_buyers', 0),
                        'percent_market_cap_bought': insider_metrics.get('percent_market_cap_bought', 0),
                        'net_insider_value': insider_metrics.get('net_insider_value', 0),
                        'conviction_score': insider_metrics.get('insider_conviction_score', 0),
                        'timing_score': insider_metrics.get('timing_score', 0),
                        'market_cap': metrics.get('market_cap', 0),
                        'current_price': metrics.get('current_price', 0)
                    }
                
                return None
                
            except Exception as e:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(analyze_stock, symbol): symbol 
                              for symbol in self.stock_universe}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x['conviction_score'], reverse=True)
        return results[:20]
    
    def _screen_smart_money_convergence(self) -> List[Dict]:
        """Screen for stocks where insiders and institutions are both bullish"""
        results = []
        
        def analyze_stock(symbol):
            try:
                metrics = self.get_comprehensive_insider_metrics(symbol, 60)
                if 'error' in metrics:
                    return None
                
                insider_metrics = metrics.get('insider_metrics', {})
                valuation_metrics = metrics.get('valuation_metrics', {})
                insider_data = metrics.get('insider_data', {})
                
                institutional_data = insider_data.get('institutional_data', {})
                institutional_ownership = institutional_data.get('total_institutional_ownership', 0)
                
                insider_bullish = (
                    insider_metrics.get('buy_sell_value_ratio', 0) >= 1.5 and
                    insider_metrics.get('unique_insider_buyers', 0) >= 2
                )
                
                institutional_bullish = institutional_ownership >= 60
                
                reasonable_valuation = (
                    valuation_metrics.get('pe_ratio', 999) < 30 and
                    valuation_metrics.get('peg_ratio', 999) < 2.0
                )
                
                if insider_bullish and institutional_bullish and reasonable_valuation:
                    return {
                        'symbol': symbol,
                        'company_name': metrics.get('company_name', symbol),
                        'insider_buyers': insider_metrics.get('unique_insider_buyers', 0),
                        'institutional_ownership': institutional_ownership,
                        'buy_sell_ratio': insider_metrics.get('buy_sell_value_ratio', 0),
                        'pe_ratio': valuation_metrics.get('pe_ratio', 0),
                        'peg_ratio': valuation_metrics.get('peg_ratio', 0),
                        'conviction_score': insider_metrics.get('insider_conviction_score', 0)
                    }
                
                return None
                
            except Exception as e:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(analyze_stock, symbol): symbol 
                              for symbol in self.stock_universe}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x['conviction_score'], reverse=True)
        return results[:15]
    
    def _screen_undervalued_with_buying(self) -> List[Dict]:
        """Screen for undervalued stocks with insider buying"""
        results = []
        
        def analyze_stock(symbol):
            try:
                metrics = self.get_comprehensive_insider_metrics(symbol, 90)
                if 'error' in metrics:
                    return None
                
                insider_metrics = metrics.get('insider_metrics', {})
                valuation_metrics = metrics.get('valuation_metrics', {})
                
                pe_ratio = valuation_metrics.get('pe_ratio', 999)
                peg_ratio = valuation_metrics.get('peg_ratio', 999)
                price_to_book = valuation_metrics.get('price_to_book', 999)
                
                undervalued = (
                    (pe_ratio > 0 and pe_ratio < 15) or
                    (peg_ratio > 0 and peg_ratio < 1.0) or
                    (price_to_book > 0 and price_to_book < 2.0)
                )
                
                insider_buying = (
                    insider_metrics.get('unique_insider_buyers', 0) >= 2 and
                    insider_metrics.get('net_insider_value', 0) > 500000
                )
                
                if undervalued and insider_buying:
                    return {
                        'symbol': symbol,
                        'company_name': metrics.get('company_name', symbol),
                        'pe_ratio': pe_ratio,
                        'peg_ratio': peg_ratio,
                        'price_to_book': price_to_book,
                        'insider_buyers': insider_metrics.get('unique_insider_buyers', 0),
                        'net_insider_value': insider_metrics.get('net_insider_value', 0),
                        'percent_market_cap_bought': insider_metrics.get('percent_market_cap_bought', 0),
                        'conviction_score': insider_metrics.get('insider_conviction_score', 0)
                    }
                
                return None
                
            except Exception as e:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(analyze_stock, symbol): symbol 
                              for symbol in self.stock_universe}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x['conviction_score'], reverse=True)
        return results[:15]
    
    def _screen_momentum_insider(self) -> List[Dict]:
        """Screen for stocks with price momentum and insider activity"""
        results = []
        
        def analyze_stock(symbol):
            try:
                metrics = self.get_comprehensive_insider_metrics(symbol, 60)
                if 'error' in metrics:
                    return None
                
                insider_metrics = metrics.get('insider_metrics', {})
                price_history = metrics.get('price_history', pd.DataFrame())
                
                if price_history.empty:
                    return None
                
                if len(price_history) >= 20:
                    price_20d_ago = price_history['Close'].iloc[-20]
                    current_price = price_history['Close'].iloc[-1]
                    momentum_20d = (current_price - price_20d_ago) / price_20d_ago * 100
                else:
                    momentum_20d = 0
                
                has_momentum = momentum_20d >= 10
                has_insider_activity = (
                    insider_metrics.get('unique_insider_buyers', 0) >= 1 and
                    insider_metrics.get('timing_score', 0) >= 60
                )
                
                if has_momentum and has_insider_activity:
                    return {
                        'symbol': symbol,
                        'company_name': metrics.get('company_name', symbol),
                        'momentum_20d': momentum_20d,
                        'insider_buyers': insider_metrics.get('unique_insider_buyers', 0),
                        'timing_score': insider_metrics.get('timing_score', 0),
                        'net_insider_value': insider_metrics.get('net_insider_value', 0),
                        'current_price': metrics.get('current_price', 0)
                    }
                
                return None
                
            except Exception as e:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(analyze_stock, symbol): symbol 
                              for symbol in self.stock_universe}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x['momentum_20d'], reverse=True)
        return results[:15]
    
    def _screen_executive_confidence(self) -> List[Dict]:
        """Screen for stocks with executive-level insider buying"""
        results = []
        
        def analyze_stock(symbol):
            try:
                metrics = self.get_comprehensive_insider_metrics(symbol, 90)
                if 'error' in metrics:
                    return None
                
                insider_data = metrics.get('insider_data', {})
                insider_trades = insider_data.get('insider_trades', [])
                
                executive_purchases = [
                    t for t in insider_trades 
                    if t['transaction_type'] == 'Purchase' and 
                    t['title'] in ['CEO', 'CFO', 'President', 'COO', 'Chairman']
                ]
                
                if len(executive_purchases) >= 2:
                    total_executive_value = sum(t['value'] for t in executive_purchases)
                    avg_executive_purchase = total_executive_value / len(executive_purchases)
                    
                    return {
                        'symbol': symbol,
                        'company_name': metrics.get('company_name', symbol),
                        'executive_purchases': len(executive_purchases),
                        'total_executive_value': total_executive_value,
                        'avg_executive_purchase': avg_executive_purchase,
                        'executive_titles': list(set(t['title'] for t in executive_purchases)),
                        'market_cap': metrics.get('market_cap', 0)
                    }
                
                return None
                
            except Exception as e:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(analyze_stock, symbol): symbol 
                              for symbol in self.stock_universe}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x['total_executive_value'], reverse=True)
        return results[:12]
    
    def _screen_hidden_gems(self) -> List[Dict]:
        """Screen for hidden gems with strong insider activity but low attention"""
        results = []
        
        def analyze_stock(symbol):
            try:
                metrics = self.get_comprehensive_insider_metrics(symbol, 120)
                if 'error' in metrics:
                    return None
                
                insider_metrics = metrics.get('insider_metrics', {})
                valuation_metrics = metrics.get('valuation_metrics', {})
                market_cap = metrics.get('market_cap', 0)
                
                small_to_mid_cap = 100000000 <= market_cap <= 10000000000
                strong_insider_activity = (
                    insider_metrics.get('unique_insider_buyers', 0) >= 3 and
                    insider_metrics.get('insider_conviction_score', 0) >= 75
                )
                reasonable_growth = valuation_metrics.get('revenue_growth', 0) > 0.05
                
                if small_to_mid_cap and strong_insider_activity and reasonable_growth:
                    return {
                        'symbol': symbol,
                        'company_name': metrics.get('company_name', symbol),
                        'market_cap': market_cap,
                        'insider_buyers': insider_metrics.get('unique_insider_buyers', 0),
                        'conviction_score': insider_metrics.get('insider_conviction_score', 0),
                        'revenue_growth': valuation_metrics.get('revenue_growth', 0) * 100,
                        'percent_market_cap_bought': insider_metrics.get('percent_market_cap_bought', 0),
                        'pe_ratio': valuation_metrics.get('pe_ratio', 0)
                    }
                
                return None
                
            except Exception as e:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(analyze_stock, symbol): symbol 
                              for symbol in self.stock_universe}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: x['conviction_score'], reverse=True)
        return results[:10]
    
    def _screen_insider_selling(self) -> List[Dict]:
        """Screen for stocks with concerning insider selling patterns"""
        results = []
        
        def analyze_stock(symbol):
            try:
                metrics = self.get_comprehensive_insider_metrics(symbol, 60)
                if 'error' in metrics:
                    return None
                
                insider_metrics = metrics.get('insider_metrics', {})
                
                heavy_selling = (
                    insider_metrics.get('insider_seller_count', 0) >= 3 and
                    insider_metrics.get('buy_sell_value_ratio', 999) < 0.5 and
                    insider_metrics.get('percent_market_cap_sold', 0) > 0.2
                )
                
                if heavy_selling:
                    return {
                        'symbol': symbol,
                        'company_name': metrics.get('company_name', symbol),
                        'insider_sellers': insider_metrics.get('unique_insider_sellers', 0),
                        'percent_market_cap_sold': insider_metrics.get('percent_market_cap_sold', 0),
                        'net_insider_value': insider_metrics.get('net_insider_value', 0),
                        'buy_sell_ratio': insider_metrics.get('buy_sell_value_ratio', 0),
                        'market_cap': metrics.get('market_cap', 0)
                    }
                
                return None
                
            except Exception as e:
                return None
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            future_to_symbol = {executor.submit(analyze_stock, symbol): symbol 
                              for symbol in self.stock_universe}
            
            for future in as_completed(future_to_symbol):
                result = future.result()
                if result:
                    results.append(result)
        
        results.sort(key=lambda x: abs(x['net_insider_value']), reverse=True)
        return results[:12]
    
    def generate_price_insider_overlay_data(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Generate data for price chart with insider activity overlay"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                return {'error': 'No price data available'}
            
            lookback_days = {'3mo': 90, '6mo': 180, '1y': 365, '2y': 730}.get(period, 365)
            insider_data = self.insider_intel.get_insider_data(symbol, lookback_days)
            
            if 'error' in insider_data:
                return insider_data
            
            insider_trades = insider_data.get('insider_trades', [])
            
            overlay_data = {
                'symbol': symbol,
                'price_data': hist,
                'insider_transactions': [],
                'summary_stats': {
                    'total_transactions': len(insider_trades),
                    'buy_transactions': len([t for t in insider_trades if t['transaction_type'] == 'Purchase']),
                    'sell_transactions': len([t for t in insider_trades if t['transaction_type'] == 'Sale']),
                    'date_range': f"{hist.index[0].strftime('%Y-%m-%d')} to {hist.index[-1].strftime('%Y-%m-%d')}"
                }
            }
            
            for trade in insider_trades:
                trade_date = pd.to_datetime(trade['date'])
                
                if trade_date in hist.index:
                    price_at_trade = hist.loc[trade_date, 'Close']
                elif trade_date < hist.index[-1]:
                    future_dates = hist.index[hist.index > trade_date]
                    if len(future_dates) > 0:
                        trade_date = future_dates[0]
                        price_at_trade = hist.loc[trade_date, 'Close']
                    else:
                        continue
                else:
                    continue
                
                current_price = hist['Close'][-1]
                performance_since_trade = (current_price - price_at_trade) / price_at_trade * 100
                
                transaction_data = {
                    'date': trade_date,
                    'insider_name': trade['insider_name'],
                    'title': trade['title'],
                    'transaction_type': trade['transaction_type'],
                    'shares': trade['shares'],
                    'price_at_trade': price_at_trade,
                    'value': trade['value'],
                    'performance_since': performance_since_trade,
                    'chart_annotation': {
                        'x': trade_date,
                        'y': price_at_trade,
                        'color': '#22c55e' if trade['transaction_type'] == 'Purchase' else '#ef4444',
                        'symbol': 'triangle-up' if trade['transaction_type'] == 'Purchase' else 'triangle-down',
                        'size': min(max(trade['value'] / 100000, 8), 20)
                    }
                }
                
                overlay_data['insider_transactions'].append(transaction_data)
            
            return overlay_data
            
        except Exception as e:
            return {'error': str(e), 'symbol': symbol} 