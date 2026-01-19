"""
Paper Trading Module
Execute paper trades using Alpaca API
"""

import os
import sys
from typing import Dict, Optional, List
from datetime import datetime
import time

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.alpaca_client import AlpacaClient
from src.risk.risk_manager import RiskManager


class PaperTrader:
    """Execute paper trades with risk management"""
    
    def __init__(self):
        """Initialize paper trader"""
        self.alpaca = AlpacaClient()
        self.risk_mgr = RiskManager()
        
        # Get starting portfolio value
        account = self.alpaca.get_account_info()
        if account:
            self.risk_mgr.set_starting_portfolio_value(account['portfolio_value'])
        
        print("[OK] Paper trader initialized")
    
    def place_market_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        validate_risk: bool = True
    ) -> Optional[Dict]:
        """
        Place a market order
        
        Args:
            symbol: Stock ticker
            qty: Number of shares
            side: 'buy' or 'sell'
            validate_risk: Whether to validate against risk limits
        
        Returns:
            Order details or None if failed
        """
        try:
            # Get current price
            current_price = self.alpaca.get_latest_price(symbol)
            if not current_price:
                print(f"[ERROR] Could not get price for {symbol}")
                return None
            
            # Validate risk if requested
            if validate_risk and side.lower() == 'buy':
                account = self.alpaca.get_account_info()
                validation = self.risk_mgr.validate_trade(
                    symbol=symbol,
                    shares=qty,
                    price=current_price,
                    action='buy',
                    account_info=account
                )
                
                if not validation['approved']:
                    print(f"[REJECTED] Trade validation failed:")
                    for warning in validation['warnings']:
                        print(f"  - {warning}")
                    return None
                
                print(f"[VALIDATED] Stop Loss: ${validation['stop_loss']:.2f}, "
                      f"Take Profit: ${validation['take_profit']:.2f}")
            
            # Place order through Alpaca
            print(f"[PLACING ORDER] {side.upper()} {qty} shares of {symbol} @ market")
            
            order = self.alpaca.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='day'
            )
            
            # Wait a moment for order to process
            time.sleep(1)
            
            # Get order status
            order_status = self.alpaca.api.get_order(order.id)
            
            order_details = {
                'id': order.id,
                'symbol': symbol,
                'qty': int(order.qty),
                'side': order.side,
                'type': order.type,
                'status': order_status.status,
                'filled_qty': int(order_status.filled_qty) if order_status.filled_qty else 0,
                'filled_avg_price': float(order_status.filled_avg_price) if order_status.filled_avg_price else None,
                'submitted_at': order.submitted_at,
                'filled_at': order_status.filled_at
            }
            
            print(f"[ORDER PLACED] ID: {order.id}, Status: {order_status.status}")
            
            # Record trade
            self.risk_mgr.record_trade({
                'symbol': symbol,
                'qty': qty,
                'side': side,
                'price': current_price,
                'order_id': order.id
            })
            
            return order_details
            
        except Exception as e:
            print(f"[ERROR] Failed to place order: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def place_limit_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        limit_price: float
    ) -> Optional[Dict]:
        """
        Place a limit order
        
        Args:
            symbol: Stock ticker
            qty: Number of shares
            side: 'buy' or 'sell'
            limit_price: Limit price per share
        
        Returns:
            Order details or None if failed
        """
        try:
            print(f"[PLACING LIMIT ORDER] {side.upper()} {qty} shares of {symbol} @ ${limit_price:.2f}")
            
            order = self.alpaca.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='limit',
                time_in_force='day',
                limit_price=limit_price
            )
            
            order_details = {
                'id': order.id,
                'symbol': symbol,
                'qty': int(order.qty),
                'side': order.side,
                'type': order.type,
                'limit_price': float(order.limit_price),
                'status': order.status,
                'submitted_at': order.submitted_at
            }
            
            print(f"[LIMIT ORDER PLACED] ID: {order.id}")
            
            return order_details
            
        except Exception as e:
            print(f"[ERROR] Failed to place limit order: {e}")
            return None
    
    def place_bracket_order(
        self,
        symbol: str,
        qty: int,
        side: str,
        take_profit_price: float,
        stop_loss_price: float
    ) -> Optional[Dict]:
        """
        Place a bracket order (entry with stop loss and take profit)
        
        Args:
            symbol: Stock ticker
            qty: Number of shares
            side: 'buy' or 'sell'
            take_profit_price: Take profit limit price
            stop_loss_price: Stop loss price
        
        Returns:
            Order details or None if failed
        """
        try:
            print(f"[PLACING BRACKET ORDER] {side.upper()} {qty} shares of {symbol}")
            print(f"  Stop Loss: ${stop_loss_price:.2f}")
            print(f"  Take Profit: ${take_profit_price:.2f}")
            
            order = self.alpaca.api.submit_order(
                symbol=symbol,
                qty=qty,
                side=side,
                type='market',
                time_in_force='day',
                order_class='bracket',
                take_profit={'limit_price': take_profit_price},
                stop_loss={'stop_price': stop_loss_price}
            )
            
            print(f"[BRACKET ORDER PLACED] ID: {order.id}")
            
            return {
                'id': order.id,
                'symbol': symbol,
                'qty': int(order.qty),
                'side': order.side,
                'status': order.status
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to place bracket order: {e}")
            return None
    
    def cancel_order(self, order_id: str) -> bool:
        """Cancel an open order"""
        try:
            self.alpaca.api.cancel_order(order_id)
            print(f"[ORDER CANCELLED] ID: {order_id}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to cancel order: {e}")
            return False
    
    def get_open_orders(self) -> List[Dict]:
        """Get all open orders"""
        try:
            orders = self.alpaca.api.list_orders(status='open')
            return [{
                'id': order.id,
                'symbol': order.symbol,
                'qty': int(order.qty),
                'side': order.side,
                'type': order.type,
                'status': order.status,
                'submitted_at': order.submitted_at
            } for order in orders]
        except Exception as e:
            print(f"[ERROR] Failed to get open orders: {e}")
            return []
    
    def close_position(self, symbol: str) -> bool:
        """Close an entire position"""
        try:
            print(f"[CLOSING POSITION] {symbol}")
            self.alpaca.api.close_position(symbol)
            print(f"[POSITION CLOSED] {symbol}")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to close position: {e}")
            return False
    
    def close_all_positions(self) -> bool:
        """Close all open positions"""
        try:
            print("[CLOSING ALL POSITIONS]")
            self.alpaca.api.close_all_positions()
            print("[ALL POSITIONS CLOSED]")
            return True
        except Exception as e:
            print(f"[ERROR] Failed to close all positions: {e}")
            return False


def test_paper_trading():
    """Test paper trading functionality"""
    print("\n" + "="*60)
    print("TESTING PAPER TRADING")
    print("="*60 + "\n")
    
    trader = PaperTrader()
    
    # Check account
    print("\n[ACCOUNT STATUS]")
    account = trader.alpaca.get_account_info()
    print(f"  Cash: ${account['cash']:,.2f}")
    print(f"  Portfolio Value: ${account['portfolio_value']:,.2f}")
    print(f"  Buying Power: ${account['buying_power']:,.2f}")
    
    # Check positions
    print("\n[CURRENT POSITIONS]")
    positions = trader.alpaca.get_positions()
    if positions:
        for pos in positions:
            print(f"  {pos['symbol']}: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
            print(f"    Current: ${pos['current_price']:.2f}, P/L: {pos['unrealized_plpc']*100:+.2f}%")
    else:
        print("  No open positions")
    
    # Check open orders
    print("\n[OPEN ORDERS]")
    orders = trader.get_open_orders()
    if orders:
        for order in orders:
            print(f"  {order['symbol']}: {order['side']} {order['qty']} shares")
            print(f"    Type: {order['type']}, Status: {order['status']}")
    else:
        print("  No open orders")
    
    # Test order placement (small position)
    print("\n[TEST ORDER] (This will place a real paper trade!)")
    response = input("  Place a test order for 1 share of AAPL? (yes/no): ").lower()
    
    if response == 'yes':
        order = trader.place_market_order('AAPL', 1, 'buy', validate_risk=True)
        if order:
            print(f"\n  [SUCCESS] Order placed!")
            print(f"  Order ID: {order['id']}")
            print(f"  Status: {order['status']}")
            
            # Wait and check position
            time.sleep(2)
            print("\n  [CHECKING POSITION]")
            positions = trader.alpaca.get_positions()
            aapl_pos = [p for p in positions if p['symbol'] == 'AAPL']
            if aapl_pos:
                pos = aapl_pos[0]
                print(f"  AAPL Position: {pos['qty']} shares @ ${pos['avg_entry_price']:.2f}")
    else:
        print("  Test order skipped")
    
    print("\n" + "="*60)
    print("PAPER TRADING TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    
    test_paper_trading()
