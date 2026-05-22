class FilterBase:
    def matches(self, line):
        """Return True to run process_line on this line. Override for selection criteria."""
        return True

    def process_line(self, line, source):
        """
        Transform a line. Return bytes to forward, or None to drop entirely.
        line:   bytes — complete line (may include trailing \\r\\n)
        source: 'A' or 'B'
        """
        raise NotImplementedError
