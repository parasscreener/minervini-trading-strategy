"""
Configuration module for Mark Minervini Trading Strategy
Centralizes all configuration settings and defaults
"""

import os
from datetime import datetime

class TradingConfig:
    """Centralized configuration for the trading strategy"""

    # Email Configuration
    SENDER_EMAIL = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
    SENDER_PASSWORD = os.getenv('SENDER_PASSWORD', 'your-app-password')  
    RECIPIENT_EMAIL = os.getenv('RECIPIENT_EMAIL', 'paras.m.parmar@gmail.com')

    # Trading Parameters
    INITIAL_CAPITAL = float(os.getenv('INITIAL_CAPITAL', '1000000'))  # ₹10 Lakh
    RISK_PER_TRADE = float(os.getenv('RISK_PER_TRADE', '0.01'))  # 1%
    MAX_POSITION_SIZE = float(os.getenv('MAX_POSITION_SIZE', '0.05'))  # 5%
    MAX_POSITIONS = int(os.getenv('MAX_POSITIONS', '10'))  # Max concurrent positions

    # Stop Loss Configuration  
    STOP_LOSS_PERCENT = float(os.getenv('STOP_LOSS_PERCENT', '0.07'))  # 7%
    TRAILING_STOP_ENABLED = os.getenv('TRAILING_STOP_ENABLED', 'true').lower() == 'true'

    # Data Configuration
    DATA_PERIOD_SCREENING = os.getenv('DATA_PERIOD_SCREENING', '2y')
    DATA_PERIOD_BACKTESTING = os.getenv('DATA_PERIOD_BACKTESTING', '10y')
    NIFTY_INDEX_SYMBOL = os.getenv('NIFTY_INDEX_SYMBOL', '^NSEI')

    # Screening Configuration
    MIN_STOCK_PRICE = float(os.getenv('MIN_STOCK_PRICE', '100'))  # Minimum ₹100
    MIN_VOLUME_RATIO = float(os.getenv('MIN_VOLUME_RATIO', '0.5'))  # 50% of avg volume

    # Trend Template Configuration
    SMA_PERIODS = [50, 150, 200]  # Moving average periods
    MIN_DISTANCE_FROM_HIGH = float(os.getenv('MIN_DISTANCE_FROM_HIGH', '25'))  # 25%
    MIN_DISTANCE_FROM_LOW = float(os.getenv('MIN_DISTANCE_FROM_LOW', '30'))  # 30%

    # VCP Configuration
    MIN_VCP_CONTRACTIONS = int(os.getenv('MIN_VCP_CONTRACTIONS', '2'))
    VCP_VOLUME_THRESHOLD = float(os.getenv('VCP_VOLUME_THRESHOLD', '1.2'))  # 20% above average

    # Backtesting Configuration
    BACKTEST_START_YEAR = int(os.getenv('BACKTEST_START_YEAR', str(datetime.now().year - 10)))
    BENCHMARK_SYMBOL = os.getenv('BENCHMARK_SYMBOL', '^NSEI')

    # Runtime Flags
    FORCE_BACKTEST = os.getenv('FORCE_BACKTEST', 'false').lower() == 'true'
    TEST_MODE = os.getenv('TEST_MODE', 'false').lower() == 'true'
    ENABLE_DEBUG = os.getenv('ENABLE_DEBUG', 'false').lower() == 'true'

    # Output Configuration
    SAVE_CSV_REPORTS = os.getenv('SAVE_CSV_REPORTS', 'true').lower() == 'true'
    EMAIL_HTML_FORMAT = os.getenv('EMAIL_HTML_FORMAT', 'true').lower() == 'true'

    @classmethod
    def get_email_config(cls):
        """Get email configuration dictionary"""
        return {
            'sender_email': cls.SENDER_EMAIL,
            'sender_password': cls.SENDER_PASSWORD,
            'recipient_email': cls.RECIPIENT_EMAIL,
            'html_format': cls.EMAIL_HTML_FORMAT
        }

    @classmethod
    def get_trading_config(cls):
        """Get trading configuration dictionary"""
        return {
            'initial_capital': cls.INITIAL_CAPITAL,
            'risk_per_trade': cls.RISK_PER_TRADE,
            'max_position_size': cls.MAX_POSITION_SIZE,
            'max_positions': cls.MAX_POSITIONS,
            'stop_loss_percent': cls.STOP_LOSS_PERCENT,
            'trailing_stop_enabled': cls.TRAILING_STOP_ENABLED
        }

    @classmethod
    def get_screening_config(cls):
        """Get screening configuration dictionary"""
        return {
            'min_stock_price': cls.MIN_STOCK_PRICE,
            'min_volume_ratio': cls.MIN_VOLUME_RATIO,
            'sma_periods': cls.SMA_PERIODS,
            'min_distance_from_high': cls.MIN_DISTANCE_FROM_HIGH,
            'min_distance_from_low': cls.MIN_DISTANCE_FROM_LOW,
            'min_vcp_contractions': cls.MIN_VCP_CONTRACTIONS,
            'vcp_volume_threshold': cls.VCP_VOLUME_THRESHOLD
        }

    @classmethod
    def print_config(cls):
        """Print current configuration for debugging"""
        print("🔧 TRADING STRATEGY CONFIGURATION")
        print("=" * 40)
        print(f"💰 Initial Capital: ₹{cls.INITIAL_CAPITAL:,.0f}")
        print(f"⚠️ Risk per Trade: {cls.RISK_PER_TRADE*100:.1f}%")
        print(f"📊 Max Position Size: {cls.MAX_POSITION_SIZE*100:.1f}%")
        print(f"🎯 Max Positions: {cls.MAX_POSITIONS}")
        print(f"🛑 Stop Loss: {cls.STOP_LOSS_PERCENT*100:.1f}%")
        print(f"📧 Recipient: {cls.RECIPIENT_EMAIL}")
        print(f"🧪 Test Mode: {cls.TEST_MODE}")
        print(f"📈 Force Backtest: {cls.FORCE_BACKTEST}")

if __name__ == "__main__":
    # Test configuration loading
    config = TradingConfig()
    config.print_config()
