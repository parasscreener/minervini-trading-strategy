"""
Data Fetcher Module for Mark Minervini Trading Strategy - DATETIME FIXED VERSION
Fetches stock data from NSE for Nifty 750 stocks with proper timezone handling
Author: Trading Strategy System
"""

import pandas as pd
import yfinance as yf
import numpy as np
from datetime import datetime, timedelta
import requests
from io import StringIO
import warnings
warnings.filterwarnings('ignore')

class DataFetcher:
    def __init__(self):
        self.nifty_750_symbols = []
        self.session = requests.Session()
        self.setup_session()

    def setup_session(self):
        """Setup requests session with headers for NSE data"""
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.session.headers.update(headers)

    def normalize_datetime_column(self, df, column_name='Date'):
        """Normalize datetime column to be timezone-naive"""
        try:
            if column_name not in df.columns:
                return df

            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(df[column_name]):
                df[column_name] = pd.to_datetime(df[column_name], errors='coerce')

            # Remove timezone info if present
            if hasattr(df[column_name].dtype, 'tz') and df[column_name].dtype.tz is not None:
                df[column_name] = df[column_name].dt.tz_convert(None)

            # Additional check for individual datetime objects
            if df[column_name].dtype == 'object':
                df[column_name] = df[column_name].apply(
                    lambda x: x.replace(tzinfo=None) if hasattr(x, 'tzinfo') and x.tzinfo else x
                )

            return df

        except Exception as e:
            print(f"Warning: Error normalizing datetime column {column_name}: {e}")
            return df

    def get_nifty_stocks_list(self):
        """
        Get list of Nifty 750 stocks from multiple sources
        Returns list of stock symbols
        """
        try:
            # Try to get Nifty 500 first (closest available to 750)
            url = "https://nsearchives.nseindia.com/content/indices/ind_nifty500list.csv"

            # Warm-up request
            self.session.get("https://www.nseindia.com", timeout=5)
            response = self.session.get(url, timeout=10)

            if response.status_code == 200:
                csv_content = response.content.decode('utf-8')
                df = pd.read_csv(StringIO(csv_content))
                symbols = df['Symbol'].tolist()

                # Add .NS suffix for yfinance
                symbols_with_suffix = [symbol + '.NS' for symbol in symbols]
                self.nifty_750_symbols = symbols_with_suffix[:750]  # Limit to 750

                print(f"✅ Successfully fetched {len(self.nifty_750_symbols)} stock symbols")
                return self.nifty_750_symbols

        except Exception as e:
            print(f"⚠️ Error fetching from NSE, using fallback list: {e}")

        # Fallback hardcoded list of major Nifty stocks
        fallback_symbols = [
            'RELIANCE.NS', 'TCS.NS', 'HDFCBANK.NS', 'INFY.NS', 'HINDUNILVR.NS',
            'ICICIBANK.NS', 'KOTAKBANK.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'ITC.NS',
            'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS', 'SUNPHARMA.NS',
            'TITAN.NS', 'ULTRACEMCO.NS', 'BAJFINANCE.NS', 'NESTLEIND.NS', 'WIPRO.NS',
            'M&M.NS', 'TATASTEEL.NS', 'NTPC.NS', 'POWERGRID.NS', 'ONGC.NS',
            'JSWSTEEL.NS', 'GRASIM.NS', 'TECHM.NS', 'BAJAJFINSV.NS', 'COALINDIA.NS',
        ]

        # Extend with more stocks to reach closer to 750
        additional_stocks = [
            'ADANIPORTS.NS', 'ADANIENT.NS', 'APOLLOHOSP.NS', 'BAJAJ-AUTO.NS',
            'CIPLA.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'HCLTECH.NS', 'HDFCLIFE.NS',
            'HEROMOTOCO.NS', 'HINDALCO.NS', 'INDUSINDBK.NS', 'IOC.NS', 'JIOFIN.NS',
            'TATACONSUM.NS', 'TATAMOTORS.NS', 'TRENT.NS', 'DIVISLAB.NS', 'BRITANNIA.NS',
            'SHRIRAMFIN.NS', 'GODREJCP.NS', 'PIDILITIND.NS', 'DABUR.NS', 'MARICO.NS'
        ]

        self.nifty_750_symbols = fallback_symbols + additional_stocks
        print(f"✅ Using fallback list with {len(self.nifty_750_symbols)} symbols")
        return self.nifty_750_symbols

    def fetch_stock_data(self, symbol, period="2y"):
        """
        Fetch historical stock data for a single symbol with timezone fix
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)

            if data.empty:
                return None

            # Reset index to get Date as a column
            data.reset_index(inplace=True)

            # Normalize datetime column to remove timezone issues
            data = self.normalize_datetime_column(data, 'Date')

            # Clean data
            data = data.dropna()

            # Add technical indicators
            data = self.add_technical_indicators(data)

            return data

        except Exception as e:
            print(f"❌ Error fetching data for {symbol}: {e}")
            return None

    def add_technical_indicators(self, df):
        """Add technical indicators required for Minervini strategy"""
        try:
            # Ensure we have the required columns
            required_columns = ['Open', 'High', 'Low', 'Close', 'Volume']
            if not all(col in df.columns for col in required_columns):
                print(f"Warning: Missing required columns for technical indicators")
                return df

            # Simple Moving Averages
            df['SMA_50'] = df['Close'].rolling(window=50, min_periods=1).mean()
            df['SMA_150'] = df['Close'].rolling(window=150, min_periods=1).mean()
            df['SMA_200'] = df['Close'].rolling(window=200, min_periods=1).mean()
            df['SMA_10'] = df['Close'].rolling(window=10, min_periods=1).mean()  # For trailing stop

            # Volume indicators
            df['Volume_SMA_50'] = df['Volume'].rolling(window=50, min_periods=1).mean()
            df['Volume_Ratio'] = df['Volume'] / df['Volume_SMA_50']

            # Replace infinite values with NaN, then forward fill
            df['Volume_Ratio'] = df['Volume_Ratio'].replace([np.inf, -np.inf], np.nan)
            df['Volume_Ratio'].fillna(method='ffill', inplace=True)
            df['Volume_Ratio'].fillna(1.0, inplace=True)  # Default to 1.0 if still NaN

            # Price position indicators
            df['52_Week_High'] = df['High'].rolling(window=252, min_periods=1).max()
            df['52_Week_Low'] = df['Low'].rolling(window=252, min_periods=1).min()

            # Distance from 52-week high/low
            df['Pct_From_High'] = ((df['52_Week_High'] - df['Close']) / df['52_Week_High']) * 100
            df['Pct_From_Low'] = ((df['Close'] - df['52_Week_Low']) / df['52_Week_Low']) * 100

            # Replace infinite values
            df['Pct_From_High'] = df['Pct_From_High'].replace([np.inf, -np.inf], 0)
            df['Pct_From_Low'] = df['Pct_From_Low'].replace([np.inf, -np.inf], 0)

            # ATR for volatility
            df['ATR'] = self.calculate_atr(df)

            # Relative Strength (simplified)
            df['RS'] = df['Close'].pct_change(20) * 100  # 20-day return as proxy for RS
            df['RS'].fillna(0, inplace=True)

            # Fill any remaining NaN values
            numeric_columns = df.select_dtypes(include=[np.number]).columns
            df[numeric_columns] = df[numeric_columns].fillna(method='ffill').fillna(method='bfill')

            return df

        except Exception as e:
            print(f"❌ Error adding technical indicators: {e}")
            return df

    def calculate_atr(self, df, period=14):
        """Calculate Average True Range with error handling"""
        try:
            high_low = df['High'] - df['Low']
            high_close_prev = abs(df['High'] - df['Close'].shift(1))
            low_close_prev = abs(df['Low'] - df['Close'].shift(1))

            true_range = pd.concat([high_low, high_close_prev, low_close_prev], axis=1).max(axis=1)
            atr = true_range.rolling(window=period, min_periods=1).mean()

            # Fill NaN values
            atr.fillna(method='ffill', inplace=True)
            atr.fillna(0, inplace=True)

            return atr
        except Exception as e:
            print(f"Warning: Error calculating ATR: {e}")
            return pd.Series([0] * len(df), index=df.index)

    def fetch_multiple_stocks(self, symbols=None, period="2y"):
        """
        Fetch data for multiple stocks with proper error handling
        Returns dictionary with symbol as key and DataFrame as value
        """
        if symbols is None:
            symbols = self.get_nifty_stocks_list()

        stock_data = {}
        failed_symbols = []

        print(f"📊 Starting to fetch data for {len(symbols)} symbols...")

        for i, symbol in enumerate(symbols):
            try:
                data = self.fetch_stock_data(symbol, period)
                if data is not None and len(data) > 200:  # Ensure sufficient data
                    stock_data[symbol] = data
                    if (i + 1) % 10 == 0:  # Progress update every 10 stocks
                        print(f"✅ {i+1}/{len(symbols)}: Processed {len(stock_data)} stocks successfully")
                else:
                    failed_symbols.append(symbol)

            except Exception as e:
                failed_symbols.append(symbol)
                print(f"❌ {i+1}/{len(symbols)}: {symbol} - Error: {e}")

        print(f"\n📈 Successfully fetched: {len(stock_data)} stocks")
        print(f"❌ Failed to fetch: {len(failed_symbols)} stocks")

        if failed_symbols and len(failed_symbols) < 10:
            print(f"Failed symbols: {failed_symbols}")

        return stock_data

    def get_market_data(self):
        """Get overall market data for context with timezone handling"""
        try:
            # Fetch Nifty 50 data
            nifty = yf.Ticker("^NSEI")
            nifty_data = nifty.history(period="2y")

            if not nifty_data.empty:
                # Reset index and normalize datetime
                nifty_data.reset_index(inplace=True)
                nifty_data = self.normalize_datetime_column(nifty_data, 'Date')
                nifty_data = self.add_technical_indicators(nifty_data)
                return nifty_data
            else:
                return None

        except Exception as e:
            print(f"❌ Error fetching market data: {e}")
            return None

if __name__ == "__main__":
    # Test the data fetcher with datetime fixes
    fetcher = DataFetcher()

    # Test single stock
    print("Testing single stock data fetch with datetime fix...")
    reliance_data = fetcher.fetch_stock_data("RELIANCE.NS", "1y")
    if reliance_data is not None:
        print(f"RELIANCE data shape: {reliance_data.shape}")
        print(f"Date column type: {reliance_data['Date'].dtype}")
        print(reliance_data[['Date', 'Close', 'SMA_50', 'SMA_200']].tail())

        # Test datetime comparison
        latest_date = reliance_data['Date'].iloc[-1]
        comparison_date = datetime.now() - timedelta(days=30)

        print(f"\nTesting datetime comparison:")
        print(f"Latest date: {latest_date} (type: {type(latest_date)})")
        print(f"Comparison date: {comparison_date} (type: {type(comparison_date)})")

        # This should work without errors now
        try:
            is_recent = latest_date >= comparison_date
            print(f"✅ Datetime comparison successful: {is_recent}")
        except Exception as e:
            print(f"❌ Datetime comparison failed: {e}")

    # Test multiple stocks (small sample)
    print("\nTesting multiple stocks...")
    test_symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
    test_data = fetcher.fetch_multiple_stocks(test_symbols, "6mo")
    print(f"Successfully fetched data for {len(test_data)} stocks")

    # Test datetime consistency across all stocks
    if test_data:
        print("\nTesting datetime consistency across stocks:")
        for symbol, df in test_data.items():
            if not df.empty:
                latest_date = df['Date'].iloc[-1]
                print(f"{symbol}: {latest_date} (type: {type(latest_date)})")
