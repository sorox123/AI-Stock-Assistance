"""
Automated Portfolio Manager
Intelligently allocates capital to best opportunities based on risk/reward analysis
"""

import os
import sys
from typing import List, Dict, Optional, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.data.alpaca_client import AlpacaClient
from src.risk.risk_manager import RiskManager


class PortfolioManager:
    """
    Automated portfolio allocation system
    Analyzes opportunities and deploys capital intelligently
    """
    
    def __init__(self, config_path: str = 'config/settings.yaml'):
        """Initialize portfolio manager"""
        self.alpaca = AlpacaClient()
        self.risk_mgr = RiskManager(config_path)
        
        # Get account info
        self.account = self.alpaca.get_account_info()
        if self.account:
            self.risk_mgr.set_starting_portfolio_value(self.account['portfolio_value'])
        
        print("[OK] Portfolio manager initialized")
    
    def get_available_capital(self) -> float:
        """
        Calculate available capital for new investments
        
        Returns:
            Available cash considering risk limits
        """
        if not self.account:
            print("[ERROR] Could not fetch account info")
            return 0.0
        
        cash = self.account['cash']
        buying_power = self.account['buying_power']
        
        # Use the lower of cash or buying power (more conservative)
        available = min(cash, buying_power)
        
        # Check if we've hit daily loss limit
        if self.risk_mgr.should_stop_trading(self.account['portfolio_value']):
            print("[WARN] Daily loss limit reached - no new trades allowed")
            return 0.0
        
        # Check current position count
        current_positions = len(self.alpaca.get_positions())
        max_positions = self.risk_mgr.max_positions
        
        if current_positions >= max_positions:
            print(f"[WARN] Max positions ({max_positions}) reached - no new trades")
            return 0.0
        
        print(f"[CAPITAL] Available: ${available:,.2f}")
        print(f"[POSITIONS] Current: {current_positions}/{max_positions}")
        
        return available
    
    def calculate_risk_reward_ratio(self, analysis: Dict) -> Tuple[float, Dict]:
        """
        Calculate risk/reward ratio for an investment opportunity
        
        Args:
            analysis: Stock analysis result
            
        Returns:
            Tuple of (risk_reward_ratio, details_dict)
        """
        symbol = analysis['symbol']
        current_price = analysis['current_price']
        
        # Calculate potential positions size
        position_result = self.risk_mgr.calculate_position_size(
            symbol,
            current_price,
            self.account['portfolio_value']
        )
        
        if not position_result['approved']:
            return 0.0, {'error': position_result['reason']}
        
        position_size_dollars = position_result['cost']
        
        if position_size_dollars == 0:
            return 0.0, {'error': 'Position size too small'}
        
        # Calculate stop loss and take profit
        stop_loss = self.risk_mgr.calculate_stop_loss(current_price)
        take_profit = self.risk_mgr.calculate_take_profit(current_price)
        
        # Calculate risk and reward
        risk_per_share = current_price - stop_loss  # How much we could lose
        reward_per_share = take_profit - current_price  # How much we could gain
        
        if risk_per_share <= 0:
            return 0.0, {'error': 'Invalid risk calculation'}
        
        # Risk/Reward ratio (higher is better)
        risk_reward_ratio = reward_per_share / risk_per_share
        
        # Adjust by signal strength (0.0 to 1.0)
        signal_strength = analysis.get('signal_strength', 0)
        adjusted_ratio = risk_reward_ratio * max(0, signal_strength)
        
        details = {
            'current_price': current_price,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'risk_per_share': risk_per_share,
            'reward_per_share': reward_per_share,
            'risk_reward_ratio': risk_reward_ratio,
            'signal_strength': signal_strength,
            'adjusted_ratio': adjusted_ratio,
            'position_size_dollars': position_size_dollars
        }
        
        return adjusted_ratio, details
    
    def rank_opportunities(self, analyses: List[Dict], min_ratio: float = 1.5) -> List[Dict]:
        """
        Rank investment opportunities by risk/reward ratio
        
        Args:
            analyses: List of stock analysis results
            min_ratio: Minimum risk/reward ratio to consider (default: 1.5:1)
            
        Returns:
            List of opportunities sorted by attractiveness
        """
        opportunities = []
        
        print(f"\n[RANKING] Evaluating {len(analyses)} opportunities...")
        print(f"[FILTER] Minimum risk/reward ratio: {min_ratio}:1")
        print()
        
        for analysis in analyses:
            symbol = analysis['symbol']
            
            # Only consider BUY signals
            recommendation = analysis.get('recommendation', 'HOLD')
            if recommendation not in ['BUY', 'STRONG_BUY']:
                continue
            
            # Calculate risk/reward
            ratio, details = self.calculate_risk_reward_ratio(analysis)
            
            if 'error' in details:
                continue
            
            # Filter by minimum ratio
            if ratio < min_ratio:
                print(f"  {symbol}: R/R {ratio:.2f} - Below minimum threshold")
                continue
            
            # Add to opportunities
            opportunity = {
                'symbol': symbol,
                'analysis': analysis,
                'risk_reward_ratio': ratio,
                'details': details
            }
            opportunities.append(opportunity)
            
            print(f"  {symbol}: R/R {ratio:.2f} - QUALIFIED ✓")
        
        # Sort by risk/reward ratio (highest first)
        opportunities.sort(key=lambda x: x['risk_reward_ratio'], reverse=True)
        
        print(f"\n[RESULT] {len(opportunities)} qualified opportunities")
        return opportunities
    
    def allocate_capital(self, opportunities: List[Dict], 
                        available_capital: float,
                        diversify: bool = True) -> List[Dict]:
        """
        Allocate capital across opportunities
        
        Args:
            opportunities: Ranked list of opportunities
            available_capital: Total capital available
            diversify: If True, spread across multiple stocks
            
        Returns:
            List of allocation decisions
        """
        allocations = []
        remaining_capital = available_capital
        max_positions = self.risk_mgr.max_positions
        current_positions = len(self.alpaca.get_positions())
        available_slots = max_positions - current_positions
        
        print(f"\n[ALLOCATION] Deploying ${available_capital:,.2f}")
        print(f"[SLOTS] {available_slots} position slots available")
        print()
        
        if available_slots <= 0:
            print("[WARN] No position slots available")
            return allocations
        
        if diversify:
            # Spread capital across top opportunities
            positions_to_fill = min(len(opportunities), available_slots)
            
            for i, opp in enumerate(opportunities[:positions_to_fill]):
                symbol = opp['symbol']
                details = opp['details']
                
                # Calculate position size respecting max position %
                position_size = min(
                    details['position_size_dollars'],
                    remaining_capital
                )
                
                if position_size < 100:  # Minimum $100 per position
                    print(f"  {symbol}: Insufficient capital (${position_size:.2f})")
                    continue
                
                current_price = details['current_price']
                shares = int(position_size / current_price)
                
                if shares < 1:
                    continue
                
                actual_cost = shares * current_price
                
                allocation = {
                    'symbol': symbol,
                    'shares': shares,
                    'entry_price': current_price,
                    'cost': actual_cost,
                    'stop_loss': details['stop_loss'],
                    'take_profit': details['take_profit'],
                    'risk_reward_ratio': opp['risk_reward_ratio'],
                    'max_loss': shares * details['risk_per_share'],
                    'max_gain': shares * details['reward_per_share'],
                    'reason': f"Top {i+1} opportunity - R/R {opp['risk_reward_ratio']:.2f}"
                }
                
                allocations.append(allocation)
                remaining_capital -= actual_cost
                
                print(f"  ✓ {symbol}: {shares} shares @ ${current_price:.2f} = ${actual_cost:,.2f}")
                print(f"    Risk/Reward: {opp['risk_reward_ratio']:.2f} | Max Loss: ${allocation['max_loss']:.2f} | Max Gain: ${allocation['max_gain']:.2f}")
        else:
            # Put all capital into best opportunity
            if opportunities:
                best = opportunities[0]
                symbol = best['symbol']
                details = best['details']
                current_price = details['current_price']
                
                # Use all available capital (respecting position size limit)
                position_size = min(
                    details['position_size_dollars'],
                    available_capital
                )
                
                shares = int(position_size / current_price)
                
                if shares >= 1:
                    actual_cost = shares * current_price
                    
                    allocation = {
                        'symbol': symbol,
                        'shares': shares,
                        'entry_price': current_price,
                        'cost': actual_cost,
                        'stop_loss': details['stop_loss'],
                        'take_profit': details['take_profit'],
                        'risk_reward_ratio': best['risk_reward_ratio'],
                        'max_loss': shares * details['risk_per_share'],
                        'max_gain': shares * details['reward_per_share'],
                        'reason': f"Best opportunity - R/R {best['risk_reward_ratio']:.2f}"
                    }
                    
                    allocations.append(allocation)
                    print(f"  ✓ {symbol}: {shares} shares @ ${current_price:.2f} = ${actual_cost:,.2f}")
                    print(f"    Risk/Reward: {best['risk_reward_ratio']:.2f}")
        
        print()
        print(f"[SUMMARY] {len(allocations)} allocations created")
        if allocations:
            total_deployed = sum(a['cost'] for a in allocations)
            total_risk = sum(a['max_loss'] for a in allocations)
            total_potential = sum(a['max_gain'] for a in allocations)
            
            print(f"  Total deployed: ${total_deployed:,.2f}")
            print(f"  Total risk: ${total_risk:,.2f} ({total_risk/self.account['portfolio_value']*100:.2f}%)")
            print(f"  Total potential: ${total_potential:,.2f} ({total_potential/total_deployed*100:.2f}%)")
        
        return allocations
    
    def generate_allocation_report(self, allocations: List[Dict]) -> str:
        """Generate detailed allocation report"""
        if not allocations:
            return "\n[PORTFOLIO] No allocations to execute\n"
        
        report = []
        report.append("\n" + "=" * 70)
        report.append("AUTOMATED PORTFOLIO ALLOCATION")
        report.append("=" * 70)
        
        total_cost = sum(a['cost'] for a in allocations)
        total_risk = sum(a['max_loss'] for a in allocations)
        total_potential = sum(a['max_gain'] for a in allocations)
        
        report.append(f"\nTotal Investment: ${total_cost:,.2f}")
        report.append(f"Maximum Risk: ${total_risk:,.2f} ({total_risk/self.account['portfolio_value']*100:.2f}% of portfolio)")
        report.append(f"Maximum Potential: ${total_potential:,.2f} (+{total_potential/total_cost*100:.2f}%)")
        report.append(f"Overall Risk/Reward: {total_potential/total_risk:.2f}:1")
        
        report.append("\n" + "-" * 70)
        report.append("ALLOCATIONS:")
        report.append("-" * 70)
        
        for i, alloc in enumerate(allocations, 1):
            report.append(f"\n{i}. {alloc['symbol']}")
            report.append(f"   Action: BUY {alloc['shares']} shares @ ${alloc['entry_price']:.2f}")
            report.append(f"   Cost: ${alloc['cost']:,.2f}")
            report.append(f"   Stop Loss: ${alloc['stop_loss']:.2f} (Max Loss: ${alloc['max_loss']:.2f})")
            report.append(f"   Take Profit: ${alloc['take_profit']:.2f} (Max Gain: ${alloc['max_gain']:.2f})")
            report.append(f"   Risk/Reward: {alloc['risk_reward_ratio']:.2f}:1")
            report.append(f"   Reason: {alloc['reason']}")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)


