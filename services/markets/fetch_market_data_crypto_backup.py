"""
Financial Markets Data Collector
Fetches stock market and cryptocurrency data from various free APIs
"""

import requests
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MarketsDataCollector:
    """Collector for financial markets data"""
    
    def __init__(self):
        # Using free APIs that don't require keys
        self.crypto_url = "https://api.coingecko.com/api/v3"
        self.timeout = 15
        self.max_retries = 3
        self.retry_delay = 2
        
    def fetch_crypto_data(self, coins: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch cryptocurrency market data
        
        Args:
            coins: List of coin IDs (default: ['bitcoin', 'ethereum', 'cardano'])
            
        Returns:
            Dictionary containing crypto market data or None if failed
        """
        if coins is None:
            coins = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin']
        
        params = {
            'ids': ','.join(coins),
            'vs_currencies': 'usd',
            'include_24hr_change': 'true',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true'
        }
        
        endpoint = f"{self.crypto_url}/simple/price"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching crypto data for {len(coins)} coins "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info(f"Successfully fetched crypto data for {len(data)} coins")
                
                return data
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if e.response.status_code == 429:
                    logger.warning("Rate limit hit, waiting longer")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 5)
                else:
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def fetch_crypto_global(self) -> Optional[Dict[str, Any]]:
        """
        Fetch global cryptocurrency market statistics
        
        Returns:
            Dictionary containing global market data or None if failed
        """
        endpoint = f"{self.crypto_url}/global"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Fetching global crypto market data "
                          f"(attempt {attempt + 1}/{self.max_retries})")
                
                response = requests.get(
                    endpoint,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = response.json()
                
                logger.info("Successfully fetched global crypto market data")
                
                return data.get('data', {})
                
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout on attempt {attempt + 1}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.ConnectionError as e:
                logger.error(f"Connection error on attempt {attempt + 1}: {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                    
            except requests.exceptions.HTTPError as e:
                logger.error(f"HTTP error: {e}")
                if e.response.status_code == 429:
                    logger.warning("Rate limit hit, waiting longer")
                    if attempt < self.max_retries - 1:
                        time.sleep(self.retry_delay * 5)
                else:
                    return None
                    
            except requests.exceptions.RequestException as e:
                logger.error(f"Request failed: {e}")
                return None
                
            except ValueError as e:
                logger.error(f"JSON decode error: {e}")
                return None
                
            except Exception as e:
                logger.error(f"Unexpected error: {e}", exc_info=True)
                return None
        
        logger.error("All retry attempts failed")
        return None
    
    def fetch_data(self, coins: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch comprehensive market data
        
        Args:
            coins: List of cryptocurrency IDs to fetch
            
        Returns:
            Dictionary containing all market data or None if failed
        """
        logger.info("Starting comprehensive market data collection")
        
        # Fetch crypto prices
        crypto_data = self.fetch_crypto_data(coins)
        
        # Fetch global market stats
        global_data = self.fetch_crypto_global()
        
        # If both failed, return None
        if crypto_data is None and global_data is None:
            logger.error("All market data collection failed")
            return None
        
        # Process and enrich the data
        enriched_data = self._enrich_data(crypto_data or {}, global_data or {})
        
        return enriched_data
    
    def _enrich_data(self, crypto_data: Dict, global_data: Dict) -> Dict[str, Any]:
        """Process and enrich market data"""
        
        # Process individual coin data
        coins_info = []
        total_market_cap = 0
        
        for coin_id, coin_data in crypto_data.items():
            coin_info = {
                'id': coin_id,
                'name': coin_id.replace('-', ' ').title(),
                'price_usd': coin_data.get('usd'),
                'change_24h': coin_data.get('usd_24h_change'),
                'market_cap': coin_data.get('usd_market_cap'),
                'volume_24h': coin_data.get('usd_24h_vol')
            }
            coins_info.append(coin_info)
            
            if coin_info['market_cap']:
                total_market_cap += coin_info['market_cap']
        
        # Sort by market cap
        coins_info.sort(key=lambda x: x.get('market_cap', 0), reverse=True)
        
        # Extract global market data
        global_market_cap = global_data.get('total_market_cap', {}).get('usd')
        global_volume_24h = global_data.get('total_volume', {}).get('usd')
        btc_dominance = global_data.get('market_cap_percentage', {}).get('btc')
        
        return {
            'cryptocurrencies': coins_info,
            'total_coins_tracked': len(coins_info),
            'global_market_cap_usd': global_market_cap,
            'global_volume_24h_usd': global_volume_24h,
            'bitcoin_dominance_percent': btc_dominance,
            'active_cryptocurrencies': global_data.get('active_cryptocurrencies'),
            'markets': global_data.get('markets'),
            'collection_time': datetime.utcnow().isoformat(),
            'status': 'success'
        }

def main():
    """Main execution function"""
    collector = MarketsDataCollector()
    
    logger.info("Starting market data collection")
    
    # Fetch data for popular cryptocurrencies
    coins = ['bitcoin', 'ethereum', 'cardano', 'solana', 'dogecoin', 'ripple', 'polkadot']
    data = collector.fetch_data(coins)
    
    if data:
        logger.info("Market data collection successful")
        print("\n=== Financial Markets Data ===")
        print(f"\nGlobal Cryptocurrency Market:")
        if data['global_market_cap_usd']:
            print(f"  Total Market Cap: ${data['global_market_cap_usd']:,.0f}")
        if data['global_volume_24h_usd']:
            print(f"  24h Volume: ${data['global_volume_24h_usd']:,.0f}")
        if data['bitcoin_dominance_percent']:
            print(f"  Bitcoin Dominance: {data['bitcoin_dominance_percent']:.2f}%")
        
        print(f"\nTop Cryptocurrencies ({data['total_coins_tracked']} tracked):")
        for coin in data['cryptocurrencies'][:5]:  # Show top 5
            change_symbol = "📈" if coin.get('change_24h', 0) > 0 else "📉"
            print(f"  {change_symbol} {coin['name']}: ${coin['price_usd']:,.2f} "
                  f"({coin.get('change_24h', 0):+.2f}% 24h)")
            if coin['market_cap']:
                print(f"      Market Cap: ${coin['market_cap']:,.0f}")
        
        print(f"\nCollection Time: {data['collection_time']}")
        
        return data
    else:
        logger.error("Market data collection failed")
        return None

if __name__ == "__main__":
    main()
