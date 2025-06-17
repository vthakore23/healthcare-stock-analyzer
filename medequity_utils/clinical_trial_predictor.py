import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional
import json
from bs4 import BeautifulSoup
import time
import yfinance as yf
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

class ClinicalTrialPredictor:
    """Advanced clinical trial event predictor with real-time data"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.predictor_model = None
        self.scaler = StandardScaler()
        self._initialize_model()
        
    def _initialize_model(self):
        """Initialize the ML model for trial success prediction"""
        try:
            # Create a simple model with historical trial success patterns
            self.predictor_model = RandomForestClassifier(n_estimators=100, random_state=42)
            
            # Train with synthetic historical data (in production, use real historical data)
            X_train = np.random.rand(1000, 8)  # Features: phase, company_size, therapeutic_area, etc.
            y_train = np.random.choice([0, 1], size=1000, p=[0.7, 0.3])  # Success/failure
            
            self.predictor_model.fit(X_train, y_train)
            self.scaler.fit(X_train)
        except Exception as e:
            print(f"Model initialization warning: {e}")
    
    def fetch_clinicaltrials_data(self, ticker: str) -> Dict:
        """Fetch real-time clinical trials data from ClinicalTrials.gov"""
        try:
            # Get company name from ticker
            stock = yf.Ticker(ticker)
            company_name = stock.info.get('longName', ticker)
            
            # Search ClinicalTrials.gov API
            base_url = "https://clinicaltrials.gov/api/query/study_fields"
            params = {
                'expr': f'"{company_name}" OR "{ticker}"',
                'fields': 'NCTId,BriefTitle,Phase,StudyType,OverallStatus,StartDate,CompletionDate,Condition',
                'min_rnk': 1,
                'max_rnk': 100,
                'fmt': 'json'
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                studies = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
                
                trials = []
                for study in studies:
                    trial_info = {
                        'nct_id': study.get('NCTId', [''])[0],
                        'title': study.get('BriefTitle', [''])[0],
                        'phase': study.get('Phase', [''])[0],
                        'status': study.get('OverallStatus', [''])[0],
                        'condition': study.get('Condition', [''])[0],
                        'start_date': study.get('StartDate', [''])[0],
                        'completion_date': study.get('CompletionDate', [''])[0],
                        'study_type': study.get('StudyType', [''])[0]
                    }
                    trials.append(trial_info)
                
                return {
                    'ticker': ticker,
                    'company_name': company_name,
                    'trials': trials,
                    'total_trials': len(trials),
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'error': f"Failed to fetch trials data: {str(e)}",
                'ticker': ticker,
                'trials': [],
                'total_trials': 0
            }
    
    def predict_trial_success(self, trial_data: Dict) -> Dict:
        """Predict trial success probability using ML model"""
        try:
            # Extract features from trial data
            features = self._extract_trial_features(trial_data)
            
            if features is None:
                return {'success_probability': 0.5, 'confidence': 'low', 'factors': []}
            
            # Predict using model
            features_scaled = self.scaler.transform([features])
            probability = self.predictor_model.predict_proba(features_scaled)[0][1]
            
            # Determine confidence level
            confidence = self._calculate_confidence(features, probability)
            
            # Get key factors
            factors = self._get_success_factors(trial_data, features)
            
            return {
                'success_probability': round(probability, 3),
                'confidence': confidence,
                'factors': factors,
                'risk_level': self._get_risk_level(probability)
            }
            
        except Exception as e:
            return {
                'success_probability': 0.5,
                'confidence': 'low',
                'factors': [f"Error in prediction: {str(e)}"],
                'risk_level': 'Unknown'
            }
    
    def _extract_trial_features(self, trial_data: Dict) -> Optional[List[float]]:
        """Extract numerical features from trial data for ML model"""
        try:
            features = []
            
            # Phase feature (0-4 scale)
            phase = trial_data.get('phase', '')
            phase_map = {'Phase 1': 1, 'Phase 2': 2, 'Phase 3': 3, 'Phase 4': 4}
            features.append(phase_map.get(phase, 0))
            
            # Therapeutic area (oncology=1, others=0)
            condition = trial_data.get('condition', '').lower()
            features.append(1 if any(word in condition for word in ['cancer', 'tumor', 'oncology']) else 0)
            
            # Study type (interventional=1, observational=0)
            study_type = trial_data.get('study_type', '').lower()
            features.append(1 if 'interventional' in study_type else 0)
            
            # Status progression (recruiting/active=1, others=0)
            status = trial_data.get('status', '').lower()
            features.append(1 if any(word in status for word in ['recruiting', 'active']) else 0)
            
            # Trial duration (estimated in months)
            duration = self._estimate_trial_duration(trial_data)
            features.append(duration)
            
            # Company experience (mock feature - would use real data in production)
            features.append(np.random.uniform(0.3, 1.0))  # Company track record
            
            # Market size indicator (mock feature)
            features.append(np.random.uniform(0.1, 1.0))  # Market potential
            
            # Innovation score (mock feature)
            features.append(np.random.uniform(0.2, 1.0))  # Innovation level
            
            return features
            
        except Exception:
            return None
    
    def _estimate_trial_duration(self, trial_data: Dict) -> float:
        """Estimate trial duration in months"""
        try:
            start_date = trial_data.get('start_date', '')
            completion_date = trial_data.get('completion_date', '')
            
            if start_date and completion_date:
                start = datetime.strptime(start_date, '%B %Y')
                completion = datetime.strptime(completion_date, '%B %Y')
                duration = (completion - start).days / 30.44  # Convert to months
                return max(duration, 1)
            else:
                # Estimate based on phase
                phase = trial_data.get('phase', '')
                phase_durations = {
                    'Phase 1': 12, 'Phase 2': 24, 'Phase 3': 36, 'Phase 4': 48
                }
                return phase_durations.get(phase, 24)
                
        except Exception:
            return 24  # Default 24 months
    
    def _calculate_confidence(self, features: List[float], probability: float) -> str:
        """Calculate confidence level for prediction"""
        # Higher confidence for more extreme probabilities and complete feature sets
        if len(features) >= 6 and (probability > 0.8 or probability < 0.2):
            return 'high'
        elif len(features) >= 4 and (probability > 0.7 or probability < 0.3):
            return 'medium'
        else:
            return 'low'
    
    def _get_success_factors(self, trial_data: Dict, features: List[float]) -> List[str]:
        """Get key factors affecting trial success"""
        factors = []
        
        phase = trial_data.get('phase', '')
        if 'Phase 3' in phase:
            factors.append("Late-stage trial (higher success probability)")
        elif 'Phase 1' in phase:
            factors.append("Early-stage trial (higher risk)")
        
        condition = trial_data.get('condition', '').lower()
        if any(word in condition for word in ['cancer', 'oncology']):
            factors.append("Oncology indication (complex regulatory path)")
        
        status = trial_data.get('status', '').lower()
        if 'recruiting' in status:
            factors.append("Currently recruiting patients")
        elif 'active' in status:
            factors.append("Trial actively enrolling")
        
        return factors
    
    def _get_risk_level(self, probability: float) -> str:
        """Get risk level based on success probability"""
        if probability > 0.7:
            return 'Low Risk'
        elif probability > 0.4:
            return 'Medium Risk'
        else:
            return 'High Risk'
    
    def analyze_upcoming_events(self, ticker: str) -> Dict:
        """Analyze upcoming trial events and catalysts"""
        try:
            trials_data = self.fetch_clinicaltrials_data(ticker)
            
            if 'error' in trials_data:
                return trials_data
            
            upcoming_events = []
            current_date = datetime.now()
            
            for trial in trials_data['trials']:
                completion_date = trial.get('completion_date', '')
                if completion_date:
                    try:
                        completion = datetime.strptime(completion_date, '%B %Y')
                        if completion > current_date:
                            # Calculate time to completion
                            days_to_completion = (completion - current_date).days
                            
                            # Predict success
                            prediction = self.predict_trial_success(trial)
                            
                            event = {
                                'trial_id': trial['nct_id'],
                                'title': trial['title'],
                                'phase': trial['phase'],
                                'completion_date': completion_date,
                                'days_to_completion': days_to_completion,
                                'success_probability': prediction['success_probability'],
                                'risk_level': prediction['risk_level'],
                                'confidence': prediction['confidence'],
                                'condition': trial['condition']
                            }
                            upcoming_events.append(event)
                    except ValueError:
                        continue
            
            # Sort by completion date
            upcoming_events.sort(key=lambda x: x['days_to_completion'])
            
            return {
                'ticker': ticker,
                'company_name': trials_data['company_name'],
                'upcoming_events': upcoming_events[:10],  # Top 10 upcoming events
                'total_upcoming': len(upcoming_events),
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to analyze upcoming events: {str(e)}",
                'ticker': ticker,
                'upcoming_events': [],
                'total_upcoming': 0
            }
    
    def calculate_stock_impact(self, ticker: str, event_data: Dict) -> Dict:
        """Calculate potential stock price impact of trial events"""
        try:
            # Get current stock data
            stock = yf.Ticker(ticker)
            info = stock.info
            current_price = info.get('regularMarketPrice', 0)
            market_cap = info.get('marketCap', 0)
            
            # Calculate impact based on trial importance and success probability
            impact_scenarios = {}
            
            for event in event_data.get('upcoming_events', []):
                success_prob = event['success_probability']
                phase = event['phase']
                
                # Estimate impact magnitude based on phase
                phase_impact = {
                    'Phase 1': 0.05,   # 5% impact
                    'Phase 2': 0.15,   # 15% impact
                    'Phase 3': 0.30,   # 30% impact
                    'Phase 4': 0.10    # 10% impact
                }
                
                base_impact = phase_impact.get(phase, 0.10)
                
                # Calculate scenarios
                success_impact = current_price * (1 + base_impact)
                failure_impact = current_price * (1 - base_impact * 0.7)
                expected_impact = (success_impact * success_prob + 
                                 failure_impact * (1 - success_prob))
                
                impact_scenarios[event['trial_id']] = {
                    'trial_title': event['title'],
                    'phase': phase,
                    'success_probability': success_prob,
                    'current_price': current_price,
                    'success_scenario': round(success_impact, 2),
                    'failure_scenario': round(failure_impact, 2),
                    'expected_price': round(expected_impact, 2),
                    'upside_potential': round((success_impact - current_price) / current_price * 100, 1),
                    'downside_risk': round((failure_impact - current_price) / current_price * 100, 1),
                    'days_to_event': event['days_to_completion']
                }
            
            return {
                'ticker': ticker,
                'current_price': current_price,
                'market_cap': market_cap,
                'impact_scenarios': impact_scenarios,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'error': f"Failed to calculate stock impact: {str(e)}",
                'ticker': ticker,
                'impact_scenarios': {}
            }
    
    def get_trial_alerts(self, ticker: str, alert_threshold: int = 30) -> List[Dict]:
        """Get alerts for trials with events in the next N days"""
        try:
            upcoming_events = self.analyze_upcoming_events(ticker)
            
            if 'error' in upcoming_events:
                return []
            
            alerts = []
            for event in upcoming_events.get('upcoming_events', []):
                if event['days_to_completion'] <= alert_threshold:
                    alert = {
                        'type': 'trial_event',
                        'urgency': 'high' if event['days_to_completion'] <= 7 else 'medium',
                        'title': f"{event['phase']} trial completion approaching",
                        'description': event['title'],
                        'days_remaining': event['days_to_completion'],
                        'success_probability': event['success_probability'],
                        'risk_level': event['risk_level'],
                        'trial_id': event['trial_id']
                    }
                    alerts.append(alert)
            
            return alerts
            
        except Exception as e:
            return [{
                'type': 'error',
                'title': 'Alert generation failed',
                'description': str(e)
            }]

    def get_competitive_trials(self, indication: str) -> Dict:
        """Get competitive trials in the same indication"""
        try:
            base_url = "https://clinicaltrials.gov/api/query/study_fields"
            params = {
                'expr': f'"{indication}"',
                'fields': 'NCTId,BriefTitle,Phase,OverallStatus,LeadSponsorName,CompletionDate',
                'min_rnk': 1,
                'max_rnk': 50,
                'fmt': 'json'
            }
            
            response = self.session.get(base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                studies = data.get('StudyFieldsResponse', {}).get('StudyFields', [])
                
                competitive_trials = []
                for study in studies:
                    trial_info = {
                        'nct_id': study.get('NCTId', [''])[0],
                        'title': study.get('BriefTitle', [''])[0],
                        'phase': study.get('Phase', [''])[0],
                        'status': study.get('OverallStatus', [''])[0],
                        'sponsor': study.get('LeadSponsorName', [''])[0],
                        'completion_date': study.get('CompletionDate', [''])[0]
                    }
                    competitive_trials.append(trial_info)
                
                return {
                    'indication': indication,
                    'competitive_trials': competitive_trials,
                    'total_competitors': len(competitive_trials),
                    'last_updated': datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                'error': f"Failed to fetch competitive trials: {str(e)}",
                'indication': indication,
                'competitive_trials': [],
                'total_competitors': 0
            } 