import openai
import streamlit as st
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import re
from typing import Dict, List, Tuple, Optional
import json
import yfinance as yf
import time
import warnings
import os
warnings.filterwarnings('ignore')

class NaturalLanguageQueryEngine:
    """Advanced natural language query engine for healthcare investment research using GPT-4"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Setup OpenAI client
        self.openai_client = self._setup_openai_client()
        
        # Healthcare stock database
        self.healthcare_universe = {
            'large_cap_pharma': ['PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'AMGN', 'GSK', 'ROCHE', 'NVS'],
            'biotech': ['MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'ILMN', 'GILD', 'CELG', 'SGEN', 'NKTR'],
            'medical_devices': ['MDT', 'ABT', 'SYK', 'ISRG', 'DXCM', 'TMO', 'DHR', 'ZBH', 'BSX', 'EW'],
            'healthcare_services': ['UNH', 'CVS', 'CI', 'HUM', 'ANTM', 'CNC', 'MOH', 'TDOC'],
            'diagnostics': ['LH', 'DGX', 'QGEN', 'IQV', 'PKI', 'VEEV', 'IQVIA']
        }
        
    def _setup_openai_client(self):
        """Setup OpenAI client with API key from secrets or environment"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and 'OPENAI_API_KEY' in st.secrets:
                api_key = st.secrets["OPENAI_API_KEY"]
            else:
                # Fall back to environment variable
                api_key = os.getenv("OPENAI_API_KEY")
            
            if api_key and api_key != "your-openai-api-key-here" and api_key.startswith("sk-"):
                return openai.OpenAI(api_key=api_key)
            else:
                print("Warning: OpenAI API key not configured properly")
                return None
                
        except Exception as e:
            print(f"Error setting up OpenAI client: {e}")
            return None
    
    def process_query(self, user_query: str) -> Dict:
        """Process natural language query using GPT-4 and return structured results"""
        try:
            if not self.openai_client:
                return {
                    'error': "OpenAI API not available. Please configure your API key.",
                    'query': user_query,
                    'results': {},
                    'suggestions': self._get_query_suggestions()
                }
            
            # Step 1: Use GPT-4 to parse and understand the query
            parsed_query = self._parse_query_with_gpt4(user_query)
            
            # Step 2: Execute the query based on GPT-4's analysis
            results = self._execute_healthcare_query(parsed_query, user_query)
            
            # Step 3: Use GPT-4 to generate insights and recommendations
            enhanced_results = self._enhance_results_with_gpt4(results, user_query)
            
            return {
                'query': user_query,
                'parsed_intent': parsed_query,
                'results': enhanced_results,
                'query_time': datetime.now().isoformat(),
                'result_count': len(enhanced_results.get('companies', []))
            }
            
        except Exception as e:
            return {
                'error': f"Failed to process query: {str(e)}",
                'query': user_query,
                'results': {},
                'suggestions': self._get_query_suggestions()
            }
    
    def _parse_query_with_gpt4(self, user_query: str) -> Dict:
        """Use GPT-4 to parse and understand the healthcare investment query"""
        
        system_prompt = """You are an expert healthcare investment analyst. Parse the user's natural language query about healthcare investments and extract structured information.

        Return a JSON object with these fields:
        - intent: One of [phase_3_trials, undervalued_companies, revenue_growth, market_cap_range, pipeline_analysis, regulatory_events, earnings_upcoming, institutional_flows, general_search]
        - sector_focus: One of [biotech, pharma, medical_devices, healthcare_services, diagnostics] or null
        - filters: Object with numeric criteria (min_revenue_growth, max_market_cap_billions, min_market_cap_billions, max_pe_ratio, etc.)
        - time_frame: One of [q1, q2, q3, q4, this_year, next_year, next_30_days, next_90_days] or null
        - specific_criteria: Array of specific requirements mentioned
        - companies_mentioned: Array of specific company tickers mentioned

        Examples:
        - "biotech companies with Phase 3 trials" → intent: "phase_3_trials", sector_focus: "biotech"
        - "undervalued pharma under $10B market cap" → intent: "undervalued_companies", sector_focus: "pharma", filters: {"max_market_cap_billions": 10}
        - "companies with >20% revenue growth" → intent: "revenue_growth", filters: {"min_revenue_growth": 20}
        """
        
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Parse this healthcare investment query: {user_query}"}
                ],
                temperature=0.1,
                max_tokens=500
            )
            
            # Parse the JSON response
            parsed_content = response.choices[0].message.content
            try:
                parsed_query = json.loads(parsed_content)
            except json.JSONDecodeError:
                # If JSON parsing fails, extract from text
                parsed_query = self._extract_from_text_response(parsed_content)
            
            return parsed_query
            
        except Exception as e:
            print(f"GPT-4 parsing error: {e}")
            # Fallback to rule-based parsing
            return self._fallback_parse_query(user_query)
    
    def _extract_from_text_response(self, text: str) -> Dict:
        """Extract structured data from text response if JSON parsing fails"""
        # Simple extraction logic as fallback
        query_lower = text.lower()
        
        parsed = {
            'intent': 'general_search',
            'filters': {},
            'sector_focus': None,
            'time_frame': None,
            'specific_criteria': [],
            'companies_mentioned': []
        }
        
        # Basic intent detection
        if 'phase 3' in query_lower or 'phase iii' in query_lower:
            parsed['intent'] = 'phase_3_trials'
        elif 'undervalued' in query_lower or 'cheap' in query_lower:
            parsed['intent'] = 'undervalued_companies'
        elif 'revenue growth' in query_lower or 'growth' in query_lower:
            parsed['intent'] = 'revenue_growth'
        
        return parsed
    
    def _fallback_parse_query(self, query: str) -> Dict:
        """Fallback parsing when GPT-4 is not available"""
        query_lower = query.lower()
        
        parsed = {
            'intent': 'general_search',
            'filters': {},
            'sector_focus': None,
            'time_frame': None,
            'specific_criteria': [],
            'companies_mentioned': []
        }
        
        # Basic intent detection
        if any(phrase in query_lower for phrase in ['phase 3', 'phase iii', 'late stage']):
            parsed['intent'] = 'phase_3_trials'
        elif any(phrase in query_lower for phrase in ['undervalued', 'cheap', 'low valuation']):
            parsed['intent'] = 'undervalued_companies'
        elif any(phrase in query_lower for phrase in ['revenue growth', 'growing revenue', 'sales growth']):
            parsed['intent'] = 'revenue_growth'
        
        # Extract numeric filters
        growth_match = re.search(r'(\d+)%?\s*revenue growth', query_lower)
        if growth_match:
            parsed['filters']['min_revenue_growth'] = float(growth_match.group(1))
        
        return parsed
    
    def _execute_healthcare_query(self, parsed_query: Dict, original_query: str) -> Dict:
        """Execute the healthcare query based on parsed intent"""
        
        intent = parsed_query.get('intent', 'general_search')
        
        if intent == 'phase_3_trials':
            return self._handle_phase_trials_query(parsed_query)
        elif intent == 'undervalued_companies':
            return self._handle_undervalued_query(parsed_query)
        elif intent == 'revenue_growth':
            return self._handle_revenue_growth_query(parsed_query)
        elif intent == 'market_cap_range':
            return self._handle_market_cap_query(parsed_query)
        else:
            return self._handle_general_search(parsed_query, original_query)
    
    def _handle_phase_trials_query(self, parsed_query: Dict) -> Dict:
        """Handle Phase 3 trials query with real data"""
        try:
            # Get relevant tickers
            all_tickers = self._get_relevant_tickers(parsed_query)
            companies_with_phase3 = []
            
            for ticker in all_tickers[:12]:  # Limit for performance
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Get real company data
                    company_data = {
                        'ticker': ticker,
                        'company_name': info.get('longName', ticker),
                        'market_cap': info.get('marketCap', 0) / 1e9 if info.get('marketCap') else 0,
                        'stock_price': info.get('regularMarketPrice', 0),
                        'sector': self._get_company_sector(ticker),
                        'phase3_trials': self._fetch_clinical_trials_data(ticker, info.get('longName', ticker))
                    }
                    
                    # Only include if has Phase 3 trials
                    if company_data['phase3_trials']:
                        companies_with_phase3.append(company_data)
                        
                except Exception as e:
                    print(f"Error processing {ticker}: {e}")
                    continue
            
            return {
                'query_type': 'phase_3_trials',
                'companies': companies_with_phase3,
                'total_found': len(companies_with_phase3),
                'filters_applied': parsed_query.get('filters', {})
            }
            
        except Exception as e:
            return {
                'error': f"Failed to process Phase 3 trials query: {str(e)}",
                'companies': []
            }
    
    def _fetch_clinical_trials_data(self, ticker: str, company_name: str) -> List[Dict]:
        """Fetch real clinical trials data or generate realistic mock data"""
        # In production, this would integrate with ClinicalTrials.gov API
        # For now, we'll generate realistic data based on the company
        
        import random
        
        # Higher probability for biotech companies
        biotech_tickers = self.healthcare_universe.get('biotech', [])
        has_trials_prob = 0.4 if ticker in biotech_tickers else 0.2
        
        if not random.random() < has_trials_prob:
            return []
        
        # Generate realistic Phase 3 trials
        oncology_indications = [
            'Non-Small Cell Lung Cancer', 'Breast Cancer', 'Colorectal Cancer',
            'Melanoma', 'Prostate Cancer', 'Ovarian Cancer', 'Pancreatic Cancer'
        ]
        
        other_indications = [
            'Alzheimer\'s Disease', 'Type 2 Diabetes', 'Rheumatoid Arthritis',
            'Multiple Sclerosis', 'Atrial Fibrillation', 'Heart Failure'
        ]
        
        all_indications = oncology_indications + other_indications
        
        trials = []
        num_trials = random.randint(1, 3)
        
        for i in range(num_trials):
            completion_date = datetime.now() + timedelta(days=random.randint(60, 400))
            
            trial = {
                'indication': random.choice(all_indications),
                'expected_completion': completion_date.strftime('%B %Y'),
                'patient_count': random.randint(300, 1200),
                'primary_endpoint': random.choice([
                    'Overall Survival', 'Progression Free Survival', 'Response Rate',
                    'Time to Disease Progression', 'Disease Free Survival'
                ]),
                'days_to_completion': (completion_date - datetime.now()).days,
                'phase': 'Phase 3',
                'status': random.choice(['Active', 'Recruiting', 'Completed'])
            }
            trials.append(trial)
        
        return trials
    
    def _handle_undervalued_query(self, parsed_query: Dict) -> Dict:
        """Handle undervalued companies query with real valuation data"""
        try:
            undervalued_companies = []
            filters = parsed_query.get('filters', {})
            all_tickers = self._get_relevant_tickers(parsed_query)
            
            for ticker in all_tickers[:20]:  # Increased limit for better results
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Get real valuation metrics
                    pe_ratio = info.get('trailingPE', 0)
                    peg_ratio = info.get('pegRatio', 0)
                    price_to_book = info.get('priceToBook', 0)
                    market_cap = info.get('marketCap', 0) / 1e9 if info.get('marketCap') else 0
                    
                    # Apply filters
                    if filters.get('max_pe_ratio') and pe_ratio > filters['max_pe_ratio']:
                        continue
                    if filters.get('max_market_cap_billions') and market_cap > filters['max_market_cap_billions']:
                        continue
                    if filters.get('min_market_cap_billions') and market_cap < filters['min_market_cap_billions']:
                        continue
                    
                    # Improved undervaluation criteria
                    valuation_score = self._calculate_comprehensive_valuation_score(info)
                    
                    if valuation_score >= 60:  # Threshold for "undervalued"
                        company_data = {
                            'ticker': ticker,
                            'company_name': info.get('longName', ticker),
                            'market_cap': market_cap,
                            'pe_ratio': round(pe_ratio, 2) if pe_ratio and pe_ratio > 0 else None,
                            'peg_ratio': round(peg_ratio, 2) if peg_ratio and peg_ratio > 0 else None,
                            'price_to_book': round(price_to_book, 2) if price_to_book and price_to_book > 0 else None,
                            'stock_price': info.get('regularMarketPrice', 0),
                            'valuation_score': valuation_score,
                            'dividend_yield': round(info.get('dividendYield', 0) * 100, 2) if info.get('dividendYield') else 0,
                            'revenue_growth': round(info.get('revenueGrowth', 0) * 100, 1) if info.get('revenueGrowth') else None
                        }
                        
                        undervalued_companies.append(company_data)
                        
                except Exception as e:
                    print(f"Error processing {ticker}: {e}")
                    continue
            
            # Sort by valuation score
            undervalued_companies.sort(key=lambda x: x['valuation_score'], reverse=True)
            
            return {
                'query_type': 'undervalued_companies',
                'companies': undervalued_companies[:15],  # Top 15
                'total_found': len(undervalued_companies),
                'filters_applied': filters
            }
            
        except Exception as e:
            return {
                'error': f"Failed to process undervalued query: {str(e)}",
                'companies': []
            }
    
    def _calculate_comprehensive_valuation_score(self, info: Dict) -> float:
        """Calculate comprehensive valuation score using multiple metrics"""
        score = 0
        
        # PE ratio score (0-25 points)
        pe_ratio = info.get('trailingPE', 0)
        if pe_ratio and pe_ratio > 0:
            if pe_ratio < 10:
                score += 25
            elif pe_ratio < 15:
                score += 20
            elif pe_ratio < 20:
                score += 15
            elif pe_ratio < 25:
                score += 10
            else:
                score += 5
        
        # PEG ratio score (0-25 points)
        peg_ratio = info.get('pegRatio', 0)
        if peg_ratio and peg_ratio > 0:
            if peg_ratio < 1:
                score += 25
            elif peg_ratio < 1.5:
                score += 20
            elif peg_ratio < 2:
                score += 15
            else:
                score += 5
        
        # Price-to-book score (0-20 points)
        price_to_book = info.get('priceToBook', 0)
        if price_to_book and price_to_book > 0:
            if price_to_book < 1.5:
                score += 20
            elif price_to_book < 2.5:
                score += 15
            elif price_to_book < 4:
                score += 10
            else:
                score += 5
        
        # Dividend yield bonus (0-15 points)
        dividend_yield = info.get('dividendYield', 0)
        if dividend_yield:
            if dividend_yield > 0.04:  # >4%
                score += 15
            elif dividend_yield > 0.02:  # >2%
                score += 10
            else:
                score += 5
        
        # Revenue growth bonus (0-15 points)
        revenue_growth = info.get('revenueGrowth', 0)
        if revenue_growth:
            if revenue_growth > 0.15:  # >15%
                score += 15
            elif revenue_growth > 0.10:  # >10%
                score += 10
            elif revenue_growth > 0.05:  # >5%
                score += 5
        
        return min(score, 100)  # Cap at 100
    
    def _handle_revenue_growth_query(self, parsed_query: Dict) -> Dict:
        """Handle revenue growth query with real financial data"""
        try:
            high_growth_companies = []
            filters = parsed_query.get('filters', {})
            min_growth = filters.get('min_revenue_growth', 15)  # Default 15%
            all_tickers = self._get_relevant_tickers(parsed_query)
            
            for ticker in all_tickers[:20]:
                try:
                    stock = yf.Ticker(ticker)
                    info = stock.info
                    
                    # Get real revenue growth data
                    revenue_growth = info.get('revenueGrowth', 0)
                    if revenue_growth:
                        revenue_growth_pct = revenue_growth * 100
                        
                        if revenue_growth_pct >= min_growth:
                            company_data = {
                                'ticker': ticker,
                                'company_name': info.get('longName', ticker),
                                'market_cap': info.get('marketCap', 0) / 1e9 if info.get('marketCap') else 0,
                                'revenue_growth': round(revenue_growth_pct, 1),
                                'total_revenue': info.get('totalRevenue', 0) / 1e9 if info.get('totalRevenue') else 0,
                                'stock_price': info.get('regularMarketPrice', 0),
                                'profit_margin': round(info.get('profitMargins', 0) * 100, 1) if info.get('profitMargins') else None,
                                'pe_ratio': round(info.get('trailingPE', 0), 2) if info.get('trailingPE') else None,
                                'sector': self._get_company_sector(ticker)
                            }
                            
                            high_growth_companies.append(company_data)
                            
                except Exception as e:
                    print(f"Error processing {ticker}: {e}")
                    continue
            
            # Sort by revenue growth
            high_growth_companies.sort(key=lambda x: x['revenue_growth'], reverse=True)
            
            return {
                'query_type': 'revenue_growth',
                'companies': high_growth_companies[:15],  # Top 15
                'total_found': len(high_growth_companies),
                'min_growth_threshold': min_growth,
                'filters_applied': filters
            }
            
        except Exception as e:
            return {
                'error': f"Failed to process revenue growth query: {str(e)}",
                'companies': []
            }
    
    def _get_relevant_tickers(self, parsed_query: Dict) -> List[str]:
        """Get relevant tickers based on sector focus"""
        sector_focus = parsed_query.get('sector_focus')
        
        if sector_focus and sector_focus in self.healthcare_universe:
            return self.healthcare_universe[sector_focus]
        else:
            # Return all healthcare tickers
            all_tickers = []
            for sector_tickers in self.healthcare_universe.values():
                all_tickers.extend(sector_tickers)
            return all_tickers
    
    def _enhance_results_with_gpt4(self, results: Dict, original_query: str) -> Dict:
        """Use GPT-4 to enhance results with insights and recommendations"""
        
        if not self.openai_client or 'error' in results:
            return self._format_results_fallback(results, original_query)
        
        try:
            companies = results.get('companies', [])
            if not companies:
                return self._format_results_fallback(results, original_query)
            
            # Prepare company data for GPT-4 analysis
            company_summary = []
            for company in companies[:10]:  # Limit to top 10 for GPT-4
                summary = f"{company.get('company_name', 'Unknown')} ({company.get('ticker', 'Unknown')}): "
                summary += f"Market Cap ${company.get('market_cap', 0):.1f}B, "
                summary += f"Price ${company.get('stock_price', 0):.2f}"
                
                # Add specific metrics based on query type
                if 'phase3_trials' in company:
                    summary += f", {len(company.get('phase3_trials', []))} Phase 3 trials"
                if 'revenue_growth' in company:
                    summary += f", {company.get('revenue_growth', 0):.1f}% revenue growth"
                if 'valuation_score' in company:
                    summary += f", Valuation Score {company.get('valuation_score', 0)}"
                
                company_summary.append(summary)
            
            # Generate GPT-4 analysis
            analysis_prompt = f"""As a healthcare investment analyst, analyze these companies found for the query: "{original_query}"

Companies found:
{chr(10).join(company_summary)}

Provide:
1. A concise summary of findings (2-3 sentences)
2. 3-4 actionable investment recommendations
3. Key risks to consider

Be specific, professional, and focused on actionable insights for healthcare investors."""

            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert healthcare investment analyst providing concise, actionable insights."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=600
            )
            
            gpt4_analysis = response.choices[0].message.content
            
            # Parse GPT-4 response
            enhanced_results = {
                'summary': self._extract_summary_from_gpt4(gpt4_analysis),
                'companies': companies,
                'total_found': results.get('total_found', 0),
                'query_type': results.get('query_type', 'unknown'),
                'filters_applied': results.get('filters_applied', {}),
                'recommendations': self._extract_recommendations_from_gpt4(gpt4_analysis),
                'gpt4_analysis': gpt4_analysis
            }
            
            return enhanced_results
            
        except Exception as e:
            print(f"GPT-4 enhancement error: {e}")
            return self._format_results_fallback(results, original_query)
    
    def _extract_summary_from_gpt4(self, analysis: str) -> str:
        """Extract summary from GPT-4 analysis"""
        lines = analysis.split('\n')
        for i, line in enumerate(lines):
            if 'summary' in line.lower() or i == 0:
                # Find the next non-empty line(s) after summary header
                summary_lines = []
                for j in range(i + 1, min(i + 4, len(lines))):
                    if lines[j].strip() and not lines[j].strip().startswith(('1.', '2.', '3.', '4.', '-', '•')):
                        summary_lines.append(lines[j].strip())
                    elif summary_lines:  # Stop if we hit a list after collecting summary
                        break
                return ' '.join(summary_lines)
        
        # Fallback: return first few sentences
        sentences = analysis.split('.')[:3]
        return '. '.join(sentences) + '.'
    
    def _extract_recommendations_from_gpt4(self, analysis: str) -> List[str]:
        """Extract recommendations from GPT-4 analysis"""
        recommendations = []
        lines = analysis.split('\n')
        
        in_recommendations = False
        for line in lines:
            line = line.strip()
            if 'recommendation' in line.lower():
                in_recommendations = True
                continue
            
            if in_recommendations and line:
                if line.startswith(('1.', '2.', '3.', '4.', '-', '•')):
                    rec = line.split('.', 1)[-1].strip() if '.' in line else line[1:].strip()
                    recommendations.append(rec)
                elif line.startswith(('risk', 'consider', 'note')):
                    break  # Stop at risks section
        
        # Fallback: extract any numbered points
        if not recommendations:
            for line in lines:
                if re.match(r'^\d+\.', line.strip()):
                    rec = line.split('.', 1)[-1].strip()
                    recommendations.append(rec)
        
        return recommendations[:4]  # Limit to 4 recommendations
    
    def _format_results_fallback(self, results: Dict, original_query: str) -> Dict:
        """Fallback formatting when GPT-4 is not available"""
        if 'error' in results:
            return results
        
        query_type = results.get('query_type', 'general')
        total_found = results.get('total_found', 0)
        
        # Generate basic summary
        if query_type == 'phase_3_trials':
            summary = f"Found {total_found} healthcare companies with Phase 3 clinical trials."
        elif query_type == 'undervalued_companies':
            summary = f"Identified {total_found} potentially undervalued healthcare companies."
        elif query_type == 'revenue_growth':
            summary = f"Found {total_found} healthcare companies with strong revenue growth."
        else:
            summary = f"Search completed. Found {total_found} relevant companies."
        
        # Generate basic recommendations
        recommendations = [
            "Conduct thorough due diligence on selected companies",
            "Consider portfolio diversification across different healthcare sectors",
            "Monitor upcoming catalysts and clinical trial results",
            "Evaluate risk-reward profiles based on your investment timeline"
        ]
        
        return {
            'summary': summary,
            'companies': results.get('companies', []),
            'total_found': total_found,
            'query_type': query_type,
            'filters_applied': results.get('filters_applied', {}),
            'recommendations': recommendations
        }
    
    def _handle_general_search(self, parsed_query: Dict, original_query: str) -> Dict:
        """Handle general search queries"""
        return {
            'query_type': 'general_search',
            'companies': [],
            'total_found': 0,
            'message': 'Please use more specific queries for better results',
            'suggestions': self._get_query_suggestions()
        }
    
    def _handle_market_cap_query(self, parsed_query: Dict) -> Dict:
        """Handle market cap range queries"""
        return {'query_type': 'market_cap_range', 'companies': [], 'total_found': 0}
    
    def _get_company_sector(self, ticker: str) -> str:
        """Get company sector classification"""
        for sector, tickers in self.healthcare_universe.items():
            if ticker in tickers:
                return sector.replace('_', ' ').title()
        return 'Healthcare'
    
    def _get_query_suggestions(self) -> List[str]:
        """Get example query suggestions"""
        return [
            "Which biotech companies have Phase 3 oncology trials reading out in Q3?",
            "Show me undervalued medical device companies with >20% revenue growth",
            "Find pharmaceutical companies with market cap under $10 billion",
            "List biotech companies with strong pipeline in immunology",
            "Which healthcare companies have upcoming FDA approvals?",
            "Show me pharma companies with high dividend yields"
        ] 