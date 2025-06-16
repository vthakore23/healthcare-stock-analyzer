# Data Validation Module
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Union
import re
from datetime import datetime

class DataValidationError(Exception):
    """Custom exception for data validation errors"""
    pass

class HealthcareDataValidator:
    """Comprehensive data validation for healthcare company data"""
    
    def __init__(self):
        self.required_basic_fields = ['ticker', 'longName', 'sector']
        self.numeric_fields = ['marketCap', 'totalRevenue', 'trailingPE', 'forwardPE']
        self.percentage_fields = ['profitMargins', 'grossMargins', 'operatingMargins']
        
    def validate_ticker(self, ticker: str) -> bool:
        """Validate ticker symbol format"""
        if not ticker:
            return False
        
        # Clean ticker
        ticker = ticker.strip().upper()
        
        # Basic validation
        if len(ticker) > 5 or len(ticker) < 1:
            return False
            
        # Allow letters, numbers, and dots (for some international tickers)
        if not re.match(r'^[A-Z0-9\.]+$', ticker):
            return False
            
        return True
        
    def validate_company_data(self, data: dict) -> bool:
        """Validate company data structure and content"""
        if not isinstance(data, dict):
            return False
            
        # Check for error in data
        if "error" in data:
            return False
            
        # Check basic required fields
        basic_info = data.get('basic_info', {})
        if not basic_info:
            return False
            
        # Validate ticker
        ticker = basic_info.get('symbol') or data.get('ticker')
        if not self.validate_ticker(ticker):
            return False
            
        return True
        
    def validate_financial_data(self, financials: dict) -> Dict[str, Any]:
        """Validate and clean financial data"""
        validated = {}
        errors = []
        
        for field, value in financials.items():
            try:
                if field in self.numeric_fields:
                    validated[field] = self._validate_numeric(value, field)
                elif field in self.percentage_fields:
                    validated[field] = self._validate_percentage(value, field)
                else:
                    validated[field] = value
            except Exception as e:
                errors.append(f"Error validating {field}: {str(e)}")
                validated[field] = None
                
        return {
            'data': validated,
            'errors': errors,
            'is_valid': len(errors) == 0
        }
        
    def _validate_numeric(self, value: Any, field_name: str) -> Optional[float]:
        """Validate numeric values"""
        if value is None:
            return None
            
        if isinstance(value, (int, float)):
            if np.isnan(value) or np.isinf(value):
                return None
            return float(value)
            
        if isinstance(value, str):
            try:
                # Handle percentage strings
                if '%' in value:
                    return float(value.replace('%', '')) / 100
                # Handle currency strings
                cleaned = re.sub(r'[^\d.-]', '', value)
                return float(cleaned) if cleaned else None
            except ValueError:
                return None
                
        return None
        
    def _validate_percentage(self, value: Any, field_name: str) -> Optional[float]:
        """Validate percentage values (should be 0-1 or 0-100)"""
        validated = self._validate_numeric(value, field_name)
        if validated is None:
            return None
            
        # Convert percentage to decimal if needed
        if validated > 1.0:
            validated = validated / 100
            
        # Clamp to reasonable range
        return max(0.0, min(1.0, validated))
        
    def validate_pipeline_data(self, pipeline: List[Dict]) -> Dict[str, Any]:
        """Validate pipeline data"""
        if not isinstance(pipeline, list):
            return {'data': [], 'errors': ['Pipeline data must be a list'], 'is_valid': False}
            
        validated_pipeline = []
        errors = []
        
        for i, item in enumerate(pipeline):
            if not isinstance(item, dict):
                errors.append(f"Pipeline item {i} must be a dictionary")
                continue
                
            validated_item = {}
            
            # Validate phase
            phase = item.get('phase', 'Unknown')
            validated_item['phase'] = self._validate_clinical_phase(phase)
            
            # Validate indication
            indication = item.get('indication', 'Various')
            validated_item['indication'] = str(indication)[:100]  # Limit length
            
            # Validate description
            description = item.get('description', '')
            validated_item['description'] = str(description)[:500]  # Limit length
            
            # Add metadata
            validated_item['source'] = item.get('source', 'Unknown')
            validated_item['confidence'] = item.get('confidence', 'medium')
            
            validated_pipeline.append(validated_item)
            
        return {
            'data': validated_pipeline,
            'errors': errors,
            'is_valid': len(errors) == 0
        }
        
    def _validate_clinical_phase(self, phase: str) -> str:
        """Validate and standardize clinical phase"""
        if not phase:
            return 'Unknown'
            
        phase_lower = phase.lower()
        
        # Standardize phase names
        phase_mapping = {
            'preclinical': 'Preclinical',
            'phase i': 'Phase I',
            'phase 1': 'Phase I',
            'phase ii': 'Phase II',
            'phase 2': 'Phase II',
            'phase iii': 'Phase III',
            'phase 3': 'Phase III',
            'approved': 'Approved/Commercial',
            'commercial': 'Approved/Commercial',
            'registration': 'Registration',
            'fda review': 'FDA Review'
        }
        
        for key, standard_name in phase_mapping.items():
            if key in phase_lower:
                return standard_name
                
        return phase  # Return original if no match
        
    def validate_news_data(self, news: List[Dict]) -> Dict[str, Any]:
        """Validate news data"""
        if not isinstance(news, list):
            return {'data': [], 'errors': ['News data must be a list'], 'is_valid': False}
            
        validated_news = []
        errors = []
        
        for i, article in enumerate(news):
            if not isinstance(article, dict):
                errors.append(f"News article {i} must be a dictionary")
                continue
                
            validated_article = {}
            
            # Validate title
            title = article.get('title', '')
            if not title:
                errors.append(f"Article {i} missing title")
                continue
                
            validated_article['title'] = str(title)[:200]  # Limit length
            
            # Validate source
            validated_article['source'] = str(article.get('source', 'Unknown'))[:100]
            
            # Validate sentiment
            sentiment = article.get('sentiment', 'neutral')
            validated_article['sentiment'] = self._validate_sentiment(sentiment)
            
            # Validate link
            link = article.get('link', '')
            validated_article['link'] = str(link)[:500]
            
            # Validate timestamp
            timestamp = article.get('published', 0)
            validated_article['published'] = self._validate_timestamp(timestamp)
            
            validated_news.append(validated_article)
            
        return {
            'data': validated_news,
            'errors': errors,
            'is_valid': len(errors) == 0
        }
        
    def _validate_sentiment(self, sentiment: str) -> str:
        """Validate sentiment value"""
        valid_sentiments = ['positive', 'negative', 'neutral']
        if sentiment and sentiment.lower() in valid_sentiments:
            return sentiment.lower()
        return 'neutral'
        
    def _validate_timestamp(self, timestamp: Any) -> int:
        """Validate timestamp value"""
        if isinstance(timestamp, (int, float)):
            return int(timestamp)
        return 0
        
    def validate_price_data(self, price_data: Dict) -> Dict[str, Any]:
        """Validate price and market data"""
        if not isinstance(price_data, dict):
            return {'data': {}, 'errors': ['Price data must be a dictionary'], 'is_valid': False}
            
        validated = {}
        errors = []
        
        # Validate current price
        current_price = price_data.get('current_price')
        if current_price is not None:
            validated_price = self._validate_numeric(current_price, 'current_price')
            if validated_price is None or validated_price <= 0:
                errors.append("Invalid current price")
            else:
                validated['current_price'] = validated_price
                
        # Validate price changes
        price_changes = price_data.get('price_changes', {})
        if isinstance(price_changes, dict):
            validated_changes = {}
            for period, change in price_changes.items():
                validated_change = self._validate_numeric(change, f'price_change_{period}')
                if validated_change is not None:
                    # Reasonable bounds for price changes (-99% to +1000%)
                    validated_changes[period] = max(-99.0, min(1000.0, validated_change))
            validated['price_changes'] = validated_changes
            
        # Validate volume data
        volume_data = price_data.get('volume_metrics', {})
        if isinstance(volume_data, dict):
            validated_volume = {}
            for key, value in volume_data.items():
                validated_val = self._validate_numeric(value, f'volume_{key}')
                if validated_val is not None and validated_val >= 0:
                    validated_volume[key] = validated_val
            validated['volume_metrics'] = validated_volume
            
        return {
            'data': validated,
            'errors': errors,
            'is_valid': len(errors) == 0
        }
        
    def validate_complete_dataset(self, data: Dict) -> Dict[str, Any]:
        """Validate complete company dataset"""
        validation_results = {
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'validated_data': {}
        }
        
        try:
            # Validate basic company data
            if not self.validate_company_data(data):
                validation_results['errors'].append("Invalid company data structure")
                validation_results['is_valid'] = False
                
            # Validate financials
            financials = data.get('financials', {})
            if financials:
                financial_validation = self.validate_financial_data(financials)
                validation_results['validated_data']['financials'] = financial_validation['data']
                validation_results['errors'].extend(financial_validation['errors'])
                if not financial_validation['is_valid']:
                    validation_results['warnings'].append("Some financial data validation issues")
                    
            # Validate pipeline
            pipeline = data.get('pipeline', [])
            if pipeline:
                pipeline_validation = self.validate_pipeline_data(pipeline)
                validation_results['validated_data']['pipeline'] = pipeline_validation['data']
                validation_results['errors'].extend(pipeline_validation['errors'])
                
            # Validate news
            news = data.get('news', [])
            if news:
                news_validation = self.validate_news_data(news)
                validation_results['validated_data']['news'] = news_validation['data']
                validation_results['errors'].extend(news_validation['errors'])
                
            # Validate price data
            price_data = data.get('price_history', {})
            if price_data:
                price_validation = self.validate_price_data(price_data)
                validation_results['validated_data']['price_history'] = price_validation['data']
                validation_results['errors'].extend(price_validation['errors'])
                
            # Overall validation status
            validation_results['is_valid'] = len(validation_results['errors']) == 0
            
        except Exception as e:
            validation_results['errors'].append(f"Validation error: {str(e)}")
            validation_results['is_valid'] = False
            
        return validation_results

# Convenience functions
def validate_data(data: Dict) -> Dict[str, Any]:
    """Main validation function - validates complete dataset"""
    validator = HealthcareDataValidator()
    return validator.validate_complete_dataset(data)

def validate_ticker(ticker: str) -> bool:
    """Validate ticker symbol"""
    validator = HealthcareDataValidator()
    return validator.validate_ticker(ticker)

def validate_company_data(data: dict) -> bool:
    """Validate company data"""
    validator = HealthcareDataValidator()
    return validator.validate_company_data(data)

def clean_financial_data(financials: dict) -> dict:
    """Clean and validate financial data"""
    validator = HealthcareDataValidator()
    result = validator.validate_financial_data(financials)
    return result['data']

def validate_pipeline(pipeline: list) -> dict:
    """Validate pipeline data"""
    validator = HealthcareDataValidator()
    return validator.validate_pipeline_data(pipeline)

def validate_news(news: list) -> dict:
    """Validate news data"""
    validator = HealthcareDataValidator()
    return validator.validate_news_data(news)
