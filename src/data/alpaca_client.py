"""
Alpaca API Client - Data Layer
Handles connection to Alpaca API for market data and trading operations
"""

import os
from datetime import datetime, timedelta
import alpaca_trade_api as tradeapi
from typing import Optional, List, Dict
import pandas as pd


class AlpacaClient:
    """Wrapper for Alpaca API with error handling and data fetching"""
    
    def __init__(self):
        """Initialize Alpaca API client with credentials from environment"""
        self.api_key = os.getenv('ALPACA_PAPER_KEY_ID')
        self.api_secret = os.getenv('ALPACA_PAPER_SECRET')
        self.base_url = os.getenv('ALPACA_BASE_URL', 'https://paper-api.alpaca.markets')
        
        if not all([self.api_key, self.api_secret]):
            raise ValueError("Missing Alpaca API credentials in environment")
        
        self.api = tradeapi.REST(
            key_id=self.api_key,
            secret_key=self.api_secret,
            base_url=self.base_url
        )
        
        print(f"[OK] Connected to Alpaca API ({self.base_url})")
    
    def get_account_info(self) -> Dict:
        """Get account information and status"""
        try:
            account = self.api.get_account()
            return {
                'cash': float(account.cash),
                'portfolio_value': float(account.portfolio_value),
                'buying_power': float(account.buying_power),
                'equity': float(account.equity),
                'status': account.status,
                'trading_blocked': account.trading_blocked,
                'account_blocked': account.account_blocked
            }
        except Exception as e:
            print(f"[ERROR] Error fetching account info: {e}")
            return {}
    
    def get_historical_data(
        self, 
        symbol: str, 
        days_back: int = 30,
        timeframe: str = '1Day'
    ) -> Optional[pd.DataFrame]:
        """
        Fetch historical OHLCV data for a symbol
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            days_back: Number of days of historical data
            timeframe: Timeframe for bars ('1Min', '1Hour', '1Day')
        
        Returns:
            DataFrame with columns: timestamp, open, high, low, close, volume
        """
        try:
            end = datetime.now()
            start = end - timedelta(days=days_back)
            
            # Fetch bars from Alpaca
            bars = self.api.get_bars(
                symbol,
                timeframe,
                start=start.strftime('%Y-%m-%d'),
                end=end.strftime('%Y-%m-%d')
            ).df
            
            if bars.empty:
                print(f"[WARN] No data found for {symbol}")
                return None
            
            # Rename columns to standard format
            bars = bars.rename(columns={
                't': 'timestamp',
                'o': 'open',
                'h': 'high',
                'l': 'low',
                'c': 'close',
                'v': 'volume'
            })
            
            print(f"[OK] Fetched {len(bars)} bars for {symbol}")
            return bars
            
        except Exception as e:
            print(f"[ERROR] Error fetching data for {symbol}: {e}")
            return None
    
    def get_latest_price(self, symbol: str) -> Optional[float]:
        """Get the latest trade price for a symbol"""
        try:
            trade = self.api.get_latest_trade(symbol)
            return float(trade.price)
        except Exception as e:
            print(f"[ERROR] Error fetching latest price for {symbol}: {e}")
            return None
    
    def get_positions(self) -> List[Dict]:
        """Get all current positions"""
        try:
            positions = self.api.list_positions()
            return [{
                'symbol': pos.symbol,
                'qty': float(pos.qty),
                'avg_entry_price': float(pos.avg_entry_price),
                'current_price': float(pos.current_price),
                'market_value': float(pos.market_value),
                'unrealized_pl': float(pos.unrealized_pl),
                'unrealized_plpc': float(pos.unrealized_plpc)
            } for pos in positions]
        except Exception as e:
            print(f"[ERROR] Error fetching positions: {e}")
            return []
    
    def is_market_open(self) -> bool:
        """Check if the market is currently open"""
        try:
            clock = self.api.get_clock()
            return clock.is_open
        except Exception as e:
            print(f"[ERROR] Error checking market status: {e}")
            return False
    
    def get_market_calendar(self, days_ahead: int = 7) -> List[Dict]:
        """Get market calendar for the next N days"""
        try:
            start = datetime.now()
            end = start + timedelta(days=days_ahead)
            
            calendar = self.api.get_calendar(
                start=start.strftime('%Y-%m-%d'),
                end=end.strftime('%Y-%m-%d')
            )
            
            return [{
                'date': str(day.date),
                'open': str(day.open),
                'close': str(day.close)
            } for day in calendar]
            
        except Exception as e:
            print(f"[ERROR] Error fetching market calendar: {e}")
            return []


def test_connection():
    """Test function to verify API connection and data fetching"""
    print("\n" + "="*60)
    print("TESTING ALPACA API CONNECTION")
    print("="*60)
    
    # Initialize client
    client = AlpacaClient()
    
    # Test 1: Account info
    print("\n[ACCOUNT INFO]:")
    account = client.get_account_info()
    if account:
        print(f"   Cash: ${account['cash']:,.2f}")
        print(f"   Portfolio Value: ${account['portfolio_value']:,.2f}")
        print(f"   Buying Power: ${account['buying_power']:,.2f}")
        print(f"   Status: {account['status']}")
    
    # Test 2: Market status
    print("\n[MARKET STATUS]:")
    is_open = client.is_market_open()
    print(f"   Market is {'OPEN' if is_open else 'CLOSED'}")
    
    # Test 3: Fetch sample data
    print("\n[SAMPLE DATA] (AAPL - last 5 days):")
    data = client.get_historical_data('AAPL', days_back=5)
    if data is not None:
        print(data.tail())
    
    # Test 4: Latest price
    print("\n[LATEST PRICES]:")
    for symbol in ['AAPL', 'MSFT', 'GOOGL']:
        price = client.get_latest_price(symbol)
        if price:
            print(f"   {symbol}: ${price:.2f}")
    
    # Test 5: Current positions
    print("\n[CURRENT POSITIONS]:")
    positions = client.get_positions()
    if positions:
        for pos in positions:
            print(f"   {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f} "
                  f"(P/L: {pos['unrealized_plpc']*100:.2f}%)")
    else:
        print("   No open positions")
    
    print("\n" + "="*60)
    print("CONNECTION TEST COMPLETE [SUCCESS]")
    print("="*60 + "\n")


if __name__ == "__main__":
    # Load environment if running directly
    from dotenv import load_dotenv
    load_dotenv()
    
    # Run connection test
    test_connection()
