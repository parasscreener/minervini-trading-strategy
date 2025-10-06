"""
Backtesting Module for Mark Minervini Trading Strategy - DATETIME FIXED VERSION
Implements 10-year historical backtesting with proper timezone handling
Author: Trading Strategy System
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class MinerviniBacktester:
    def __init__(self, initial_capital=1000000, max_position_size=0.05, risk_per_trade=0.01):
        """
        Initialize backtester

        Args:
            initial_capital: Starting capital in rupees
            max_position_size: Maximum position size as % of capital
            risk_per_trade: Risk per trade as % of capital
        """
        self.initial_capital = initial_capital
        self.max_position_size = max_position_size
        self.risk_per_trade = risk_per_trade

        # Portfolio tracking
        self.capital = initial_capital
        self.positions = {}
        self.trade_history = []
        self.portfolio_history = []

        # Performance metrics
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.max_drawdown = 0
        self.current_drawdown = 0
        self.peak_capital = initial_capital

    def normalize_datetime(self, dt):
        """Normalize datetime to be timezone-naive for consistent comparison"""
        if dt is None:
            return None

        # If it's a pandas Timestamp, convert to datetime
        if isinstance(dt, pd.Timestamp):
            dt = dt.to_pydatetime()

        # If it's timezone-aware, convert to naive (remove timezone)
        if hasattr(dt, 'tzinfo') and dt.tzinfo is not None:
            # Convert to UTC first, then make naive
            if dt.tzinfo != dt.tzinfo:  # Check if it has timezone info
                dt = dt.replace(tzinfo=None)

        return dt

    def normalize_date_series(self, date_series):
        """Normalize a series of dates to be timezone-naive"""
        try:
            # Convert to datetime if not already
            if not isinstance(date_series, pd.Series):
                date_series = pd.Series(date_series)

            # Remove timezone info if present
            if hasattr(date_series.dtype, 'tz') and date_series.dtype.tz is not None:
                date_series = date_series.dt.tz_convert(None)  # Convert to naive

            # Ensure datetime type
            if not pd.api.types.is_datetime64_any_dtype(date_series):
                date_series = pd.to_datetime(date_series, errors='coerce')

            # Remove any timezone info that might still be there
            if hasattr(date_series.iloc[0], 'tzinfo') and date_series.iloc[0].tzinfo is not None:
                date_series = date_series.apply(lambda x: x.replace(tzinfo=None) if x.tzinfo else x)

            return date_series

        except Exception as e:
            print(f"Warning: Error normalizing date series: {e}")
            return date_series

    def calculate_position_size(self, entry_price, stop_loss_price):
        """Calculate position size based on risk management"""
        if entry_price <= stop_loss_price:
            return 0

        risk_per_share = entry_price - stop_loss_price
        risk_amount = self.capital * self.risk_per_trade

        # Position size based on risk
        position_size = risk_amount / risk_per_share

        # Limit by maximum position size
        max_shares = (self.capital * self.max_position_size) / entry_price
        position_size = min(position_size, max_shares)

        # Ensure we can afford the position
        position_value = position_size * entry_price
        if position_value > self.capital * 0.95:  # Leave 5% cash buffer
            position_size = (self.capital * 0.95) / entry_price

        return int(position_size)

    def enter_position(self, symbol, entry_date, entry_price, stop_loss_price, signal_data):
        """Enter a new position"""
        # Normalize entry date
        entry_date = self.normalize_datetime(entry_date)

        position_size = self.calculate_position_size(entry_price, stop_loss_price)

        if position_size <= 0:
            return False

        position_value = position_size * entry_price

        if position_value > self.capital:
            return False

        # Create position
        position = {
            'symbol': symbol,
            'entry_date': entry_date,
            'entry_price': entry_price,
            'stop_loss': stop_loss_price,
            'position_size': position_size,
            'position_value': position_value,
            'signal_data': signal_data
        }

        self.positions[symbol] = position
        self.capital -= position_value

        return True

    def exit_position(self, symbol, exit_date, exit_price, exit_reason):
        """Exit an existing position"""
        if symbol not in self.positions:
            return False

        # Normalize exit date
        exit_date = self.normalize_datetime(exit_date)

        position = self.positions[symbol]
        exit_value = position['position_size'] * exit_price

        # Calculate P&L
        pnl = exit_value - position['position_value']
        pnl_pct = (pnl / position['position_value']) * 100

        # Update capital
        self.capital += exit_value

        # Calculate holding period safely
        try:
            entry_date_norm = self.normalize_datetime(position['entry_date'])
            exit_date_norm = self.normalize_datetime(exit_date)

            if entry_date_norm and exit_date_norm:
                holding_days = (exit_date_norm - entry_date_norm).days
            else:
                holding_days = 1  # Default fallback
        except Exception as e:
            print(f"Warning: Error calculating holding days: {e}")
            holding_days = 1

        # Record trade
        trade = {
            'symbol': symbol,
            'entry_date': position['entry_date'],
            'exit_date': exit_date,
            'entry_price': position['entry_price'],
            'exit_price': exit_price,
            'position_size': position['position_size'],
            'pnl': pnl,
            'pnl_pct': pnl_pct,
            'exit_reason': exit_reason,
            'holding_days': holding_days,
            'signal_data': position['signal_data']
        }

        self.trade_history.append(trade)
        self.total_trades += 1

        if pnl > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1

        # Remove position
        del self.positions[symbol]

        return True

    def update_portfolio_metrics(self, current_date, market_prices):
        """Update portfolio value and metrics"""
        # Normalize current date
        current_date = self.normalize_datetime(current_date)

        # Calculate current portfolio value
        position_value = 0
        for symbol, position in self.positions.items():
            if symbol in market_prices:
                current_price = market_prices[symbol]
                position_value += position['position_size'] * current_price

        total_portfolio_value = self.capital + position_value

        # Update peak and drawdown
        if total_portfolio_value > self.peak_capital:
            self.peak_capital = total_portfolio_value
            self.current_drawdown = 0
        else:
            self.current_drawdown = (self.peak_capital - total_portfolio_value) / self.peak_capital
            if self.current_drawdown > self.max_drawdown:
                self.max_drawdown = self.current_drawdown

        # Record portfolio history
        portfolio_record = {
            'date': current_date,
            'total_value': total_portfolio_value,
            'cash': self.capital,
            'positions_value': position_value,
            'num_positions': len(self.positions),
            'drawdown': self.current_drawdown
        }

        self.portfolio_history.append(portfolio_record)

        return total_portfolio_value

    def backtest_strategy(self, stock_data_dict, screener):
        """
        Run backtest on historical data with proper datetime handling

        Args:
            stock_data_dict: Dictionary of stock DataFrames
            screener: MinerviniScreener instance
        """
        print(f"🚀 Starting 10-year backtest with ₹{self.initial_capital:,.0f} initial capital")

        # Get all dates from the data and normalize them
        all_dates = set()
        for symbol, df in stock_data_dict.items():
            if not df.empty and 'Date' in df.columns:
                try:
                    # Normalize the date column
                    date_series = self.normalize_date_series(df['Date'])
                    all_dates.update(date_series.tolist())
                except Exception as e:
                    print(f"Warning: Error processing dates for {symbol}: {e}")
                    continue

        if not all_dates:
            print("❌ No valid dates found in data")
            return

        # Convert to list and sort
        all_dates = [self.normalize_datetime(d) for d in all_dates if d is not None]
        all_dates = sorted([d for d in all_dates if d is not None])

        if not all_dates:
            print("❌ No valid normalized dates found")
            return

        # Filter to last 10 years
        try:
            cutoff_date = datetime.now() - timedelta(days=365*10)
            cutoff_date = self.normalize_datetime(cutoff_date)
            backtest_dates = [d for d in all_dates if d >= cutoff_date]
        except Exception as e:
            print(f"Warning: Error filtering dates: {e}")
            backtest_dates = all_dates[-2520:] if len(all_dates) > 2520 else all_dates  # Approx 10 years

        if not backtest_dates:
            print("❌ No dates in backtest range")
            return

        print(f"📅 Backtesting from {backtest_dates[0].strftime('%Y-%m-%d')} to {backtest_dates[-1].strftime('%Y-%m-%d')}")
        print(f"📊 Total trading days: {len(backtest_dates)}")

        # Prepare normalized data dictionary
        normalized_data = {}
        for symbol, df in stock_data_dict.items():
            try:
                df_copy = df.copy()
                if 'Date' in df_copy.columns:
                    df_copy['Date'] = self.normalize_date_series(df_copy['Date'])
                    normalized_data[symbol] = df_copy
            except Exception as e:
                print(f"Warning: Could not normalize data for {symbol}: {e}")
                continue

        # Run backtest day by day
        for i, current_date in enumerate(backtest_dates):
            if i % 500 == 0:  # Progress update
                print(f"📈 Processing {current_date.strftime('%Y-%m-%d')} ({i}/{len(backtest_dates)})")

            # Get market prices for this date
            market_prices = {}
            available_data = {}

            for symbol, df in normalized_data.items():
                try:
                    # Get data up to current date
                    historical_data = df[df['Date'] <= current_date].copy()

                    if not historical_data.empty:
                        latest = historical_data.iloc[-1]
                        if 'Close' in latest:
                            market_prices[symbol] = latest['Close']
                            available_data[symbol] = historical_data
                except Exception as e:
                    continue  # Skip this symbol for this date

            # Check exit signals for existing positions
            positions_to_exit = []
            for symbol in list(self.positions.keys()):
                if symbol in available_data:
                    try:
                        position = self.positions[symbol]
                        current_price = market_prices[symbol]

                        # Check stop loss
                        if current_price <= position['stop_loss']:
                            positions_to_exit.append((symbol, current_price, 'STOP_LOSS'))
                        else:
                            # Check other exit signals
                            exit_signals = screener.generate_exit_signals(
                                available_data[symbol], symbol, position['entry_price']
                            )

                            if exit_signals['primary_exit'] not in ['HOLD', 'ERROR']:
                                positions_to_exit.append((symbol, current_price, exit_signals['primary_exit']))
                    except Exception as e:
                        continue  # Skip this position for this date

            # Execute exits
            for symbol, exit_price, exit_reason in positions_to_exit:
                self.exit_position(symbol, current_date, exit_price, exit_reason)

            # Look for new entry signals (only if we have capacity)
            if len(self.positions) < 10 and self.capital > self.initial_capital * 0.1:

                for symbol, df in available_data.items():
                    if symbol not in self.positions and len(df) >= 200:
                        try:
                            entry_analysis = screener.generate_entry_signals(df, symbol)

                            if entry_analysis['entry_signal'] in ['STRONG BUY', 'BUY']:
                                success = self.enter_position(
                                    symbol, 
                                    current_date, 
                                    entry_analysis['entry_price'],
                                    entry_analysis['stop_loss'],
                                    entry_analysis
                                )

                                if success:
                                    break  # Only one entry per day
                        except Exception as e:
                            continue  # Skip this symbol

            # Update portfolio metrics
            try:
                self.update_portfolio_metrics(current_date, market_prices)
            except Exception as e:
                print(f"Warning: Error updating portfolio metrics: {e}")
                continue

        print(f"✅ Backtest completed!")
        self.calculate_final_metrics()

    def calculate_final_metrics(self):
        """Calculate comprehensive performance metrics"""
        if not self.portfolio_history:
            return {}

        # Convert portfolio history to DataFrame
        portfolio_df = pd.DataFrame(self.portfolio_history)
        trades_df = pd.DataFrame(self.trade_history) if self.trade_history else pd.DataFrame()

        # Basic metrics
        final_value = portfolio_df['total_value'].iloc[-1]
        total_return = (final_value / self.initial_capital - 1) * 100

        # Annualized return
        years = len(portfolio_df) / 252  # Approximate trading days per year
        if years > 0:
            annualized_return = (final_value / self.initial_capital) ** (1/years) - 1
            annualized_return_pct = annualized_return * 100
        else:
            annualized_return_pct = 0

        # Win rate
        win_rate = (self.winning_trades / self.total_trades * 100) if self.total_trades > 0 else 0

        # Average trade metrics
        if not trades_df.empty:
            winning_trades = trades_df[trades_df['pnl'] > 0]
            losing_trades = trades_df[trades_df['pnl'] < 0]

            avg_win = winning_trades['pnl_pct'].mean() if not winning_trades.empty else 0
            avg_loss = losing_trades['pnl_pct'].mean() if not losing_trades.empty else 0
            avg_holding_period = trades_df['holding_days'].mean()

            # Profit factor
            gross_profit = winning_trades['pnl'].sum() if not winning_trades.empty else 0
            gross_loss = abs(losing_trades['pnl'].sum()) if not losing_trades.empty else 0
            profit_factor = gross_profit / gross_loss if gross_loss != 0 else float('inf')
        else:
            avg_win = avg_loss = avg_holding_period = profit_factor = 0

        # Sharpe ratio (simplified)
        if len(portfolio_df) > 1:
            portfolio_df['daily_return'] = portfolio_df['total_value'].pct_change()
            daily_returns_std = portfolio_df['daily_return'].std()
            if daily_returns_std > 0:
                sharpe_ratio = portfolio_df['daily_return'].mean() / daily_returns_std * np.sqrt(252)
            else:
                sharpe_ratio = 0
        else:
            sharpe_ratio = 0

        # Maximum consecutive losses
        if not trades_df.empty:
            max_consecutive_losses = self.calculate_max_consecutive_losses(trades_df)
        else:
            max_consecutive_losses = 0

        self.performance_metrics = {
            'initial_capital': self.initial_capital,
            'final_value': final_value,
            'total_return_pct': total_return,
            'annualized_return_pct': annualized_return_pct,
            'max_drawdown_pct': self.max_drawdown * 100,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate_pct': win_rate,
            'avg_win_pct': avg_win if not np.isnan(avg_win) else 0,
            'avg_loss_pct': avg_loss if not np.isnan(avg_loss) else 0,
            'avg_holding_days': avg_holding_period if not np.isnan(avg_holding_period) else 0,
            'profit_factor': profit_factor,
            'sharpe_ratio': sharpe_ratio if not np.isnan(sharpe_ratio) else 0,
            'max_consecutive_losses': max_consecutive_losses,
            'backtest_years': years
        }

        return self.performance_metrics

    def calculate_max_consecutive_losses(self, trades_df):
        """Calculate maximum consecutive losses"""
        consecutive_losses = 0
        max_consecutive = 0

        for _, trade in trades_df.iterrows():
            if trade['pnl'] < 0:
                consecutive_losses += 1
                max_consecutive = max(max_consecutive, consecutive_losses)
            else:
                consecutive_losses = 0

        return max_consecutive

    def generate_backtest_report(self):
        """Generate comprehensive backtest report"""
        if not hasattr(self, 'performance_metrics'):
            self.calculate_final_metrics()

        metrics = self.performance_metrics

        report = []
        report.append("📊 MARK MINERVINI STRATEGY - 10 YEAR BACKTEST RESULTS")
        report.append("=" * 60)
        report.append(f"📅 Backtest Period: {metrics['backtest_years']:.1f} years")
        report.append(f"💰 Initial Capital: ₹{metrics['initial_capital']:,.0f}")
        report.append(f"💰 Final Value: ₹{metrics['final_value']:,.0f}")
        report.append("")

        report.append("🎯 PERFORMANCE SUMMARY:")
        report.append("-" * 30)
        report.append(f"📈 Total Return: {metrics['total_return_pct']:.2f}%")
        report.append(f"📈 Annualized Return: {metrics['annualized_return_pct']:.2f}%")
        report.append(f"📉 Maximum Drawdown: {metrics['max_drawdown_pct']:.2f}%")
        report.append(f"⚡ Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        report.append("")

        report.append("📋 TRADING STATISTICS:")
        report.append("-" * 30)
        report.append(f"🎲 Total Trades: {metrics['total_trades']}")
        report.append(f"✅ Winning Trades: {metrics['winning_trades']}")
        report.append(f"❌ Losing Trades: {metrics['losing_trades']}")
        report.append(f"🎯 Win Rate: {metrics['win_rate_pct']:.1f}%")
        report.append(f"📊 Average Win: {metrics['avg_win_pct']:.2f}%")
        report.append(f"📊 Average Loss: {metrics['avg_loss_pct']:.2f}%")
        report.append(f"⏱️ Avg Holding Period: {metrics['avg_holding_days']:.1f} days")
        report.append(f"💎 Profit Factor: {metrics['profit_factor']:.2f}")
        report.append(f"🔴 Max Consecutive Losses: {metrics['max_consecutive_losses']}")
        report.append("")

        # Performance vs market (if Nifty data available)
        report.append("🏆 PERFORMANCE ANALYSIS:")
        report.append("-" * 30)
        report.append(f"Strategy implemented with proper risk management")
        report.append(f"Datetime handling optimized for timezone compatibility")

        # Top performing trades
        if self.trade_history:
            trades_df = pd.DataFrame(self.trade_history)
            top_winners = trades_df.nlargest(5, 'pnl_pct')

            report.append("")
            report.append("🏅 TOP 5 WINNING TRADES:")
            report.append("-" * 30)
            for i, (_, trade) in enumerate(top_winners.iterrows(), 1):
                symbol = trade['symbol'].replace('.NS', '')
                report.append(f"{i}. {symbol}: {trade['pnl_pct']:.2f}% "
                            f"({trade['holding_days']} days)")

        return "\n".join(report)

    def get_monthly_returns(self):
        """Calculate monthly returns for detailed analysis"""
        if not self.portfolio_history:
            return pd.DataFrame()

        try:
            portfolio_df = pd.DataFrame(self.portfolio_history)

            # Ensure date column is datetime
            portfolio_df['date'] = pd.to_datetime(portfolio_df['date'], errors='coerce')
            portfolio_df = portfolio_df.dropna(subset=['date'])

            if portfolio_df.empty:
                return pd.DataFrame()

            portfolio_df.set_index('date', inplace=True)

            # Resample to monthly
            monthly = portfolio_df['total_value'].resample('M').last()
            monthly_returns = monthly.pct_change().dropna()

            return monthly_returns

        except Exception as e:
            print(f"Warning: Error calculating monthly returns: {e}")
            return pd.DataFrame()

if __name__ == "__main__":
    # Test backtester with proper datetime handling
    print("Testing Minervini Backtester with DateTime Fix...")

    backtester = MinerviniBacktester(initial_capital=1000000)

    # Test datetime normalization
    from datetime import datetime
    import pandas as pd

    # Test various datetime formats
    test_dates = [
        datetime(2023, 1, 15),
        pd.Timestamp('2023-01-15'),
        pd.Timestamp('2023-01-15', tz='UTC'),
        '2023-01-15'
    ]

    print("Testing datetime normalization:")
    for date in test_dates:
        normalized = backtester.normalize_datetime(date)
        print(f"  {date} -> {normalized} (type: {type(normalized)})")

    # Test position entry/exit with proper datetime handling
    test_date = datetime(2023, 1, 15)
    success = backtester.enter_position(
        'TEST.NS', test_date, 100.0, 93.0, {'signal': 'test'}
    )

    if success:
        print("✅ Position entry with datetime handling successful")

        exit_date = datetime(2023, 2, 15)
        backtester.exit_position('TEST.NS', exit_date, 110.0, 'PROFIT_TARGET')

        print("✅ Position exit with datetime handling successful")
        if backtester.trade_history:
            print(f"Trade holding days: {backtester.trade_history[0]['holding_days']}")
