"""
Email Sender Module for Automated Trading Reports
Sends detailed screening and backtesting results via email
Author: Trading Strategy System
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime
import json
import pandas as pd
from io import StringIO

class TradingEmailSender:
    def __init__(self):
        """Initialize email sender with configuration"""
        self.smtp_server = "smtp.gmail.com"
        self.port = 587  # For starttls

        # Get credentials from environment variables
        self.sender_email = os.getenv('SENDER_EMAIL', 'your-email@gmail.com')
        self.sender_password = os.getenv('SENDER_PASSWORD', 'your-app-password')
        self.recipient_email = os.getenv('RECIPIENT_EMAIL', 'paras.m.parmar@gmail.com')

    def create_screening_email(self, screening_results, backtest_results=None, market_context=None):
        """
        Create comprehensive email with screening and backtest results
        """
        # Create message container
        message = MIMEMultipart("alternative")
        message["Subject"] = f"📊 Minervini Stock Screening Report - {datetime.now().strftime('%Y-%m-%d')}"
        message["From"] = self.sender_email
        message["To"] = self.recipient_email

        # Create email content
        email_content = self.generate_email_content(screening_results, backtest_results, market_context)

        # Create HTML and plain text versions
        html_content = self.convert_to_html(email_content)
        text_content = email_content

        # Turn these into MIMEText objects
        part1 = MIMEText(text_content, "plain")
        part2 = MIMEText(html_content, "html")

        # Add HTML/plain-text parts to MIMEMultipart message
        message.attach(part1)
        message.attach(part2)

        return message

    def generate_email_content(self, screening_results, backtest_results=None, market_context=None):
        """Generate comprehensive email content"""
        content = []

        # Header
        content.append("🚀 MARK MINERVINI TRADING STRATEGY - DAILY SCREENING REPORT")
        content.append("=" * 70)
        content.append(f"📅 Report Date: {datetime.now().strftime('%A, %B %d, %Y at %I:%M %p IST')}")
        content.append(f"🎯 Strategy: SEPA (Specific Entry Point Analysis)")
        content.append(f"📧 Automated Report for: {self.recipient_email}")
        content.append("")

        # Market context (if provided)
        if market_context:
            content.append("🌍 MARKET OVERVIEW:")
            content.append("-" * 30)
            content.append(f"Nifty 50: {market_context.get('nifty_level', 'N/A')}")
            content.append(f"Market Trend: {market_context.get('market_trend', 'Analyzing...')}")
            content.append(f"Volatility (VIX): {market_context.get('vix_level', 'N/A')}")
            content.append("")

        # Screening Results Summary
        if screening_results:
            strong_buys = [r for r in screening_results if r.get("entry_signal") == "STRONG BUY"]
            buys = [r for r in screening_results if r.get("entry_signal") == "BUY"]  
            watches = [r for r in screening_results if r.get("entry_signal") == "WATCH"]

            content.append("📋 TODAY'S SCREENING RESULTS:")
            content.append("-" * 30)
            content.append(f"🟢 STRONG BUY Signals: {len(strong_buys)}")
            content.append(f"🔵 BUY Signals: {len(buys)}")
            content.append(f"🟡 WATCH Signals: {len(watches)}")
            content.append(f"📊 Total Stocks Screened: ~750 (Nifty Total Market)")
            content.append("")

            # Detailed stock recommendations
            if strong_buys or buys:
                content.append("🎯 TOP STOCK RECOMMENDATIONS:")
                content.append("-" * 50)

                priority_stocks = strong_buys + buys
                for i, result in enumerate(priority_stocks[:15], 1):  # Top 15 recommendations
                    symbol = result["symbol"].replace('.NS', '')
                    signal = result["entry_signal"]
                    strength = result.get("signal_strength", 0)
                    price = result.get("entry_price", 0)
                    stop_loss = result.get("stop_loss", 0)
                    position_pct = result.get("position_size_pct", 0)

                    template = result.get("template_result", {})
                    latest = template.get("latest_data", {})

                    content.append(f"{i:2d}. {symbol:12} | {signal:10} | Score: {strength}/10")
                    content.append(f"    💰 Entry: ₹{price:.2f} | Stop: ₹{stop_loss:.2f} | Size: {position_pct:.1f}%")

                    if latest:
                        content.append(f"    📊 52W High: -{latest.get('pct_from_high', 0):.1f}% | "
                                     f"Low: +{latest.get('pct_from_low', 0):.1f}%")

                    # VCP status
                    vcp = result.get("vcp_result", {})
                    vcp_status = "✅ VCP" if vcp.get("has_vcp", False) else "⏳ Building"
                    breakout = "🚀 Breakout!" if vcp.get("vcp_data", {}).get("breakout_candidate", False) else ""
                    content.append(f"    📈 Pattern: {vcp_status} {breakout}")
                    content.append("")
            else:
                content.append("⚠️ No strong buy or buy signals found today.")
                content.append("Market may be in a consolidation or weak phase.")
                content.append("")

        # Backtesting results summary
        if backtest_results:
            content.append("📊 STRATEGY PERFORMANCE (10-Year Backtest):")
            content.append("-" * 45)
            metrics = backtest_results.get('performance_metrics', {})

            content.append(f"📈 Total Return: {metrics.get('total_return_pct', 0):.2f}%")
            content.append(f"📈 Annualized Return: {metrics.get('annualized_return_pct', 0):.2f}%")
            content.append(f"🎯 Win Rate: {metrics.get('win_rate_pct', 0):.1f}%")
            content.append(f"📉 Max Drawdown: {metrics.get('max_drawdown_pct', 0):.2f}%")
            content.append(f"💰 Final Portfolio Value: ₹{metrics.get('final_value', 0):,.0f}")
            content.append(f"🎲 Total Trades: {metrics.get('total_trades', 0)}")
            content.append("")

        # Risk Management Reminder
        content.append("⚠️ RISK MANAGEMENT GUIDELINES:")
        content.append("-" * 35)
        content.append("• Never risk more than 1% of capital per trade")
        content.append("• Always use stop-losses at 7-8% below entry")
        content.append("• Maximum position size: 5% of portfolio")
        content.append("• Trail stops using 10-day EMA for profit protection")
        content.append("• Cut losses quickly, let winners run")
        content.append("")

        # Market Timing Notes
        content.append("⏰ MARKET TIMING NOTES:")
        content.append("-" * 25)
        content.append("• Best entries: Market opens with strong volume")
        content.append("• Avoid: Last 30 minutes of trading day")
        content.append("• Monitor: Overall market direction (Nifty trend)")
        content.append("• VIX above 25: Reduce position sizes")
        content.append("")

        # Educational Resources
        content.append("📚 STRATEGY RESOURCES:")
        content.append("-" * 22)
        content.append("• Book: 'Trade Like a Stock Market Wizard' - Mark Minervini")
        content.append("• Focus: SEPA (Specific Entry Point Analysis)")
        content.append("• Key: Trend Template + VCP Pattern Recognition")
        content.append("• Goal: Consistent 20-30% annual returns")
        content.append("")

        # Footer
        content.append("🤖 AUTOMATION DETAILS:")
        content.append("-" * 22)
        content.append("• Generated: GitHub Actions (Weekdays 9:30 AM IST)")
        content.append("• Data Source: NSE via yfinance")
        content.append("• Strategy: Mark Minervini SEPA System")
        content.append("• Contact: This is an automated report")
        content.append("")
        content.append("⚠️  DISCLAIMER: This is for educational purposes only.")
        content.append("    Always consult with a financial advisor before trading.")
        content.append("")
        content.append("Happy Trading! 🚀")
        content.append("=" * 70)

        return "\n".join(content)

    def convert_to_html(self, text_content):
        """Convert plain text content to HTML with basic formatting"""
        html_lines = []
        html_lines.append("<html><body style='font-family: Arial, sans-serif; line-height: 1.6;'>")
        html_lines.append("<div style='max-width: 800px; margin: 0 auto; padding: 20px;'>")

        lines = text_content.split('\n')

        for line in lines:
            line = line.strip()

            if not line:
                html_lines.append("<br>")
            elif line.startswith("🚀") and "REPORT" in line:
                html_lines.append(f"<h1 style='color: #2E8B57; text-align: center;'>{line}</h1>")
            elif line.startswith("=" * 70):
                html_lines.append("<hr style='border: 2px solid #2E8B57;'>")
            elif line.startswith("=" * 30) or line.startswith("-" * 30):
                html_lines.append("<hr style='border: 1px solid #ccc;'>")
            elif line.endswith(":") and any(emoji in line for emoji in ["📅", "🌍", "📋", "🎯", "📊", "⚠️", "⏰", "📚", "🤖"]):
                html_lines.append(f"<h3 style='color: #1E90FF; margin-top: 25px;'>{line}</h3>")
            elif line.startswith("•"):
                html_lines.append(f"<li style='margin: 5px 0;'>{line[1:].strip()}</li>")
            elif any(signal in line for signal in ["STRONG BUY", "BUY:", "WATCH:"]):
                html_lines.append(f"<p style='background: #E6F3FF; padding: 10px; border-left: 4px solid #1E90FF; margin: 8px 0;'><strong>{line}</strong></p>")
            elif line.startswith(("📈", "📉", "🎯", "💰", "🎲")):
                html_lines.append(f"<p style='margin: 5px 0; padding-left: 20px;'><strong>{line}</strong></p>")
            elif "Happy Trading!" in line:
                html_lines.append(f"<p style='text-align: center; font-size: 18px; color: #2E8B57; font-weight: bold;'>{line}</p>")
            elif "DISCLAIMER" in line:
                html_lines.append(f"<p style='color: #FF6B6B; font-weight: bold; text-align: center;'>{line}</p>")
            else:
                html_lines.append(f"<p style='margin: 5px 0;'>{line}</p>")

        html_lines.append("</div></body></html>")

        return "".join(html_lines)

    def create_csv_attachment(self, screening_results, filename="screening_results.csv"):
        """Create CSV attachment with screening results"""
        try:
            if not screening_results:
                return None

            # Convert results to DataFrame
            rows = []
            for result in screening_results:
                symbol = result["symbol"].replace('.NS', '')
                template = result.get("template_result", {})
                latest = template.get("latest_data", {})
                vcp = result.get("vcp_result", {})

                row = {
                    'Symbol': symbol,
                    'Signal': result.get("entry_signal", ""),
                    'Strength': result.get("signal_strength", 0),
                    'Entry_Price': result.get("entry_price", 0),
                    'Stop_Loss': result.get("stop_loss", 0),
                    'Position_Size_Pct': result.get("position_size_pct", 0),
                    'From_52W_High_Pct': latest.get('pct_from_high', 0),
                    'From_52W_Low_Pct': latest.get('pct_from_low', 0),
                    'Has_VCP': vcp.get("has_vcp", False),
                    'Breakout_Candidate': vcp.get("vcp_data", {}).get("breakout_candidate", False),
                    'Template_Score': f"{template.get('criteria_passed', 0)}/{template.get('total_criteria', 8)}",
                    'Analysis_Date': latest.get('date', '')
                }
                rows.append(row)

            df = pd.DataFrame(rows)

            # Create CSV attachment
            csv_buffer = StringIO()
            df.to_csv(csv_buffer, index=False)
            csv_content = csv_buffer.getvalue()

            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(csv_content.encode())
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename= {filename}'
            )

            return attachment

        except Exception as e:
            print(f"❌ Error creating CSV attachment: {e}")
            return None

    def send_email(self, screening_results, backtest_results=None, market_context=None, include_csv=True):
        """
        Send complete trading report email
        """
        try:
            # Create email message
            message = self.create_screening_email(screening_results, backtest_results, market_context)

            # Add CSV attachment if requested
            if include_csv and screening_results:
                csv_attachment = self.create_csv_attachment(screening_results)
                if csv_attachment:
                    message.attach(csv_attachment)

            # Create secure connection and send email
            context = ssl.create_default_context()

            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)

                text = message.as_string()
                server.sendmail(self.sender_email, self.recipient_email, text)

            print(f"✅ Email sent successfully to {self.recipient_email}")
            print(f"📧 Subject: {message['Subject']}")
            return True

        except Exception as e:
            print(f"❌ Failed to send email: {e}")
            return False

    def send_error_notification(self, error_message, script_name="Trading Strategy"):
        """Send error notification email"""
        try:
            message = MIMEText(f"""
