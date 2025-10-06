"""
Stock Screener Module implementing Mark Minervini's SEPA Strategy
Includes Trend Template, VCP Pattern Detection, and Entry/Exit Signals
Author: Trading Strategy System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MinerviniScreener:
    def __init__(self):
        self.trend_template_criteria = {
            'price_above_150_sma': False,
            'price_above_200_sma': False,
            'sma_150_above_200': False,
            'sma_200_trending_up': False,
            'price_above_50_sma': False,
            'sma_50_above_150_200': False,
            'price_near_52w_high': False,
            'price_above_52w_low_30pct': False
        }

    def apply_trend_template(self, df, symbol="Unknown"):
        """
        Apply Mark Minervini's 8-point Trend Template
        Returns dict with criteria results and overall pass/fail
        """
        if df.empty or len(df) < 200:
            return {"symbol": symbol, "passes_template": False, "criteria": {}, "latest_data": {}}

        try:
            # Get latest data point
            latest = df.iloc[-1]

            # Calculate trend template criteria
            criteria = {}

            # 1. Current stock price is above both 150-day and 200-day SMA
            criteria['price_above_150_sma'] = latest['Close'] > latest['SMA_150']
            criteria['price_above_200_sma'] = latest['Close'] > latest['SMA_200']

            # 2. 150-day SMA is above 200-day SMA
            criteria['sma_150_above_200'] = latest['SMA_150'] > latest['SMA_200']

            # 3. 200-day SMA is trending up for at least 1 month (20 trading days)
            if len(df) >= 220:
                sma_200_20_days_ago = df.iloc[-21]['SMA_200']
                criteria['sma_200_trending_up'] = latest['SMA_200'] > sma_200_20_days_ago
            else:
                criteria['sma_200_trending_up'] = False

            # 4. 50-day SMA is above both 150-day and 200-day SMA
            criteria['sma_50_above_150'] = latest['SMA_50'] > latest['SMA_150']
            criteria['sma_50_above_200'] = latest['SMA_50'] > latest['SMA_200']
            criteria['sma_50_above_150_200'] = criteria['sma_50_above_150'] and criteria['sma_50_above_200']

            # 5. Current stock price is trading above 50-day SMA
            criteria['price_above_50_sma'] = latest['Close'] > latest['SMA_50']

            # 6. Current price at least 25% above 52-week low (Minervini uses 30%)
            criteria['price_above_52w_low_30pct'] = latest['Pct_From_Low'] >= 30.0

            # 7. Current price within 25% of 52-week high
            criteria['price_near_52w_high'] = latest['Pct_From_High'] <= 25.0

            # 8. Relative Strength (simplified - using 20-day return > 70th percentile)
            # Note: In real implementation, you'd use IBD RS ranking or similar
            criteria['relative_strength'] = latest['RS'] > 0  # Positive momentum

            # Overall pass/fail - all criteria must be true
            main_criteria = [
                criteria['price_above_150_sma'],
                criteria['price_above_200_sma'], 
                criteria['sma_150_above_200'],
                criteria['sma_200_trending_up'],
                criteria['sma_50_above_150_200'],
                criteria['price_above_50_sma'],
                criteria['price_above_52w_low_30pct'],
                criteria['price_near_52w_high']
            ]

            passes_template = all(main_criteria)

            # Additional quality checks
            criteria['sufficient_volume'] = latest['Volume'] > latest['Volume_SMA_50'] * 0.5
            criteria['not_penny_stock'] = latest['Close'] > 100  # Above ₹100

            # Collect latest data for analysis
            latest_data = {
                'date': latest['Date'],
                'close': latest['Close'],
                'volume': latest['Volume'],
                'sma_50': latest['SMA_50'],
                'sma_150': latest['SMA_150'],
                'sma_200': latest['SMA_200'],
                'pct_from_high': latest['Pct_From_High'],
                'pct_from_low': latest['Pct_From_Low'],
                'rs': latest['RS'],
                'atr': latest['ATR']
            }

            return {
                "symbol": symbol,
                "passes_template": passes_template,
                "criteria": criteria,
                "latest_data": latest_data,
                "criteria_passed": sum(main_criteria),
                "total_criteria": len(main_criteria)
            }

        except Exception as e:
            print(f"❌ Error applying trend template to {symbol}: {e}")
            return {"symbol": symbol, "passes_template": False, "criteria": {}, "latest_data": {}}

    def detect_vcp_pattern(self, df, symbol="Unknown", min_contractions=2):
        """
        Detect Volatility Contraction Pattern (VCP)
        Returns dict with VCP analysis
        """
        try:
            if df.empty or len(df) < 100:
                return {"symbol": symbol, "has_vcp": False, "vcp_data": {}}

            # Look at last 100 days for VCP pattern
            recent_data = df.tail(100).copy()

            # Calculate rolling volatility (20-day ATR)
            recent_data['Rolling_ATR'] = recent_data['ATR'].rolling(window=20).mean()

            # Detect contractions (decreasing volatility periods)
            contractions = []
            volatility_values = recent_data['Rolling_ATR'].dropna()

            if len(volatility_values) < 20:
                return {"symbol": symbol, "has_vcp": False, "vcp_data": {}}

            # Find peaks and troughs in volatility
            for i in range(1, len(volatility_values) - 1):
                if (volatility_values.iloc[i] < volatility_values.iloc[i-1] and 
                    volatility_values.iloc[i] < volatility_values.iloc[i+1]):
                    contractions.append(i)

            # Check for progressive tightening
            has_vcp = False
            vcp_quality = "None"

            if len(contractions) >= min_contractions:
                # Check if contractions are getting tighter
                recent_contractions = contractions[-min_contractions:]
                volatility_at_contractions = [volatility_values.iloc[i] for i in recent_contractions]

                # Check if each contraction is smaller than the previous
                is_tightening = all(volatility_at_contractions[i] < volatility_at_contractions[i-1] 
                                  for i in range(1, len(volatility_at_contractions)))

                if is_tightening:
                    has_vcp = True
                    vcp_quality = "Good" if len(contractions) >= 3 else "Fair"

            # Check for breakout condition
            latest = recent_data.iloc[-1]
            breakout_candidate = False

            # Simple breakout check: price above recent resistance with volume
            if len(recent_data) >= 20:
                recent_high = recent_data['High'].tail(20).max()
                if (latest['Close'] > recent_high * 0.98 and  # Near or above recent high
                    latest['Volume'] > latest['Volume_SMA_50'] * 1.2):  # Above average volume
                    breakout_candidate = True

            vcp_data = {
                'contractions_found': len(contractions),
                'has_progressive_tightening': is_tightening if len(contractions) >= min_contractions else False,
                'vcp_quality': vcp_quality,
                'breakout_candidate': breakout_candidate,
                'current_atr': latest['ATR'],
                'avg_atr_20d': latest['Rolling_ATR'] if pd.notna(latest.get('Rolling_ATR', np.nan)) else 0
            }

            return {
                "symbol": symbol,
                "has_vcp": has_vcp,
                "vcp_data": vcp_data
            }

        except Exception as e:
            print(f"❌ Error detecting VCP for {symbol}: {e}")
            return {"symbol": symbol, "has_vcp": False, "vcp_data": {}}

    def generate_entry_signals(self, df, symbol="Unknown"):
        """
        Generate entry signals based on Minervini criteria
        """
        try:
            # Apply trend template
            template_result = self.apply_trend_template(df, symbol)

            # Check VCP pattern
            vcp_result = self.detect_vcp_pattern(df, symbol)

            # Generate entry signal
            entry_signal = "NONE"
            signal_strength = 0

            if template_result["passes_template"]:
                signal_strength += 5

                if vcp_result["has_vcp"]:
                    signal_strength += 3

                    if vcp_result["vcp_data"]["breakout_candidate"]:
                        signal_strength += 2
                        entry_signal = "STRONG BUY"
                    else:
                        entry_signal = "BUY"
                else:
                    entry_signal = "WATCH"

            # Calculate position sizing (risk-based)
            latest = df.iloc[-1]
            entry_price = latest['Close']
            atr = latest['ATR']

            # Risk 1% of capital with stop-loss at 7-8% below entry
            stop_loss_price = entry_price * 0.93  # 7% below entry
            risk_per_share = entry_price - stop_loss_price
            position_size_multiplier = 0.01 / (risk_per_share / entry_price) if risk_per_share > 0 else 0

            return {
                "symbol": symbol,
                "entry_signal": entry_signal,
                "signal_strength": signal_strength,
                "entry_price": entry_price,
                "stop_loss": stop_loss_price,
                "position_size_pct": min(position_size_multiplier * 100, 5.0),  # Max 5% position
                "template_result": template_result,
                "vcp_result": vcp_result,
                "analysis_date": latest['Date']
            }

        except Exception as e:
            print(f"❌ Error generating entry signals for {symbol}: {e}")
            return {"symbol": symbol, "entry_signal": "ERROR", "signal_strength": 0}

    def generate_exit_signals(self, df, symbol="Unknown", entry_price=None):
        """
        Generate exit signals based on Minervini exit rules
        """
        try:
            latest = df.iloc[-1]
            exit_signals = []

            current_price = latest['Close']

            if entry_price:
                # Calculate returns
                returns = (current_price - entry_price) / entry_price * 100

                # Stop-loss at 7-8% 
                if returns <= -7.0:
                    exit_signals.append("STOP_LOSS")

                # Take profits at significant levels
                if returns >= 20.0:
                    exit_signals.append("TAKE_PROFIT_20")
                elif returns >= 50.0:
                    exit_signals.append("TAKE_PROFIT_50")

            # Technical exit signals
            if current_price < latest['SMA_10']:  # Below 10-day SMA (trailing stop)
                exit_signals.append("TRAILING_STOP")

            if current_price < latest['SMA_50']:  # Below 50-day SMA
                exit_signals.append("SMA_50_BREAK")

            # Volume-based exit (selling pressure)
            if (latest['Volume'] > latest['Volume_SMA_50'] * 2.0 and 
                latest['Close'] < latest['Open']):  # High volume down day
                exit_signals.append("VOLUME_SELL")

            primary_exit = exit_signals[0] if exit_signals else "HOLD"

            return {
                "symbol": symbol,
                "exit_signals": exit_signals,
                "primary_exit": primary_exit,
                "current_price": current_price,
                "analysis_date": latest['Date']
            }

        except Exception as e:
            print(f"❌ Error generating exit signals for {symbol}: {e}")
            return {"symbol": symbol, "exit_signals": ["ERROR"], "primary_exit": "ERROR"}

    def screen_stocks(self, stock_data_dict):
        """
        Screen all stocks and return ranked results
        """
        results = []

        print(f"🔍 Screening {len(stock_data_dict)} stocks with Minervini criteria...")

        for symbol, df in stock_data_dict.items():
            try:
                entry_analysis = self.generate_entry_signals(df, symbol)

                if entry_analysis["signal_strength"] > 0:
                    results.append(entry_analysis)

            except Exception as e:
                print(f"❌ Error screening {symbol}: {e}")

        # Sort by signal strength
        results.sort(key=lambda x: x["signal_strength"], reverse=True)

        print(f"✅ Screening complete. Found {len(results)} stocks with signals")

        return results

    def create_screening_report(self, screening_results):
        """
        Create a detailed screening report
        """
        if not screening_results:
            return "No stocks passed the screening criteria."

        report = []
        report.append("🚀 MARK MINERVINI STOCK SCREENING RESULTS")
        report.append("=" * 50)
        report.append(f"📅 Analysis Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append(f"📊 Stocks Screened: {len(screening_results)} stocks passed criteria")
        report.append("")

        # Summary by signal type
        strong_buys = [r for r in screening_results if r["entry_signal"] == "STRONG BUY"]
        buys = [r for r in screening_results if r["entry_signal"] == "BUY"]
        watches = [r for r in screening_results if r["entry_signal"] == "WATCH"]

        report.append("📋 SIGNAL SUMMARY:")
        report.append(f"   🟢 STRONG BUY: {len(strong_buys)} stocks")
        report.append(f"   🔵 BUY: {len(buys)} stocks")
        report.append(f"   🟡 WATCH: {len(watches)} stocks")
        report.append("")

        # Detailed results for top signals
        report.append("🎯 TOP OPPORTUNITIES (Ranked by Signal Strength):")
        report.append("-" * 50)

        for i, result in enumerate(screening_results[:20], 1):  # Top 20
            symbol = result["symbol"].replace('.NS', '')
            signal = result["entry_signal"]
            strength = result["signal_strength"]
            price = result["entry_price"]
            stop_loss = result["stop_loss"]
            position_pct = result["position_size_pct"]

            template = result["template_result"]
            vcp = result["vcp_result"]

            report.append(f"{i:2d}. {symbol:15} | Signal: {signal:10} | Strength: {strength}/10")
            report.append(f"     💰 Price: ₹{price:.2f} | Stop: ₹{stop_loss:.2f} | Position: {position_pct:.1f}%")

            # Template criteria summary
            passed = template["criteria_passed"]
            total = template["total_criteria"]
            report.append(f"     📊 Template: {passed}/{total} | VCP: {'✅' if vcp['has_vcp'] else '❌'}")

            latest = template["latest_data"]
            report.append(f"     📈 From 52W High: {latest['pct_from_high']:.1f}% | From Low: {latest['pct_from_low']:.1f}%")
            report.append("")

        return "\n".join(report)

if __name__ == "__main__":
    # Test the screener
    print("Testing Minervini Screener...")

    screener = MinerviniScreener()

    # Test with sample data (you would use real data)
    import yfinance as yf

    test_symbol = "RELIANCE.NS"
    test_data = yf.Ticker(test_symbol).history(period="2y")

    if not test_data.empty:
        # Add indicators (simplified)
        test_data['SMA_50'] = test_data['Close'].rolling(50).mean()
        test_data['SMA_150'] = test_data['Close'].rolling(150).mean()
        test_data['SMA_200'] = test_data['Close'].rolling(200).mean()
        test_data['ATR'] = (test_data['High'] - test_data['Low']).rolling(14).mean()
        test_data.reset_index(inplace=True)

        result = screener.apply_trend_template(test_data, test_symbol)
        print(f"\nTrend Template Result for {test_symbol}:")
        print(f"Passes Template: {result['passes_template']}")
        print(f"Criteria Passed: {result['criteria_passed']}/{result['total_criteria']}")
