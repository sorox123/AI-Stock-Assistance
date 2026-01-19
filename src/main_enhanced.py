"""
Enhanced Quantitative Stock Trading Bot
Features:
- Universe scanning (all tradable stocks)
- Position-aware signals (only SELL if we own it)
- Automatic trade execution (optional)
"""

import os
import sys
from datetime import datetime
from dotenv import load_dotenv
from typing import List, Dict

# Add current directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__) + '/..'))

from src.strategies.trading_strategy import TradingStrategy
from src.trading.paper_trader import PaperTrader


class EnhancedTradingBot:
    """Enhanced trading bot with universe scanning and auto-trading"""
    
    def __init__(self, auto_trade: bool = False, scan_universe: bool = False, 
                 max_stocks: int = 50):
        """
        Initialize the enhanced trading bot
        
        Args:
            auto_trade: If True, automatically execute trades
            scan_universe: If True, scan all tradable stocks
            max_stocks: Maximum number of stocks to scan
        """
        self.auto_trade = auto_trade
        self.scan_universe = scan_universe
        self.max_stocks = max_stocks
        
        # Initialize strategy and trader
        self.strategy = TradingStrategy()
        self.trader = PaperTrader() if auto_trade else None
        
        # Get current positions
        self.current_positions = self._get_position_symbols()
        
        print(f"[CONFIG] Auto-trade: {auto_trade}")
        print(f"[CONFIG] Scan universe: {scan_universe}")
        print(f"[CONFIG] Max stocks: {max_stocks}")
        print(f"[POSITIONS] Currently holding: {len(self.current_positions)} stocks")
        if self.current_positions:
            print(f"  {', '.join(self.current_positions)}")
        print()
    
    def _get_position_symbols(self) -> List[str]:
        """Get list of symbols we currently own"""
        positions = self.strategy.alpaca.get_positions()
        return [pos['symbol'] for pos in positions]
    
    def _get_watchlist(self) -> List[str]:
        """Get watchlist - either default or full universe"""
        if self.scan_universe:
            print("[UNIVERSE] Fetching all tradable stocks...")
            all_stocks = self.strategy.alpaca.get_tradable_assets(
                min_price=5.0,
                max_price=500.0
            )
            
            # Limit to max_stocks for performance
            if len(all_stocks) > self.max_stocks:
                print(f"[UNIVERSE] Limiting scan to {self.max_stocks} most liquid stocks")
                # TODO: Could sort by volume/market cap here
                watchlist = all_stocks[:self.max_stocks]
            else:
                watchlist = all_stocks
            
            # Always include current positions
            for symbol in self.current_positions:
                if symbol not in watchlist:
                    watchlist.append(symbol)
            
            return watchlist
        else:
            # Default watchlist + any positions we hold
            default = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'NVDA', 'AMZN', 'META', 'AMD']
            watchlist = list(set(default + self.current_positions))
            return watchlist
    
    def _filter_signals(self, results: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Filter signals based on position ownership
        
        Returns:
            Dictionary with 'buy', 'sell', 'hold' lists
        """
        buy_signals = []
        sell_signals = []
        hold_signals = []
        
        for result in results:
            symbol = result['symbol']
            signal = result.get('recommendation', 'HOLD')
            
            # Only show SELL signals for stocks we own
            if signal in ['SELL', 'STRONG_SELL']:
                if symbol in self.current_positions:
                    sell_signals.append(result)
                # Else: Ignore sell signal for stocks we don't own
            
            # Only show HOLD signals for stocks we own
            elif signal == 'HOLD':
                if symbol in self.current_positions:
                    hold_signals.append(result)
                # Else: Ignore hold signal for stocks we don't own
            
            # BUY signals always relevant (if we have capital)
            elif signal in ['BUY', 'STRONG_BUY']:
                buy_signals.append(result)
        
        return {
            'buy': buy_signals,
            'sell': sell_signals,
            'hold': hold_signals
        }
    
    def _execute_trade(self, result: Dict, action: str) -> bool:
        """
        Execute a trade based on analysis result
        
        Args:
            result: Analysis result dictionary
            action: 'BUY' or 'SELL'
            
        Returns:
            True if trade was successful
        """
        if not self.auto_trade or not self.trader:
            return False
        
        symbol = result['symbol']
        price = result['current_price']
        
        try:
            if action == 'BUY':
                # Calculate position size
                shares = self.strategy.get_position_size(symbol, price)
                
                if shares > 0:
                    # Place bracket order with stop loss and take profit
                    order = self.trader.place_bracket_order(
                        symbol=symbol,
                        qty=shares,
                        side='buy'
                    )
                    
                    if order:
                        print(f"[TRADE EXECUTED] BUY {shares} shares of {symbol} @ ${price:.2f}")
                        return True
                    else:
                        print(f"[TRADE FAILED] Could not place BUY order for {symbol}")
                        return False
                else:
                    print(f"[TRADE SKIPPED] Position size too small for {symbol}")
                    return False
            
            elif action == 'SELL':
                # Close entire position
                result = self.trader.close_position(symbol)
                
                if result:
                    print(f"[TRADE EXECUTED] SOLD all {symbol} @ ${price:.2f}")
                    return True
                else:
                    print(f"[TRADE FAILED] Could not close position in {symbol}")
                    return False
        
        except Exception as e:
            print(f"[TRADE ERROR] {symbol}: {e}")
            return False
    
    def run(self):
        """Main execution loop"""
        print("=" * 70)
        print("ENHANCED QUANTITATIVE STOCK TRADING BOT")
        print("=" * 70)
        print(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Mode: {os.getenv('TRADING_MODE', 'paper').upper()}")
        print()
        
        # Get watchlist
        watchlist = self._get_watchlist()
        print(f"[WATCHLIST] Scanning {len(watchlist)} symbols")
        print()
        
        # Scan watchlist
        results = self.strategy.scan_watchlist(watchlist)
        
        # Filter signals by position ownership
        filtered = self._filter_signals(results)
        
        # Display results
        print("\n" + "=" * 70)
        print("POSITION-AWARE RECOMMENDATIONS")
        print("=" * 70)
        
        # BUY signals
        if filtered['buy']:
            print(f"\n[BUY OPPORTUNITIES] {len(filtered['buy'])} signals")
            print("-" * 70)
            for result in sorted(filtered['buy'], 
                               key=lambda x: x['signal_strength'], 
                               reverse=True):
                symbol = result['symbol']
                price = result['current_price']
                strength = result['signal_strength']
                signal = result['recommendation']
                shares = self.strategy.get_position_size(symbol, price)
                cost = shares * price
                
                print(f"\n{symbol}: {signal} (Strength: {strength:.2f})")
                print(f"  Price: ${price:.2f}")
                print(f"  Recommended: {shares} shares (${cost:,.2f})")
                
                reasons = result['signals']['reasons']
                for reason in reasons[:3]:  # Top 3 reasons
                    print(f"  - {reason}")
                
                # Auto-trade if enabled
                if self.auto_trade:
                    self._execute_trade(result, 'BUY')
        else:
            print("\n[BUY OPPORTUNITIES] No buy signals")
        
        # SELL signals
        if filtered['sell']:
            print(f"\n\n[SELL ALERTS] {len(filtered['sell'])} signals (stocks you own)")
            print("-" * 70)
            for result in filtered['sell']:
                symbol = result['symbol']
                price = result['current_price']
                strength = result['signal_strength']
                signal = result['recommendation']
                
                print(f"\n{symbol}: {signal} (Strength: {strength:.2f})")
                print(f"  Current Price: ${price:.2f}")
                
                reasons = result['signals']['reasons']
                for reason in reasons[:3]:
                    print(f"  - {reason}")
                
                # Auto-trade if enabled
                if self.auto_trade:
                    self._execute_trade(result, 'SELL')
        else:
            print("\n\n[SELL ALERTS] No sell signals for your positions")
        
        # HOLD signals
        if filtered['hold']:
            print(f"\n\n[POSITIONS TO HOLD] {len(filtered['hold'])} stocks")
            print("-" * 70)
            for result in filtered['hold']:
                symbol = result['symbol']
                price = result['current_price']
                strength = result['signal_strength']
                print(f"  {symbol}: ${price:.2f} (Strength: {strength:.2f})")
        
        # Summary
        print("\n" + "=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Total scanned: {len(results)}")
        print(f"Buy opportunities: {len(filtered['buy'])}")
        print(f"Sell alerts: {len(filtered['sell'])}")
        print(f"Positions to hold: {len(filtered['hold'])}")
        
        if self.auto_trade:
            print(f"\nAUTO-TRADING: ENABLED")
            print("Trades were automatically executed based on signals above.")
        else:
            print(f"\nAUTO-TRADING: DISABLED")
            print("Review signals above and place trades manually if desired.")
        
        print("\n" + "=" * 70)
        print(f"End Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 70)


def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Parse configuration from environment
    auto_trade = os.getenv('AUTO_TRADE', 'false').lower() == 'true'
    scan_universe = os.getenv('SCAN_UNIVERSE', 'false').lower() == 'true'
    max_stocks = int(os.getenv('MAX_STOCKS_TO_SCAN', '50'))
    
    # Validate required environment variables
    required_vars = ['ALPACA_PAPER_KEY_ID', 'ALPACA_PAPER_SECRET']
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        print("[ERROR] Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        sys.exit(1)
    
    # Safety check for auto-trading
    if auto_trade:
        print("\n" + "!" * 70)
        print("WARNING: AUTO-TRADING IS ENABLED!")
        print("The bot will automatically place trades based on signals.")
        print("!" * 70)
        
        # Require explicit confirmation in .env
        confirm = os.getenv('AUTO_TRADE_CONFIRMED', 'false').lower()
        if confirm != 'true':
            print("\n[ERROR] Auto-trading requires AUTO_TRADE_CONFIRMED=true in .env")
            print("This ensures you understand trades will be placed automatically.")
            sys.exit(1)
    
    # Initialize and run bot
    try:
        bot = EnhancedTradingBot(
            auto_trade=auto_trade,
            scan_universe=scan_universe,
            max_stocks=max_stocks
        )
        bot.run()
    except Exception as e:
        print(f"\n[ERROR] Bot failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
