"""
Technical Analysis Module
Implements RSI, Moving Averages, and other technical indicators
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


class TechnicalAnalyzer:
    """Calculate technical indicators and generate trading signals"""
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize technical analyzer with configuration
        
        Args:
            config: Dictionary with indicator parameters
        """
        # Default configuration from settings.yaml
        if config is None:
            self.config = {
                'rsi_period': 14,
                'rsi_oversold': 30,
                'rsi_overbought': 70,
                'sma_short': 20,
                'sma_long': 50,
                'ema_short': 12,
                'ema_long': 26
            }
        else:
            # Extract from nested config if provided
            rsi = config.get('rsi', {})
            ma = config.get('moving_averages', {})
            
            self.config = {
                'rsi_period': rsi.get('period', 14),
                'rsi_oversold': rsi.get('oversold', 30),
                'rsi_overbought': rsi.get('overbought', 70),
                'sma_short': ma.get('short_period', 20),
                'sma_long': ma.get('long_period', 50),
                'ema_short': 12,
                'ema_long': 26
            }
    
    def calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI)
        
        Args:
            prices: Series of closing prices
            period: RSI period (default 14)
        
        Returns:
            Series with RSI values (0-100)
        """
        # Calculate price changes
        delta = prices.diff()
        
        # Separate gains and losses
        gains = delta.where(delta > 0, 0)
        losses = -delta.where(delta < 0, 0)
        
        # Calculate average gains and losses
        avg_gains = gains.rolling(window=period, min_periods=period).mean()
        avg_losses = losses.rolling(window=period, min_periods=period).mean()
        
        # Calculate RS and RSI
        rs = avg_gains / avg_losses
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_sma(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Simple Moving Average"""
        return prices.rolling(window=period, min_periods=period).mean()
    
    def calculate_ema(self, prices: pd.Series, period: int) -> pd.Series:
        """Calculate Exponential Moving Average"""
        return prices.ewm(span=period, adjust=False).mean()
    
    def calculate_bollinger_bands(
        self, 
        prices: pd.Series, 
        period: int = 20, 
        std_dev: float = 2.0
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands
        
        Returns:
            Tuple of (upper_band, middle_band, lower_band)
        """
        middle = self.calculate_sma(prices, period)
        std = prices.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        return upper, middle, lower
    
    def calculate_macd(
        self, 
        prices: pd.Series,
        fast: int = 12,
        slow: int = 26,
        signal: int = 9
    ) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Returns:
            Tuple of (macd_line, signal_line, histogram)
        """
        ema_fast = self.calculate_ema(prices, fast)
        ema_slow = self.calculate_ema(prices, slow)
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    def analyze_stock(self, df: pd.DataFrame) -> Dict:
        """
        Perform complete technical analysis on stock data
        
        Args:
            df: DataFrame with OHLCV data (must have 'close' column)
        
        Returns:
            Dictionary with indicators and signals
        """
        if df is None or df.empty:
            return {'error': 'No data provided'}
        
        if 'close' not in df.columns:
            return {'error': 'Missing close price column'}
        
        prices = df['close']
        
        # Calculate all indicators
        rsi = self.calculate_rsi(prices, self.config['rsi_period'])
        sma_short = self.calculate_sma(prices, self.config['sma_short'])
        sma_long = self.calculate_sma(prices, self.config['sma_long'])
        ema_short = self.calculate_ema(prices, self.config['ema_short'])
        ema_long = self.calculate_ema(prices, self.config['ema_long'])
        
        bb_upper, bb_middle, bb_lower = self.calculate_bollinger_bands(prices)
        macd_line, macd_signal, macd_hist = self.calculate_macd(prices)
        
        # Get latest values
        latest = {
            'current_price': float(prices.iloc[-1]),
            'rsi': float(rsi.iloc[-1]) if not pd.isna(rsi.iloc[-1]) else None,
            'sma_short': float(sma_short.iloc[-1]) if not pd.isna(sma_short.iloc[-1]) else None,
            'sma_long': float(sma_long.iloc[-1]) if not pd.isna(sma_long.iloc[-1]) else None,
            'ema_short': float(ema_short.iloc[-1]) if not pd.isna(ema_short.iloc[-1]) else None,
            'ema_long': float(ema_long.iloc[-1]) if not pd.isna(ema_long.iloc[-1]) else None,
            'bb_upper': float(bb_upper.iloc[-1]) if not pd.isna(bb_upper.iloc[-1]) else None,
            'bb_middle': float(bb_middle.iloc[-1]) if not pd.isna(bb_middle.iloc[-1]) else None,
            'bb_lower': float(bb_lower.iloc[-1]) if not pd.isna(bb_lower.iloc[-1]) else None,
            'macd': float(macd_line.iloc[-1]) if not pd.isna(macd_line.iloc[-1]) else None,
            'macd_signal': float(macd_signal.iloc[-1]) if not pd.isna(macd_signal.iloc[-1]) else None,
            'macd_histogram': float(macd_hist.iloc[-1]) if not pd.isna(macd_hist.iloc[-1]) else None,
        }
        
        # Generate signals
        signals = self._generate_signals(latest)
        
        return {
            'indicators': latest,
            'signals': signals,
            'summary': self._generate_summary(latest, signals)
        }
    
    def _generate_signals(self, indicators: Dict) -> Dict:
        """
        Generate buy/sell/hold signals based on technical indicators
        
        Returns:
            Dictionary with signal type and reasons
        """
        signals = {
            'rsi_signal': 'neutral',
            'ma_signal': 'neutral',
            'macd_signal': 'neutral',
            'bb_signal': 'neutral',
            'overall_signal': 'hold',
            'strength': 0,  # -1 (strong sell) to +1 (strong buy)
            'reasons': []
        }
        
        # RSI Signals
        if indicators['rsi'] is not None:
            if indicators['rsi'] < self.config['rsi_oversold']:
                signals['rsi_signal'] = 'buy'
                signals['reasons'].append(f"RSI oversold ({indicators['rsi']:.1f})")
                signals['strength'] += 0.3
            elif indicators['rsi'] > self.config['rsi_overbought']:
                signals['rsi_signal'] = 'sell'
                signals['reasons'].append(f"RSI overbought ({indicators['rsi']:.1f})")
                signals['strength'] -= 0.3
        
        # Moving Average Signals (Golden/Death Cross)
        if indicators['sma_short'] and indicators['sma_long']:
            if indicators['sma_short'] > indicators['sma_long']:
                signals['ma_signal'] = 'bullish'
                signals['reasons'].append(f"SMA Golden Cross (Short > Long)")
                signals['strength'] += 0.25
            elif indicators['sma_short'] < indicators['sma_long']:
                signals['ma_signal'] = 'bearish'
                signals['reasons'].append(f"SMA Death Cross (Short < Long)")
                signals['strength'] -= 0.25
        
        # MACD Signals
        if indicators['macd'] and indicators['macd_signal']:
            if indicators['macd'] > indicators['macd_signal'] and indicators['macd_histogram'] > 0:
                signals['macd_signal'] = 'buy'
                signals['reasons'].append("MACD bullish crossover")
                signals['strength'] += 0.25
            elif indicators['macd'] < indicators['macd_signal'] and indicators['macd_histogram'] < 0:
                signals['macd_signal'] = 'sell'
                signals['reasons'].append("MACD bearish crossover")
                signals['strength'] -= 0.25
        
        # Bollinger Bands Signals
        if all([indicators['current_price'], indicators['bb_upper'], indicators['bb_lower']]):
            if indicators['current_price'] <= indicators['bb_lower']:
                signals['bb_signal'] = 'buy'
                signals['reasons'].append("Price at lower Bollinger Band")
                signals['strength'] += 0.2
            elif indicators['current_price'] >= indicators['bb_upper']:
                signals['bb_signal'] = 'sell'
                signals['reasons'].append("Price at upper Bollinger Band")
                signals['strength'] -= 0.2
        
        # Determine overall signal
        if signals['strength'] >= 0.4:
            signals['overall_signal'] = 'strong_buy'
        elif signals['strength'] >= 0.2:
            signals['overall_signal'] = 'buy'
        elif signals['strength'] <= -0.4:
            signals['overall_signal'] = 'strong_sell'
        elif signals['strength'] <= -0.2:
            signals['overall_signal'] = 'sell'
        else:
            signals['overall_signal'] = 'hold'
        
        return signals
    
    def _generate_summary(self, indicators: Dict, signals: Dict) -> str:
        """Generate human-readable summary of analysis"""
        price = indicators['current_price']
        signal = signals['overall_signal'].upper().replace('_', ' ')
        strength = signals['strength']
        
        summary = f"Signal: {signal} (Strength: {strength:+.2f})\n"
        summary += f"Current Price: ${price:.2f}\n"
        
        if indicators['rsi']:
            summary += f"RSI: {indicators['rsi']:.1f} - "
            if indicators['rsi'] < 30:
                summary += "Oversold\n"
            elif indicators['rsi'] > 70:
                summary += "Overbought\n"
            else:
                summary += "Neutral\n"
        
        if signals['reasons']:
            summary += "\nKey Indicators:\n"
            for reason in signals['reasons']:
                summary += f"  - {reason}\n"
        
        return summary.strip()


def test_technical_analysis():
    """Test function for technical analysis"""
    print("\n" + "="*60)
    print("TESTING TECHNICAL ANALYSIS MODULE")
    print("="*60)
    
    # Create sample data
    dates = pd.date_range(start='2025-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Generate realistic price movement
    price = 100
    prices = [price]
    for _ in range(99):
        change = np.random.randn() * 2
        price = max(price + change, 50)  # Prevent negative prices
        prices.append(price)
    
    df = pd.DataFrame({
        'timestamp': dates,
        'close': prices,
        'open': [p * 0.99 for p in prices],
        'high': [p * 1.02 for p in prices],
        'low': [p * 0.98 for p in prices],
        'volume': np.random.randint(1000000, 5000000, 100)
    })
    
    # Initialize analyzer
    analyzer = TechnicalAnalyzer()
    
    # Analyze the data
    print("\n[ANALYZING SAMPLE STOCK DATA]")
    results = analyzer.analyze_stock(df)
    
    if 'error' in results:
        print(f"[ERROR] {results['error']}")
        return
    
    print("\n[INDICATORS]:")
    for key, value in results['indicators'].items():
        if value is not None:
            if isinstance(value, float):
                print(f"  {key}: {value:.2f}")
            else:
                print(f"  {key}: {value}")
    
    print("\n[SIGNALS]:")
    print(f"  Overall Signal: {results['signals']['overall_signal'].upper()}")
    print(f"  Signal Strength: {results['signals']['strength']:+.2f}")
    print(f"  RSI Signal: {results['signals']['rsi_signal']}")
    print(f"  MA Signal: {results['signals']['ma_signal']}")
    print(f"  MACD Signal: {results['signals']['macd_signal']}")
    print(f"  BB Signal: {results['signals']['bb_signal']}")
    
    print("\n[SUMMARY]:")
    print(results['summary'])
    
    print("\n" + "="*60)
    print("TECHNICAL ANALYSIS TEST COMPLETE")
    print("="*60 + "\n")


if __name__ == "__main__":
    test_technical_analysis()
