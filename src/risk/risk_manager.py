"""
Risk Management Module
Implements position sizing, stop losses, and portfolio limits
"""

import os
import yaml
from typing import Dict, Optional, List
from datetime import datetime


class RiskManager:
    """Manage trading risk and position sizing"""
    
    def __init__(self, config_path: str = 'config/settings.yaml'):
        """Initialize risk manager with configuration"""
        
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        self.risk_config = config['risk']
        
        # Risk parameters
        self.max_position_size = self.risk_config['max_position_size']
        self.max_daily_loss = self.risk_config['max_daily_loss']
        self.stop_loss_pct = self.risk_config['stop_loss_pct']
        self.max_positions = self.risk_config['max_positions']
        self.min_volume = self.risk_config.get('min_volume', 1000000)
        
        # Tracking
        self.daily_pnl = 0.0
        self.starting_portfolio_value = 0.0
        self.trades_today = []
        
        print("[OK] Risk manager initialized")
        print(f"  Max position size: {self.max_position_size*100:.1f}%")
        print(f"  Max daily loss: {self.max_daily_loss*100:.1f}%")
        print(f"  Stop loss: {self.stop_loss_pct*100:.1f}%")
        print(f"  Max positions: {self.max_positions}")
    
    def set_starting_portfolio_value(self, value: float):
        """Set the starting portfolio value for the day"""
        self.starting_portfolio_value = value
        print(f"[OK] Starting portfolio value: ${value:,.2f}")
    
    def calculate_position_size(
        self,
        symbol: str,
        current_price: float,
        portfolio_value: float,
        current_positions: int = 0
    ) -> Dict:
        """
        Calculate safe position size for a new trade
        
        Args:
            symbol: Stock ticker
            current_price: Current price per share
            portfolio_value: Total portfolio value
            current_positions: Number of open positions
        
        Returns:
            Dictionary with position sizing details
        """
        result = {
            'symbol': symbol,
            'approved': False,
            'shares': 0,
            'cost': 0,
            'reason': ''
        }
        
        # Check if we've hit max positions
        if current_positions >= self.max_positions:
            result['reason'] = f"Max positions reached ({self.max_positions})"
            return result
        
        # Check daily loss limit
        if self.starting_portfolio_value > 0:
            daily_loss_pct = self.daily_pnl / self.starting_portfolio_value
            if daily_loss_pct <= -self.max_daily_loss:
                result['reason'] = f"Daily loss limit reached ({daily_loss_pct*100:.2f}%)"
                return result
        
        # Calculate max position value
        max_position_value = portfolio_value * self.max_position_size
        
        # Calculate shares
        shares = int(max_position_value / current_price)
        
        if shares == 0:
            result['reason'] = "Insufficient capital for position"
            return result
        
        cost = shares * current_price
        
        # Final validation
        if cost > portfolio_value:
            result['reason'] = "Position cost exceeds portfolio value"
            return result
        
        result['approved'] = True
        result['shares'] = shares
        result['cost'] = cost
        result['reason'] = 'Position approved'
        
        return result
    
    def calculate_stop_loss(self, entry_price: float, direction: str = 'long') -> float:
        """
        Calculate stop loss price
        
        Args:
            entry_price: Entry price per share
            direction: 'long' or 'short'
        
        Returns:
            Stop loss price
        """
        if direction == 'long':
            return entry_price * (1 - self.stop_loss_pct)
        else:  # short
            return entry_price * (1 + self.stop_loss_pct)
    
    def calculate_take_profit(
        self,
        entry_price: float,
        risk_reward_ratio: float = 2.0,
        direction: str = 'long'
    ) -> float:
        """
        Calculate take profit price based on risk/reward ratio
        
        Args:
            entry_price: Entry price per share
            risk_reward_ratio: Target reward relative to risk
            direction: 'long' or 'short'
        
        Returns:
            Take profit price
        """
        risk_amount = entry_price * self.stop_loss_pct
        reward_amount = risk_amount * risk_reward_ratio
        
        if direction == 'long':
            return entry_price + reward_amount
        else:  # short
            return entry_price - reward_amount
    
    def should_stop_trading(self, current_portfolio_value: float) -> bool:
        """
        Check if we should stop trading due to risk limits
        
        Args:
            current_portfolio_value: Current portfolio value
        
        Returns:
            True if should stop trading
        """
        if self.starting_portfolio_value == 0:
            return False
        
        # Calculate daily P&L
        self.daily_pnl = current_portfolio_value - self.starting_portfolio_value
        daily_loss_pct = self.daily_pnl / self.starting_portfolio_value
        
        # Check if daily loss limit exceeded
        if daily_loss_pct <= -self.max_daily_loss:
            print(f"[ALERT] Daily loss limit reached: {daily_loss_pct*100:.2f}%")
            return True
        
        return False
    
    def record_trade(self, trade: Dict):
        """Record a trade for tracking"""
        trade['timestamp'] = datetime.now().isoformat()
        self.trades_today.append(trade)
    
    def validate_trade(
        self,
        symbol: str,
        shares: int,
        price: float,
        action: str,
        account_info: Dict
    ) -> Dict:
        """
        Validate if a trade meets all risk criteria
        
        Args:
            symbol: Stock ticker
            shares: Number of shares
            price: Price per share
            action: 'buy' or 'sell'
            account_info: Current account information
        
        Returns:
            Dictionary with validation result
        """
        validation = {
            'approved': True,
            'warnings': [],
            'stop_loss': None,
            'take_profit': None
        }
        
        portfolio_value = account_info.get('portfolio_value', 0)
        
        # Check daily loss limit
        if self.should_stop_trading(portfolio_value):
            validation['approved'] = False
            validation['warnings'].append("Daily loss limit reached")
            return validation
        
        # For buy orders
        if action.lower() == 'buy':
            cost = shares * price
            position_size_pct = cost / portfolio_value if portfolio_value > 0 else 0
            
            # Check position size
            if position_size_pct > self.max_position_size:
                validation['warnings'].append(
                    f"Position size ({position_size_pct*100:.1f}%) exceeds limit "
                    f"({self.max_position_size*100:.1f}%)"
                )
                validation['approved'] = False
            
            # Calculate stop loss and take profit
            validation['stop_loss'] = self.calculate_stop_loss(price, 'long')
            validation['take_profit'] = self.calculate_take_profit(price, 2.0, 'long')
        
        return validation
    
    def get_risk_summary(self) -> str:
        """Generate risk summary report"""
        summary = "\n" + "="*60 + "\n"
        summary += "RISK MANAGEMENT SUMMARY\n"
        summary += "="*60 + "\n"
        
        if self.starting_portfolio_value > 0:
            daily_pnl_pct = (self.daily_pnl / self.starting_portfolio_value) * 100
            summary += f"Daily P&L: ${self.daily_pnl:+,.2f} ({daily_pnl_pct:+.2f}%)\n"
            
            remaining_loss_allowed = (self.max_daily_loss * self.starting_portfolio_value) + self.daily_pnl
            summary += f"Remaining loss buffer: ${remaining_loss_allowed:,.2f}\n"
        
        summary += f"\nTrades today: {len(self.trades_today)}\n"
        summary += f"Max positions: {self.max_positions}\n"
        summary += f"Position size limit: {self.max_position_size*100:.1f}%\n"
        summary += f"Stop loss: {self.stop_loss_pct*100:.1f}%\n"
        
        summary += "="*60 + "\n"
        
        return summary


