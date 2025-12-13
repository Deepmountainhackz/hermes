"""
Technical Indicators Service
Calculates technical analysis indicators for stocks and crypto.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class IndicatorResult:
    """Result of an indicator calculation."""
    name: str
    value: float
    signal: str  # 'bullish', 'bearish', 'neutral'
    description: str


class IndicatorsService:
    """Service for calculating technical indicators."""

    def __init__(self):
        pass

    # =========================================================================
    # TREND INDICATORS
    # =========================================================================

    def sma(self, prices: pd.Series, period: int = 20) -> pd.Series:
        """Simple Moving Average."""
        return prices.rolling(window=period).mean()

    def ema(self, prices: pd.Series, period: int = 12) -> pd.Series:
        """Exponential Moving Average."""
        return prices.ewm(span=period, adjust=False).mean()

    def calculate_moving_averages(self, prices: pd.Series) -> Dict[str, pd.Series]:
        """Calculate common moving averages."""
        return {
            'SMA_20': self.sma(prices, 20),
            'SMA_50': self.sma(prices, 50),
            'SMA_200': self.sma(prices, 200),
            'EMA_12': self.ema(prices, 12),
            'EMA_26': self.ema(prices, 26),
        }

    # =========================================================================
    # MOMENTUM INDICATORS
    # =========================================================================

    def rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """
        Relative Strength Index (RSI).
        Returns values between 0-100.
        >70 = overbought, <30 = oversold
        """
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    def macd(self, prices: pd.Series,
             fast: int = 12, slow: int = 26, signal: int = 9) -> Dict[str, pd.Series]:
        """
        Moving Average Convergence Divergence (MACD).
        Returns MACD line, signal line, and histogram.
        """
        ema_fast = self.ema(prices, fast)
        ema_slow = self.ema(prices, slow)

        macd_line = ema_fast - ema_slow
        signal_line = self.ema(macd_line, signal)
        histogram = macd_line - signal_line

        return {
            'MACD': macd_line,
            'Signal': signal_line,
            'Histogram': histogram
        }

    def stochastic(self, high: pd.Series, low: pd.Series, close: pd.Series,
                   k_period: int = 14, d_period: int = 3) -> Dict[str, pd.Series]:
        """
        Stochastic Oscillator.
        Returns %K and %D lines (0-100).
        """
        lowest_low = low.rolling(window=k_period).min()
        highest_high = high.rolling(window=k_period).max()

        k = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_period).mean()

        return {'%K': k, '%D': d}

    # =========================================================================
    # VOLATILITY INDICATORS
    # =========================================================================

    def bollinger_bands(self, prices: pd.Series,
                        period: int = 20, std_dev: float = 2) -> Dict[str, pd.Series]:
        """
        Bollinger Bands.
        Returns upper, middle (SMA), and lower bands.
        """
        middle = self.sma(prices, period)
        std = prices.rolling(window=period).std()

        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)

        # Band width percentage
        width = ((upper - lower) / middle) * 100

        # %B - where price is relative to bands
        percent_b = (prices - lower) / (upper - lower)

        return {
            'Upper': upper,
            'Middle': middle,
            'Lower': lower,
            'Width': width,
            'Percent_B': percent_b
        }

    def atr(self, high: pd.Series, low: pd.Series, close: pd.Series,
            period: int = 14) -> pd.Series:
        """Average True Range - volatility indicator."""
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())

        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()

        return atr

    # =========================================================================
    # VOLUME INDICATORS
    # =========================================================================

    def obv(self, close: pd.Series, volume: pd.Series) -> pd.Series:
        """On-Balance Volume."""
        direction = np.where(close > close.shift(), 1,
                            np.where(close < close.shift(), -1, 0))
        obv = (volume * direction).cumsum()
        return pd.Series(obv, index=close.index)

    def volume_sma(self, volume: pd.Series, period: int = 20) -> pd.Series:
        """Volume Simple Moving Average."""
        return volume.rolling(window=period).mean()

    # =========================================================================
    # SIGNAL GENERATION
    # =========================================================================

    def get_rsi_signal(self, rsi_value: float) -> IndicatorResult:
        """Interpret RSI value."""
        if pd.isna(rsi_value):
            return IndicatorResult('RSI', 0, 'neutral', 'Insufficient data')

        if rsi_value >= 70:
            signal = 'bearish'
            desc = f'Overbought ({rsi_value:.1f})'
        elif rsi_value <= 30:
            signal = 'bullish'
            desc = f'Oversold ({rsi_value:.1f})'
        else:
            signal = 'neutral'
            desc = f'Neutral ({rsi_value:.1f})'

        return IndicatorResult('RSI', rsi_value, signal, desc)

    def get_macd_signal(self, macd: float, signal: float, histogram: float) -> IndicatorResult:
        """Interpret MACD values."""
        if pd.isna(macd) or pd.isna(signal):
            return IndicatorResult('MACD', 0, 'neutral', 'Insufficient data')

        if histogram > 0 and macd > signal:
            sig = 'bullish'
            desc = 'Bullish momentum'
        elif histogram < 0 and macd < signal:
            sig = 'bearish'
            desc = 'Bearish momentum'
        else:
            sig = 'neutral'
            desc = 'Consolidating'

        return IndicatorResult('MACD', histogram, sig, desc)

    def get_ma_signal(self, price: float, sma_20: float, sma_50: float,
                      sma_200: float) -> IndicatorResult:
        """Interpret moving average positions."""
        if pd.isna(sma_20) or pd.isna(sma_50):
            return IndicatorResult('MA', 0, 'neutral', 'Insufficient data')

        signals = []
        if price > sma_20:
            signals.append('above SMA20')
        if price > sma_50:
            signals.append('above SMA50')
        if not pd.isna(sma_200) and price > sma_200:
            signals.append('above SMA200')

        bullish_count = len(signals)

        if bullish_count >= 2:
            sig = 'bullish'
            desc = f'Price {", ".join(signals)}'
        elif bullish_count == 0:
            sig = 'bearish'
            desc = 'Price below all MAs'
        else:
            sig = 'neutral'
            desc = f'Price {", ".join(signals)}' if signals else 'Mixed signals'

        return IndicatorResult('Moving Averages', bullish_count, sig, desc)

    def get_bb_signal(self, price: float, upper: float, lower: float,
                      percent_b: float) -> IndicatorResult:
        """Interpret Bollinger Band position."""
        if pd.isna(upper) or pd.isna(lower):
            return IndicatorResult('Bollinger Bands', 0, 'neutral', 'Insufficient data')

        if price >= upper or percent_b >= 1:
            sig = 'bearish'
            desc = 'At upper band (potential reversal)'
        elif price <= lower or percent_b <= 0:
            sig = 'bullish'
            desc = 'At lower band (potential reversal)'
        else:
            sig = 'neutral'
            desc = f'Within bands (%B: {percent_b:.2f})'

        return IndicatorResult('Bollinger Bands', percent_b, sig, desc)

    # =========================================================================
    # COMPREHENSIVE ANALYSIS
    # =========================================================================

    def analyze(self, df: pd.DataFrame) -> Dict:
        """
        Perform comprehensive technical analysis on price data.

        Args:
            df: DataFrame with columns: close, high (optional), low (optional), volume (optional)

        Returns:
            Dictionary with all indicators and signals
        """
        close = df['close'] if 'close' in df.columns else df['price']
        high = df.get('high', close)
        low = df.get('low', close)
        volume = df.get('volume')

        # Calculate all indicators
        mas = self.calculate_moving_averages(close)
        rsi_values = self.rsi(close)
        macd_data = self.macd(close)
        bb_data = self.bollinger_bands(close)

        # Get latest values
        latest_close = close.iloc[-1]
        latest_rsi = rsi_values.iloc[-1]
        latest_macd = macd_data['MACD'].iloc[-1]
        latest_signal = macd_data['Signal'].iloc[-1]
        latest_histogram = macd_data['Histogram'].iloc[-1]

        # Generate signals
        signals = []
        signals.append(self.get_rsi_signal(latest_rsi))
        signals.append(self.get_macd_signal(latest_macd, latest_signal, latest_histogram))
        signals.append(self.get_ma_signal(
            latest_close,
            mas['SMA_20'].iloc[-1],
            mas['SMA_50'].iloc[-1],
            mas['SMA_200'].iloc[-1]
        ))
        signals.append(self.get_bb_signal(
            latest_close,
            bb_data['Upper'].iloc[-1],
            bb_data['Lower'].iloc[-1],
            bb_data['Percent_B'].iloc[-1]
        ))

        # Overall signal
        bullish = sum(1 for s in signals if s.signal == 'bullish')
        bearish = sum(1 for s in signals if s.signal == 'bearish')

        if bullish > bearish + 1:
            overall = 'bullish'
        elif bearish > bullish + 1:
            overall = 'bearish'
        else:
            overall = 'neutral'

        return {
            'price': latest_close,
            'indicators': {
                'RSI': latest_rsi,
                'MACD': latest_macd,
                'MACD_Signal': latest_signal,
                'MACD_Histogram': latest_histogram,
                'SMA_20': mas['SMA_20'].iloc[-1],
                'SMA_50': mas['SMA_50'].iloc[-1],
                'SMA_200': mas['SMA_200'].iloc[-1],
                'BB_Upper': bb_data['Upper'].iloc[-1],
                'BB_Lower': bb_data['Lower'].iloc[-1],
                'BB_Percent_B': bb_data['Percent_B'].iloc[-1],
            },
            'signals': signals,
            'overall_signal': overall,
            'bullish_count': bullish,
            'bearish_count': bearish,
            'series': {
                'close': close,
                'rsi': rsi_values,
                'macd': macd_data,
                'bollinger': bb_data,
                'moving_averages': mas,
            }
        }

    def get_summary_table(self, analysis: Dict) -> pd.DataFrame:
        """Create a summary table of signals."""
        rows = []
        for signal in analysis['signals']:
            rows.append({
                'Indicator': signal.name,
                'Value': f"{signal.value:.2f}" if not pd.isna(signal.value) else 'N/A',
                'Signal': signal.signal.upper(),
                'Description': signal.description
            })

        rows.append({
            'Indicator': 'OVERALL',
            'Value': f"{analysis['bullish_count']}B / {analysis['bearish_count']}S",
            'Signal': analysis['overall_signal'].upper(),
            'Description': f"{analysis['bullish_count']} bullish, {analysis['bearish_count']} bearish signals"
        })

        return pd.DataFrame(rows)
