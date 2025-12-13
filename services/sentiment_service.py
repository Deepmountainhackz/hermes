"""
Sentiment Service
Calculates Fear & Greed Index and provides market sentiment analysis.
"""
import requests
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

from core.config import Config
from core.exceptions import APIError

logger = logging.getLogger(__name__)


class SentimentService:
    """Service for market sentiment indicators."""

    # Fear & Greed Index thresholds
    FEAR_GREED_LEVELS = {
        (0, 25): ('Extreme Fear', '#ff4757'),
        (25, 45): ('Fear', '#ff6b81'),
        (45, 55): ('Neutral', '#ffa502'),
        (55, 75): ('Greed', '#7bed9f'),
        (75, 100): ('Extreme Greed', '#2ed573'),
    }

    def __init__(self, config: Config):
        """Initialize the service."""
        self.config = config
        self.timeout = config.API_TIMEOUT if hasattr(config, 'API_TIMEOUT') else 30

    def fetch_crypto_fear_greed(self) -> Optional[Dict[str, Any]]:
        """Fetch Crypto Fear & Greed Index from Alternative.me API (free, no key)."""
        try:
            url = "https://api.alternative.me/fng/?limit=1"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()
            data = response.json()

            if 'data' not in data or not data['data']:
                return None

            fng = data['data'][0]
            value = int(fng.get('value', 50))
            classification = fng.get('value_classification', 'Neutral')

            # Get color based on value
            color = '#ffa502'  # default neutral
            for (low, high), (_, c) in self.FEAR_GREED_LEVELS.items():
                if low <= value < high:
                    color = c
                    break

            return {
                'value': value,
                'classification': classification,
                'color': color,
                'timestamp': datetime.fromtimestamp(int(fng.get('timestamp', datetime.now().timestamp()))),
                'type': 'crypto'
            }
        except Exception as e:
            logger.error(f"Error fetching crypto fear & greed: {e}")
            return None

    def calculate_stock_fear_greed(self, vix: float, yield_spread: float,
                                    stock_momentum: float = 0) -> Dict[str, Any]:
        """
        Calculate a simplified stock market Fear & Greed Index.

        Components:
        - VIX level (inverted - high VIX = fear)
        - Yield curve spread (negative = fear/recession signal)
        - Stock momentum (optional)
        """
        # VIX component (0-100, inverted)
        # VIX < 12 = extreme greed, VIX > 35 = extreme fear
        if vix <= 12:
            vix_score = 100
        elif vix >= 35:
            vix_score = 0
        else:
            vix_score = 100 - ((vix - 12) / 23 * 100)

        # Yield curve component (0-100)
        # Positive spread = normal/greed, negative = inverted/fear
        if yield_spread >= 1.0:
            yield_score = 100
        elif yield_spread <= -0.5:
            yield_score = 0
        else:
            yield_score = ((yield_spread + 0.5) / 1.5) * 100

        # Weight the components
        if stock_momentum != 0:
            # Momentum: 0 = neutral (50), positive = greed, negative = fear
            momentum_score = 50 + (stock_momentum * 5)  # +-10% move = +-50 points
            momentum_score = max(0, min(100, momentum_score))

            composite = (vix_score * 0.4) + (yield_score * 0.3) + (momentum_score * 0.3)
        else:
            composite = (vix_score * 0.6) + (yield_score * 0.4)

        composite = int(max(0, min(100, composite)))

        # Determine classification and color
        classification = 'Neutral'
        color = '#ffa502'
        for (low, high), (label, c) in self.FEAR_GREED_LEVELS.items():
            if low <= composite < high:
                classification = label
                color = c
                break

        return {
            'value': composite,
            'classification': classification,
            'color': color,
            'components': {
                'vix_score': int(vix_score),
                'yield_score': int(yield_score),
                'momentum_score': int(stock_momentum) if stock_momentum else None
            },
            'timestamp': datetime.now(),
            'type': 'stock'
        }

    def get_market_regime(self, vix: float, yield_spread: float) -> Dict[str, Any]:
        """
        Determine current market regime based on indicators.

        Regimes:
        - Risk-On: Low VIX, positive yield curve
        - Risk-Off: High VIX, inverted yield curve
        - Transitional: Mixed signals
        """
        # VIX regime
        if vix < 15:
            vix_regime = 'low_volatility'
        elif vix < 25:
            vix_regime = 'normal_volatility'
        elif vix < 35:
            vix_regime = 'elevated_volatility'
        else:
            vix_regime = 'high_volatility'

        # Yield curve regime
        if yield_spread > 0.5:
            curve_regime = 'steep'
        elif yield_spread > 0:
            curve_regime = 'normal'
        elif yield_spread > -0.25:
            curve_regime = 'flat'
        else:
            curve_regime = 'inverted'

        # Overall regime
        if vix_regime in ['low_volatility', 'normal_volatility'] and curve_regime in ['steep', 'normal']:
            overall = 'risk_on'
            color = '#2ed573'
        elif vix_regime in ['elevated_volatility', 'high_volatility'] and curve_regime == 'inverted':
            overall = 'risk_off'
            color = '#ff4757'
        else:
            overall = 'transitional'
            color = '#ffa502'

        return {
            'overall_regime': overall,
            'vix_regime': vix_regime,
            'curve_regime': curve_regime,
            'color': color,
            'vix': vix,
            'yield_spread': yield_spread
        }


