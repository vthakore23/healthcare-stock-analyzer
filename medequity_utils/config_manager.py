import json
import os
from typing import Dict, Any
from datetime import datetime

class ConfigManager:
    """Secure configuration manager for storing user credentials and settings"""
    
    def __init__(self):
        self.config_dir = os.path.join(os.path.dirname(__file__), '..', '.streamlit')
        self.config_file = os.path.join(self.config_dir, 'user_config.json')
        self.ensure_config_dir()
        self.load_config()
    
    def ensure_config_dir(self):
        """Ensure the config directory exists"""
        if not os.path.exists(self.config_dir):
            os.makedirs(self.config_dir, exist_ok=True)
    
    def load_config(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r') as f:
                    self.config = json.load(f)
            else:
                self.config = self.get_default_config()
                self.save_config()
        except Exception as e:
            print(f"Error loading config: {e}")
            self.config = self.get_default_config()
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'pushover': {
                'app_token': '',
                'user_key': '',
                'enabled': False,
                'setup_date': ''
            },
            'email': {
                'sender_email': '',
                'sender_password': '',
                'recipient_email': '',
                'enabled': False,
                'setup_date': ''
            },
            'sms': {
                'twilio_sid': '',
                'twilio_token': '',
                'twilio_phone': '',
                'recipient_phone': '',
                'enabled': False,
                'setup_date': ''
            },
            'alert_settings': {
                'monitoring_interval': 5,
                'auto_start_monitoring': False,
                'watchlist': [
                    'PFE', 'JNJ', 'MRK', 'ABBV', 'LLY', 'BMY', 'UNH', 'CVS',
                    'MRNA', 'BNTX', 'REGN', 'VRTX', 'BIIB', 'GILD', 'AMGN'
                ]
            },
            'version': '1.0',
            'last_updated': datetime.now().isoformat()
        }
    
    def save_config(self):
        """Save configuration to file"""
        try:
            self.config['last_updated'] = datetime.now().isoformat()
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
            print("✅ Configuration saved successfully")
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def setup_pushover_permanent(self, app_token: str, user_key: str) -> bool:
        """Setup Pushover credentials permanently"""
        try:
            self.config['pushover'] = {
                'app_token': app_token,
                'user_key': user_key,
                'enabled': True,
                'setup_date': datetime.now().isoformat()
            }
            self.save_config()
            print("🔔 Pushover credentials saved permanently!")
            return True
        except Exception as e:
            print(f"Error setting up Pushover: {e}")
            return False
    
    def setup_email_permanent(self, sender_email: str, sender_password: str, recipient_email: str) -> bool:
        """Setup email credentials permanently"""
        try:
            self.config['email'] = {
                'sender_email': sender_email,
                'sender_password': sender_password,
                'recipient_email': recipient_email,
                'enabled': True,
                'setup_date': datetime.now().isoformat()
            }
            self.save_config()
            print("📧 Email credentials saved permanently!")
            return True
        except Exception as e:
            print(f"Error setting up email: {e}")
            return False
    
    def setup_sms_permanent(self, twilio_sid: str, twilio_token: str, twilio_phone: str, recipient_phone: str) -> bool:
        """Setup SMS credentials permanently"""
        try:
            self.config['sms'] = {
                'twilio_sid': twilio_sid,
                'twilio_token': twilio_token,
                'twilio_phone': twilio_phone,
                'recipient_phone': recipient_phone,
                'enabled': True,
                'setup_date': datetime.now().isoformat()
            }
            self.save_config()
            print("📱 SMS credentials saved permanently!")
            return True
        except Exception as e:
            print(f"Error setting up SMS: {e}")
            return False
    
    def get_pushover_config(self) -> Dict[str, str]:
        """Get Pushover configuration"""
        return self.config.get('pushover', {})
    
    def get_email_config(self) -> Dict[str, str]:
        """Get email configuration"""
        return self.config.get('email', {})
    
    def get_sms_config(self) -> Dict[str, str]:
        """Get SMS configuration"""
        return self.config.get('sms', {})
    
    def get_alert_settings(self) -> Dict[str, Any]:
        """Get alert settings"""
        return self.config.get('alert_settings', {})
    
    def update_alert_settings(self, **kwargs) -> bool:
        """Update alert settings"""
        try:
            if 'alert_settings' not in self.config:
                self.config['alert_settings'] = {}
            
            self.config['alert_settings'].update(kwargs)
            self.save_config()
            return True
        except Exception as e:
            print(f"Error updating alert settings: {e}")
            return False
    
    def is_pushover_configured(self) -> bool:
        """Check if Pushover is configured"""
        pushover_config = self.get_pushover_config()
        return (pushover_config.get('enabled', False) and 
                pushover_config.get('app_token', '') and 
                pushover_config.get('user_key', ''))
    
    def is_email_configured(self) -> bool:
        """Check if email is configured"""
        email_config = self.get_email_config()
        return (email_config.get('enabled', False) and 
                email_config.get('sender_email', '') and 
                email_config.get('sender_password', '') and 
                email_config.get('recipient_email', ''))
    
    def is_sms_configured(self) -> bool:
        """Check if SMS is configured"""
        sms_config = self.get_sms_config()
        return (sms_config.get('enabled', False) and 
                sms_config.get('twilio_sid', '') and 
                sms_config.get('twilio_token', '') and 
                sms_config.get('twilio_phone', '') and 
                sms_config.get('recipient_phone', ''))
    
    def get_configured_methods(self) -> list:
        """Get list of configured notification methods"""
        methods = []
        if self.is_pushover_configured():
            methods.append('pushover')
        if self.is_email_configured():
            methods.append('email')
        if self.is_sms_configured():
            methods.append('sms')
        return methods
    
    def disable_method(self, method: str) -> bool:
        """Disable a notification method"""
        try:
            if method in self.config:
                self.config[method]['enabled'] = False
                self.save_config()
                return True
            return False
        except Exception as e:
            print(f"Error disabling {method}: {e}")
            return False
    
    def get_config_status(self) -> Dict[str, Any]:
        """Get overall configuration status"""
        return {
            'pushover_configured': self.is_pushover_configured(),
            'email_configured': self.is_email_configured(),
            'sms_configured': self.is_sms_configured(),
            'total_methods': len(self.get_configured_methods()),
            'configured_methods': self.get_configured_methods(),
            'last_updated': self.config.get('last_updated', 'Unknown'),
            'version': self.config.get('version', '1.0')
        } 