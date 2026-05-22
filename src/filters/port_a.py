from filters.base import FilterBase

# Module-level logger reference — injected by relay.py at startup
_logger = None


def set_logger(log):
    global _logger
    _logger = log


class PassthroughLogFilter(FilterBase):
    """Logs every line from Port A and passes it through unchanged."""

    def process_line(self, line, source):
        if _logger:
            _logger.log(line, source)
        return line


# A→B filter chain. Add or replace entries here to transform Port A traffic.
PORT_A_FILTERS = [
    PassthroughLogFilter(),
]