def test_portfolio_manager():
    """Test the portfolio manager"""
    from dotenv import load_dotenv
    load_dotenv()  # Load environment variables
    
    print("=" * 70)
    print("PORTFOLIO MANAGER TEST")
    print("=" * 70)
    
    # Initialize manager
    pm = PortfolioManager()
    
    # Check available capital
    capital = pm.get_available_capital()
    print(f"\nAvailable Capital: ${capital:,.2f}")
    
    # Create mock opportunities
    mock_analyses = [
        {
            'symbol': 'AAPL',
            'current_price': 255.47,
            'recommendation': 'STRONG_BUY',
            'signal_strength': 0.75,
            'signals': {'strength': 0.75}
        },
        {
            'symbol': 'MSFT',
            'current_price': 459.95,
            'recommendation': 'BUY',
            'signal_strength': 0.55,
            'signals': {'strength': 0.55}
        },
        {
            'symbol': 'NVDA',
            'current_price': 150.23,
            'recommendation': 'STRONG_BUY',
            'signal_strength': 0.82,
            'signals': {'strength': 0.82}
        }
    ]
    
    # Rank opportunities
    opportunities = pm.rank_opportunities(mock_analyses, min_ratio=1.5)
    
    # Allocate capital
    if capital > 0 and opportunities:
        allocations = pm.allocate_capital(opportunities, capital, diversify=True)
        
        # Generate report
        report = pm.generate_allocation_report(allocations)
        print(report)
    else:
        print("\n[RESULT] No viable opportunities or capital available")


if __name__ == "__main__":
    test_portfolio_manager()
