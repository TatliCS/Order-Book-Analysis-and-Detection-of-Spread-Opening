import numpy as np
from typing import Dict, List, Tuple
from datetime import datetime

def calculate_spread(bid_price: float, ask_price: float) -> float:
    """Calculate the spread between bid and ask prices."""
    return ask_price - bid_price

def detect_spread_widening(spreads: List[float], threshold: float, window_size: int = 10) -> List[bool]:
    """
    Detect spread widening events using a rolling window approach.
    
    Args:
        spreads: List of spread values
        threshold: Threshold for spread widening detection
        window_size: Size of the rolling window for baseline calculation
    
    Returns:
        List of boolean values indicating spread widening events
    """
    if len(spreads) < window_size:
        return [False] * len(spreads)
    
    widening_events = []
    for i in range(len(spreads)):
        if i < window_size:
            widening_events.append(False)
            continue
            
        baseline = np.mean(spreads[i-window_size:i])
        current_spread = spreads[i]
        
        # Detect if current spread is significantly wider than baseline
        widening_events.append(current_spread > baseline * (1 + threshold))
    
    return widening_events

def calculate_recovery_time(spreads: List[float], widening_events: List[bool], 
                          threshold: float) -> List[Tuple[datetime, float]]:
    """
    Calculate the time taken for spread to recover after widening events.
    
    Args:
        spreads: List of spread values
        widening_events: List of boolean values indicating spread widening events
        threshold: Threshold for considering spread as recovered
    
    Returns:
        List of tuples containing (event_time, recovery_time_in_seconds)
    """
    recovery_times = []
    in_widening = False
    start_time = None
    
    for i in range(len(spreads)):
        if widening_events[i] and not in_widening:
            in_widening = True
            start_time = datetime.now()
        elif not widening_events[i] and in_widening:
            if spreads[i] <= threshold:
                in_widening = False
                if start_time:
                    recovery_time = (datetime.now() - start_time).total_seconds()
                    recovery_times.append((start_time, recovery_time))
    
    return recovery_times

def detect_fake_walls(order_book: Dict[str, List[Tuple[float, float]]], 
                     volume_threshold: float = 100.0) -> List[Tuple[str, float, float]]:
    """
    Detect potential fake walls in the order book.
    
    Args:
        order_book: Dictionary containing bid and ask orders
        volume_threshold: Threshold for considering a wall as significant
    
    Returns:
        List of tuples containing (side, price, volume) of detected fake walls
    """
    fake_walls = []
    
    for side in ['bids', 'asks']:
        orders = order_book[side]
        for price, volume in orders:
            if volume > volume_threshold:
                # Check if this is an unusually large order
                avg_volume = np.mean([v for _, v in orders])
                if volume > avg_volume * 3:  # Volume is 3x larger than average
                    fake_walls.append((side, price, volume))
    
    return fake_walls

def calculate_order_book_imbalance(order_book: Dict[str, List[Tuple[float, float]]]) -> float:
    """
    Calculate the imbalance between bid and ask sides of the order book.
    
    Args:
        order_book: Dictionary containing bid and ask orders
    
    Returns:
        Imbalance ratio (positive means more bids, negative means more asks)
    """
    bid_volume = sum(volume for _, volume in order_book['bids'])
    ask_volume = sum(volume for _, volume in order_book['asks'])
    
    if ask_volume == 0:
        return 0
    
    return (bid_volume - ask_volume) / (bid_volume + ask_volume) 