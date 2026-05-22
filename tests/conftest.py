"""
Configure sys.path so that:
  1. tests/stubs/ shadows MicroPython-only modules (machine, utime, uasyncio)
  2. src/ makes the device source importable

Stubs must come before src so that `import machine` inside relay.py finds
the stub rather than any real module.
"""
from pathlib import Path
import sys
import pytest

_TESTS = Path(__file__).parent
_ROOT = _TESTS.parent

for _p in [str(_TESTS / "stubs"), str(_ROOT / "src")]:
    if _p not in sys.path:
        sys.path.insert(0, _p)


@pytest.fixture(autouse=True)
def reset_mock_time():
    """Ensure utime mock is cleared before and after every test."""
    import utime
    utime.clear_mock()
    yield
    utime.clear_mock()
