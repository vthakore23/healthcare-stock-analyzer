# Healthcare Metrics Calculator
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import math

class HealthcareMetricsCalculator:
    def __init__(self):
        # Scoring weights for MedEquity Score
        self.score_weights = {
            'financial_health': 0.3,
            'growth_potential': 0.25,
            'innovation_pipeline': 0.2,
            'market_position': 0.15,
            'risk_management': 0.1
        }
        
        # Subsector benchmarks
        self.subsector_benchmarks = {
            'Biotechnology': {
                'avg_pe': 25.0,
                'rd_intensity': 0.40,
                'profit_margin': 0.05,
                'debt_ratio': 0.3
            },
            'Pharmaceuticals': {
                'avg_pe': 15.0,
                'rd_intensity': 0.20,
                'profit_margin': 0.25,
                'debt_ratio': 0.4
            },
            'Medical Devices': {
                'avg_pe': 20.0,
                'rd_intensity': 0.10,
                'profit_margin': 0.20,
                'debt_ratio': 0.35
            },
            'Healthcare Services': {
                'avg_pe': 18.0,
                'rd_intensity': 0.02,
                'profit_margin': 0.08,
                'debt_ratio': 0.45
            }
        }

    def calculate_comprehensive_metrics(self, company_data: Dict) -> Dict[str, Any]:
        """Calculate comprehensive healthcare-specific metrics"""
        try:
            metrics = {}
            
            # Extract data
            basic_info = company_data.get('basic_info', {})
            financials = company_data.get('financials', {})
            pipeline = company_data.get('pipeline', [])
            is_healthcare = company_data.get('is_healthcare', False)
            subsector = company_data.get('subsector', 'Healthcare - Other')
            
            # Core financial metrics
            metrics.update(self._calculate_financial_metrics(financials, basic_info))
            
            # Healthcare-specific metrics
            if is_healthcare:
                metrics.update(self._calculate_healthcare_specific_metrics(
                    financials, basic_info, pipeline, subsector))
            
            # Risk metrics
            metrics.update(self._calculate_risk_metrics(financials, basic_info, subsector))
            
            # Valuation metrics
            metrics.update(self._calculate_valuation_metrics(financials, basic_info))
            
            # Innovation metrics
            metrics.update(self._calculate_innovation_metrics(pipeline, financials, basic_info))
            
            # Calculate MedEquity Score
            metrics['medequity_score'] = self._calculate_medequity_score(
                metrics, is_healthcare, subsector)
            
            # Calculate percentile rankings
            metrics.update(self._calculate_percentile_rankings(metrics, subsector))
            
            return metrics
            
        except Exception as e:
            return {'error': str(e), 'medequity_score': 50.0}

    def _calculate_financial_metrics(self, financials: Dict, basic_info: Dict) -> Dict:
        """Calculate core financial metrics"""
        metrics = {}
        
        # Revenue metrics
        revenue = financials.get('revenue', 0)
        if revenue and revenue > 0:
            metrics['revenue_billions'] = revenue / 1e9
            metrics['revenue_millions'] = revenue / 1e6
            metrics['log_revenue'] = math.log10(revenue) if revenue > 0 else 0
        
        # Profitability metrics
        profit_margin = financials.get('profit_margins')
        gross_margin = financials.get('gross_margins')
        operating_margin = financials.get('operating_margin')
        
        if profit_margin is not None:
            metrics['profit_margin_pct'] = profit_margin * 100
            metrics['profit_margin_score'] = min(profit_margin * 5, 1.0)  # Score 0-1
        
        if gross_margin is not None:
            metrics['gross_margin_pct'] = gross_margin * 100
            metrics['gross_margin_score'] = min(gross_margin * 2, 1.0)
        
        if operating_margin is not None:
            metrics['operating_margin_pct'] = operating_margin * 100
            metrics['operating_margin_score'] = min(operating_margin * 4, 1.0)
        
        # Growth metrics
        revenue_growth = financials.get('revenue_growth')
        earnings_growth = financials.get('earnings_growth')
        
        if revenue_growth is not None:
            metrics['revenue_growth_pct'] = revenue_growth * 100
            metrics['revenue_growth_score'] = min(max(revenue_growth + 0.5, 0) * 2, 1.0)
        
        if earnings_growth is not None:
            metrics['earnings_growth_pct'] = earnings_growth * 100
            metrics['earnings_growth_score'] = min(max(earnings_growth + 0.5, 0) * 2, 1.0)
        
        # Efficiency metrics
        roe = financials.get('return_on_equity')
        if roe is not None:
            metrics['roe_pct'] = roe * 100
            metrics['roe_score'] = min(roe * 5, 1.0)  # Score based on ROE
        
        # Cash metrics
        free_cash_flow = financials.get('free_cash_flow')
        total_cash = financials.get('total_cash')
        total_debt = financials.get('total_debt')
        
        if free_cash_flow:
            metrics['fcf_billions'] = free_cash_flow / 1e9
            if revenue and revenue > 0:
                metrics['fcf_margin'] = free_cash_flow / revenue
                metrics['fcf_margin_pct'] = (free_cash_flow / revenue) * 100
        
        if total_cash and total_debt:
            metrics['net_cash'] = total_cash - total_debt
            metrics['net_cash_billions'] = (total_cash - total_debt) / 1e9
            metrics['cash_debt_ratio'] = total_cash / total_debt if total_debt > 0 else 10
        
        return metrics

    def _calculate_healthcare_specific_metrics(self, financials: Dict, basic_info: Dict, 
                                             pipeline: List, subsector: str) -> Dict:
        """Calculate healthcare-specific metrics"""
        metrics = {}
        
        # R&D Intensity
        rd_intensity = financials.get('rd_intensity')
        if rd_intensity is not None:
            metrics['rd_intensity_pct'] = rd_intensity * 100
            
            # Score R&D relative to subsector
            benchmark = self.subsector_benchmarks.get(subsector, {}).get('rd_intensity', 0.15)
            metrics['rd_intensity_vs_benchmark'] = (rd_intensity / benchmark) if benchmark > 0 else 1
            metrics['rd_intensity_score'] = min(rd_intensity * 10, 1.0)
        
        # Pipeline metrics
        if pipeline and isinstance(pipeline, list):
            pipeline_count = len([p for p in pipeline if isinstance(p, dict)])
            metrics['pipeline_count'] = pipeline_count
            
            # Phase distribution
            phases = {}
            for item in pipeline:
                if isinstance(item, dict) and 'phase' in item:
                    phase = item['phase']
                    phases[phase] = phases.get(phase, 0) + 1
            
            metrics['pipeline_phases'] = phases
            
            # Pipeline value score (rough estimate)
            phase_values = {
                'Preclinical': 1,
                'Phase I': 2,
                'Phase II': 4,
                'Phase III': 8,
                'Approved/Commercial': 15
            }
            
            pipeline_value_score = 0
            for phase, count in phases.items():
                value = phase_values.get(phase, 1)
                pipeline_value_score += value * count
            
            metrics['pipeline_value_score'] = pipeline_value_score
            metrics['pipeline_score'] = min(pipeline_value_score / 20, 1.0)  # Normalized score
        
        # Market cap health score
        market_cap = basic_info.get('marketCap', 0)
        if market_cap > 0:
            metrics['market_cap_billions'] = market_cap / 1e9
            
            # Market cap health relative to subsector
            if market_cap > 50e9:
                metrics['market_cap_tier_score'] = 1.0  # Large cap
            elif market_cap > 10e9:
                metrics['market_cap_tier_score'] = 0.8   # Mid cap
            elif market_cap > 2e9:
                metrics['market_cap_tier_score'] = 0.6   # Small cap
            else:
                metrics['market_cap_tier_score'] = 0.4   # Micro cap
        
        return metrics

    def _calculate_risk_metrics(self, financials: Dict, basic_info: Dict, subsector: str) -> Dict:
        """Calculate risk-related metrics"""
        metrics = {}
        
        # Financial risk metrics
        debt_to_equity = financials.get('debt_to_equity')
        current_ratio = financials.get('current_ratio')
        beta = financials.get('beta')
        
        if debt_to_equity is not None:
            metrics['debt_to_equity'] = debt_to_equity
            # Lower debt = better score
            metrics['debt_score'] = max(1 - (debt_to_equity / 2), 0)
        
        if current_ratio is not None:
            metrics['current_ratio'] = current_ratio
            # Optimal current ratio around 1.5-2.5
            if 1.5 <= current_ratio <= 2.5:
                metrics['liquidity_score'] = 1.0
            elif current_ratio >= 1.0:
                metrics['liquidity_score'] = 0.8
            else:
                metrics['liquidity_score'] = current_ratio * 0.5
        
        if beta is not None:
            metrics['beta'] = beta
            # Lower beta = lower risk (but also potentially lower returns)
            metrics['beta_risk_score'] = max(1 - abs(beta - 1) * 0.5, 0)
        
        # Subsector risk adjustment
        subsector_risk_multipliers = {
            'Biotechnology': 0.7,        # Higher risk
            'Pharmaceuticals': 0.9,      # Medium risk
            'Medical Devices': 0.85,     # Medium risk
            'Healthcare Services': 0.95,  # Lower risk
            'Diagnostics': 0.8,          # Medium risk
            'Digital Health': 0.75       # Higher risk
        }
        
        metrics['subsector_risk_multiplier'] = subsector_risk_multipliers.get(subsector, 0.8)
        
        return metrics

    def _calculate_valuation_metrics(self, financials: Dict, basic_info: Dict) -> Dict:
        """Calculate valuation metrics"""
        metrics = {}
        
        pe_ratio = financials.get('pe_ratio')
        forward_pe = financials.get('forward_pe')
        peg_ratio = financials.get('peg_ratio')
        price_to_book = financials.get('price_to_book')
        
        if pe_ratio is not None and pe_ratio > 0:
            metrics['pe_ratio'] = pe_ratio
            # Score PE ratio (lower is generally better, but context matters)
            if pe_ratio < 15:
                metrics['pe_score'] = 1.0
            elif pe_ratio < 25:
                metrics['pe_score'] = 0.8
            elif pe_ratio < 40:
                metrics['pe_score'] = 0.6
            else:
                metrics['pe_score'] = 0.4
        
        if forward_pe is not None and forward_pe > 0:
            metrics['forward_pe'] = forward_pe
            metrics['forward_pe_score'] = min(30 / forward_pe if forward_pe > 0 else 0, 1.0)
        
        if peg_ratio is not None and peg_ratio > 0:
            metrics['peg_ratio'] = peg_ratio
            # PEG ratio < 1 is generally considered attractive
            metrics['peg_score'] = max(1 - peg_ratio, 0) if peg_ratio > 0 else 0
        
        if price_to_book is not None and price_to_book > 0:
            metrics['price_to_book'] = price_to_book
            # P/B scoring (lower generally better)
            metrics['pb_score'] = max(1 - (price_to_book - 1) * 0.2, 0) if price_to_book > 0 else 0
        
        return metrics

    def _calculate_innovation_metrics(self, pipeline: List, financials: Dict, basic_info: Dict) -> Dict:
        """Calculate innovation and growth potential metrics"""
        metrics = {}
        
        # R&D efficiency
        rd_intensity = financials.get('rd_intensity', 0)
        pipeline_count = len(pipeline) if pipeline else 0
        
        if rd_intensity > 0 and pipeline_count > 0:
            metrics['rd_efficiency'] = pipeline_count / rd_intensity
            metrics['rd_efficiency_score'] = min(metrics['rd_efficiency'] / 20, 1.0)
        
        # Innovation momentum (based on pipeline breadth)
        if pipeline and isinstance(pipeline, list):
            unique_indications = set()
            for item in pipeline:
                if isinstance(item, dict) and 'indication' in item:
                    unique_indications.add(item['indication'])
            
            metrics['pipeline_breadth'] = len(unique_indications)
            metrics['innovation_breadth_score'] = min(len(unique_indications) / 5, 1.0)
        
        # Patent cliff risk (simplified assessment)
        description = basic_info.get('longBusinessSummary', '').lower()
        if 'patent' in description:
            if 'expir' in description or 'cliff' in description:
                metrics['patent_risk_flag'] = True
                metrics['patent_risk_score'] = 0.5
            else:
                metrics['patent_risk_flag'] = False
                metrics['patent_risk_score'] = 0.8
        else:
            metrics['patent_risk_score'] = 0.7  # Neutral
        
        return metrics

    def _calculate_medequity_score(self, metrics: Dict, is_healthcare: bool, subsector: str) -> float:
        """Calculate the proprietary MedEquity Score (0-100)"""
        if not is_healthcare:
            return 50.0  # Neutral score for non-healthcare
        
        try:
            # Component scores (0-1)
            financial_health = self._score_financial_health(metrics)
            growth_potential = self._score_growth_potential(metrics)
            innovation_pipeline = self._score_innovation_pipeline(metrics)
            market_position = self._score_market_position(metrics)
            risk_management = self._score_risk_management(metrics)
            
            # Apply weights
            weighted_score = (
                financial_health * self.score_weights['financial_health'] +
                growth_potential * self.score_weights['growth_potential'] +
                innovation_pipeline * self.score_weights['innovation_pipeline'] +
                market_position * self.score_weights['market_position'] +
                risk_management * self.score_weights['risk_management']
            )
            
            # Apply subsector adjustment
            subsector_multiplier = metrics.get('subsector_risk_multiplier', 0.8)
            adjusted_score = weighted_score * (0.5 + subsector_multiplier * 0.5)
            
            # Convert to 0-100 scale
            final_score = max(min(adjusted_score * 100, 100), 0)
            
            return round(final_score, 1)
            
        except Exception:
            return 50.0  # Default on error

    def _score_financial_health(self, metrics: Dict) -> float:
        """Score financial health component"""
        scores = []
        
        # Profitability
        if 'profit_margin_score' in metrics:
            scores.append(metrics['profit_margin_score'])
        
        # Cash flow
        if 'fcf_margin' in metrics:
            fcf_score = min(max(metrics['fcf_margin'] * 10, 0), 1)
            scores.append(fcf_score)
        
        # ROE
        if 'roe_score' in metrics:
            scores.append(metrics['roe_score'])
        
        # Debt management
        if 'debt_score' in metrics:
            scores.append(metrics['debt_score'])
        
        # Liquidity
        if 'liquidity_score' in metrics:
            scores.append(metrics['liquidity_score'])
        
        return np.mean(scores) if scores else 0.5

    def _score_growth_potential(self, metrics: Dict) -> float:
        """Score growth potential component"""
        scores = []
        
        # Revenue growth
        if 'revenue_growth_score' in metrics:
            scores.append(metrics['revenue_growth_score'])
        
        # Earnings growth
        if 'earnings_growth_score' in metrics:
            scores.append(metrics['earnings_growth_score'])
        
        # Market cap tier (growth potential inverse to size)
        if 'market_cap_tier_score' in metrics:
            # Invert for growth potential (smaller companies have higher growth potential)
            growth_tier_score = 1.5 - metrics['market_cap_tier_score']
            scores.append(max(min(growth_tier_score, 1), 0))
        
        return np.mean(scores) if scores else 0.5

    def _score_innovation_pipeline(self, metrics: Dict) -> float:
        """Score innovation and pipeline component"""
        scores = []
        
        # R&D intensity
        if 'rd_intensity_score' in metrics:
            scores.append(metrics['rd_intensity_score'])
        
        # Pipeline score
        if 'pipeline_score' in metrics:
            scores.append(metrics['pipeline_score'])
        
        # R&D efficiency
        if 'rd_efficiency_score' in metrics:
            scores.append(metrics['rd_efficiency_score'])
        
        # Innovation breadth
        if 'innovation_breadth_score' in metrics:
            scores.append(metrics['innovation_breadth_score'])
        
        # Patent risk
        if 'patent_risk_score' in metrics:
            scores.append(metrics['patent_risk_score'])
        
        return np.mean(scores) if scores else 0.4  # Lower default for innovation

    def _score_market_position(self, metrics: Dict) -> float:
        """Score market position component"""
        scores = []
        
        # Market cap tier
        if 'market_cap_tier_score' in metrics:
            scores.append(metrics['market_cap_tier_score'])
        
        # Valuation attractiveness
        valuation_scores = []
        if 'pe_score' in metrics:
            valuation_scores.append(metrics['pe_score'])
        if 'peg_score' in metrics:
            valuation_scores.append(metrics['peg_score'])
        if 'pb_score' in metrics:
            valuation_scores.append(metrics['pb_score'])
        
        if valuation_scores:
            scores.append(np.mean(valuation_scores))
        
        return np.mean(scores) if scores else 0.5

    def _score_risk_management(self, metrics: Dict) -> float:
        """Score risk management component"""
        scores = []
        
        # Beta risk
        if 'beta_risk_score' in metrics:
            scores.append(metrics['beta_risk_score'])
        
        # Debt management
        if 'debt_score' in metrics:
            scores.append(metrics['debt_score'])
        
        # Liquidity
        if 'liquidity_score' in metrics:
            scores.append(metrics['liquidity_score'])
        
        return np.mean(scores) if scores else 0.6

    def _calculate_percentile_rankings(self, metrics: Dict, subsector: str) -> Dict:
        """Calculate percentile rankings vs peers (simplified)"""
        rankings = {}
        
        # Use benchmark data to estimate percentiles
        benchmark = self.subsector_benchmarks.get(subsector, {})
        
        # PE percentile
        if 'pe_ratio' in metrics and 'avg_pe' in benchmark:
            pe_ratio = metrics['pe_ratio']
            avg_pe = benchmark['avg_pe']
            # Lower PE = better percentile
            pe_percentile = max(100 - (pe_ratio / avg_pe) * 50, 10)
            rankings['pe_percentile'] = min(pe_percentile, 90)
        
        # R&D intensity percentile  
        if 'rd_intensity_pct' in metrics and 'rd_intensity' in benchmark:
            rd_intensity = metrics['rd_intensity_pct'] / 100
            avg_rd = benchmark['rd_intensity']
            # Higher R&D intensity = better percentile (for innovation)
            rd_percentile = min((rd_intensity / avg_rd) * 50 + 25, 90)
            rankings['rd_percentile'] = max(rd_percentile, 10)
        
        # Profit margin percentile
        if 'profit_margin_pct' in metrics and 'profit_margin' in benchmark:
            profit_margin = metrics['profit_margin_pct'] / 100
            avg_margin = benchmark['profit_margin']
            margin_percentile = min((profit_margin / avg_margin) * 50 + 25, 90)
            rankings['profit_margin_percentile'] = max(margin_percentile, 10)
        
        return rankings

def calculate_healthcare_metrics(company_data: Dict) -> Dict[str, Any]:
    """Convenience function for calculating comprehensive healthcare metrics"""
    calculator = HealthcareMetricsCalculator()
    return calculator.calculate_comprehensive_metrics(company_data)
