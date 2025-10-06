#!/usr/bin/env python3
"""
Mark Minervini Trading Strategy - Main Application
Coordinates data fetching, screening, backtesting, and email reporting
Author: Trading Strategy System
"""

import sys
import os
import traceback
from datetime import datetime, timedelta
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

# Import our custom modules
from data_fetcher import DataFetcher
from screener import MinerviniScreener
from backtester import MinerviniBacktester
from email_sender import TradingEmailSender

def setup_environment():
    """Setup environment and check requirements"""
    print("🔧 Setting up trading strategy environment...")

    # Check if required environment variables are set
    required_vars = ['SENDER_EMAIL', 'SENDER_PASSWORD']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print(f"⚠️ Missing environment variables: {missing_vars}")
        print("Note: Email functionality will use default values")

    # Ensure recipient email is set
    if not os.getenv('RECIPIENT_EMAIL'):
        os.environ['RECIPIENT_EMAIL'] = 'paras.m.parmar@gmail.com'

    print("✅ Environment setup complete")

def get_market_context():
    """Get overall market context for analysis"""
    try:
        import yfinance as yf

        # Fetch Nifty 50 data
        nifty = yf.Ticker("^NSEI")
        nifty_data = nifty.history(period="5d")

        if nifty_data.empty:
            return {"status": "No market data available"}

        latest = nifty_data.iloc[-1]
        previous = nifty_data.iloc[-2] if len(nifty_data) > 1 else latest

        # Calculate basic metrics
        current_level = latest['Close']
        change_pct = ((current_level - previous['Close']) / previous['Close']) * 100

        # Determine trend
        if change_pct > 0.5:
            trend = "🟢 Bullish"
        elif change_pct < -0.5:
            trend = "🔴 Bearish"
        else:
            trend = "🟡 Neutral"

        # Try to get VIX (India VIX)
        try:
            vix = yf.Ticker("^INDIAVIX")
            vix_data = vix.history(period="1d")
            vix_level = vix_data.iloc[-1]['Close'] if not vix_data.empty else "N/A"
        except:
            vix_level = "N/A"

        return {
            "nifty_level": f"{current_level:.2f} ({change_pct:+.2f}%)",
            "market_trend": trend,
            "vix_level": str(vix_level),
            "status": "success"
        }

    except Exception as e:
        print(f"⚠️ Could not fetch market context: {e}")
        return {"status": f"Error: {e}"}

def run_daily_screening():
    """Run the complete daily screening process"""
    print("\n" + "="*60)
    print("🚀 MARK MINERVINI TRADING STRATEGY - DAILY EXECUTION")
    print("="*60)
    print(f"📅 Execution Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}")
    print()

    results = {
        "screening_results": [],
        "backtest_results": None,
        "market_context": None,
        "execution_summary": {},
        "errors": []
    }

    try:
        # Step 1: Setup
        setup_environment()

        # Step 2: Get market context
        print("\n📊 STEP 1: Analyzing Market Context")
        print("-" * 40)
        market_context = get_market_context()
        results["market_context"] = market_context

        if market_context["status"] == "success":
            print(f"Nifty 50: {market_context['nifty_level']}")
            print(f"Trend: {market_context['market_trend']}")
            print(f"VIX: {market_context['vix_level']}")
        else:
            print("⚠️ Market context unavailable")

        # Step 3: Data Collection
        print("\n📈 STEP 2: Collecting Stock Data")
        print("-" * 40)

        fetcher = DataFetcher()
        stock_data = fetcher.fetch_multiple_stocks(period="2y")

        if not stock_data:
            raise Exception("No stock data could be fetched")

        print(f"✅ Successfully collected data for {len(stock_data)} stocks")
        results["execution_summary"]["stocks_collected"] = len(stock_data)

        # Step 4: Stock Screening
        print("\n🔍 STEP 3: Screening Stocks with Minervini Criteria")
        print("-" * 50)

        screener = MinerviniScreener()
        screening_results = screener.screen_stocks(stock_data)
        results["screening_results"] = screening_results

        if screening_results:
            strong_buys = len([r for r in screening_results if r["entry_signal"] == "STRONG BUY"])
            buys = len([r for r in screening_results if r["entry_signal"] == "BUY"])
            watches = len([r for r in screening_results if r["entry_signal"] == "WATCH"])

            print(f"✅ Screening completed:")
            print(f"   🟢 STRONG BUY: {strong_buys}")
            print(f"   🔵 BUY: {buys}")
            print(f"   🟡 WATCH: {watches}")

            results["execution_summary"].update({
                "strong_buys": strong_buys,
                "buys": buys,
                "watches": watches
            })
        else:
            print("⚠️ No stocks passed screening criteria")

        # Step 5: Backtesting (run weekly or on demand)
        current_day = datetime.now().weekday()  # 0=Monday, 6=Sunday
        run_backtest = current_day == 0 or os.getenv('FORCE_BACKTEST', '').lower() == 'true'

        if run_backtest and len(stock_data) >= 5:  # Only if sufficient data
            print("\n📊 STEP 4: Running Strategy Backtesting (Weekly)")
            print("-" * 45)

            try:
                backtester = MinerviniBacktester(initial_capital=1000000)

                # Use subset of stocks for faster backtesting in daily runs
                sample_stocks = dict(list(stock_data.items())[:50])  # Top 50 for speed

                backtester.backtest_strategy(sample_stocks, screener)
                backtest_report = backtester.generate_backtest_report()

                results["backtest_results"] = {
                    "performance_metrics": backtester.performance_metrics,
                    "report": backtest_report
                }

                print("✅ Backtesting completed")
                print(f"   📈 Annualized Return: {backtester.performance_metrics['annualized_return_pct']:.2f}%")
                print(f"   🎯 Win Rate: {backtester.performance_metrics['win_rate_pct']:.1f}%")

            except Exception as e:
                print(f"⚠️ Backtesting failed: {e}")
                results["errors"].append(f"Backtesting error: {e}")
        else:
            print("\n⏭️ STEP 4: Skipping backtesting (runs weekly on Mondays)")

        # Step 6: Generate Reports
        print("\n📧 STEP 5: Preparing Email Report")
        print("-" * 35)

        email_sender = TradingEmailSender()

        # Send main report
        success = email_sender.send_email(
            screening_results=screening_results,
            backtest_results=results["backtest_results"],
            market_context=market_context,
            include_csv=True
        )

        if success:
            print("✅ Email report sent successfully")
            results["execution_summary"]["email_sent"] = True
        else:
            print("❌ Failed to send email report")
            results["execution_summary"]["email_sent"] = False
            results["errors"].append("Email sending failed")

        # Step 7: Summary
        print("\n📋 EXECUTION SUMMARY")
        print("-" * 25)
        summary = results["execution_summary"]

        print(f"📊 Stocks Analyzed: {summary.get('stocks_collected', 0)}")
        print(f"🎯 Signals Generated: {summary.get('strong_buys', 0) + summary.get('buys', 0) + summary.get('watches', 0)}")
        print(f"📧 Email Status: {'✅ Sent' if summary.get('email_sent', False) else '❌ Failed'}")

        if results["errors"]:
            print(f"⚠️ Errors Encountered: {len(results['errors'])}")
            for error in results["errors"][:3]:  # Show first 3 errors
                print(f"   - {error}")

        print("\n🎉 Daily execution completed!")

        return results

    except Exception as e:
        error_msg = f"Critical error in main execution: {str(e)}"
        print(f"\n❌ {error_msg}")

        # Log full traceback
        traceback.print_exc()

        # Try to send error notification
        try:
            email_sender = TradingEmailSender()
            email_sender.send_error_notification(
                error_message=f"{error_msg}\n\nTraceback:\n{traceback.format_exc()}",
                script_name="Minervini Trading Strategy"
            )
        except:
            print("❌ Could not send error notification")

        results["errors"].append(error_msg)
        return results

