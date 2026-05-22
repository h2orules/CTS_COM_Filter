import utime


class LineBuffer:
    def __init__(self, max_size=512, flush_timeout_ms=100):
        self._max_size = max_size
        self._timeout_ms = flush_timeout_ms
        self._buf = bytearray()
        self._last_feed_ms = utime.ticks_ms()

    def feed(self, data):
        lines = []
        now = utime.ticks_ms()

        if data:
            self._buf.extend(data)
            self._last_feed_ms = now

        # Split on newlines, keeping the delimiter with the line
        while True:
            idx = self._buf.find(b"\n")
            if idx == -1:
                break
            lines.append(bytes(self._buf[: idx + 1]))
            del self._buf[: idx + 1]

        # Overflow flush: emit the whole buffer even without a newline
        if len(self._buf) >= self._max_size:
            lines.append(bytes(self._buf))
            self._buf = bytearray()
            return lines

        # Timeout flush: emit a partial line if no new data has arrived
        if self._buf and utime.ticks_diff(now, self._last_feed_ms) >= self._timeout_ms:
            lines.append(bytes(self._buf))
            self._buf = bytearray()

        return lines

    def reset(self):
        self._buf = bytearray()
        self._last_feed_ms = utime.ticks_ms()
