"""Stub for MicroPython machine module."""


class Pin:
    def __init__(self, id, *args, **kwargs):
        self.id = id


class UART:
    """
    Minimal UART stub. Tests inject bytes via inject_rx() and
    drain the TX side via get_tx().
    """

    def __init__(self, id, *args, **kwargs):
        self.id = id
        self._rx = bytearray()
        self._tx = bytearray()

    def any(self):
        return len(self._rx)

    def read(self, n=None):
        if n is None:
            data, self._rx = bytes(self._rx), bytearray()
        else:
            data, self._rx = bytes(self._rx[:n]), self._rx[n:]
        return data or None

    def write(self, data):
        self._tx.extend(data)

    # ---- test helpers ----

    def inject_rx(self, data):
        """Simulate bytes arriving on the RX line."""
        self._rx.extend(data)

    def get_tx(self):
        """Drain and return everything written to TX."""
        data, self._tx = bytes(self._tx), bytearray()
        return data
