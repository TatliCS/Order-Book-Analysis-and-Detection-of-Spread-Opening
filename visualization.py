import matplotlib.pyplot as plt
import pandas as pd
from typing import List, Tuple, Dict
from datetime import datetime
import numpy as np

def plot_spread_analysis(timestamps: List[datetime], spreads: List[float], 
                        widening_events: List[bool], threshold: float):
    """
    Create a plot showing spread changes and widening events.
    
    Args:
        timestamps: List of timestamps
        spreads: List of spread values
        widening_events: List of boolean values indicating spread widening events
        threshold: Threshold line for spread widening
    """
    plt.figure(figsize=(12, 6))
    
    # Plot spread values
    plt.plot(timestamps, spreads, label='Spread', color='blue')
    
    # Plot threshold line
    plt.axhline(y=threshold, color='r', linestyle='--', label='Threshold')
    
    # Mark widening events
    widening_times = [t for t, w in zip(timestamps, widening_events) if w]
    widening_spreads = [s for s, w in zip(spreads, widening_events) if w]
    plt.scatter(widening_times, widening_spreads, color='red', 
               label='Spread Widening Events', zorder=5)
    
    plt.title('Spread Analysis Over Time')
    plt.xlabel('Time')
    plt.ylabel('Spread (USDT)')
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('spread_analysis.png')
    plt.close()

def plot_order_book_depth(order_book: Dict[str, List[Tuple[float, float]]], 
                         current_price: float):
    """
    Create a depth chart showing the order book.
    
    Args:
        order_book: Dictionary containing bid and ask orders
        current_price: Current market price
    """
    plt.figure(figsize=(12, 6))
    
    # Prepare data
    bids = order_book['bids']
    asks = order_book['asks']
    
    bid_prices = [price for price, _ in bids]
    bid_volumes = [volume for _, volume in bids]
    ask_prices = [price for price, _ in asks]
    ask_volumes = [volume for _, volume in asks]
    
    # Plot bids
    plt.bar(bid_prices, bid_volumes, width=0.1, color='green', alpha=0.6, label='Bids')
    
    # Plot asks
    plt.bar(ask_prices, ask_volumes, width=0.1, color='red', alpha=0.6, label='Asks')
    
    # Plot current price
    plt.axvline(x=current_price, color='black', linestyle='--', label='Current Price')
    
    plt.title('Order Book Depth')
    plt.xlabel('Price (USDT)')
    plt.ylabel('Volume (BTC)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('order_book_depth.png')
    plt.close()

def plot_fake_wall_detection(order_book: Dict[str, List[Tuple[float, float]]], 
                           fake_walls: List[Tuple[str, float, float]]):
    """
    Create a plot highlighting detected fake walls in the order book.
    
    Args:
        order_book: Dictionary containing bid and ask orders
        fake_walls: List of detected fake walls
    """
    plt.figure(figsize=(12, 6))
    
    # Plot all orders
    for side in ['bids', 'asks']:
        prices = [price for price, _ in order_book[side]]
        volumes = [volume for _, volume in order_book[side]]
        color = 'green' if side == 'bids' else 'red'
        plt.bar(prices, volumes, width=0.1, color=color, alpha=0.3, 
               label=f'{side.capitalize()}')
    
    # Highlight fake walls
    for side, price, volume in fake_walls:
        color = 'darkgreen' if side == 'bids' else 'darkred'
        plt.bar(price, volume, width=0.1, color=color, alpha=0.8, 
               label=f'Fake Wall ({side})')
    
    plt.title('Fake Wall Detection')
    plt.xlabel('Price (USDT)')
    plt.ylabel('Volume (BTC)')
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    
    # Save the plot
    plt.savefig('fake_wall_detection.png')
    plt.close()

def generate_analysis_report(spreads: List[float], widening_events: List[bool],
                           recovery_times: List[Tuple[datetime, float]],
                           fake_walls: List[Tuple[str, float, float]]) -> str:
    """
    Generate a text report summarizing the analysis results.
    
    Args:
        spreads: List of spread values
        widening_events: List of boolean values indicating spread widening events
        recovery_times: List of recovery time tuples
        fake_walls: List of detected fake walls
    
    Returns:
        String containing the analysis report
    """
    report = []
    report.append("Order Book Analysis Report")
    report.append("=" * 50)
    
    # Spread Analysis
    report.append("\nSpread Analysis:")
    report.append(f"Average Spread: {np.mean(spreads):.2f} USDT")
    report.append(f"Maximum Spread: {np.max(spreads):.2f} USDT")
    report.append(f"Minimum Spread: {np.min(spreads):.2f} USDT")
    report.append(f"Number of Spread Widening Events: {sum(widening_events)}")
    
    # Recovery Time Analysis
    if recovery_times:
        avg_recovery = np.mean([t for _, t in recovery_times])
        report.append(f"\nRecovery Time Analysis:")
        report.append(f"Average Recovery Time: {avg_recovery:.2f} seconds")
        report.append(f"Number of Recovery Events: {len(recovery_times)}")
    
    # Fake Wall Analysis
    if fake_walls:
        report.append(f"\nFake Wall Detection:")
        report.append(f"Number of Detected Fake Walls: {len(fake_walls)}")
        for side, price, volume in fake_walls:
            report.append(f"- {side.capitalize()} at {price:.2f} USDT with volume {volume:.4f} BTC")
    
    return "\n".join(report) 