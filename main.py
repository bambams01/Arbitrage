# main.py

from config import load_config
from exchange_sync import sync_exchanges, build_pair_index
from market_scanner import scan_market
from trade_executor import execute_trade
from utils.logger import setup_logger
import time

def main():
    # Set up logger
    logger = setup_logger()

    logger.info("BOOT SYSTEM: Starting Arbitrage Bot")

    # Load configuration
    logger.info("LOAD CONFIG: Loading configuration values...")
    config = load_config()

    # Sync exchanges and build pair index
    logger.info("LOAD EXCHANGE MARKETS: Synchronizing exchange data...")
    pair_index = sync_exchanges(config)

    # Build pair index
    logger.info("BUILD PAIR INDEX: Indexing tradeable pairs...")
    filtered_pairs = build_pair_index(pair_index)

    logger.info("STARTING MARKET SCANNER: Ready to scan for arbitrage opportunities.")

    # Start scanning loop
    while True:
        try:
            logger.info("MARKET SCANNER: Scanning market prices...")
            opportunities = scan_market(filtered_pairs, config)

            for opportunity in opportunities:
                logger.info(f"TRADE OPPORTUNITY FOUND: {opportunity}")
                execute_trade(opportunity, config)

            time.sleep(config['scan_interval'])

        except KeyboardInterrupt:
            logger.info("SYSTEM: Stopping Arbitrage Bot...")
            break
        except Exception as e:
            logger.error(f"ERROR: {e}")

if __name__ == "__main__":
    main()