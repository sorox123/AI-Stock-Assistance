"""
Trading Strategy - Combines technical analysis with decision logic
"""

import os
import sys
import yaml
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.alpaca_client import AlpacaClient
from src.analysis.technical_indicators import TechnicalAnalyzer


class TradingStrategy:
    """Main trading strategy that combines data and technical analysis"""
    
    def __init__(self, config_path: str = 'config/settings.yaml'):
        """Initialize trading strategy with configuration"""
        
        # Load configuration
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        # Initialize components
        self.alpaca = AlpacaClient()
        self.analyzer = TechnicalAnalyzer(self.config['technical'])
        
        print("[OK] Trading strategy initialized")
    
    def analyze_symbol(self, symbol: str, days_back: int = 60) -> Optional[Dict]:
        """
        Analyze a single stock symbol
        
        Args:
            symbol: Stock ticker (e.g., 'AAPL')
            days_back: Days of historical data to fetch
        
        Returns:
            Dictionary with analysis results and recommendation
        """
        print(f"\n[ANALYZING] {symbol}")
        
        # Get latest price (always works)
        current_price = self.alpaca.get_latest_price(symbol)
        if not current_price:
            print(f"[ERROR] Could not fetch price for {symbol}")
            return None
        
        # Try to get historical data
        df = self.alpaca.get_historical_data(symbol, days_back=days_back)
        
        # If historical data fails, create minimal dataframe with current price
        if df is None or df.empty:
            print(f"[WARN] Using current price only for {symbol}")
            # Create a minimal dataset with just current price
            df = pd.DataFrame({
                'close': [current_price] * 20,  # Repeat current price
                'timestamp': pd.date_range(end=datetime.now(), periods=20, freq='D')
            })
        
        # Perform technical analysis
        analysis = self.analyzer.analyze_stock(df)
        
        if 'error' in analysis:
            print(f"[ERROR] Analysis failed: {analysis['error']}")
            return None
        
        # Add symbol and timestamp
        analysis['symbol'] = symbol
        analysis['timestamp'] = datetime.now().isoformat()
        analysis['current_price'] = current_price
        
        # Print summary
        print(f"  Price: ${current_price:.2f}")
        print(f"  Signal: {analysis['signals']['overall_signal'].upper()}")
        print(f"  Strength: {analysis['signals']['strength']:+.2f}")
        
        return analysis
    
    def scan_watchlist(self, symbols: List[str]) -> List[Dict]:
        """
        Scan multiple symbols and return analysis results
        
        Args:
            symbols: List of stock tickers
        
        Returns:
            List of analysis results sorted by signal strength
        """
        print("\n" + "="*60)
        print(f"SCANNING {len(symbols)} SYMBOLS")
        print("="*60)
        
        results = []
        
        for symbol in symbols:
            analysis = self.analyze_symbol(symbol)
            if analysis:
                results.append(analysis)
        
        # Sort by signal strength (strongest buy signals first)
        results.sort(key=lambda x: x['signals']['strength'], reverse=True)
        
        return results
    
    def should_buy(self, analysis: Dict) -> bool:
        """
        Determine if we should buy based on analysis
        
        Args:
            analysis: Analysis results from analyze_symbol
        
        Returns:
            True if buy conditions are met
        """
        signal = analysis['signals']['overall_signal']
        strength = analysis['signals']['strength']
        
        # Buy conditions
        if signal in ['buy', 'strong_buy'] and strength >= 0.3:
            return True
        
        return False
    
    def should_sell(self, analysis: Dict) -> bool:
        """
        Determine if we should sell based on analysis
        
        Args:
            analysis: Analysis results from analyze_symbol
        
        Returns:
            True if sell conditions are met
        """
        signal = analysis['signals']['overall_signal']
        strength = analysis['signals']['strength']
        
        # Sell conditions
        if signal in ['sell', 'strong_sell'] and strength <= -0.3:
            return True
        
        return False
    
    def get_position_size(self, symbol: str, current_price: float) -> int:
        """
        Calculate position size based on risk management rules
        
        Args:
            symbol: Stock ticker
            current_price: Current price per share
        
        Returns:
            Number of shares to buy (0 if shouldn't buy)
        """
        # Get account info
        account = self.alpaca.get_account_info()
        if not account:
            return 0
        
        # Calculate max position size
        max_position_value = account['portfolio_value'] * self.config['risk']['max_position_size']
        
        # Calculate shares
        shares = int(max_position_value / current_price)
        
        return shares
    
    def generate_trade_report(self, results: List[Dict]) -> str:
        """Generate a formatted report of trading opportunities"""
        
        report = "\n" + "="*60 + "\n"
        report += "TRADING OPPORTUNITIES REPORT\n"
        report += "="*60 + "\n"
        report += f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        report += f"Analyzed: {len(results)} symbols\n\n"
        
        # Buy opportunities
        buy_signals = [r for r in results if self.should_buy(r)]
        if buy_signals:
            report += "[BUY SIGNALS]\n"
            for r in buy_signals:
                report += f"\n  {r['symbol']}: ${r['current_price']:.2f}\n"
                report += f"    Signal: {r['signals']['overall_signal'].upper()}\n"
                report += f"    Strength: {r['signals']['strength']:+.2f}\n"
                if r['signals']['reasons']:
                    report += f"    Reasons: {', '.join(r['signals']['reasons'][:2])}\n"
        else:
            report += "[BUY SIGNALS]\n  None found\n"
        
        # Sell signals
        sell_signals = [r for r in results if self.should_sell(r)]
        if sell_signals:
            report += "\n[SELL SIGNALS]\n"
            for r in sell_signals:
                report += f"\n  {r['symbol']}: ${r['current_price']:.2f}\n"
                report += f"    Signal: {r['signals']['overall_signal'].upper()}\n"
                report += f"    Strength: {r['signals']['strength']:+.2f}\n"
        else:
            report += "\n[SELL SIGNALS]\n  None found\n"
        
        report += "\n" + "="*60 + "\n"
        
        return report


def test_strategy():
    """Test the complete trading strategy"""
    print("\n" + "="*60)
    print("TESTING TRADING STRATEGY")
    print("="*60)
    
    # Initialize strategy
    strategy = TradingStrategy()
    
    # Test with popular stocks
    watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA']
    
    # Scan watchlist
    results = strategy.scan_watchlist(watchlist)
    
    # Generate report
    report = strategy.generate_trade_report(results)
    print(report)
    
    print("STRATEGY TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_strategy()
