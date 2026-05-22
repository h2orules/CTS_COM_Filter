import sys
import utime

_ARROW = {"A": "A→B", "B": "B→A"}


def _escape(data):
    out = []
    for b in data:
        if 0x20 <= b < 0x7F:
            out.append(chr(b))
        elif b == 0x0D:
            out.append("\\r")
        elif b == 0x0A:
            out.append("\\n")
        elif b == 0x09:
            out.append("\\t")
        else:
            out.append("\\x{:02x}".format(b))
    return "".join(out)


def _hex_dump(data):
    return " ".join("{:02X}".format(b) for b in data)


class Logger:
    def __init__(self, cfg):
        self._ts = cfg["log"].get("show_timestamps", True)
        self._hex = cfg["log"].get("show_hex", False)
        self._verbose = cfg["log"].get("verbose", False)

    def _prefix(self):
        if self._ts:
            return "[{:07d}ms] ".format(utime.ticks_ms())
        return ""

    def log(self, data, source):
        arrow = _ARROW.get(source, source)
        prefix = self._prefix()
        sys.stdout.write("{}{}: {}\r\n".format(prefix, arrow, _escape(data)))
        if self._hex:
            sys.stdout.write("{}         hex: {}\r\n".format(prefix, _hex_dump(data)))

    def info(self, msg):
        sys.stdout.write("{}[INFO] {}\r\n".format(self._prefix(), msg))

    def debug(self, msg):
        if self._verbose:
            sys.stdout.write("{}[DBG]  {}\r\n".format(self._prefix(), msg))
