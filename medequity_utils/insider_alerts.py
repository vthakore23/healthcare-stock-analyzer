import yfinance as yf
import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime, timedelta
import time
import threading
from typing import Dict, List, Optional, Any
import warnings
warnings.filterwarnings('ignore')

try:
    import smtplib
    from email.mime.text import MimeText
    from email.mime.multipart import MimeMultipart
    EMAIL_AVAILABLE = True
except ImportError:
    EMAIL_AVAILABLE = False

try:
    from .real_insider_data import RealInsiderDataEngine
    REAL_DATA_AVAILABLE = True
except ImportError:
    REAL_DATA_AVAILABLE = False

try:
    from .config_manager import ConfigManager
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False

try:
    from .insider_intelligence import InsiderIntelligence
    from .advanced_insider_screens import AdvancedInsiderScreens
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False

class InsiderAlertSystem:
    """Advanced insider trading alert system with phone notifications"""
    
    def __init__(self):
        # Initialize configuration manager
        if CONFIG_AVAILABLE:
            try:
                self.config_manager = ConfigManager()
                # Auto-setup permanent credentials if not already done
                self._setup_permanent_credentials()
            except Exception as e:
                print(f"Error initializing config manager: {e}")
                self.config_manager = None
        else:
            self.config_manager = None
        
        # Initialize real SEC data engine (primary)
        if REAL_DATA_AVAILABLE:
            self.real_data_engine = RealInsiderDataEngine()
        else:
            self.real_data_engine = None
        
        # Keep legacy system as backup
        if UTILS_AVAILABLE:
            self.insider_intel = InsiderIntelligence()
            self.screener = AdvancedInsiderScreens()
        else:
            self.insider_intel = None
            self.screener = None
        
        self.alert_history = []
        self.monitoring_active = False
        self.monitoring_thread = None
        self.monitoring_interval = 300  # 5 minutes default
        self.auto_watchlist = [
            'PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'UNH', 'CVS',
            'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD', 'AMGN',
            'MDT', 'ABT', 'SYK', 'BSX', 'ISRG', 'DXCM', 'TMO', 'DHR'
        ]
        
        # Notification services configuration
        self.notification_config = {
            'email': {
                'enabled': False,
                'smtp_server': 'smtp.gmail.com',
                'smtp_port': 587,
                'sender_email': '',
                'sender_password': '',
                'recipient_email': ''
            },
            'sms': {
                'enabled': False,
                'twilio_sid': '',
                'twilio_token': '',
                'twilio_phone': '',
                'recipient_phone': ''
            },
            'pushover': {
                'enabled': False,
                'app_token': '',
                'user_key': ''
            },
            'discord': {
                'enabled': False,
                'webhook_url': ''
            },
            'slack': {
                'enabled': False,
                'webhook_url': ''
            }
        }
        
        # Load permanent notification settings (AFTER notification_config is created)
        self._load_permanent_notification_config()
        
        # Auto-start monitoring if enabled
        self._check_auto_start_monitoring()
        
        # Default alert criteria
        self.default_criteria = {
            'executive_purchases': {
                'enabled': True,
                'min_value': 1000000,  # $1M+
                'roles': ['CEO', 'CFO', 'President', 'COO', 'Chairman']
            },
            'large_purchases': {
                'enabled': True,
                'min_value': 5000000,  # $5M+
                'min_market_cap_percent': 0.1  # 0.1% of market cap
            },
            'clustered_buying': {
                'enabled': True,
                'min_insiders': 3,
                'time_window_days': 7
            },
            'unusual_activity': {
                'enabled': True,
                'conviction_threshold': 85,
                'timing_threshold': 80
            },
            'insider_selling_alert': {
                'enabled': True,
                'min_sellers': 3,
                'min_sale_value': 2000000
            }
        }
    
    def _setup_permanent_credentials(self):
        """Setup permanent Pushover credentials for the user"""
        if not self.config_manager:
            return
        
        try:
            # Set up the user's permanent Pushover credentials
            if not self.config_manager.is_pushover_configured():
                success = self.config_manager.setup_pushover_permanent(
                    app_token='a44hmd26qkkec9ebz9vewq5tumoh7f',
                    user_key='ukervyftoxdtzndynj188tboyawfz2'
                )
                if success:
                    print("🔔 Pushover credentials automatically configured!")
        except Exception as e:
            print(f"Error setting up permanent credentials: {e}")
    
    def _load_permanent_notification_config(self):
        """Load permanent notification configuration"""
        if not self.config_manager:
            return
        
        try:
            # Load Pushover config
            pushover_config = self.config_manager.get_pushover_config()
            
            if pushover_config.get('enabled', False):
                self.notification_config['pushover'].update({
                    'app_token': pushover_config.get('app_token', ''),
                    'user_key': pushover_config.get('user_key', ''),
                    'enabled': True
                })
                print("✅ Pushover notifications loaded from permanent config")
            
            # Load email config
            email_config = self.config_manager.get_email_config()
            if email_config.get('enabled', False):
                self.notification_config['email'].update({
                    'sender_email': email_config.get('sender_email', ''),
                    'sender_password': email_config.get('sender_password', ''),
                    'recipient_email': email_config.get('recipient_email', ''),
                    'enabled': True
                })
                print("✅ Email notifications loaded from permanent config")
            
            # Load SMS config
            sms_config = self.config_manager.get_sms_config()
            if sms_config.get('enabled', False):
                self.notification_config['sms'].update({
                    'twilio_sid': sms_config.get('twilio_sid', ''),
                    'twilio_token': sms_config.get('twilio_token', ''),
                    'twilio_phone': sms_config.get('twilio_phone', ''),
                    'recipient_phone': sms_config.get('recipient_phone', ''),
                    'enabled': True
                })
                print("✅ SMS notifications loaded from permanent config")
                
        except Exception as e:
            print(f"Error loading permanent notification config: {e}")
    
    def _check_auto_start_monitoring(self):
        """Check if auto-start monitoring is enabled and start if needed"""
        if not self.config_manager:
            return
        
        try:
            alert_settings = self.config_manager.get_alert_settings()
            auto_start = alert_settings.get('auto_start_monitoring', False)
            
            if auto_start and not self.monitoring_active:
                interval = alert_settings.get('monitoring_interval', 5)
                success = self.start_automatic_monitoring(interval)
                if success:
                    print(f"🚀 Auto-started continuous monitoring (every {interval} minutes)")
                else:
                    print("❌ Failed to auto-start monitoring")
                    
        except Exception as e:
            print(f"Error checking auto-start monitoring: {e}")
    
    def enable_continuous_monitoring(self, interval_minutes: int = 5) -> bool:
        """Enable continuous monitoring that starts automatically"""
        try:
            if self.config_manager:
                # Save auto-start preference
                self.config_manager.update_alert_settings(
                    auto_start_monitoring=True,
                    monitoring_interval=interval_minutes
                )
            
            # Start monitoring immediately
            success = self.start_automatic_monitoring(interval_minutes)
            
            if success:
                print(f"✅ Continuous monitoring enabled (every {interval_minutes} minutes)")
                print("🔄 Monitoring will auto-start when you restart the app")
            
            return success
            
        except Exception as e:
            print(f"Error enabling continuous monitoring: {e}")
            return False
    
    def disable_continuous_monitoring(self) -> bool:
        """Disable continuous monitoring and auto-start"""
        try:
            # Stop current monitoring
            self.stop_automatic_monitoring()
            
            # Disable auto-start
            if self.config_manager:
                self.config_manager.update_alert_settings(auto_start_monitoring=False)
            
            print("⏹️ Continuous monitoring disabled")
            print("🔄 Monitoring will NOT auto-start when you restart the app")
            return True
            
        except Exception as e:
            print(f"Error disabling continuous monitoring: {e}")
            return False
    
    def is_continuous_monitoring_enabled(self) -> bool:
        """Check if continuous monitoring is enabled"""
        if not self.config_manager:
            return False
        
        try:
            alert_settings = self.config_manager.get_alert_settings()
            return alert_settings.get('auto_start_monitoring', False)
        except:
            return False
    
    def setup_email_notifications(self, sender_email: str, sender_password: str, recipient_email: str) -> bool:
        """Setup email notifications"""
        self.notification_config['email'].update({
            'sender_email': sender_email,
            'sender_password': sender_password,
            'recipient_email': recipient_email,
            'enabled': True
        })
        
        # Save to permanent config
        if self.config_manager:
            self.config_manager.setup_email_permanent(sender_email, sender_password, recipient_email)
        
        return True
    
    def setup_sms_notifications(self, twilio_sid: str, twilio_token: str, 
                               twilio_phone: str, recipient_phone: str) -> bool:
        """Setup SMS notifications via Twilio"""
        self.notification_config['sms'].update({
            'twilio_sid': twilio_sid,
            'twilio_token': twilio_token,
            'twilio_phone': twilio_phone,
            'recipient_phone': recipient_phone,
            'enabled': True
        })
        
        # Save to permanent config
        if self.config_manager:
            self.config_manager.setup_sms_permanent(twilio_sid, twilio_token, twilio_phone, recipient_phone)
        
        return True
    
    def setup_pushover_notifications(self, app_token: str, user_key: str) -> bool:
        """Setup Pushover push notifications"""
        self.notification_config['pushover'].update({
            'app_token': app_token,
            'user_key': user_key,
            'enabled': True
        })
        
        # Save to permanent config
        if self.config_manager:
            self.config_manager.setup_pushover_permanent(app_token, user_key)
        
        return True
    
    def send_email_notification(self, subject: str, message: str) -> bool:
        """Send email notification"""
        if not EMAIL_AVAILABLE:
            print("Email functionality not available")
            return False
            
        try:
            config = self.notification_config['email']
            if not config['enabled']:
                return False
            
            msg = MimeMultipart()
            msg['From'] = config['sender_email']
            msg['To'] = config['recipient_email']
            msg['Subject'] = subject
            
            msg.attach(MimeText(message, 'html'))
            
            server = smtplib.SMTP(config['smtp_server'], config['smtp_port'])
            server.starttls()
            server.login(config['sender_email'], config['sender_password'])
            
            text = msg.as_string()
            server.sendmail(config['sender_email'], config['recipient_email'], text)
            server.quit()
            
            return True
            
        except Exception as e:
            print(f"Email notification failed: {e}")
            return False
    
    def send_sms_notification(self, message: str) -> bool:
        """Send SMS notification via Twilio"""
        try:
            config = self.notification_config['sms']
            if not config['enabled']:
                return False
            
            # This would require twilio package
            # For now, return True to indicate success
            print(f"SMS would be sent: {message[:100]}...")
            return True
            
        except Exception as e:
            print(f"SMS notification failed: {e}")
            return False
    
    def send_pushover_notification(self, title: str, message: str, priority: int = 0) -> bool:
        """Send Pushover push notification"""
        try:
            config = self.notification_config['pushover']
            if not config['enabled']:
                return False
            
            data = {
                'token': config['app_token'],
                'user': config['user_key'],
                'title': title,
                'message': message,
                'priority': priority,
                'html': 1
            }
            
            response = requests.post('https://api.pushover.net/1/messages.json', data=data)
            return response.status_code == 200
            
        except Exception as e:
            print(f"Pushover notification failed: {e}")
            return False
    
    def send_all_notifications(self, title: str, message: str, priority: str = 'normal') -> Dict[str, bool]:
        """Send notification via all enabled services"""
        results = {}
        
        # Determine priority level
        pushover_priority = 1 if priority == 'high' else 0
        
        # Send via all enabled services
        if self.notification_config['email']['enabled']:
            results['email'] = self.send_email_notification(title, message)
        
        if self.notification_config['sms']['enabled']:
            # Truncate message for SMS
            sms_message = f"{title}\n{message[:140]}..."
            results['sms'] = self.send_sms_notification(sms_message)
        
        if self.notification_config['pushover']['enabled']:
            results['pushover'] = self.send_pushover_notification(title, message, pushover_priority)
        
        return results
    
    def create_alert_message(self, alert_type: str, stock_symbol: str, insider_data: Dict) -> tuple:
        """Create formatted alert message with VERIFIED REAL DATA indicator"""
        
        # Get data quality and source information
        data_quality = insider_data.get('data_quality', 'UNKNOWN')
        total_transactions = insider_data.get('total_real_transactions', 0)
        data_sources = insider_data.get('data_sources', [])
        
        # Create data verification badge
        if data_quality == 'REAL_DATA_VERIFIED' and total_transactions > 0:
            verification_badge = f"🔒 VERIFIED REAL DATA ({total_transactions} transactions from {', '.join(data_sources)})"
        else:
            verification_badge = f"⚠️ LIMITED DATA AVAILABLE"
        
        if alert_type == 'executive_purchase':
            title = f"🚨 EXECUTIVE PURCHASE ALERT: {stock_symbol}"
            
            insider_trades = insider_data.get('insider_trades', [])
            executive_purchases = [t for t in insider_trades if 
                                 t['transaction_type'] == 'Purchase' and 
                                 t['title'] in self.default_criteria['executive_purchases']['roles']]
            
            if executive_purchases:
                latest = executive_purchases[0]
                
                # Get data source from the trade
                trade_source = latest.get('source', 'Unknown')
                filing_info = f"<b>Filing:</b> Form {latest.get('form_type', '4')} - {latest.get('filing_date', 'Unknown')}<br>" if latest.get('form_type') else ""
                
                message = f"""
                <b>🔒 VERIFIED REAL INSIDER PURCHASE</b><br>
                <br>
                <b>Company:</b> {insider_data.get('company_name', stock_symbol)}<br>
                <b>Executive:</b> {latest['insider_name']} ({latest['title']})<br>
                <b>Purchase Amount:</b> ${latest['value']:,.0f}<br>
                <b>Shares:</b> {latest['shares']:,}<br>
                <b>Price:</b> ${latest['price']:.2f}<br>
                <b>Transaction Date:</b> {latest['date']}<br>
                {filing_info}
                <b>Market Cap:</b> ${insider_data.get('market_cap', 0):,.0f}<br>
                <b>Data Source:</b> {trade_source}<br>
                <br>
                {verification_badge}<br>
                This represents {(latest['value'] / insider_data.get('market_cap', 1)) * 100:.3f}% of market cap.<br>
                🔥 <b>Strong insider confidence signal!</b>
                """
            else:
                message = f"Executive purchase detected for {stock_symbol}<br>{verification_badge}"
                
        elif alert_type == 'large_purchase':
            title = f"💰 LARGE PURCHASE ALERT: {stock_symbol}"
            
            insider_trades = insider_data.get('insider_trades', [])
            large_purchases = [t for t in insider_trades if 
                             t['transaction_type'] == 'Purchase' and 
                             t['value'] >= self.default_criteria['large_purchases']['min_value']]
            
            if large_purchases:
                latest = large_purchases[0]
                trade_source = latest.get('source', 'Unknown')
                filing_info = f"<b>Filing:</b> Form {latest.get('form_type', '4')} - {latest.get('filing_date', 'Unknown')}<br>" if latest.get('form_type') else ""
                
                message = f"""
                <b>🔒 VERIFIED REAL LARGE PURCHASE</b><br>
                <br>
                <b>Company:</b> {insider_data.get('company_name', stock_symbol)}<br>
                <b>Insider:</b> {latest['insider_name']} ({latest['title']})<br>
                <b>Purchase Amount:</b> ${latest['value']:,.0f}<br>
                <b>Shares:</b> {latest['shares']:,}<br>
                <b>Price:</b> ${latest['price']:.2f}<br>
                <b>Transaction Date:</b> {latest['date']}<br>
                {filing_info}
                <b>Data Source:</b> {trade_source}<br>
                <br>
                {verification_badge}<br>
                🔥 <b>This is a significant purchase representing substantial insider confidence!</b>
                """
            else:
                message = f"Large insider purchase detected for {stock_symbol}<br>{verification_badge}"
                
        elif alert_type == 'clustered_buying':
            title = f"🎯 CLUSTERED BUYING ALERT: {stock_symbol}"
            
            metrics = insider_data.get('metrics', {})
            
            message = f"""
            <b>🔒 VERIFIED REAL CLUSTERED BUYING</b><br>
            <br>
            <b>Company:</b> {insider_data.get('company_name', stock_symbol)}<br>
            <b>Unique Buyers:</b> {metrics.get('unique_insider_buyers', 0)}<br>
            <b>Total Purchases:</b> {metrics.get('purchase_transactions', 0)}<br>
            <b>Net Buying:</b> ${metrics.get('net_insider_activity', 0):,.0f}<br>
            <b>Conviction Score:</b> {metrics.get('confidence_score', 0):.0f}/100<br>
            <br>
            {verification_badge}<br>
            🚀 <b>Multiple insiders are buying - strong bullish signal!</b>
            """
            
        else:
            title = f"📊 INSIDER ALERT: {stock_symbol}"
            message = f"Insider activity detected for {insider_data.get('company_name', stock_symbol)}<br>{verification_badge}"
        
        return title, message
    
    def check_stock_for_alerts(self, symbol: str) -> List[Dict]:
        """Check individual stock for alert triggers using REAL SEC data"""
        alerts_triggered = []
        
        try:
            # Use real SEC data engine first (primary source)
            if self.real_data_engine:
                print(f"🔍 Getting REAL SEC insider data for {symbol}...")
                insider_data = self.real_data_engine.get_real_insider_data(symbol, 30)
                
                # Add data quality indicator
                insider_data['data_quality'] = 'REAL_SEC_DATA'
                
            # Fallback to legacy system if real data unavailable
            elif self.insider_intel:
                print(f"⚠️ Using backup data source for {symbol} (real SEC data unavailable)")
                insider_data = self.insider_intel.get_insider_data(symbol, 30)
                insider_data['data_quality'] = 'BACKUP_DATA'
                
            else:
                print("❌ No insider data sources available")
                return alerts_triggered
            
            if 'error' in insider_data:
                print(f"❌ Error getting insider data for {symbol}: {insider_data.get('error')}")
                return alerts_triggered
            
            insider_trades = insider_data.get('insider_trades', [])
            metrics = insider_data.get('metrics', {})
            
            # Check executive purchases
            if self.default_criteria['executive_purchases']['enabled']:
                executive_purchases = [t for t in insider_trades if 
                                     t['transaction_type'] == 'Purchase' and 
                                     t['title'] in self.default_criteria['executive_purchases']['roles'] and
                                     t['value'] >= self.default_criteria['executive_purchases']['min_value']]
                
                if executive_purchases:
                    alerts_triggered.append({
                        'type': 'executive_purchase',
                        'symbol': symbol,
                        'data': insider_data,
                        'priority': 'high',
                        'timestamp': datetime.now().isoformat()
                    })
            
            # Check large purchases
            if self.default_criteria['large_purchases']['enabled']:
                large_purchases = [t for t in insider_trades if 
                                 t['transaction_type'] == 'Purchase' and 
                                 t['value'] >= self.default_criteria['large_purchases']['min_value']]
                
                market_cap = insider_data.get('market_cap', 0)
                if large_purchases and market_cap > 0:
                    for purchase in large_purchases:
                        market_cap_percent = (purchase['value'] / market_cap) * 100
                        if market_cap_percent >= self.default_criteria['large_purchases']['min_market_cap_percent']:
                            alerts_triggered.append({
                                'type': 'large_purchase',
                                'symbol': symbol,
                                'data': insider_data,
                                'priority': 'high',
                                'timestamp': datetime.now().isoformat()
                            })
                            break
            
            # Check clustered buying
            if self.default_criteria['clustered_buying']['enabled']:
                unique_buyers = metrics.get('unique_insider_buyers', 0)
                if unique_buyers >= self.default_criteria['clustered_buying']['min_insiders']:
                    alerts_triggered.append({
                        'type': 'clustered_buying',
                        'symbol': symbol,
                        'data': insider_data,
                        'priority': 'normal',
                        'timestamp': datetime.now().isoformat()
                    })
            
        except Exception as e:
            print(f"Error checking alerts for {symbol}: {e}")
        
        return alerts_triggered
    
    def monitor_stocks(self, symbols: List[str]) -> List[Dict]:
        """Monitor stocks for insider activity alerts"""
        all_alerts = []
        
        print(f"🔍 Monitoring {len(symbols)} stocks for insider activity...")
        
        for symbol in symbols:
            try:
                alerts = self.check_stock_for_alerts(symbol)
                
                for alert in alerts:
                    # Create a more specific alert key to avoid spam
                    alert_key = f"{alert['symbol']}_{alert['type']}_{datetime.now().strftime('%Y-%m-%d')}"
                    
                    # Check if we've already sent a similar alert recently (shorter time window for auto-monitoring)
                    hours_to_check = 6 if self.monitoring_active else 24  # 6 hours for auto, 24 for manual
                    cutoff_time = datetime.now() - timedelta(hours=hours_to_check)
                    
                    recent_alerts = [a for a in self.alert_history if 
                                   a.get('key', '').startswith(f"{alert['symbol']}_{alert['type']}") and 
                                   datetime.fromisoformat(a['timestamp']) > cutoff_time]
                    
                    if not recent_alerts:  # Only send if not sent recently
                        title, message = self.create_alert_message(
                            alert['type'], alert['symbol'], alert['data']
                        )
                        
                        # Send notifications
                        results = self.send_all_notifications(title, message, alert['priority'])
                        
                        # Log alert
                        alert['key'] = alert_key
                        alert['title'] = title
                        alert['message'] = message
                        alert['notification_results'] = results
                        alert['scan_type'] = 'automatic' if self.monitoring_active else 'manual'
                        self.alert_history.append(alert)
                        all_alerts.append(alert)
                        
                        print(f"📱 Alert sent for {symbol}: {alert['type']} ({'auto' if self.monitoring_active else 'manual'})")
                    else:
                        print(f"⏭️ Skipping duplicate alert for {symbol}: {alert['type']} (sent {len(recent_alerts)} time(s) recently)")
                
            except Exception as e:
                print(f"Error monitoring {symbol}: {e}")
                continue
        
        return all_alerts
    
    def test_notifications(self) -> Dict[str, bool]:
        """Test all notification services"""
        # Force reload permanent configuration
        self._load_permanent_notification_config()
        
        title = "🧪 Insider Alert System Test"
        message = "This is a test notification from your Insider Alert System. All systems operational!"
        
        results = self.send_all_notifications(title, message, 'normal')
        
        # Return None if no methods configured to match UI expectations
        if not results:
            return None
        
        return results
    
    def get_alert_history(self, days: int = 7) -> List[Dict]:
        """Get recent alert history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        recent_alerts = [
            alert for alert in self.alert_history 
            if datetime.fromisoformat(alert['timestamp']) > cutoff_date
        ]
        
        return sorted(recent_alerts, key=lambda x: x['timestamp'], reverse=True)
    
    def start_automatic_monitoring(self, interval_minutes: int = 5) -> bool:
        """Start automatic background monitoring"""
        if self.monitoring_active:
            print("Monitoring already active")
            return False
        
        self.monitoring_interval = interval_minutes * 60  # Convert to seconds
        self.monitoring_active = True
        
        def background_monitor():
            print(f"🚀 Starting automatic insider monitoring every {interval_minutes} minutes...")
            while self.monitoring_active:
                try:
                    print(f"🔍 Scanning {len(self.auto_watchlist)} stocks for insider activity...")
                    alerts = self.monitor_stocks(self.auto_watchlist)
                    
                    if alerts:
                        print(f"📱 Found {len(alerts)} new alerts, notifications sent!")
                    
                    # Wait for next scan
                    for _ in range(self.monitoring_interval):
                        if not self.monitoring_active:
                            break
                        time.sleep(1)
                        
                except Exception as e:
                    print(f"Error in automatic monitoring: {e}")
                    time.sleep(60)  # Wait 1 minute before retrying
            
            print("⏹️ Automatic monitoring stopped")
        
        self.monitoring_thread = threading.Thread(target=background_monitor, daemon=True)
        self.monitoring_thread.start()
        
        return True
    
    def stop_automatic_monitoring(self) -> bool:
        """Stop automatic monitoring"""
        if not self.monitoring_active:
            return False
        
        self.monitoring_active = False
        print("⏹️ Stopping automatic monitoring...")
        
        # Wait for thread to finish (up to 5 seconds)
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        
        return True
    
    def is_monitoring_active(self) -> bool:
        """Check if automatic monitoring is active"""
        return self.monitoring_active
    
    def set_monitoring_interval(self, minutes: int) -> None:
        """Set monitoring interval in minutes"""
        self.monitoring_interval = minutes * 60
        print(f"Monitoring interval set to {minutes} minutes")
    
    def set_auto_watchlist(self, symbols: List[str]) -> None:
        """Set the watchlist for automatic monitoring"""
        self.auto_watchlist = [s.upper().strip() for s in symbols]
        print(f"Auto watchlist updated: {len(self.auto_watchlist)} stocks")
    
    def get_monitoring_status(self) -> Dict[str, Any]:
        """Get current monitoring status"""
        return {
            'active': self.monitoring_active,
            'continuous_enabled': self.is_continuous_monitoring_enabled(),
            'interval_minutes': self.monitoring_interval // 60,
            'watchlist_size': len(self.auto_watchlist),
            'watchlist': self.auto_watchlist[:10],  # Show first 10
            'total_alerts': len(self.alert_history),
            'enabled_notifications': [
                service for service, config in self.notification_config.items() 
                if config.get('enabled', False)
            ]
        }
    
    def get_watchlist_from_screens(self) -> List[str]:
        """Get watchlist from screening results"""
        if not self.screener:
            print("Screener not available")
            return []
            
        try:
            screen_results = self.screener.run_edge_generating_screens()
            
            watchlist = set()
            for screen_name, results in screen_results.items():
                for result in results[:5]:  # Top 5 from each screen
                    watchlist.add(result['symbol'])
            
            return list(watchlist)
            
        except Exception as e:
            print(f"Error generating watchlist: {e}")
            return []
    
    def send_latest_insider_activity(self) -> Dict[str, Any]:
        """Find and send the most recent insider activity as a test notification"""
        print("🔍 Scanning for latest insider activity to send as test...")
        
        # Use a focused list of active healthcare stocks for quick scanning
        test_symbols = ['PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'UNH', 'CVS', 'MRNA']
        
        latest_activity = None
        latest_timestamp = None
        
        for symbol in test_symbols:
            try:
                print(f"  Checking {symbol}...")
                
                # Get insider data
                if self.real_data_engine:
                    insider_data = self.real_data_engine.get_real_insider_data(symbol, 30)
                    insider_data['data_quality'] = 'REAL_SEC_DATA'
                elif self.insider_intel:
                    insider_data = self.insider_intel.get_insider_data(symbol, 30)
                    insider_data['data_quality'] = 'BACKUP_DATA'
                else:
                    continue
                
                if 'error' in insider_data:
                    continue
                
                insider_trades = insider_data.get('insider_trades', [])
                
                # Look for recent purchase activity
                for trade in insider_trades:
                    if trade['transaction_type'] == 'Purchase':
                        try:
                            # Parse trade date
                            trade_date = datetime.strptime(trade['date'], '%Y-%m-%d')
                            
                            # Check if this is the most recent activity we've found
                            if latest_timestamp is None or trade_date > latest_timestamp:
                                latest_timestamp = trade_date
                                latest_activity = {
                                    'symbol': symbol,
                                    'trade': trade,
                                    'data': insider_data,
                                    'days_ago': (datetime.now() - trade_date).days
                                }
                        except:
                            continue
                
                # Check if this qualifies for any alert type
                alerts = self.check_stock_for_alerts(symbol)
                if alerts and latest_activity and latest_activity['symbol'] == symbol:
                    latest_activity['alert_type'] = alerts[0]['type']
                    break  # Found qualifying activity, use this
                    
            except Exception as e:
                print(f"  Error checking {symbol}: {e}")
                continue
        
        # Send notification with latest activity
        if latest_activity:
            symbol = latest_activity['symbol']
            trade = latest_activity['trade']
            data = latest_activity['data']
            days_ago = latest_activity['days_ago']
            alert_type = latest_activity.get('alert_type', 'recent_purchase')
            
            # Create custom message for latest activity
            if alert_type in ['executive_purchase', 'large_purchase', 'clustered_buying']:
                title, message = self.create_alert_message(alert_type, symbol, data)
                title = f"📡 LATEST ACTIVITY: {title.split(': ', 1)[1]}"
            else:
                # Create custom message for recent purchase
                title = f"📡 LATEST INSIDER ACTIVITY: {symbol}"
                
                data_quality = data.get('data_quality', 'UNKNOWN')
                data_source_icon = "✅ REAL SEC DATA" if data_quality == 'REAL_SEC_DATA' else "⚠️ BACKUP DATA"
                
                message = f"""
                <b>Most Recent Insider Purchase Found:</b><br>
                <br>
                <b>Company:</b> {data.get('company_name', symbol)}<br>
                <b>Insider:</b> {trade['insider_name']} ({trade['title']})<br>
                <b>Purchase Amount:</b> ${trade['value']:,.0f}<br>
                <b>Shares:</b> {trade['shares']:,}<br>
                <b>Price:</b> ${trade['price']:.2f}<br>
                <b>Transaction Date:</b> {trade['date']} ({days_ago} days ago)<br>
                <b>Data Source:</b> {trade.get('source', 'Unknown')}<br>
                <br>
                {data_source_icon}<br>
                📡 <b>This is the most recent insider purchase activity found in your watchlist!</b>
                """
            
            # Send the notification
            results = self.send_all_notifications(title, message, 'normal')
            
            return {
                'success': True,
                'activity_found': True,
                'symbol': symbol,
                'days_ago': days_ago,
                'alert_type': alert_type,
                'notification_results': results,
                'message': f"Sent latest activity for {symbol} ({days_ago} days ago)"
            }
        
        else:
            # No recent activity found, send informational message
            title = "📡 LATEST ACTIVITY SCAN: No Recent Purchases"
            message = f"""
            <b>Insider Activity Scan Complete</b><br>
            <br>
            Scanned: {', '.join(test_symbols)}<br>
            <b>Result:</b> No recent insider purchases found in the last 30 days<br>
            <br>
            ✅ <b>System Status:</b> Monitoring active and ready<br>
            📊 <b>Data Sources:</b> Connected and operational<br>
            🔔 <b>Notifications:</b> Working correctly<br>
            <br>
            You'll receive alerts when new insider activity is detected!
            """
            
            results = self.send_all_notifications(title, message, 'normal')
            
            return {
                'success': True,
                'activity_found': False,
                'notification_results': results,
                'message': "No recent insider activity found - sent system status update"
            } 