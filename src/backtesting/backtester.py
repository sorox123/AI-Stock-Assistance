"""
Backtesting Module
Test trading strategy on historical data
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.analysis.technical_indicators import TechnicalAnalyzer


class Backtester:
    """Backtest trading strategies on historical data"""
    
    def __init__(self, initial_capital: float = 100000.0):
        """
        Initialize backtester
        
        Args:
            initial_capital: Starting capital for backtest
        """
        self.initial_capital = initial_capital
        self.analyzer = TechnicalAnalyzer()
        
        print(f"[OK] Backtester initialized with ${initial_capital:,.2f}")
    
    def run_backtest(
        self,
        symbol: str,
        data: pd.DataFrame,
        position_size_pct: float = 0.10
    ) -> Dict:
        """
        Run backtest on historical data
        
        Args:
            symbol: Stock ticker
            data: DataFrame with OHLCV data
            position_size_pct: Position size as percentage of capital
        
        Returns:
            Dictionary with backtest results
        """
        print(f"\n[BACKTESTING] {symbol}")
        print(f"  Period: {data.index[0]} to {data.index[-1]}")
        print(f"  Data points: {len(data)}")
        
        # Initialize tracking
        capital = self.initial_capital
        position = 0  # Number of shares held
        entry_price = 0
        trades = []
        equity_curve = [capital]
        
        # Analyze each data point
        for i in range(len(data)):
            if i < 50:  # Skip first 50 bars for indicator warmup
                equity_curve.append(capital + (position * data['close'].iloc[i] if position > 0 else 0))
                continue
            
            # Get data up to this point
            historical_data = data.iloc[:i+1]
            
            # Analyze
            analysis = self.analyzer.analyze_stock(historical_data)
            
            if 'error' in analysis:
                continue
            
            current_price = data['close'].iloc[i]
            signal = analysis['signals']['overall_signal']
            strength = analysis['signals']['strength']
            
            # Trading logic
            if position == 0 and signal in ['buy', 'strong_buy'] and strength >= 0.3:
                # Enter long position
                position_value = capital * position_size_pct
                shares = int(position_value / current_price)
                
                if shares > 0:
                    position = shares
                    entry_price = current_price
                    cost = shares * current_price
                    capital -= cost
                    
                    trades.append({
                        'date': data.index[i],
                        'type': 'BUY',
                        'price': current_price,
                        'shares': shares,
                        'signal': signal,
                        'strength': strength
                    })
            
            elif position > 0:
                # Check exit conditions
                current_value = position * current_price
                pnl_pct = (current_price - entry_price) / entry_price
                
                # Exit if: strong sell signal OR stop loss (-5%) OR take profit (+10%)
                should_exit = False
                exit_reason = ''
                
                if signal in ['sell', 'strong_sell'] and strength <= -0.3:
                    should_exit = True
                    exit_reason = f'Sell signal ({signal})'
                elif pnl_pct <= -0.05:
                    should_exit = True
                    exit_reason = 'Stop loss (-5%)'
                elif pnl_pct >= 0.10:
                    should_exit = True
                    exit_reason = 'Take profit (+10%)'
                
                if should_exit:
                    # Exit position
                    capital += position * current_price
                    
                    trades.append({
                        'date': data.index[i],
                        'type': 'SELL',
                        'price': current_price,
                        'shares': position,
                        'signal': signal,
                        'strength': strength,
                        'pnl_pct': pnl_pct * 100,
                        'reason': exit_reason
                    })
                    
                    position = 0
                    entry_price = 0
            
            # Track equity
            portfolio_value = capital + (position * current_price if position > 0 else 0)
            equity_curve.append(portfolio_value)
        
        # Close any open position at end
        if position > 0:
            final_price = data['close'].iloc[-1]
            capital += position * final_price
            pnl_pct = (final_price - entry_price) / entry_price
            
            trades.append({
                'date': data.index[-1],
                'type': 'SELL',
                'price': final_price,
                'shares': position,
                'signal': 'end_of_test',
                'pnl_pct': pnl_pct * 100,
                'reason': 'End of backtest'
            })
        
        # Calculate metrics
        final_capital = capital
        total_return = ((final_capital - self.initial_capital) / self.initial_capital) * 100
        
        # Calculate buy & hold return for comparison
        buy_hold_return = ((data['close'].iloc[-1] - data['close'].iloc[0]) / data['close'].iloc[0]) * 100
        
        # Calculate winning percentage
        winning_trades = [t for t in trades if t.get('pnl_pct', 0) > 0]
        losing_trades = [t for t in trades if t.get('pnl_pct', 0) < 0]
        
        win_rate = len(winning_trades) / (len(winning_trades) + len(losing_trades)) * 100 if (len(winning_trades) + len(losing_trades)) > 0 else 0
        
        # Calculate max drawdown
        equity_series = pd.Series(equity_curve)
        cummax = equity_series.cummax()
        drawdown = (equity_series - cummax) / cummax * 100
        max_drawdown = drawdown.min()
        
        results = {
            'symbol': symbol,
            'initial_capital': self.initial_capital,
            'final_capital': final_capital,
            'total_return_pct': total_return,
            'buy_hold_return_pct': buy_hold_return,
            'outperformance': total_return - buy_hold_return,
            'total_trades': len(trades),
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate_pct': win_rate,
            'max_drawdown_pct': max_drawdown,
            'trades': trades,
            'equity_curve': equity_curve
        }
        
        return results
    
    def print_results(self, results: Dict):
        """Print backtest results in formatted way"""
        print("\n" + "="*60)
        print(f"BACKTEST RESULTS: {results['symbol']}")
        print("="*60)
        
        print(f"\nCapital:")
        print(f"  Initial: ${results['initial_capital']:,.2f}")
        print(f"  Final: ${results['final_capital']:,.2f}")
        print(f"  Profit/Loss: ${results['final_capital'] - results['initial_capital']:+,.2f}")
        
        print(f"\nReturns:")
        print(f"  Strategy Return: {results['total_return_pct']:+.2f}%")
        print(f"  Buy & Hold Return: {results['buy_hold_return_pct']:+.2f}%")
        print(f"  Outperformance: {results['outperformance']:+.2f}%")
        
        print(f"\nTrade Statistics:")
        print(f"  Total Trades: {results['total_trades']}")
        print(f"  Winning Trades: {results['winning_trades']}")
        print(f"  Losing Trades: {results['losing_trades']}")
        print(f"  Win Rate: {results['win_rate_pct']:.1f}%")
        print(f"  Max Drawdown: {results['max_drawdown_pct']:.2f}%")
        
        print(f"\nTrade History:")
        for i, trade in enumerate(results['trades'][:10], 1):  # Show first 10
            if trade['type'] == 'BUY':
                print(f"  {i}. BUY {trade['shares']} @ ${trade['price']:.2f} on {trade['date']} "
                      f"(Signal: {trade.get('signal', 'N/A')})")
            else:
                pnl = trade.get('pnl_pct', 0)
                print(f"  {i}. SELL {trade['shares']} @ ${trade['price']:.2f} on {trade['date']} "
                      f"(P/L: {pnl:+.2f}%, {trade.get('reason', 'N/A')})")
        
        if len(results['trades']) > 10:
            print(f"  ... and {len(results['trades']) - 10} more trades")
        
        print("\n" + "="*60 + "\n")


def test_backtesting():
    """Test backtesting functionality with sample data"""
    print("\n" + "="*60)
    print("TESTING BACKTESTING MODULE")
    print("="*60)
    
    # Create realistic sample data (1 year of daily data)
    dates = pd.date_range(start='2025-01-01', periods=252, freq='D')
    np.random.seed(42)
    
    # Generate price movement with trend and volatility
    prices = [100]
    for _ in range(251):
        change = np.random.randn() * 1.5 + 0.05  # Slight upward bias
        price = max(prices[-1] + change, 50)
        prices.append(price)
    
    # Create OHLCV dataframe
    df = pd.DataFrame({
        'close': prices,
        'open': [p * np.random.uniform(0.98, 1.02) for p in prices],
        'high': [p * np.random.uniform(1.0, 1.05) for p in prices],
        'low': [p * np.random.uniform(0.95, 1.0) for p in prices],
        'volume': np.random.randint(1000000, 5000000, 252)
    }, index=dates)
    
    # Run backtest
    backtester = Backtester(initial_capital=100000.0)
    results = backtester.run_backtest('TEST', df, position_size_pct=0.10)
    
    # Print results
    backtester.print_results(results)
    
    print("="*60)
    print("BACKTESTING TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_backtesting()
