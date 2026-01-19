"""
Quantitative Stock Trading Bot - Main Entry Point
Paper trading implementation with cloud deployment support
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from src.strategies.trading_strategy import TradingStrategy


def main():
    """Main entry point for the trading bot"""
    
    # Load environment variables
    load_dotenv()
    
    print("=" * 60)
    print("QUANTITATIVE STOCK TRADING BOT")
    print("=" * 60)
    print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {os.getenv('TRADING_MODE', 'paper').upper()}")
    print()
    
    # Validate required environment variables
    required_vars = [
        'ALPACA_PAPER_KEY_ID',
        'ALPACA_PAPER_SECRET',
    ]
    
    missing_vars = []
    for var in required_vars:
        value = os.getenv(var)
        if not value or value.startswith('your_'):
            missing_vars.append(var)
        else:
            # Show first 4 chars of keys for verification
            print(f"[OK] {var}: {value[:4]}...{value[-4:]}")
    
    if missing_vars:
        print()
        print("[ERROR] Missing or unconfigured environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print()
        print("Please configure these in your .env file")
        print("See .env.example for template")
        sys.exit(1)
    
    print()
    print("[OK] Environment validated successfully!")
    print()
    
    # Initialize trading strategy
    try:
        strategy = TradingStrategy()
        
        # Define watchlist
        watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'AMD']
        
        print(f"[WATCHLIST] Scanning {len(watchlist)} symbols")
        print()
        
        # Scan watchlist
        results = strategy.scan_watchlist(watchlist)
        
        # Generate and display report
        report = strategy.generate_trade_report(results)
        print(report)
        
        # Check for buy opportunities
        buy_opportunities = [r for r in results if strategy.should_buy(r)]
        if buy_opportunities:
            print("[ACTION ITEMS]")
            for opp in buy_opportunities:
                shares = strategy.get_position_size(opp['symbol'], opp['current_price'])
                if shares > 0:
                    cost = shares * opp['current_price']
                    print(f"  Consider buying {shares} shares of {opp['symbol']} @ ${opp['current_price']:.2f} (${cost:,.2f})")
        
    except Exception as e:
        print(f"[ERROR] Trading strategy failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print()
    print("=" * 60)
    print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)


if __name__ == "__main__":
    main()