def test_risk_management():
    """Test risk management functionality"""
    print("\n" + "="*60)
    print("TESTING RISK MANAGEMENT")
    print("="*60 + "\n")
    
    # Initialize risk manager
    risk_mgr = RiskManager()
    
    # Set starting portfolio
    portfolio_value = 100000.00
    risk_mgr.set_starting_portfolio_value(portfolio_value)
    
    print("\n[TEST 1: Position Sizing]")
    result = risk_mgr.calculate_position_size(
        symbol='AAPL',
        current_price=255.47,
        portfolio_value=portfolio_value,
        current_positions=0
    )
    print(f"  Symbol: {result['symbol']}")
    print(f"  Approved: {result['approved']}")
    print(f"  Shares: {result['shares']}")
    print(f"  Cost: ${result['cost']:,.2f}")
    print(f"  Reason: {result['reason']}")
    
    print("\n[TEST 2: Stop Loss & Take Profit]")
    entry_price = 255.47
    stop_loss = risk_mgr.calculate_stop_loss(entry_price)
    take_profit = risk_mgr.calculate_take_profit(entry_price, 2.0)
    print(f"  Entry: ${entry_price:.2f}")
    print(f"  Stop Loss: ${stop_loss:.2f} ({-risk_mgr.stop_loss_pct*100:.1f}%)")
    print(f"  Take Profit: ${take_profit:.2f} (+{((take_profit/entry_price)-1)*100:.1f}%)")
    
    print("\n[TEST 3: Trade Validation]")
    account_info = {
        'portfolio_value': portfolio_value,
        'cash': portfolio_value
    }
    
    validation = risk_mgr.validate_trade(
        symbol='AAPL',
        shares=result['shares'],
        price=entry_price,
        action='buy',
        account_info=account_info
    )
    print(f"  Approved: {validation['approved']}")
    print(f"  Warnings: {validation['warnings'] if validation['warnings'] else 'None'}")
    print(f"  Stop Loss: ${validation['stop_loss']:.2f}")
    print(f"  Take Profit: ${validation['take_profit']:.2f}")
    
    print("\n[TEST 4: Risk Summary]")
    print(risk_mgr.get_risk_summary())
    
    print("="*60)
    print("RISK MANAGEMENT TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_risk_management()