def run_backtest_only():
    """Run comprehensive backtesting only"""
    print("\n🔍 Running comprehensive 10-year backtesting...")

    try:
        # Get data
        fetcher = DataFetcher()
        stock_data = fetcher.fetch_multiple_stocks(period="10y")  # 10 years

        if len(stock_data) < 10:
            print("❌ Insufficient data for meaningful backtesting")
            return

        # Initialize backtester
        backtester = MinerviniBacktester(
            initial_capital=1000000,  # 10 Lakh initial capital
            max_position_size=0.05,   # 5% max position
            risk_per_trade=0.01       # 1% risk per trade
        )

        # Initialize screener
        screener = MinerviniScreener()

        # Run backtest
        print(f"Starting backtest with {len(stock_data)} stocks...")
        backtester.backtest_strategy(stock_data, screener)

        # Generate report
        report = backtester.generate_backtest_report()
        print("\n" + "="*60)
        print(report)
        print("="*60)

        # Save detailed results
        with open("backtest_results.txt", "w") as f:
            f.write(report)

        # Save trades to CSV
        if backtester.trade_history:
            trades_df = pd.DataFrame(backtester.trade_history)
            trades_df.to_csv("trade_history.csv", index=False)
            print(f"\n💾 Saved {len(backtester.trade_history)} trades to trade_history.csv")

        # Save portfolio history
        if backtester.portfolio_history:
            portfolio_df = pd.DataFrame(backtester.portfolio_history)
            portfolio_df.to_csv("portfolio_history.csv", index=False)
            print(f"💾 Saved portfolio history to portfolio_history.csv")

    except Exception as e:
        print(f"❌ Backtesting failed: {e}")
        traceback.print_exc()

def main():
    """Main entry point"""
    print("🚀 Mark Minervini Trading Strategy System")
    print("📊 Implementing SEPA (Specific Entry Point Analysis)")
    print()

    # Parse command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--backtest-only":
            run_backtest_only()
        elif sys.argv[1] == "--test":
            print("🧪 Running in test mode...")
            # Run with limited data for testing
            os.environ['FORCE_BACKTEST'] = 'false'
            results = run_daily_screening()
            print(f"\n✅ Test completed. Errors: {len(results.get('errors', []))}")
        else:
            print("Usage: python main.py [--backtest-only | --test]")
            sys.exit(1)
    else:
        # Normal daily execution
        results = run_daily_screening()

        # Exit with error code if there were critical issues
        if results.get("errors"):
            sys.exit(1)

if __name__ == "__main__":
    main()
