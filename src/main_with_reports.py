"""
Main Entry Point with Report Generation
Outputs formatted reports to text files
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from src.strategies.trading_strategy import TradingStrategy


def create_formatted_report(results, account_info, start_time, end_time):
    """Create a beautifully formatted text report"""
    
    report_lines = []
    
    # Header
    report_lines.append("=" * 80)
    report_lines.append("QUANTITATIVE STOCK TRADING BOT - DAILY REPORT")
    report_lines.append("=" * 80)
    report_lines.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Analysis Period: {start_time} to {end_time}")
    report_lines.append(f"Trading Mode: {os.getenv('TRADING_MODE', 'paper').upper()}")
    report_lines.append("")
    
    # Account Summary
    report_lines.append("-" * 80)
    report_lines.append("ACCOUNT SUMMARY")
    report_lines.append("-" * 80)
    if account_info:
        report_lines.append(f"Portfolio Value:  ${account_info.get('portfolio_value', 0):,.2f}")
        report_lines.append(f"Cash Available:   ${account_info.get('cash', 0):,.2f}")
        report_lines.append(f"Buying Power:     ${account_info.get('buying_power', 0):,.2f}")
        report_lines.append(f"Account Status:   {account_info.get('status', 'UNKNOWN')}")
    report_lines.append("")
    
    # Categorize signals
    strong_buy = [r for r in results if r.get('recommendation') == 'STRONG_BUY']
    buy = [r for r in results if r.get('recommendation') == 'BUY']
    hold = [r for r in results if r.get('recommendation') == 'HOLD']
    sell = [r for r in results if r.get('recommendation') == 'SELL']
    strong_sell = [r for r in results if r.get('recommendation') == 'STRONG_SELL']
    
    # Summary Statistics
    report_lines.append("-" * 80)
    report_lines.append("MARKET ANALYSIS SUMMARY")
    report_lines.append("-" * 80)
    report_lines.append(f"Total Stocks Analyzed:    {len(results)}")
    report_lines.append(f"Strong Buy Signals:       {len(strong_buy)}")
    report_lines.append(f"Buy Signals:              {len(buy)}")
    report_lines.append(f"Hold Signals:             {len(hold)}")
    report_lines.append(f"Sell Signals:             {len(sell)}")
    report_lines.append(f"Strong Sell Signals:      {len(strong_sell)}")
    report_lines.append("")
    
    # Strong Buy Opportunities
    if strong_buy:
        report_lines.append("=" * 80)
        report_lines.append("STRONG BUY OPPORTUNITIES")
        report_lines.append("=" * 80)
        for i, stock in enumerate(sorted(strong_buy, key=lambda x: x['signal_strength'], reverse=True), 1):
            report_lines.append(f"\n{i}. {stock['symbol']}")
            report_lines.append(f"   Current Price:     ${stock['current_price']:.2f}")
            report_lines.append(f"   Signal Strength:   {stock['signal_strength']:.2f}")
            report_lines.append(f"   Recommendation:    {stock['recommendation']}")
            report_lines.append(f"   Reasons:")
            for reason in stock['signals']['reasons'][:5]:
                report_lines.append(f"      - {reason}")
        report_lines.append("")
    
    # Buy Opportunities
    if buy:
        report_lines.append("=" * 80)
        report_lines.append("BUY OPPORTUNITIES")
        report_lines.append("=" * 80)
        for i, stock in enumerate(sorted(buy, key=lambda x: x['signal_strength'], reverse=True), 1):
            report_lines.append(f"\n{i}. {stock['symbol']}")
            report_lines.append(f"   Current Price:     ${stock['current_price']:.2f}")
            report_lines.append(f"   Signal Strength:   {stock['signal_strength']:.2f}")
            report_lines.append(f"   Reasons:")
            for reason in stock['signals']['reasons'][:3]:
                report_lines.append(f"      - {reason}")
        report_lines.append("")
    
    # Sell Alerts
    if sell or strong_sell:
        report_lines.append("=" * 80)
        report_lines.append("SELL ALERTS")
        report_lines.append("=" * 80)
        for stock in strong_sell + sell:
            report_lines.append(f"\n{stock['symbol']}")
            report_lines.append(f"   Current Price:     ${stock['current_price']:.2f}")
            report_lines.append(f"   Signal Strength:   {stock['signal_strength']:.2f}")
            report_lines.append(f"   Recommendation:    {stock['recommendation']}")
            report_lines.append(f"   Reasons:")
            for reason in stock['signals']['reasons'][:3]:
                report_lines.append(f"      - {reason}")
        report_lines.append("")
    
    # Hold Positions
    if hold:
        report_lines.append("=" * 80)
        report_lines.append("HOLD POSITIONS")
        report_lines.append("=" * 80)
        report_lines.append(f"{'Symbol':<10} {'Price':<12} {'Strength':<12} {'Status'}")
        report_lines.append("-" * 80)
        for stock in sorted(hold, key=lambda x: x['signal_strength'], reverse=True):
            report_lines.append(
                f"{stock['symbol']:<10} "
                f"${stock['current_price']:<11.2f} "
                f"{stock['signal_strength']:<12.2f} "
                f"{stock['recommendation']}"
            )
        report_lines.append("")
    
    # Complete Stock List
    report_lines.append("=" * 80)
    report_lines.append("COMPLETE ANALYSIS - ALL STOCKS")
    report_lines.append("=" * 80)
    report_lines.append(f"{'Symbol':<10} {'Price':<12} {'Signal':<15} {'Strength':<10} {'Recommendation'}")
    report_lines.append("-" * 80)
    
    for stock in sorted(results, key=lambda x: x['signal_strength'], reverse=True):
        report_lines.append(
            f"{stock['symbol']:<10} "
            f"${stock['current_price']:<11.2f} "
            f"{stock['signals']['signal']:<15} "
            f"{stock['signal_strength']:<10.2f} "
            f"{stock['recommendation']}"
        )
    
    report_lines.append("")
    report_lines.append("=" * 80)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 80)
    
    return "\n".join(report_lines)


def save_report(report_text, filename=None):
    """Save report to file"""
    
    # Create logs directory if it doesn't exist
    os.makedirs('logs', exist_ok=True)
    
    # Generate filename with timestamp
    if filename is None:
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
        filename = f'logs/trading-report_{timestamp}.txt'
    
    # Write report
    with open(filename, 'w') as f:
        f.write(report_text)
    
    print(f"\n[REPORT SAVED] {filename}")
    return filename


def main():
    """Main entry point for the trading bot"""
    
    # Load environment variables
    load_dotenv()
    
    start_time = datetime.now()
    
    print("=" * 80)
    print("QUANTITATIVE STOCK TRADING BOT")
    print("=" * 80)
    print(f"Start Time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Mode: {os.getenv('TRADING_MODE', 'paper').upper()}")
    print()
    
    # Validate required environment variables
    required_vars = ['ALPACA_PAPER_KEY_ID', 'ALPACA_PAPER_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("[ERROR] Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        sys.exit(1)
    
    print("[OK] Environment validated successfully!")
    print()
    
    # Initialize trading strategy
    try:
        strategy = TradingStrategy()
        
        # Get account info
        account_info = strategy.alpaca.get_account_info()
        
        # Determine watchlist
        scan_universe = os.getenv('SCAN_UNIVERSE', 'false').lower() == 'true'
        max_stocks = int(os.getenv('MAX_STOCKS_TO_SCAN', '50'))
        
        if scan_universe:
            print(f"[UNIVERSE SCAN] Fetching tradable stocks...")
            watchlist = strategy.alpaca.get_tradable_assets()
            if len(watchlist) > max_stocks:
                print(f"[UNIVERSE SCAN] Limiting to {max_stocks} stocks")
                watchlist = watchlist[:max_stocks]
        else:
            # Default watchlist
            watchlist = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'AMD']
        
        print(f"[WATCHLIST] Scanning {len(watchlist)} symbols")
        print()
        
        # Scan watchlist
        results = strategy.scan_watchlist(watchlist)
        
        # Generate console report
        console_report = strategy.generate_trade_report(results)
        print(console_report)
        
        # End time
        end_time = datetime.now()
        
        # Generate formatted file report
        file_report = create_formatted_report(
            results, 
            account_info,
            start_time.strftime('%Y-%m-%d %H:%M:%S'),
            end_time.strftime('%Y-%m-%d %H:%M:%S')
        )
        
        # Save report
        report_file = save_report(file_report)
        
        print()
        print("=" * 80)
        print(f"End Time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration: {(end_time - start_time).total_seconds():.1f} seconds")
        print("=" * 80)
        
    except Exception as e:
        print(f"[ERROR] Trading strategy failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
