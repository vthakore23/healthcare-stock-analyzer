import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional
import json
from bs4 import BeautifulSoup
import yfinance as yf
import time
import warnings
warnings.filterwarnings('ignore')

class PatentCliffAnalyzer:
    """Advanced patent cliff analyzer with real-time patent and revenue data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.patent_databases = {
            'uspto': 'https://patents.uspto.gov/api/',
            'epo': 'https://ops.epo.org/',
            'google_patents': 'https://patents.google.com/'
        }
        
    def analyze_patent_portfolio(self, ticker: str) -> Dict:
        """Analyze company's patent portfolio and expiration timeline"""
        try:
            # Get company information
            stock = yf.Ticker(ticker)
            info = stock.info
            company_name = info.get('longName', ticker)
            
            # Search for patents
            patent_data = self._search_company_patents(company_name, ticker)
            
            # Analyze patent cliff timing
            cliff_analysis = self._analyze_patent_cliffs(patent_data)
            
            # Get revenue data for impact analysis
            revenue_data = self._get_revenue_data(ticker)
            
            # Calculate financial impact
            financial_impact = self._calculate_financial_impact(cliff_analysis, revenue_data)
            
            return {
                'ticker': ticker,
                'company_name': company_name,
                'patent_portfolio': patent_data,
                'cliff_analysis': cliff_analysis,
                'financial_impact': financial_impact,
                'revenue_data': revenue_data,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to analyze patent portfolio: {str(e)}",
                'ticker': ticker,
                'patent_portfolio': {},
                'cliff_analysis': {},
                'financial_impact': {}
            }
    
    def _search_company_patents(self, company_name: str, ticker: str) -> Dict:
        """Search for company patents from multiple sources"""
        patents = {
            'active_patents': [],
            'expired_patents': [],
            'pending_applications': [],
            'total_count': 0
        }
        
        try:
            # Mock patent data - in production, use actual patent APIs
            mock_patents = self._generate_mock_patent_data(company_name)
            patents['active_patents'].extend(mock_patents['active'])
            patents['expired_patents'].extend(mock_patents['expired'])
            patents['pending_applications'].extend(mock_patents['pending'])
            
            patents['total_count'] = (len(patents['active_patents']) + 
                                    len(patents['expired_patents']) + 
                                    len(patents['pending_applications']))
            
            return patents
            
        except Exception as e:
            return {
                'active_patents': [],
                'expired_patents': [],
                'pending_applications': [],
                'total_count': 0,
                'error': str(e)
            }
    
    def _generate_mock_patent_data(self, search_term: str) -> Dict:
        """Generate mock patent data - replace with real API calls in production"""
        import random
        
        current_year = datetime.now().year
        
        # Generate active patents
        active_patents = []
        for i in range(random.randint(5, 15)):
            filing_year = random.randint(current_year - 15, current_year - 2)
            expiry_year = filing_year + 20  # Standard patent term
            
            patent = {
                'patent_number': f"US{random.randint(8000000, 9999999)}",
                'title': f"Pharmaceutical compound and method of treatment {i+1}",
                'filing_date': f"{filing_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                'expiry_date': f"{expiry_year}-{random.randint(1,12):02d}-{random.randint(1,28):02d}",
                'status': 'Active',
                'technology_area': random.choice(['Pharmaceuticals', 'Biotechnology', 'Medical Devices']),
                'estimated_revenue_share': random.uniform(0.05, 0.30),
                'blockbuster_potential': random.choice([True, False])
            }
            active_patents.append(patent)
        
        return {
            'active': active_patents,
            'expired': [],
            'pending': []
        }
    
    def _analyze_patent_cliffs(self, patent_data: Dict) -> Dict:
        """Analyze patent cliff timing and severity"""
        try:
            current_date = datetime.now()
            
            cliff_timeline = {}
            major_cliffs = []
            
            # Analyze active patents for upcoming expirations
            for patent in patent_data.get('active_patents', []):
                expiry_date = datetime.strptime(patent['expiry_date'], '%Y-%m-%d')
                years_to_expiry = (expiry_date - current_date).days / 365.25
                
                if years_to_expiry > 0 and years_to_expiry <= 10:  # Next 10 years
                    year = int(expiry_date.year)
                    
                    if year not in cliff_timeline:
                        cliff_timeline[year] = {
                            'patents_expiring': 0,
                            'estimated_revenue_impact': 0,
                            'patents': []
                        }
                    
                    cliff_timeline[year]['patents_expiring'] += 1
                    cliff_timeline[year]['estimated_revenue_impact'] += patent.get('estimated_revenue_share', 0)
                    cliff_timeline[year]['patents'].append(patent)
                    
                    # Identify major cliffs (>15% revenue impact)
                    if patent.get('estimated_revenue_share', 0) > 0.15:
                        major_cliffs.append({
                            'patent_number': patent['patent_number'],
                            'title': patent['title'],
                            'expiry_date': patent['expiry_date'],
                            'revenue_impact': patent['estimated_revenue_share'],
                            'years_remaining': round(years_to_expiry, 1),
                            'severity': 'High' if patent['estimated_revenue_share'] > 0.25 else 'Medium'
                        })
            
            return {
                'cliff_timeline': cliff_timeline,
                'major_cliffs': sorted(major_cliffs, key=lambda x: x['years_remaining']),
                'next_major_cliff': min(major_cliffs, key=lambda x: x['years_remaining']) if major_cliffs else None,
                'total_patents_at_risk': sum(data['patents_expiring'] for data in cliff_timeline.values())
            }
            
        except Exception as e:
            return {
                'cliff_timeline': {},
                'major_cliffs': [],
                'error': str(e)
            }
    
    def _get_revenue_data(self, ticker: str) -> Dict:
        """Get revenue data for impact calculations"""
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            current_revenue = info.get('totalRevenue', 0) / 1e9 if info.get('totalRevenue') else 0
            
            return {
                'current_annual_revenue': current_revenue,
                'average_growth_rate': 0
            }
            
        except Exception as e:
            return {
                'error': f"Failed to get revenue data: {str(e)}",
                'current_annual_revenue': 0,
                'average_growth_rate': 0
            }
    
    def _calculate_financial_impact(self, cliff_analysis: Dict, revenue_data: Dict) -> Dict:
        """Calculate financial impact of patent cliffs"""
        try:
            current_revenue = revenue_data.get('current_annual_revenue', 0)
            
            if current_revenue == 0:
                return {'error': 'No revenue data available for impact calculation'}
            
            impact_scenarios = {}
            cumulative_impact = 0
            
            # Calculate year-by-year impact
            for year, cliff_data in cliff_analysis.get('cliff_timeline', {}).items():
                revenue_at_risk = current_revenue * cliff_data['estimated_revenue_impact']
                generic_impact = revenue_at_risk * 0.85
                
                impact_scenarios[year] = {
                    'revenue_at_risk': round(revenue_at_risk, 2),
                    'expected_loss_to_generics': round(generic_impact, 2),
                    'percentage_of_total_revenue': round(cliff_data['estimated_revenue_impact'] * 100, 1),
                    'patents_expiring': cliff_data['patents_expiring']
                }
                
                cumulative_impact += generic_impact
            
            total_revenue_at_risk = sum(scenario['revenue_at_risk'] for scenario in impact_scenarios.values())
            portfolio_risk_score = min((total_revenue_at_risk / current_revenue) * 100, 100) if current_revenue > 0 else 0
            
            return {
                'impact_by_year': impact_scenarios,
                'total_revenue_at_risk': round(total_revenue_at_risk, 2),
                'cumulative_expected_loss': round(cumulative_impact, 2),
                'portfolio_risk_score': round(portfolio_risk_score, 1),
                'risk_level': 'High' if portfolio_risk_score > 30 else 'Medium' if portfolio_risk_score > 15 else 'Low'
            }
            
        except Exception as e:
            return {
                'error': f"Failed to calculate financial impact: {str(e)}",
                'impact_by_year': {},
                'total_revenue_at_risk': 0
            }
    
    def analyze_biosimilar_threats(self, ticker: str) -> Dict:
        """Analyze biosimilar competition threats"""
        try:
            # Get company's biologic products
            biologics = self._identify_biologic_products(ticker)
            
            # Search for biosimilar development
            biosimilar_threats = []
            
            for biologic in biologics:
                competitors = self._search_biosimilar_competitors(biologic)
                
                if competitors:
                    threat_analysis = {
                        'product_name': biologic['name'],
                        'annual_revenue': biologic['revenue'],
                        'patent_expiry': biologic['patent_expiry'],
                        'biosimilar_competitors': competitors,
                        'threat_level': self._assess_biosimilar_threat_level(competitors, biologic),
                        'estimated_market_share_loss': self._estimate_biosimilar_impact(competitors)
                    }
                    biosimilar_threats.append(threat_analysis)
            
            return {
                'ticker': ticker,
                'biologic_products': biologics,
                'biosimilar_threats': biosimilar_threats,
                'total_revenue_at_risk': sum(threat['annual_revenue'] * threat['estimated_market_share_loss'] 
                                           for threat in biosimilar_threats),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to analyze biosimilar threats: {str(e)}",
                'ticker': ticker,
                'biosimilar_threats': []
            }
    
    def _identify_biologic_products(self, ticker: str) -> List[Dict]:
        """Identify company's biologic products (mock data - use real product databases in production)"""
        import random
        
        # Mock biologic products
        mock_biologics = [
            {'name': 'Therapeutic Antibody A', 'revenue': random.uniform(1, 5), 'patent_expiry': '2027-03-15'},
            {'name': 'Recombinant Protein B', 'revenue': random.uniform(0.5, 3), 'patent_expiry': '2026-08-22'},
            {'name': 'Monoclonal Antibody C', 'revenue': random.uniform(2, 8), 'patent_expiry': '2028-11-10'}
        ]
        
        return mock_biologics[:random.randint(1, 3)]
    
    def _search_biosimilar_competitors(self, biologic: Dict) -> List[Dict]:
        """Search for biosimilar competitors (mock data)"""
        import random
        
        # Mock biosimilar competitors
        competitors = []
        num_competitors = random.randint(0, 3)
        
        for i in range(num_competitors):
            competitor = {
                'company': f'Biosimilar Company {i+1}',
                'development_stage': random.choice(['Phase III', 'Filed', 'Approved']),
                'expected_launch': f'202{random.randint(5, 8)}-Q{random.randint(1, 4)}',
                'approval_probability': random.uniform(0.6, 0.9)
            }
            competitors.append(competitor)
        
        return competitors
    
    def _assess_biosimilar_threat_level(self, competitors: List[Dict], biologic: Dict) -> str:
        """Assess threat level based on competitor analysis"""
        if not competitors:
            return 'Low'
        
        approved_competitors = sum(1 for comp in competitors if comp['development_stage'] == 'Approved')
        late_stage_competitors = sum(1 for comp in competitors if comp['development_stage'] in ['Phase III', 'Filed'])
        
        if approved_competitors >= 2:
            return 'Very High'
        elif approved_competitors >= 1 or late_stage_competitors >= 3:
            return 'High'
        elif late_stage_competitors >= 1:
            return 'Medium'
        else:
            return 'Low'
    
    def _estimate_biosimilar_impact(self, competitors: List[Dict]) -> float:
        """Estimate market share loss to biosimilars"""
        if not competitors:
            return 0.0
        
        # Historical biosimilar impact: 15-30% market share loss in first year
        approved_competitors = sum(1 for comp in competitors if comp['development_stage'] == 'Approved')
        
        if approved_competitors == 0:
            return 0.0
        elif approved_competitors == 1:
            return 0.20  # 20% market share loss
        else:
            return min(0.15 + (approved_competitors - 1) * 0.10, 0.50)  # Max 50% loss
    
    def get_patent_cliff_alerts(self, ticker: str, alert_threshold_years: int = 2) -> List[Dict]:
        """Get alerts for patents expiring within threshold period"""
        try:
            analysis = self.analyze_patent_portfolio(ticker)
            
            if 'error' in analysis:
                return []
            
            alerts = []
            current_date = datetime.now()
            
            for cliff in analysis['cliff_analysis'].get('major_cliffs', []):
                if cliff['years_remaining'] <= alert_threshold_years:
                    urgency = 'critical' if cliff['years_remaining'] <= 1 else 'high'
                    
                    alert = {
                        'type': 'patent_expiry',
                        'urgency': urgency,
                        'title': f"Major patent expiring in {cliff['years_remaining']:.1f} years",
                        'description': cliff['title'],
                        'expiry_date': cliff['expiry_date'],
                        'revenue_impact': f"{cliff['revenue_impact']*100:.1f}%",
                        'severity': cliff['severity'],
                        'patent_number': cliff['patent_number']
                    }
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            return [{
                'type': 'error',
                'title': 'Patent cliff alert generation failed',
                'description': str(e)
            }]
    
    def generate_replacement_pipeline_score(self, ticker: str) -> Dict:
        """Generate score for replacement pipeline strength"""
        try:
            # This would integrate with clinical trial data in production
            analysis = self.analyze_patent_portfolio(ticker)
            
            if 'error' in analysis:
                return {'error': analysis['error']}
            
            # Mock pipeline assessment
            import random
            
            pipeline_strength = {
                'late_stage_programs': random.randint(2, 8),
                'novel_mechanisms': random.randint(1, 5),
                'estimated_peak_sales': random.uniform(5, 20),  # Billions
                'replacement_score': random.uniform(0.3, 0.9)
            }
            
            # Calculate overall replacement capability
            cliff_impact = analysis['financial_impact'].get('total_revenue_at_risk', 0)
            replacement_capability = pipeline_strength['estimated_peak_sales']
            
            replacement_ratio = replacement_capability / cliff_impact if cliff_impact > 0 else 1.0
            
            return {
                'ticker': ticker,
                'pipeline_strength': pipeline_strength,
                'replacement_ratio': round(replacement_ratio, 2),
                'replacement_adequacy': 'Strong' if replacement_ratio > 1.2 else 'Adequate' if replacement_ratio > 0.8 else 'Weak',
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to generate replacement pipeline score: {str(e)}",
                'ticker': ticker
            } 