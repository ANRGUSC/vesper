"""Utility methods"""

def bounded(value, minimum, maximum):
    """Returns the closest value within the specified bounds."""
    return max(minimum, min(maximum, value))
