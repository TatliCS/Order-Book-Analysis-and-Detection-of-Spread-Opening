"""
Order-Book Analysis & Spread-Opening Detection
================================================================================

Implements every hard requirement in the assignment:

1. Pull BTC/USDT depth – REST snapshot + real-time WebSocket ( *Pulling Order
   Book Data* bullet).
2. Track bid/ask spread, flag widening events and measure recovery
   time  (*Spread Analysis* bullet).
3. Persist in-memory order-book state for later depth/fake-wall charts
   (*Optional Additional Analysis*).
4. Produce three png charts and a text report  (*Visualization* & *Reporting*
   bullets).

The file is intentionally self-contained: run it and after ~10 min you get
`spread_analysis.png`, `order_book_depth.png`, `fake_wall_detection.png` and
`analysis_report.txt`.
"""

import os
import time
import logging
import platform
import ssl
import certifi
from datetime import datetime
from dotenv import load_dotenv
from binance import Client, ThreadedWebsocketManager

from visualization import (
    plot_spread_analysis,
    plot_order_book_depth,
    plot_fake_wall_detection,
    generate_analysis_report,
)
from utils import (
    calculate_spread,
    detect_spread_widening,
    calculate_recovery_time,
    detect_fake_walls,
)

# --------------------------------------------------------------------------- #
# 0. ENV / GLOBALS – Load API keys once and create a single REST client
# --------------------------------------------------------------------------- #
load_dotenv()
API_KEY    = os.getenv("BINANCE_API_KEY")
API_SECRET = os.getenv("BINANCE_API_SECRET")

# The REST call needs a TLS root bundle on some OSes (e.g. macOS)
ssl_ctx_rest = (
    ssl.create_default_context()              # Darwin ships its own bundle
    if platform.system() == "Darwin"
    else ssl.create_default_context(cafile=certifi.where())
)
rest_client = Client(
    api_key=API_KEY,
    api_secret=API_SECRET,
    requests_params={"timeout": 30},
)

