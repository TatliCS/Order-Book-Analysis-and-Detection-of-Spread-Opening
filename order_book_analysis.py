# order_book_analysis.py  – revised for python-binance ≥ 1.0.28
import os
import time
import json
import logging
import ssl
import certifi
import platform
from datetime import datetime
from dotenv import load_dotenv
from binance import BinanceSocketManager
from binance.client import Client
from visualization import (
    plot_spread_analysis,
    plot_order_book_depth,
    plot_fake_wall_detection,
    generate_analysis_report
)

from utils import (
    calculate_spread,
    detect_spread_widening,
    calculate_recovery_time,
    detect_fake_walls,
    calculate_order_book_imbalance
)

# ──────────────────────────────────────────────────────────────
# 1.  Setup
# ──────────────────────────────────────────────────────────────
load_dotenv()                                   # load BINANCE_API_KEY / SECRET

api_key    = os.getenv("BINANCE_API_KEY")
api_secret = os.getenv("BINANCE_API_SECRET")

# Configure SSL context based on platform
if platform.system() == 'Darwin':  # macOS
    # Use the system's certificate store
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE
else:
    # Use certifi for other platforms
    ssl_context = ssl.create_default_context(cafile=certifi.where())

# Initialize client with proper configuration
client = Client(
    api_key=api_key,
    api_secret=api_secret,
    requests_params={
        'timeout': 30,
        'proxies': {
            'http': None,
            'https': None
        }
    }
)
# Set https_proxy attribute directly on the client
client.https_proxy = None

# ──────────────────────────────────────────────────────────────
# 2.  Analyzer class
# ──────────────────────────────────────────────────────────────
class OrderBookAnalyzer:
    def __init__(self, symbol='BTCUSDT', duration=60, spread_threshold=0.001, 
                 widening_threshold=0.0005, volume_threshold=100):
        """Initialize the order book analyzer
        
        Args:
            symbol (str): Trading pair symbol (default: 'BTCUSDT')
            duration (int): Data collection duration in seconds (default: 60)
            spread_threshold (float): Threshold for spread analysis (default: 0.001)
            widening_threshold (float): Threshold for spread widening detection (default: 0.0005)
            volume_threshold (float): Threshold for fake wall detection (default: 100)
        """
        self.symbol = symbol.upper()
        self.duration = duration
        self.spread_threshold = spread_threshold
        self.widening_threshold = widening_threshold
        self.volume_threshold = volume_threshold
        
        # Initialize data structures
        self.order_book = {'bids': {}, 'asks': {}}
        self.spreads = []
        self.timestamps = []
        self.current_price = None
        
        # Initialize Binance client
        self.client = client  # Use the globally configured client
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )

    # ──────────────────────────────────────────────────────────
    # 2.1 callback: handle each depthUpdate event
    # ──────────────────────────────────────────────────────────
    def process_order_book(self, msg):
        """Process incoming order book updates."""
        try:
            print(f"Received message: {msg}")  # Debug logging
            
            if not isinstance(msg, dict):
                print(f"Unexpected message format: {type(msg)}")
                return
                
            if msg.get("e") != "depthUpdate":
                print(f"Not a depth update: {msg.get('e')}")
                return

            # bids
            for price_str, qty_str in msg["b"]:
                price, qty = float(price_str), float(qty_str)
                self.order_book["bids"] = [b for b in self.order_book["bids"] if b[0] != price]
                if qty > 0:
                    self.order_book["bids"].append((price, qty))

            # asks
            for price_str, qty_str in msg["a"]:
                price, qty = float(price_str), float(qty_str)
                self.order_book["asks"] = [a for a in self.order_book["asks"] if a[0] != price]
                if qty > 0:
                    self.order_book["asks"].append((price, qty))

            # keep sorted
            self.order_book["bids"].sort(key=lambda x: x[0], reverse=True)
            self.order_book["asks"].sort(key=lambda x: x[0])

            # compute spread
            if self.order_book["bids"] and self.order_book["asks"]:
                best_bid = self.order_book["bids"][0][0]
                best_ask = self.order_book["asks"][0][0]
                spread   = calculate_spread(best_bid, best_ask)

                self.spreads.append(spread)
                self.timestamps.append(datetime.now())
                self.current_price = (best_bid + best_ask) / 2
                
                print(f"Updated spread: {spread:.2f} USDT")  # Debug logging
                
        except Exception as e:
            print(f"Error processing order book update: {str(e)}")
            print(f"Message that caused error: {msg}")

    # ──────────────────────────────────────────────────────────
    # 2.2 main runner
    # ──────────────────────────────────────────────────────────
    def run_analysis(self):
        """Run the order book analysis"""
        try:
            # Initialize socket manager with the configured client
            bm = BinanceSocketManager(self.client)
            
            # Create the depth socket with callback
            socket = bm.depth_socket(self.symbol.lower(), self.process_order_book)
            
            logging.info(f"WebSocket connection started for {self.symbol}")

            # Start time for duration tracking
            start_time = time.time()
            
            # Wait for the specified duration
            while time.time() - start_time < self.duration:
                time.sleep(0.1)  # Small sleep to prevent CPU overuse

            # Stop the socket
            bm._stop_socket(socket)
            logging.info("WebSocket connection closed")

            # Process and visualize the data
            self.process_data()
            self.visualize_results()
        except Exception as e:
            logging.error(f"Error in run_analysis: {str(e)}")
            raise

    def process_data(self):
        """Process the collected data"""
        if len(self.spreads) == 0:
            print("Warning: No data was collected during the session")
            return

        print(f"✔ Data collection complete – collected {len(self.spreads)} updates")

        # spread-widening detection
        widening_events = detect_spread_widening(self.spreads, self.widening_threshold)
        recovery_times = calculate_recovery_time(self.spreads, widening_events, self.spread_threshold)

        # fake-wall detection
        fake_walls = detect_fake_walls(self.order_book, self.volume_threshold)

        # report
        report = generate_analysis_report(self.spreads, widening_events, recovery_times, fake_walls)
        with open("analysis_report.txt", "w") as fp:
            fp.write(report)

        print("✔ Analysis done – outputs saved:")
        print("  • analysis_report.txt")
        print("  • spread_analysis.png")
        print("  • order_book_depth.png")
        print("  • fake_wall_detection.png")

    def visualize_results(self):
        """Generate visualizations from the collected data"""
        if len(self.spreads) == 0:
            print("Warning: No data to visualize")
            return

        # Plot spread analysis
        plot_spread_analysis(
            self.timestamps,
            self.spreads,
            detect_spread_widening(self.spreads, self.widening_threshold),
            self.spread_threshold
        )

        # Plot order book depth
        plot_order_book_depth(self.order_book, self.current_price)

        # Plot fake wall detection
        fake_walls = detect_fake_walls(self.order_book, self.volume_threshold)
        plot_fake_wall_detection(self.order_book, fake_walls)

        print("✔ Visualizations generated:")
        print("  • spread_analysis.png")
        print("  • order_book_depth.png")
        print("  • fake_wall_detection.png")


# ──────────────────────────────────────────────────────────────
# 3.  CLI entry-point
# ──────────────────────────────────────────────────────────────
if __name__ == "__main__":
    OrderBookAnalyzer().run_analysis()
