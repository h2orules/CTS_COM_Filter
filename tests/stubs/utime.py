"""Stub for MicroPython utime module."""
import time

_mock_ms = None


def ticks_ms():
    if _mock_ms is not None:
        return _mock_ms
    return int(time.monotonic() * 1000) & 0x7FFFFFFF


def ticks_diff(new, old):
    """Signed difference accounting for 30-bit wraparound."""
    return (new - old) & 0x7FFFFFFF


# ---- test helpers ----

def set_mock_ms(val):
    global _mock_ms
    _mock_ms = val


def clear_mock():
    global _mock_ms
    _mock_ms = None