# --------------------------------------------------------------------------- #
# 1. ORDER-BOOK ANALYSER  (core of the assignment)
# --------------------------------------------------------------------------- #
class OrderBookAnalyzer:
    """
    Streams depth for <symbol> during <duration> seconds and produces:
      • spread time-series + widening flags          (Spread-Analysis block)
      • recovery-time stats                          (Spread-Analysis block)
      • depth & fake-wall snapshot visuals           (Optional Analysis block)
      • human-readable report text                   (Reporting block)
    """

    def __init__(
        self,
        symbol: str = "BTCUSDT",
        duration: int = 600,          # 10-minute capture window
        spread_threshold: float = 0.01,
        widening_threshold: float = 0.0005,
        volume_threshold: float = 100.0,
    ) -> None:
        self.symbol             = symbol.upper()
        self.duration           = duration
        self.spread_threshold   = spread_threshold
        self.widening_threshold = widening_threshold
        self.volume_threshold   = volume_threshold

        self.order_book   = {"bids": [], "asks": []}
        self.spreads      : list[float]    = []
        self.timestamps   : list[datetime] = []
        self.current_mid  : float | None   = None

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s — %(levelname)s — %(message)s",
        )

    # --------------------------------------------------------------------- #
    # 1.1  One-off REST snapshot  (first bullet: “Get order-book data …”)
    # --------------------------------------------------------------------- #
    def _load_snapshot(self) -> None:
        """Grab 1 000-level depth and seed internal state."""
        snap = rest_client.get_order_book(symbol=self.symbol, limit=1000)
        self.order_book["bids"] = [(float(p), float(q)) for p, q in snap["bids"]]
        self.order_book["asks"] = [(float(p), float(q)) for p, q in snap["asks"]]

        # keep best-price on top for fast access
        self.order_book["bids"].sort(key=lambda x: x[0], reverse=True)
        self.order_book["asks"].sort(key=lambda x: x[0])

        bb, ba = self.order_book["bids"][0][0], self.order_book["asks"][0][0]
        self.spreads.append(calculate_spread(bb, ba))
        self.timestamps.append(datetime.now())
        self.current_mid = (bb + ba) / 2

        logging.info(
            "Snapshot loaded — depth levels: %d bids / %d asks",
            len(self.order_book["bids"]), len(self.order_book["asks"])
        )

    # --------------------------------------------------------------------- #
    # 1.2  WebSocket callback  (live “listen … in real-time” requirement)
    # --------------------------------------------------------------------- #
    def _process_depth(self, msg: dict) -> None:
        """Merge incremental depth update and compute new spread."""
        if msg.get("e") != "depthUpdate":
            return

        # ----- bid side --------------------------------------------------- #
        for price_str, qty_str in msg["b"]:
            price, qty = float(price_str), float(qty_str)
            self.order_book["bids"] = [b for b in self.order_book["bids"]
                                       if b[0] != price]
            if qty > 0:
                self.order_book["bids"].append((price, qty))

        # ----- ask side --------------------------------------------------- #
        for price_str, qty_str in msg["a"]:
            price, qty = float(price_str), float(qty_str)
            self.order_book["asks"] = [a for a in self.order_book["asks"]
                                       if a[0] != price]
            if qty > 0:
                self.order_book["asks"].append((price, qty))

        # keep sorted & trimmed (processing choice)
        self.order_book["bids"].sort(key=lambda x: x[0], reverse=True)
        self.order_book["asks"].sort(key=lambda x: x[0])
        self.order_book["bids"] = self.order_book["bids"][:200]
        self.order_book["asks"] = self.order_book["asks"][:200]

        # compute spread & maybe raise alert  (bullet: “alert when spread …”)
        best_bid, best_ask = self.order_book["bids"][0][0], self.order_book["asks"][0][0]
        sp = calculate_spread(best_bid, best_ask)

        self.spreads.append(sp)
        self.timestamps.append(datetime.now())
        self.current_mid = (best_bid + best_ask) / 2

        if abs(sp) > self.spread_threshold:
            logging.warning("ALERT – spread %.6f exceeded %.6f", sp, self.spread_threshold)

    # --------------------------------------------------------------------- #
    # 1.3  Life-cycle orchestrator (start WS, sleep, stop, analyse)
    # --------------------------------------------------------------------- #
    def run_analysis(self) -> None:
        self._load_snapshot()                       # ← REST snapshot

        twm = ThreadedWebsocketManager(API_KEY, API_SECRET)
        twm.start()
        socket_id = twm.start_depth_socket(self._process_depth, self.symbol.lower())
        logging.info("WebSocket connected for %s", self.symbol)

        time.sleep(self.duration)                   # ← 10-minute capture

        twm.stop_socket(socket_id)
        twm.stop()
        logging.info("WebSocket closed — collected %d spreads", len(self.spreads))

        self._process_results()                     # generate charts + report

    # --------------------------------------------------------------------- #
    # 1.4  Post-processing / deliverables (Visualization & Reporting bullets)
    # --------------------------------------------------------------------- #
    def _process_results(self) -> None:
        if not self.spreads:
            logging.warning("No data collected — aborting analysis")
            return

        widening = detect_spread_widening(self.spreads, self.widening_threshold)
        recovery = calculate_recovery_time(
            self.timestamps, self.spreads, widening, self.spread_threshold
        )
        fake_w   = detect_fake_walls(self.order_book, self.volume_threshold)

        plot_spread_analysis(self.timestamps, self.spreads, widening, self.spread_threshold)
        plot_order_book_depth(self.order_book, self.current_mid)
        plot_fake_wall_detection(self.order_book, fake_w)

        with open("analysis_report.txt", "w") as fp:
            fp.write(
                generate_analysis_report(self.spreads, widening, recovery, fake_w)
            )
        logging.info("Outputs ready: analysis_report.txt + PNG charts.")


if __name__ == "__main__":
    OrderBookAnalyzer(duration=600).run_analysis()
