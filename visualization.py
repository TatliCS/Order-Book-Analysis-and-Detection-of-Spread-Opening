"""
Produce publication-quality png charts required under the
“Visualization” bullet.
"""

from __future__ import annotations
from datetime import datetime
from typing import List, Tuple, Dict

import matplotlib.pyplot as plt
import numpy as np


# --------------------------------------------------------------------------- #
# Matplotlib style – single place so all charts share the same look
# --------------------------------------------------------------------------- #
def _apply_investopedia_style() -> None:
    plt.rcParams.update(
        {
            "figure.figsize": (14, 6),
            "figure.dpi": 350,
            "font.family": "DejaVu Sans",
            "axes.titlesize": 14,
            "axes.labelsize": 11,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "axes.grid": True,
            "grid.linewidth": 0.4,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "lines.linewidth": 1.8,
        }
    )


# --------------------------------------------------------------------------- #
# 1. Spread-timeline chart  (plus red marks for widening events)
# --------------------------------------------------------------------------- #
def plot_spread_analysis(
    timestamps: List[datetime],
    spreads: List[float],
    wid_flags: List[bool],
    threshold: float,
) -> None:
    _apply_investopedia_style()
    fig, ax = plt.subplots()

    t0 = timestamps[0]
    seconds = np.array([(t - t0).total_seconds() for t in timestamps])

    # 5-point rolling median to smooth noise
    med = (
        np.concatenate((np.full(4, np.median(spreads[:5])), np.convolve(spreads, np.ones(5) / 5, "valid")))
        if len(spreads) >= 5
        else spreads
    )

    ax.plot(seconds, spreads, color="#c0c0ff", linewidth=1, label="Raw spread")
    ax.plot(seconds, med, color="#1f77b4", label="5-pt median")
    ax.axhline(threshold, color="#cc0000", linestyle="--", linewidth=1.2, label="Threshold")

    # red dots = widening
    w_sec = seconds[np.where(wid_flags)]
    ax.scatter(w_sec, np.array(spreads)[np.where(wid_flags)], color="#d62728", s=20, label="Widening")

    ypad = (max(spreads) - min(spreads)) * 0.04
    ax.set_ylim(min(spreads) - ypad, max(spreads) + ypad)

    ax.set_title("BTC/USDT Spread – 10-minute capture")
    ax.set_xlabel("Seconds since start")
    ax.set_ylabel("Spread (USDT)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig("spread_analysis.png", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 2. Depth snapshot bar-chart
# --------------------------------------------------------------------------- #
def plot_order_book_depth(
    order_book: Dict[str, List[Tuple[float, float]]],
    mid_price: float | None,
) -> None:
    _apply_investopedia_style()
    fig, ax = plt.subplots()

    bids = sorted(order_book["bids"], key=lambda x: x[0])
    asks = sorted(order_book["asks"], key=lambda x: x[0])

    if not (bids and asks):
        fig.savefig("order_book_depth.png")
        plt.close(fig)
        return

    b_px, b_vol = zip(*bids)
    a_px, a_vol = zip(*asks)
    bar_w = (max(b_px + a_px) - min(b_px + a_px)) / 400

    ax.bar(b_px, b_vol, width=bar_w, color="#1f9d55", alpha=0.7, label="Bids")
    ax.bar(a_px, a_vol, width=bar_w, color="#e15759", alpha=0.7, label="Asks")

    if mid_price:
        ax.axvline(mid_price, color="#222222", linestyle="--", linewidth=1.2, label="Mid-price")

    ax.set_title("Order-Book Depth (final snapshot)")
    ax.set_xlabel("Price (USDT)")
    ax.set_ylabel("Volume (BTC)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig("order_book_depth.png", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 3. Fake-wall overlay (optional analysis)
# --------------------------------------------------------------------------- #
def plot_fake_wall_detection(
    order_book: Dict[str, List[Tuple[float, float]]],
    fake_walls: List[Tuple[str, float, float]],
) -> None:
    _apply_investopedia_style()
    fig, ax = plt.subplots()

    bids = sorted(order_book["bids"], key=lambda x: x[0])
    asks = sorted(order_book["asks"], key=lambda x: x[0])

    if not (bids and asks):
        fig.savefig("fake_wall_detection.png")
        plt.close(fig)
        return

    b_px, b_vol = zip(*bids)
    a_px, a_vol = zip(*asks)
    bar_w = (max(b_px + a_px) - min(b_px + a_px)) / 400

    ax.bar(b_px, b_vol, width=bar_w, color="#1f9d55", alpha=0.5, label="Bids")
    ax.bar(a_px, a_vol, width=bar_w, color="#e15759", alpha=0.5, label="Asks")

    for side, price, vol in fake_walls:
        col = "#1f9d55" if side == "bids" else "#e15759"
        ax.bar(price, vol, width=bar_w, color="none", edgecolor=col, linewidth=2.0)

    ax.set_title("Detected Fake Walls")
    ax.set_xlabel("Price (USDT)")
    ax.set_ylabel("Volume (BTC)")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig("fake_wall_detection.png", bbox_inches="tight")
    plt.close(fig)


# --------------------------------------------------------------------------- #
# 4. Text report generator
# --------------------------------------------------------------------------- #
def generate_analysis_report(
    spreads: List[float],
    widening_flags: List[bool],
    recovery_times: List[Tuple[datetime, float]],
    fake_walls: List[Tuple[str, float, float]],
) -> str:
    import numpy as np

    rep = [
        "Order Book Analysis Report",
        "=" * 50,
        "",
        "Spread Analysis:",
        f"Average Spread:  {np.mean(spreads):8.3f} USDT",
        f"Maximum Spread:  {np.max(spreads):8.3f} USDT",
        f"Minimum Spread:  {np.min(spreads):8.3f} USDT",
        f"Widening Events: {sum(widening_flags)}",
    ]

    if recovery_times:
        rt = np.mean([t for _, t in recovery_times])
        rep += [
            "",
            "Recovery-time Analysis:",
            f"Average recovery: {rt:.2f} s  across {len(recovery_times)} events",
        ]

    if fake_walls:
        rep += ["", "Fake-wall Detection:"]
        for side, px, vol in fake_walls:
            rep.append(f" – {side:<4} | {px:>10.2f} | {vol:>7.3f} BTC")

    return "\n".join(rep)
