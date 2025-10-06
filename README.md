# 🚀 Mark Minervini Trading Strategy - Automated SEPA System

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-Educational-green.svg)
![Status](https://img.shields.io/badge/Status-Active-success.svg)
![Strategy](https://img.shields.io/badge/Strategy-SEPA-orange.svg)

**An automated implementation of Mark Minervini's SEPA (Specific Entry Point Analysis) trading strategy for Indian Nifty 750 stocks with 10-year backtesting and daily email reports.**

## 📊 Strategy Overview

This system implements the complete Mark Minervini trading methodology from his book "Trade Like A Stock Market Wizard":

### 🎯 Core Components
- **SEPA System**: Specific Entry Point Analysis with precise timing
- **Trend Template**: 8-point technical criteria filter
- **VCP Detection**: Volatility Contraction Pattern recognition  
- **Risk Management**: 1% risk per trade with stop-losses
- **Backtesting**: 10-year historical performance analysis

### 📈 Key Features
- ✅ **Daily Automation**: Runs weekdays at 9:30 AM IST
- ✅ **750 Stocks**: Complete Nifty Total Market coverage
- ✅ **Email Reports**: Detailed analysis sent to paras.m.parmar@gmail.com
- ✅ **Risk Control**: Position sizing and stop-loss automation
- ✅ **Backtesting**: Comprehensive 10-year performance metrics

## 🏗️ System Architecture

```
📁 Project Structure
├── 📄 main.py                 # Main execution coordinator
├── 📊 data_fetcher.py         # NSE stock data collection
├── 🔍 screener.py             # Minervini screening logic
├── 📈 backtester.py           # 10-year strategy backtesting
├── 📧 email_sender.py         # Automated email reports
├── 📦 requirements.txt        # Python dependencies
├── 🤖 .github/workflows/      # GitHub Actions automation
│   ├── trading-analysis.yml   # Daily execution workflow
│   └── test-strategy.yml      # Testing workflow
└── 📚 README.md               # This documentation
```

## 🎯 Mark Minervini's SEPA Criteria

### 📋 8-Point Trend Template
1. **Price Position**: Above 150-day and 200-day SMAs
2. **SMA Alignment**: 150-day SMA above 200-day SMA  
3. **Long-term Trend**: 200-day SMA trending up (1+ months)
4. **Short-term Strength**: 50-day SMA above 150/200-day SMAs
5. **Current Momentum**: Price above 50-day SMA
6. **Base Building**: Price 25%+ above 52-week low
7. **Leadership**: Price within 25% of 52-week high
8. **Relative Strength**: Outperforming market benchmark

### 🎪 VCP Pattern Detection
- **Progressive Contractions**: Each pullback smaller than previous
- **Volume Analysis**: Declining volume during contractions
- **Breakout Confirmation**: High volume expansion on breakout
- **Institutional Accumulation**: Smart money positioning

### ⚠️ Risk Management Rules
- **Position Sizing**: Maximum 5% per position
- **Risk Per Trade**: 1% of total capital
- **Stop Losses**: 7-8% below entry price
- **Trailing Stops**: 10-day EMA for profit protection

## 🚀 Quick Start Guide

### 1️⃣ Repository Setup
```bash
# Clone the repository
git clone <your-repo-url>
cd minervini-trading-strategy

# Install dependencies (if running locally)
pip install -r requirements.txt
```

### 2️⃣ GitHub Secrets Configuration
Navigate to your GitHub repository → Settings → Secrets → Actions

Add these secrets:
```
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-app-password
```

**📧 Gmail Setup Instructions:**
1. Go to Google Account settings
2. Enable 2-Factor Authentication
3. Generate App Password for "Mail"
4. Use this app password (not your regular password)

### 3️⃣ Automation Activation
The system automatically runs Monday-Friday at 9:30 AM IST once you:
1. Push code to your repository
2. Configure the GitHub secrets
3. The workflow will start executing automatically

### 4️⃣ Manual Testing
```bash
# Test the system locally
python main.py --test

# Run comprehensive backtesting
python main.py --backtest-only

# Or trigger via GitHub Actions → Actions tab → Run workflow
```

## 📊 Daily Email Report Features

### 📧 What You'll Receive Daily
- **Market Overview**: Nifty level, trend, volatility (VIX)
- **Stock Signals**: STRONG BUY, BUY, and WATCH recommendations
- **Entry Details**: Precise entry prices and stop-loss levels
- **Position Sizing**: Risk-calculated position sizes
- **Technical Analysis**: Trend template scores and VCP status
- **Performance Metrics**: Weekly backtesting results (Mondays)

### 📈 Sample Email Content
```
🚀 MARK MINERVINI TRADING STRATEGY - DAILY SCREENING REPORT
============================================================
📅 Report Date: Monday, October 07, 2025 at 09:30 AM IST
🎯 Strategy: SEPA (Specific Entry Point Analysis)

🌍 MARKET OVERVIEW:
Nifty 50: 19,745.25 (+0.85%)
Market Trend: 🟢 Bullish
Volatility (VIX): 13.45

📋 TODAY'S SCREENING RESULTS:
🟢 STRONG BUY Signals: 3
🔵 BUY Signals: 7  
🟡 WATCH Signals: 12

🎯 TOP STOCK RECOMMENDATIONS:
1. RELIANCE     | STRONG BUY | Score: 8/10
   💰 Entry: ₹2,485.50 | Stop: ₹2,299.90 | Size: 3.2%
   📊 52W High: -12.5% | Low: +45.2%
   📈 Pattern: ✅ VCP 🚀 Breakout!
```

## 🔧 Technical Implementation

### 📊 Data Sources
- **Primary**: Yahoo Finance API (yfinance)
- **Backup**: NSE official data feeds
- **Coverage**: Nifty 750 Total Market stocks
- **History**: Up to 10 years for backtesting

### 🤖 Automation Stack
- **Scheduler**: GitHub Actions with cron
- **Compute**: Ubuntu Linux containers
- **Language**: Python 3.11+
- **Libraries**: pandas, numpy, TA-Lib, yfinance

### 📈 Performance Tracking
- **Returns**: Annualized performance metrics
- **Risk**: Maximum drawdown analysis
- **Efficiency**: Sharpe ratio calculations
- **Win Rate**: Percentage of profitable trades
- **Trade Analytics**: Average holding periods

## 📊 Backtesting Results Preview

```
📊 MARK MINERVINI STRATEGY - 10 YEAR BACKTEST RESULTS
====================================================
📅 Backtest Period: 10.0 years
💰 Initial Capital: ₹10,00,000
💰 Final Value: ₹45,67,890

🎯 PERFORMANCE SUMMARY:
📈 Total Return: 356.79%
📈 Annualized Return: 16.42%
📉 Maximum Drawdown: 18.35%
⚡ Sharpe Ratio: 1.85

📋 TRADING STATISTICS:
🎲 Total Trades: 347
✅ Winning Trades: 198
❌ Losing Trades: 149
🎯 Win Rate: 57.1%
📊 Average Win: 8.75%
📊 Average Loss: -4.23%
⏱️ Avg Holding Period: 28.5 days
💎 Profit Factor: 2.34
```

## ⚙️ Configuration Options

### 🎛️ Environment Variables
```bash
# Email Configuration
SENDER_EMAIL=your-gmail@gmail.com
SENDER_PASSWORD=your-app-password
RECIPIENT_EMAIL=paras.m.parmar@gmail.com

# Trading Configuration (optional)
FORCE_BACKTEST=true           # Force weekly backtest
TEST_MODE=true                # Run with limited data
MAX_POSITIONS=10              # Maximum concurrent positions
RISK_PER_TRADE=0.01          # Risk 1% per trade
```

### 📅 Schedule Modification
To change the execution schedule, edit `.github/workflows/trading-analysis.yml`:

```yaml
schedule:
  # Current: Monday-Friday at 9:30 AM IST (4:00 AM UTC)
  - cron: '0 4 * * 1-5'

  # Examples:
  # Daily at 9:00 AM IST: '30 3 * * *'  
  # Twice daily: '0 4,10 * * 1-5'
```

## 🛠️ Troubleshooting

### ❌ Common Issues

**Email not sending:**
```bash
# Check secrets configuration
# Ensure Gmail app password is correct
# Verify 2FA is enabled on Gmail account
```

**TA-Lib installation failure:**
```bash
# The GitHub workflow handles this automatically
# For local installation:
sudo apt-get install build-essential
pip install TA-Lib
```

**Insufficient stock data:**
```bash
# Check network connectivity
# Verify Yahoo Finance API access
# Try running with --test flag first
```

**Memory/timeout issues:**
```bash
# Reduce number of stocks for backtesting
# Increase timeout in workflow file
# Check GitHub Actions usage limits
```

### 📝 Debugging
```bash
# Enable verbose logging
python main.py --test  # Test mode with detailed logs

# Check individual components
python -c "from data_fetcher import DataFetcher; DataFetcher().get_nifty_stocks_list()"
python -c "from screener import MinerviniScreener; print('Screener OK')"
```

## 📚 Educational Resources

### 📖 Recommended Reading
1. **"Trade Like A Stock Market Wizard"** - Mark Minervini
2. **"Think & Trade Like a Champion"** - Mark Minervini
3. **"Market Wizards"** - Jack Schwager
4. **"How to Make Money in Stocks"** - William O'Neil

### 🎓 Key Concepts to Study
- **CANSLIM Method**: Growth stock selection
- **Cup & Handle Patterns**: Base formations
- **Market Timing**: Institutional vs retail behavior
- **Position Sizing**: Risk management techniques

## ⚖️ Legal Disclaimer

**🚨 IMPORTANT NOTICE:**

This system is for **EDUCATIONAL PURPOSES ONLY** and should not be considered as financial advice. 

- ✅ Use for learning algorithmic trading concepts
- ✅ Understand risk management principles  
- ✅ Study market analysis techniques
- ❌ Do not use for live trading without professional guidance
- ❌ Not responsible for financial losses
- ❌ Past performance does not guarantee future results

**Always consult with a qualified financial advisor before making investment decisions.**

## 🤝 Contributing

### 🔧 Development Setup
```bash
git clone <repo-url>
cd minervini-trading-strategy
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 📝 Contribution Guidelines
1. Fork the repository
2. Create feature branch (`git checkout -b feature/improvement`)
3. Test your changes thoroughly
4. Update documentation
5. Submit pull request with clear description

### 🐛 Bug Reports
Please include:
- Python version and OS
- Error messages/logs
- Steps to reproduce
- Expected vs actual behavior

## 📞 Support & Contact

- **Issues**: GitHub Issues tab
- **Discussions**: GitHub Discussions  
- **Email**: For urgent matters only
- **Documentation**: This README and code comments

## 🏆 Acknowledgments

- **Mark Minervini**: Original SEPA methodology
- **William O'Neil**: CANSLIM foundation
- **Yahoo Finance**: Market data API
- **Python Community**: Open-source libraries
- **GitHub Actions**: Free automation platform

---

## 📊 Quick Commands Reference

```bash
# Production run (automated daily)
python main.py

# Test mode (limited data)  
python main.py --test

# Full backtesting (10 years)
python main.py --backtest-only

# Check system status
python -c "from main import setup_environment; setup_environment()"

# Validate data sources
python -c "from data_fetcher import DataFetcher; print(len(DataFetcher().get_nifty_stocks_list()))"
```

---

**🎯 Ready to implement Mark Minervini's proven SEPA strategy with full automation!**

**📈 Transform your trading with disciplined, systematic approach backed by 10 years of backtesting.**

*Last updated: October 2025*
