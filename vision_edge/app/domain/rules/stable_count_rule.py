from typing import Sequence


def compute_stable_count(history: Sequence[int], mode: str = "median") -> int:
    """
    Compute stable count from history using specified strategy.
    
    Args:
        history: Sequence of raw counts (sliding window)
        mode: "median" (default, robust to outliers) or "mode" (most frequent)
    
    Returns:
        Stabilized count as integer.
    """
    if not history:
        return 0
    
    if mode == "median":
        return _compute_median(history)
    elif mode == "mode":
        return _compute_mode(history)
    else:
        # Fallback to median if invalid mode
        return _compute_median(history)


def _compute_median(values: Sequence[int]) -> int:
    """Compute median without numpy dependency."""
    sorted_values = sorted(values)
    n = len(sorted_values)
    mid = n // 2
    
    if n % 2 == 0:
        # Even: average of two middle values
        return (sorted_values[mid - 1] + sorted_values[mid]) // 2
    else:
        # Odd: middle value
        return sorted_values[mid]


def _compute_mode(values: Sequence[int]) -> int:
    """Compute mode (most frequent value). If tie, return smallest."""
    if not values:
        return 0
    
    # Count frequencies
    freq: dict[int, int] = {}
    for v in values:
        freq[v] = freq.get(v, 0) + 1
    
    # Find max frequency
    max_freq = max(freq.values())
    
    # Get all values with max frequency, return smallest
    modes = [k for k, v in freq.items() if v == max_freq]
    return min(modes)
