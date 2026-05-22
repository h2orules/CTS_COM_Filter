"""
Integration test: relay_two_port mode with the default passthrough filters.

machine.UART is patched with FakeUART so no hardware is needed.
The relay coroutines run inside pytest-asyncio's event loop; we let them
spin briefly then cancel them.
"""
import asyncio
import utime
from unittest.mock import patch, MagicMock

import relay
from logger import Logger

_LOG_CFG = {"log": {"show_timestamps": False, "show_hex": False, "verbose": False}}

_PORT_A_CFG = {"uart_id": 1, "tx_pin": 1, "rx_pin": 2, "baud": 9600, "bits": 8, "parity": None, "stop": 1}
_PORT_B_CFG = {"uart_id": 2, "tx_pin": 3, "rx_pin": 4, "baud": 9600, "bits": 8, "parity": None, "stop": 1}

_CFG = {
    "port_a": _PORT_A_CFG,
    "port_b": _PORT_B_CFG,
    "log": _LOG_CFG["log"],
}


class FakeUART:
    """In-memory UART with injectable RX and readable TX."""

    def __init__(self, *args, **kwargs):
        self._rx = bytearray()
        self._tx = bytearray()

    def any(self):
        return len(self._rx)

    def read(self, n):
        data, self._rx = bytes(self._rx[:n]), self._rx[n:]
        return data or None

    def write(self, data):
        self._tx.extend(data)

    def inject_rx(self, data):
        self._rx.extend(data)

    def get_tx(self):
        data, self._tx = bytes(self._tx), bytearray()
        return data


def _make_relay_context(uart_a, uart_b):
    """Return a context-manager pair that patches relay.UART to return our fakes."""
    call_count = 0
    instances = [uart_a, uart_b]

    def _factory(*args, **kwargs):
        nonlocal call_count
        u = instances[call_count]
        call_count += 1
        return u

    return (
        patch("relay.UART", side_effect=_factory),
        patch("relay.Pin", MagicMock()),
    )


async def _run_relay_briefly(cfg, log, uart_a, uart_b, wait_s=0.06):
    """Start the relay, let it run for wait_s seconds, then cancel it."""
    ctx_uart, ctx_pin = _make_relay_context(uart_a, uart_b)
    with ctx_uart, ctx_pin:
        task = asyncio.create_task(relay.run(cfg, log))
        await asyncio.sleep(wait_s)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass


# ---- bidirectional relay tests ----

async def test_data_from_a_reaches_b(capsys):
    """Bytes injected into Port A's RX must appear in Port B's TX."""
    utime.set_mock_ms(0)
    uart_a, uart_b = FakeUART(), FakeUART()
    uart_a.inject_rx(b"hello\n")

    await _run_relay_briefly(_CFG, Logger(_LOG_CFG), uart_a, uart_b)

    assert uart_b.get_tx() == b"hello\n"


async def test_data_from_b_reaches_a(capsys):
    """Bytes injected into Port B's RX must appear in Port A's TX."""
    utime.set_mock_ms(0)
    uart_a, uart_b = FakeUART(), FakeUART()
    uart_b.inject_rx(b"world\n")

    await _run_relay_briefly(_CFG, Logger(_LOG_CFG), uart_a, uart_b)

    assert uart_a.get_tx() == b"world\n"


async def test_bidirectional_simultaneous(capsys):
    """Both directions relay independently in the same run."""
    utime.set_mock_ms(0)
    uart_a, uart_b = FakeUART(), FakeUART()
    uart_a.inject_rx(b"ping\n")
    uart_b.inject_rx(b"pong\n")

    await _run_relay_briefly(_CFG, Logger(_LOG_CFG), uart_a, uart_b)

    assert uart_b.get_tx() == b"ping\n"
    assert uart_a.get_tx() == b"pong\n"


async def test_multiple_lines_relayed(capsys):
    """Multiple complete lines are all forwarded."""
    utime.set_mock_ms(0)
    uart_a, uart_b = FakeUART(), FakeUART()
    uart_a.inject_rx(b"line1\nline2\nline3\n")

    await _run_relay_briefly(_CFG, Logger(_LOG_CFG), uart_a, uart_b)

    assert uart_b.get_tx() == b"line1\nline2\nline3\n"


async def test_relay_logs_a_to_b_traffic(capsys):
    """The passthrough filter must log A→B traffic to the terminal."""
    utime.set_mock_ms(0)
    uart_a, uart_b = FakeUART(), FakeUART()
    uart_a.inject_rx(b"logged\n")

    await _run_relay_briefly(_CFG, Logger(_LOG_CFG), uart_a, uart_b)

    out = capsys.readouterr().out
    assert "A→B" in out
    assert "logged" in out


async def test_relay_logs_b_to_a_traffic(capsys):
    """The passthrough filter must log B→A traffic to the terminal."""
    utime.set_mock_ms(0)
    uart_a, uart_b = FakeUART(), FakeUART()
    uart_b.inject_rx(b"response\n")

    await _run_relay_briefly(_CFG, Logger(_LOG_CFG), uart_a, uart_b)

    out = capsys.readouterr().out
    assert "B→A" in out
    assert "response" in out


async def test_no_data_produces_no_relay(capsys):
    """With no injected data neither UART's TX should receive anything."""
    utime.set_mock_ms(0)
    uart_a, uart_b = FakeUART(), FakeUART()

    await _run_relay_briefly(_CFG, Logger(_LOG_CFG), uart_a, uart_b)

    assert uart_a.get_tx() == b""
    assert uart_b.get_tx() == b""
