import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import re
from dataclasses import dataclass

@dataclass
class HealthcareClassification:
    """Structured healthcare classification result"""
    is_healthcare: bool
    primary_subsector: str
    secondary_subsector: Optional[str]
    confidence_score: float
    market_cap_tier: str
    business_model: str
    risk_profile: str
    growth_stage: str
    regulatory_risk: str
    revenue_model: List[str]

class HealthcareClassifier:
    def __init__(self):
        self.healthcare_keywords = {
            'biotechnology': {
                'primary': ['biotech', 'biotechnology', 'biologic', 'monoclonal', 'gene therapy', 
                           'immunotherapy', 'biologics', 'biosimilar', 'antibody'],
                'secondary': ['crispr', 'rna', 'protein', 'enzyme', 'peptide', 'vaccine', 'cell therapy'],
                'weight': 1.0
            },
            'pharmaceuticals': {
                'primary': ['pharmaceutical', 'pharma', 'drug', 'medicine', 'compound', 'molecule'],
                'secondary': ['formulation', 'generic', 'branded', 'prescription', 'therapeutic'],
                'weight': 1.0
            },
            'medical_devices': {
                'primary': ['medical device', 'surgical', 'implant', 'diagnostic equipment', 
                           'medical equipment', 'instrument'],
                'secondary': ['catheter', 'stent', 'pacemaker', 'prosthetic', 'imaging', 'monitoring'],
                'weight': 0.9
            },
            'healthcare_services': {
                'primary': ['hospital', 'health system', 'clinic', 'health insurance', 
                           'managed care', 'pharmacy benefit'],
                'secondary': ['provider', 'healthcare services', 'medical services', 'health plan'],
                'weight': 0.8
            },
            'diagnostics': {
                'primary': ['diagnostic', 'laboratory', 'testing', 'assay', 'screening'],
                'secondary': ['pathology', 'genomic testing', 'molecular diagnostics', 'biomarker'],
                'weight': 0.9
            },
            'digital_health': {
                'primary': ['digital health', 'telemedicine', 'health technology', 'digital therapeutic'],
                'secondary': ['health app', 'remote monitoring', 'ai health', 'electronic health record'],
                'weight': 0.8
            }
        }
        
        self.business_models = {
            'product_sales': ['sales', 'revenue', 'commercial', 'marketing'],
            'licensing': ['licensing', 'royalty', 'partnership', 'collaboration'],
            'services': ['services', 'consulting', 'contract', 'fee'],
            'subscription': ['subscription', 'saas', 'platform', 'recurring'],
            'transaction': ['transaction', 'processing', 'per-use', 'volume-based']
        }
        
        self.risk_indicators = {
            'high_risk': ['preclinical', 'phase i', 'phase 1', 'early stage', 'development'],
            'medium_risk': ['phase ii', 'phase iii', 'phase 2', 'phase 3', 'late stage'],
            'low_risk': ['approved', 'commercial', 'established', 'mature', 'profitable']
        }

    def classify_healthcare_company(self, data: Dict) -> HealthcareClassification:
        """Advanced classification of healthcare companies"""
        
        if not isinstance(data, dict) or 'basic_info' not in data:
            return self._create_default_classification(False)
        
        basic_info = data.get('basic_info', {})
        financials = data.get('financials', {})
        
        # Step 1: Determine if healthcare
        is_healthcare, healthcare_score = self._is_healthcare_company(basic_info)
        
        if not is_healthcare:
            return self._create_default_classification(False)
        
        # Step 2: Classify subsector
        primary_subsector, secondary_subsector, subsector_confidence = self._classify_subsector(basic_info)
        
        # Step 3: Determine market cap tier
        market_cap_tier = self._determine_market_cap_tier(basic_info.get('marketCap', 0))
        
        # Step 4: Identify business model
        business_model = self._identify_business_model(basic_info)
        
        # Step 5: Assess risk profile
        risk_profile = self._assess_risk_profile(basic_info, primary_subsector, financials)
        
        # Step 6: Determine growth stage
        growth_stage = self._determine_growth_stage(basic_info, financials)
        
        # Step 7: Assess regulatory risk
        regulatory_risk = self._assess_regulatory_risk(primary_subsector, basic_info)
        
        # Step 8: Identify revenue models
        revenue_model = self._identify_revenue_models(basic_info)
        
        # Calculate overall confidence
        confidence_score = min(healthcare_score * subsector_confidence, 1.0)
        
        return HealthcareClassification(
            is_healthcare=is_healthcare,
            primary_subsector=primary_subsector,
            secondary_subsector=secondary_subsector,
            confidence_score=confidence_score,
            market_cap_tier=market_cap_tier,
            business_model=business_model,
            risk_profile=risk_profile,
            growth_stage=growth_stage,
            regulatory_risk=regulatory_risk,
            revenue_model=revenue_model
        )

    def _is_healthcare_company(self, info: Dict) -> Tuple[bool, float]:
        """Determine if company is healthcare with confidence score"""
        score = 0.0
        max_score = 3.0  # sector + industry + description
        
        # Check sector (highest weight)
        sector = info.get('sector', '').lower()
        if 'healthcare' in sector or 'health care' in sector:
            score += 1.0
        
        # Check industry
        industry = info.get('industry', '').lower()
        industry_match = False
        for subsector_data in self.healthcare_keywords.values():
            if any(keyword in industry for keyword in subsector_data['primary']):
                score += 1.0 * subsector_data['weight']
                industry_match = True
                break
            elif any(keyword in industry for keyword in subsector_data['secondary']):
                score += 0.5 * subsector_data['weight']
                industry_match = True
                break
        
        # Check business description
        description = info.get('longBusinessSummary', '').lower()
        if description:
            healthcare_mentions = 0
            total_keywords = 0
            
            for subsector_data in self.healthcare_keywords.values():
                for keyword in subsector_data['primary']:
                    total_keywords += 1
                    if keyword in description:
                        healthcare_mentions += 1
                for keyword in subsector_data['secondary']:
                    total_keywords += 1
                    if keyword in description:
                        healthcare_mentions += 0.5
            
            if total_keywords > 0:
                description_score = min(healthcare_mentions / total_keywords * 5, 1.0)  # Cap at 1.0
                score += description_score
        
        # Check company name
        company_name = info.get('longName', '').lower()
        name_keywords = ['pharma', 'biotech', 'medical', 'health', 'therapeutic', 'diagnostics']
        if any(keyword in company_name for keyword in name_keywords):
            score += 0.5
            max_score += 0.5
        
        confidence = score / max_score
        is_healthcare = confidence >= 0.3  # Lower threshold for broader coverage
        
        return is_healthcare, confidence

    def _classify_subsector(self, info: Dict) -> Tuple[str, Optional[str], float]:
        """Classify healthcare subsector with confidence"""
        industry = info.get('industry', '').lower()
        description = (info.get('longBusinessSummary', '') + ' ' + 
                      info.get('longName', '')).lower()
        
        text_to_analyze = industry + ' ' + description
        
        scores = {}
        
        # Score each subsector
        for subsector, keywords_data in self.healthcare_keywords.items():
            subsector_score = 0
            
            # Primary keywords (full weight)
            for keyword in keywords_data['primary']:
                if keyword in text_to_analyze:
                    subsector_score += keywords_data['weight']
            
            # Secondary keywords (half weight)
            for keyword in keywords_data['secondary']:
                if keyword in text_to_analyze:
                    subsector_score += keywords_data['weight'] * 0.5
            
            if subsector_score > 0:
                scores[subsector] = subsector_score
        
        if not scores:
            return 'Healthcare - Other', None, 0.3
        
        # Sort by score
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        
        primary_subsector = self._format_subsector_name(sorted_scores[0][0])
        secondary_subsector = None
        
        if len(sorted_scores) > 1 and sorted_scores[1][1] >= sorted_scores[0][1] * 0.7:
            secondary_subsector = self._format_subsector_name(sorted_scores[1][0])
        
        # Calculate confidence based on score separation
        max_score = sorted_scores[0][1]
        confidence = min(max_score / 3.0, 1.0)  # Normalize to 0-1
        
        return primary_subsector, secondary_subsector, confidence

    def _format_subsector_name(self, subsector: str) -> str:
        """Format subsector name for display"""
        name_mapping = {
            'biotechnology': 'Biotechnology',
            'pharmaceuticals': 'Pharmaceuticals',
            'medical_devices': 'Medical Devices',
            'healthcare_services': 'Healthcare Services',
            'diagnostics': 'Diagnostics',
            'digital_health': 'Digital Health'
        }
        return name_mapping.get(subsector, 'Healthcare - Other')

    def _determine_market_cap_tier(self, market_cap: int) -> str:
        """Determine market cap tier"""
        if market_cap >= 200e9:
            return 'Mega Cap (>$200B)'
        elif market_cap >= 50e9:
            return 'Large Cap ($50B-$200B)'
        elif market_cap >= 10e9:
            return 'Mid Cap ($10B-$50B)'
        elif market_cap >= 2e9:
            return 'Small Cap ($2B-$10B)'
        elif market_cap >= 300e6:
            return 'Micro Cap ($300M-$2B)'
        elif market_cap > 0:
            return 'Nano Cap (<$300M)'
        else:
            return 'Unknown'

    def _identify_business_model(self, info: Dict) -> str:
        """Identify primary business model"""
        description = info.get('longBusinessSummary', '').lower()
        
        if not description:
            return 'Unknown'
        
        model_scores = {}
        
        for model, keywords in self.business_models.items():
            score = sum(1 for keyword in keywords if keyword in description)
            if score > 0:
                model_scores[model] = score
        
        if not model_scores:
            return 'Product Sales'  # Default assumption
        
        # Return highest scoring model
        best_model = max(model_scores, key=model_scores.get)
        
        model_names = {
            'product_sales': 'Product Sales',
            'licensing': 'Licensing/Royalties',
            'services': 'Services',
            'subscription': 'Subscription/SaaS',
            'transaction': 'Transaction-based'
        }
        
        return model_names.get(best_model, 'Mixed Model')

    def _assess_risk_profile(self, info: Dict, subsector: str, financials: Dict) -> str:
        """Assess company risk profile"""
        description = info.get('longBusinessSummary', '').lower()
        market_cap = info.get('marketCap', 0)
        
        # Base risk by subsector
        subsector_risk = {
            'Biotechnology': 'High',
            'Pharmaceuticals': 'Medium',
            'Medical Devices': 'Medium',
            'Healthcare Services': 'Low',
            'Diagnostics': 'Medium',
            'Digital Health': 'Medium-High'
        }
        
        base_risk = subsector_risk.get(subsector, 'Medium')
        
        # Adjust based on development stage
        if description:
            high_risk_count = sum(1 for indicator in self.risk_indicators['high_risk'] if indicator in description)
            low_risk_count = sum(1 for indicator in self.risk_indicators['low_risk'] if indicator in description)
            
            if high_risk_count > low_risk_count:
                base_risk = 'High' if base_risk != 'Low' else 'Medium'
            elif low_risk_count > high_risk_count:
                base_risk = 'Low' if base_risk != 'High' else 'Medium'
        
        # Adjust based on financial metrics
        if financials:
            profit_margins = financials.get('profit_margins', 0)
            debt_to_equity = financials.get('debt_to_equity', 0)
            
            if profit_margins and profit_margins > 0.2:  # 20%+ profit margins
                if base_risk == 'High':
                    base_risk = 'Medium-High'
                elif base_risk == 'Medium':
                    base_risk = 'Medium-Low'
            
            if debt_to_equity and debt_to_equity > 1.0:  # High debt
                if base_risk == 'Low':
                    base_risk = 'Medium-Low'
                elif base_risk == 'Medium':
                    base_risk = 'Medium-High'
        
        # Adjust based on market cap (larger = generally less risky)
        if market_cap > 50e9:  # Large cap
            if base_risk == 'High':
                base_risk = 'Medium-High'
        elif market_cap < 1e9:  # Small cap
            if base_risk == 'Low':
                base_risk = 'Medium-Low'
        
        return base_risk

    def _determine_growth_stage(self, info: Dict, financials: Dict) -> str:
        """Determine company growth stage"""
        description = info.get('longBusinessSummary', '').lower()
        market_cap = info.get('marketCap', 0)
        
        # Check for stage indicators in description
        if description:
            if any(word in description for word in ['preclinical', 'early stage', 'development']):
                return 'Early Stage'
            elif any(word in description for word in ['phase iii', 'phase 3', 'late stage']):
                return 'Late Stage Development'
            elif any(word in description for word in ['commercial', 'marketed', 'approved']):
                return 'Commercial'
            elif any(word in description for word in ['established', 'leading', 'mature']):
                return 'Mature'
        
        # Use financial metrics
        if financials:
            revenue = financials.get('revenue', 0)
            revenue_growth = financials.get('revenue_growth', 0)
            profit_margins = financials.get('profit_margins', 0)
            
            if revenue and revenue > 0:
                if profit_margins and profit_margins > 0.15:  # 15%+ margins
                    if revenue_growth and revenue_growth > 0.3:  # 30%+ growth
                        return 'High Growth'
                    else:
                        return 'Profitable Growth'
                else:
                    if revenue_growth and revenue_growth > 0.5:  # 50%+ growth
                        return 'Rapid Growth'
                    else:
                        return 'Revenue Stage'
            else:
                return 'Pre-Revenue'
        
        # Default based on market cap
        if market_cap > 10e9:
            return 'Mature'
        elif market_cap > 1e9:
            return 'Growth'
        else:
            return 'Early Stage'

    def _assess_regulatory_risk(self, subsector: str, info: Dict) -> str:
        """Assess regulatory risk level"""
        # Base regulatory risk by subsector
        regulatory_risk_map = {
            'Biotechnology': 'Very High',
            'Pharmaceuticals': 'Very High',
            'Medical Devices': 'High',
            'Diagnostics': 'High',
            'Healthcare Services': 'Medium',
            'Digital Health': 'Medium'
        }
        
        base_risk = regulatory_risk_map.get(subsector, 'Medium')
        
        # Check for regulatory mentions in description
        description = info.get('longBusinessSummary', '').lower()
        if description:
            fda_mentions = description.count('fda') + description.count('food and drug administration')
            if fda_mentions >= 3:
                return 'Very High'
            elif fda_mentions >= 1:
                if base_risk == 'Medium':
                    return 'High'
        
        return base_risk

    def _identify_revenue_models(self, info: Dict) -> List[str]:
        """Identify revenue models"""
        description = info.get('longBusinessSummary', '').lower()
        
        if not description:
            return ['Product Sales']  # Default
        
        revenue_models = []
        
        # Check for different revenue model indicators
        if any(word in description for word in ['sales', 'selling', 'commercial', 'marketing']):
            revenue_models.append('Product Sales')
        
        if any(word in description for word in ['licensing', 'royalty', 'partnership']):
            revenue_models.append('Licensing/Royalties')
        
        if any(word in description for word in ['services', 'consulting', 'contract']):
            revenue_models.append('Services')
        
        if any(word in description for word in ['subscription', 'recurring', 'saas']):
            revenue_models.append('Subscription')
        
        if any(word in description for word in ['milestone', 'upfront', 'development']):
            revenue_models.append('Milestone Payments')
        
        return revenue_models if revenue_models else ['Product Sales']

    def _create_default_classification(self, is_healthcare: bool) -> HealthcareClassification:
        """Create default classification for non-healthcare companies"""
        return HealthcareClassification(
            is_healthcare=is_healthcare,
            primary_subsector='Non-Healthcare' if not is_healthcare else 'Healthcare - Other',
            secondary_subsector=None,
            confidence_score=0.0 if not is_healthcare else 0.5,
            market_cap_tier='Unknown',
            business_model='Unknown',
            risk_profile='Unknown',
            growth_stage='Unknown',
            regulatory_risk='Unknown',
            revenue_model=['Unknown']
        )

    def get_peer_companies(self, classification: HealthcareClassification) -> List[str]:
        """Get list of peer companies based on classification"""
        # This would typically query a database of healthcare companies
        # For now, return common peers based on subsector
        
        peer_map = {
            'Biotechnology': ['MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD', 'AMGN'],
            'Pharmaceuticals': ['PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'GSK'],
            'Medical Devices': ['MDT', 'ABT', 'SYK', 'BSX', 'EW', 'ISRG', 'DXCM'],
            'Healthcare Services': ['UNH', 'CVS', 'CI', 'HUM', 'ANTM', 'MOH'],
            'Diagnostics': ['LH', 'DGX', 'QGEN', 'ILMN', 'TMO', 'DHR'],
            'Digital Health': ['TDOC', 'VEEV', 'DOCU', 'PTON', 'DOCS']
        }
        
        return peer_map.get(classification.primary_subsector, [])

def classify_healthcare_company(data: Dict) -> HealthcareClassification:
    """Convenience function for classification"""
    classifier = HealthcareClassifier()
    return classifier.classify_healthcare_company(data) 