class CentralBankCalendarService:
    """Service for tracking central bank meeting dates."""

    # 2024-2025 Central Bank Meeting Schedule
    # These are approximate scheduled dates - actual dates may vary
    CENTRAL_BANK_MEETINGS = {
        'Federal Reserve (FOMC)': {
            'country': 'USA',
            'currency': 'USD',
            'meetings_2024': [
                '2024-01-31', '2024-03-20', '2024-05-01', '2024-06-12',
                '2024-07-31', '2024-09-18', '2024-11-07', '2024-12-18'
            ],
            'meetings_2025': [
                '2025-01-29', '2025-03-19', '2025-05-07', '2025-06-18',
                '2025-07-30', '2025-09-17', '2025-11-05', '2025-12-17'
            ]
        },
        'European Central Bank (ECB)': {
            'country': 'EU',
            'currency': 'EUR',
            'meetings_2024': [
                '2024-01-25', '2024-03-07', '2024-04-11', '2024-06-06',
                '2024-07-18', '2024-09-12', '2024-10-17', '2024-12-12'
            ],
            'meetings_2025': [
                '2025-01-30', '2025-03-06', '2025-04-17', '2025-06-05',
                '2025-07-17', '2025-09-11', '2025-10-30', '2025-12-18'
            ]
        },
        'Bank of England (BoE)': {
            'country': 'UK',
            'currency': 'GBP',
            'meetings_2024': [
                '2024-02-01', '2024-03-21', '2024-05-09', '2024-06-20',
                '2024-08-01', '2024-09-19', '2024-11-07', '2024-12-19'
            ],
            'meetings_2025': [
                '2025-02-06', '2025-03-20', '2025-05-08', '2025-06-19',
                '2025-08-07', '2025-09-18', '2025-11-06', '2025-12-18'
            ]
        },
        'Bank of Japan (BoJ)': {
            'country': 'Japan',
            'currency': 'JPY',
            'meetings_2024': [
                '2024-01-23', '2024-03-19', '2024-04-26', '2024-06-14',
                '2024-07-31', '2024-09-20', '2024-10-31', '2024-12-19'
            ],
            'meetings_2025': [
                '2025-01-24', '2025-03-14', '2025-05-01', '2025-06-17',
                '2025-07-31', '2025-09-19', '2025-10-31', '2025-12-19'
            ]
        },
        'Reserve Bank of Australia (RBA)': {
            'country': 'Australia',
            'currency': 'AUD',
            'meetings_2024': [
                '2024-02-06', '2024-03-19', '2024-05-07', '2024-06-18',
                '2024-08-06', '2024-09-24', '2024-11-05', '2024-12-10'
            ],
            'meetings_2025': [
                '2025-02-18', '2025-04-01', '2025-05-20', '2025-07-08',
                '2025-08-12', '2025-09-30', '2025-11-04', '2025-12-09'
            ]
        },
        "People's Bank of China (PBoC)": {
            'country': 'China',
            'currency': 'CNY',
            'meetings_2024': [
                '2024-01-22', '2024-02-20', '2024-03-20', '2024-04-22',
                '2024-05-20', '2024-06-20', '2024-07-22', '2024-08-20',
                '2024-09-20', '2024-10-21', '2024-11-20', '2024-12-20'
            ],
            'meetings_2025': [
                '2025-01-20', '2025-02-20', '2025-03-20', '2025-04-21',
                '2025-05-20', '2025-06-20', '2025-07-21', '2025-08-20',
                '2025-09-22', '2025-10-20', '2025-11-20', '2025-12-22'
            ]
        },
        'Swiss National Bank (SNB)': {
            'country': 'Switzerland',
            'currency': 'CHF',
            'meetings_2024': [
                '2024-03-21', '2024-06-20', '2024-09-26', '2024-12-12'
            ],
            'meetings_2025': [
                '2025-03-20', '2025-06-19', '2025-09-18', '2025-12-11'
            ]
        },
        'Bank of Canada (BoC)': {
            'country': 'Canada',
            'currency': 'CAD',
            'meetings_2024': [
                '2024-01-24', '2024-03-06', '2024-04-10', '2024-06-05',
                '2024-07-24', '2024-09-04', '2024-10-23', '2024-12-11'
            ],
            'meetings_2025': [
                '2025-01-29', '2025-03-12', '2025-04-16', '2025-06-04',
                '2025-07-30', '2025-09-03', '2025-10-29', '2025-12-10'
            ]
        }
    }

    def __init__(self, config: Config = None):
        """Initialize the service."""
        self.config = config

    def get_upcoming_meetings(self, days_ahead: int = 30) -> List[Dict[str, Any]]:
        """Get all central bank meetings in the next N days."""
        from datetime import timedelta

        today = datetime.now().date()
        end_date = today + timedelta(days=days_ahead)

        upcoming = []

        for bank_name, bank_info in self.CENTRAL_BANK_MEETINGS.items():
            # Check both 2024 and 2025 meetings
            all_meetings = bank_info.get('meetings_2024', []) + bank_info.get('meetings_2025', [])

            for meeting_date_str in all_meetings:
                meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date()

                if today <= meeting_date <= end_date:
                    days_until = (meeting_date - today).days

                    upcoming.append({
                        'bank': bank_name,
                        'country': bank_info['country'],
                        'currency': bank_info['currency'],
                        'date': meeting_date,
                        'date_str': meeting_date.strftime('%b %d, %Y'),
                        'days_until': days_until,
                        'urgency': 'imminent' if days_until <= 3 else 'upcoming' if days_until <= 7 else 'scheduled'
                    })

        # Sort by date
        upcoming.sort(key=lambda x: x['date'])

        return upcoming

    def get_next_meeting(self, bank_name: str) -> Optional[Dict[str, Any]]:
        """Get the next meeting for a specific central bank."""
        if bank_name not in self.CENTRAL_BANK_MEETINGS:
            return None

        bank_info = self.CENTRAL_BANK_MEETINGS[bank_name]
        today = datetime.now().date()

        all_meetings = bank_info.get('meetings_2024', []) + bank_info.get('meetings_2025', [])

        for meeting_date_str in sorted(all_meetings):
            meeting_date = datetime.strptime(meeting_date_str, '%Y-%m-%d').date()

            if meeting_date >= today:
                days_until = (meeting_date - today).days
                return {
                    'bank': bank_name,
                    'country': bank_info['country'],
                    'currency': bank_info['currency'],
                    'date': meeting_date,
                    'date_str': meeting_date.strftime('%b %d, %Y'),
                    'days_until': days_until
                }

        return None

    def get_all_banks(self) -> List[str]:
        """Get list of all tracked central banks."""
        return list(self.CENTRAL_BANK_MEETINGS.keys())
