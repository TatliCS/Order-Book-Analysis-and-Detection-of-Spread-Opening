"""
Utility functions used by both the WebSocket callback and the
post-processing stage.

Each helper maps to one line of the *Spread Analysis* / *Optional Analysis*
requirements.
"""

from __future__ import annotations
from datetime import datetime
from typing import Dict, List, Tuple

import numpy as np


# --------------------------------------------------------------------------- #
# Spread-related helpers  (assignment: “analyze spread … detect widening”)
# --------------------------------------------------------------------------- #
def calculate_spread(bid: float, ask: float) -> float:
    """ask – bid in USDT (can be negative if bid > ask)."""
    return ask - bid


def detect_spread_widening(
    spreads: List[float],
    threshold: float,
    window_size: int = 10,
) -> List[bool]:
    """
    Return boolean list – True when current spread >
    rolling-mean × (1 + threshold).
    Satisfies: “alert when the spread goes above a certain threshold”.
    """
    if len(spreads) < window_size:
        return [False] * len(spreads)

    flags: List[bool] = []
    for i, s in enumerate(spreads):
        if i < window_size:
            flags.append(False)
            continue

        baseline = np.mean(spreads[i - window_size : i])
        flags.append(s > baseline * (1 + threshold))
    return flags


def calculate_recovery_time(
    timestamps: List[datetime],
    spreads: List[float],
    widening: List[bool],
    thr: float,
) -> List[Tuple[datetime, float]]:
    """
    For every widening event measure seconds until spread shrinks back
    to <= |thr|  (assignment: “calculate the time it takes to return
    to normal levels”).
    """
    rec: List[Tuple[datetime, float]] = []
    in_evt, start_t = False, None

    for t, s, flag in zip(timestamps, spreads, widening):
        if flag and not in_evt:
            start_t, in_evt = t, True
        elif in_evt and abs(s) <= thr:
            rec.append((start_t, (t - start_t).total_seconds()))
            in_evt = False
    return rec


# --------------------------------------------------------------------------- #
# Fake-wall detection  (Optional Analysis block)
# --------------------------------------------------------------------------- #
def detect_fake_walls(
    order_book: Dict[str, List[Tuple[float, float]]],
    volume_threshold: float = 100.0,
) -> List[Tuple[str, float, float]]:
    """
    Flag orders whose volume is both:
      • > volume_threshold
      • > 3× average volume on the same side
    """
    fake: List[Tuple[str, float, float]] = []
    for side in ["bids", "asks"]:
        vols = np.array([v for _, v in order_book[side]])
        if vols.size == 0:
            continue
        avg = vols.mean()
        for price, vol in order_book[side]:
            if vol > volume_threshold and vol > avg * 3:
                fake.append((side, price, vol))
    return fake
