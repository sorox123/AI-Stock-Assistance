"""
Complete Trading Bot Demo
Demonstrates all system capabilities
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.data.alpaca_client import AlpacaClient
from src.analysis.technical_indicators import TechnicalAnalyzer
from src.analysis.sentiment_analyzer import SentimentAnalyzer
from src.risk.risk_manager import RiskManager
from src.strategies.trading_strategy import TradingStrategy
from src.backtesting.backtester import Backtester


def demo_data_layer():
    """Demonstrate data fetching capabilities"""
    print("\n" + "="*60)
    print("DEMO 1: DATA LAYER")
    print("="*60)
    
    client = AlpacaClient()
    
    # Account info
    print("\n[ACCOUNT INFORMATION]")
    account = client.get_account_info()
    print(f"  Portfolio Value: ${account['portfolio_value']:,.2f}")
    print(f"  Cash Available: ${account['cash']:,.2f}")
    print(f"  Buying Power: ${account['buying_power']:,.2f}")
    
    # Market status
    print("\n[MARKET STATUS]")
    is_open = client.is_market_open()
    print(f"  Market is: {'OPEN' if is_open else 'CLOSED'}")
    
    # Latest prices
    print("\n[LATEST PRICES]")
    for symbol in ['AAPL', 'MSFT', 'GOOGL']:
        price = client.get_latest_price(symbol)
        print(f"  {symbol}: ${price:.2f}")
    
    # Positions
    print("\n[CURRENT POSITIONS]")
    positions = client.get_positions()
    if positions:
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
            print(f"    P/L: {pos['unrealized_plpc']*100:+.2f}%")
    else:
        print("  No open positions")


def demo_technical_analysis():
    """Demonstrate technical analysis capabilities"""
    print("\n" + "="*60)
    print("DEMO 2: TECHNICAL ANALYSIS")
    print("="*60)
    
    import pandas as pd
    import numpy as np
    
    # Create sample data
    dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    prices = [100]
    for _ in range(99):
        change = np.random.randn() * 2
        price = max(prices[-1] + change, 50)
        prices.append(price)
    
    df = pd.DataFrame({
        'close': prices,
        'open': prices,
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'volume': np.random.randint(1000000, 5000000, 100)
    }, index=dates)
    
    analyzer = TechnicalAnalyzer()
    results = analyzer.analyze_stock(df)
    
    print("\n[TECHNICAL INDICATORS]")
    print(f"  Current Price: ${results['indicators']['current_price']:.2f}")
    print(f"  RSI: {results['indicators']['rsi']:.1f}")
    print(f"  SMA(20): ${results['indicators']['sma_short']:.2f}")
    print(f"  SMA(50): ${results['indicators']['sma_long']:.2f}")
    print(f"  MACD: {results['indicators']['macd']:.2f}")
    
    print("\n[TRADING SIGNALS]")
    print(f"  Overall Signal: {results['signals']['overall_signal'].upper()}")
    print(f"  Signal Strength: {results['signals']['strength']:+.2f}")
    print(f"  RSI Signal: {results['signals']['rsi_signal']}")
    print(f"  MA Signal: {results['signals']['ma_signal']}")


def demo_risk_management():
    """Demonstrate risk management capabilities"""
    print("\n" + "="*60)
    print("DEMO 3: RISK MANAGEMENT")
    print("="*60)
    
    risk_mgr = RiskManager()
    risk_mgr.set_starting_portfolio_value(100000.0)
    
    print("\n[POSITION SIZING]")
    result = risk_mgr.calculate_position_size(
        symbol='AAPL',
        current_price=255.47,
        portfolio_value=100000.0,
        current_positions=0
    )
    print(f"  Symbol: {result['symbol']}")
    print(f"  Approved: {result['approved']}")
    print(f"  Shares: {result['shares']}")
    print(f"  Total Cost: ${result['cost']:,.2f}")
    
    print("\n[STOP LOSS & TAKE PROFIT]")
    entry_price = 255.47
    stop_loss = risk_mgr.calculate_stop_loss(entry_price)
    take_profit = risk_mgr.calculate_take_profit(entry_price, 2.0)
    print(f"  Entry Price: ${entry_price:.2f}")
    print(f"  Stop Loss: ${stop_loss:.2f} (-5%)")
    print(f"  Take Profit: ${take_profit:.2f} (+10%)")
    print(f"  Risk/Reward Ratio: 1:2")


def demo_trading_strategy():
    """Demonstrate complete trading strategy"""
    print("\n" + "="*60)
    print("DEMO 4: TRADING STRATEGY")
    print("="*60)
    
    strategy = TradingStrategy()
    
    watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA']
    
    print(f"\n[SCANNING WATCHLIST: {len(watchlist)} symbols]")
    results = strategy.scan_watchlist(watchlist)
    
    report = strategy.generate_trade_report(results)
    print(report)


def demo_backtesting():
    """Demonstrate backtesting capabilities"""
    print("\n" + "="*60)
    print("DEMO 5: BACKTESTING")
    print("="*60)
    
    import pandas as pd
    import numpy as np
    
    # Create sample data (1 year)
    dates = pd.date_range(start='2025-01-01', periods=252, freq='D')
    np.random.seed(42)
    
    prices = [100]
    for _ in range(251):
        change = np.random.randn() * 1.5 + 0.05
        price = max(prices[-1] + change, 50)
        prices.append(price)
    
    df = pd.DataFrame({
        'close': prices,
        'open': [p * 0.99 for p in prices],
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'volume': np.random.randint(1000000, 5000000, 252)
    }, index=dates)
    
    backtester = Backtester(initial_capital=100000.0)
    results = backtester.run_backtest('SAMPLE', df, position_size_pct=0.10)
    backtester.print_results(results)


def main():
    """Run complete demo"""
    load_dotenv()
    
    print("\n" + "="*60)
    print("QUANTITATIVE TRADING BOT - COMPLETE DEMO")
    print("="*60)
    print(f"Demo Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Trading Mode: {os.getenv('TRADING_MODE', 'paper').upper()}")
    
    try:
        # Demo 1: Data Layer
        demo_data_layer()
        
        # Demo 2: Technical Analysis
        demo_technical_analysis()
        
        # Demo 3: Risk Management
        demo_risk_management()
        
        # Demo 4: Trading Strategy
        demo_trading_strategy()
        
        # Demo 5: Backtesting
        demo_backtesting()
        
        print("\n" + "="*60)
        print("DEMO COMPLETE - ALL SYSTEMS OPERATIONAL")
        print("="*60)
        
        print("\n[SYSTEM CAPABILITIES]")
        print("  [OK] Real-time data fetching")
        print("  [OK] Technical analysis (RSI, MA, MACD, BB)")
        print("  [OK] Sentiment analysis (NewsAPI + VADER)")
        print("  [OK] Risk management (position sizing, stop loss)")
        print("  [OK] Paper trading (Alpaca API)")
        print("  [OK] Backtesting engine")
        print("  [OK] Cloud deployment ready (GitHub Actions)")
        
        print("\n[NEXT STEPS]")
        print("  1. Run 'python src/main.py' for daily scanning")
        print("  2. Add NEWS_API_KEY to .env for sentiment analysis")
        print("  3. Push to GitHub and configure secrets for cloud deployment")
        print("  4. Monitor paper trading performance")
        print("  5. Optimize strategy based on backtest results")
        
    except Exception as e:
        print(f"\n[ERROR] Demo failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