🚨 TRADING SYSTEM ERROR ALERT

Script: {script_name}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S IST')}
Error: {error_message}

Please check the GitHub Actions logs for more details.

This is an automated error notification.
            """)

            message["Subject"] = f"🚨 Error in {script_name} - {datetime.now().strftime('%Y-%m-%d')}"
            message["From"] = self.sender_email
            message["To"] = self.recipient_email

            context = ssl.create_default_context()
            with smtplib.SMTP(self.smtp_server, self.port) as server:
                server.starttls(context=context)
                server.login(self.sender_email, self.sender_password)
                server.send_message(message)

            print(f"✅ Error notification sent to {self.recipient_email}")
            return True

        except Exception as e:
            print(f"❌ Failed to send error notification: {e}")
            return False

if __name__ == "__main__":
    # Test email sender
    print("Testing Email Sender...")

    # Create mock screening results for testing
    mock_results = [
        {
            "symbol": "RELIANCE.NS",
            "entry_signal": "STRONG BUY",
            "signal_strength": 8,
            "entry_price": 2500.0,
            "stop_loss": 2325.0,
            "position_size_pct": 3.2,
            "template_result": {
                "criteria_passed": 7,
                "total_criteria": 8,
                "latest_data": {
                    "date": datetime.now(),
                    "pct_from_high": 12.5,
                    "pct_from_low": 45.2
                }
            },
            "vcp_result": {
                "has_vcp": True,
                "vcp_data": {"breakout_candidate": True}
            }
        }
    ]

    # Test email creation (don't actually send)
    email_sender = TradingEmailSender()
    content = email_sender.generate_email_content(mock_results)

    print("✅ Sample email content generated")
    print("Preview (first 500 chars):")
    print(content[:500] + "...")

    # To actually send emails, you would need to set environment variables:
    # export SENDER_EMAIL="your-gmail@gmail.com"
    # export SENDER_PASSWORD="your-app-password" 
    # export RECIPIENT_EMAIL="paras.m.parmar@gmail.com"
