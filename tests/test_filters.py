import utime
import pytest
from filters import run_filter_chain
from filters.base import FilterBase
from logger import Logger


# ---- helpers ----

class _Identity(FilterBase):
    def process_line(self, line, source):
        return line


class _Upper(FilterBase):
    def process_line(self, line, source):
        return line.upper()


class _Dropper(FilterBase):
    def process_line(self, line, source):
        return None


class _SelectiveDrop(FilterBase):
    """Drops lines that start with b'DROP'."""
    def matches(self, line):
        return line.startswith(b"DROP")

    def process_line(self, line, source):
        return None


class _CallCounter(FilterBase):
    def __init__(self):
        self.calls = 0

    def process_line(self, line, source):
        self.calls += 1
        return line


# ---- FilterBase ----

def test_filter_base_matches_returns_true_by_default():
    assert _Identity().matches(b"anything") is True


def test_filter_base_process_line_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        FilterBase().process_line(b"x", "A")


# ---- run_filter_chain ----

def test_chain_empty_returns_line():
    assert run_filter_chain(b"hello\n", "A", []) == b"hello\n"


def test_chain_single_identity():
    assert run_filter_chain(b"hello\n", "A", [_Identity()]) == b"hello\n"


def test_chain_transform():
    result = run_filter_chain(b"hello\n", "A", [_Upper()])
    assert result == b"HELLO\n"


def test_chain_drop_returns_none():
    assert run_filter_chain(b"hello\n", "A", [_Dropper()]) is None


def test_chain_drop_stops_subsequent_filters():
    counter = _CallCounter()
    result = run_filter_chain(b"hello\n", "A", [_Dropper(), counter])
    assert result is None
    assert counter.calls == 0


def test_chain_chained_transforms():
    result = run_filter_chain(b"hello\n", "A", [_Upper(), _Identity()])
    assert result == b"HELLO\n"


def test_chain_selective_match_drops():
    result = run_filter_chain(b"DROP this\n", "A", [_SelectiveDrop()])
    assert result is None


def test_chain_selective_match_passes_non_matching():
    result = run_filter_chain(b"keep this\n", "A", [_SelectiveDrop()])
    assert result == b"keep this\n"


def test_chain_source_label_passed_through():
    received = []

    class CapturingFilter(FilterBase):
        def process_line(self, line, source):
            received.append(source)
            return line

    run_filter_chain(b"x\n", "B", [CapturingFilter()])
    assert received == ["B"]


# ---- PassthroughLogFilter (port_a / port_b) ----

_LOG_CFG = {"log": {"show_timestamps": False, "show_hex": False, "verbose": False}}


def test_port_a_passthrough_returns_line_unchanged(capsys):
    import filters.port_a as pa
    pa.set_logger(Logger(_LOG_CFG))
    result = pa.PORT_A_FILTERS[0].process_line(b"test\n", "A")
    assert result == b"test\n"


def test_port_a_passthrough_logs_to_terminal(capsys):
    import filters.port_a as pa
    pa.set_logger(Logger(_LOG_CFG))
    pa.PORT_A_FILTERS[0].process_line(b"hello\n", "A")
    out = capsys.readouterr().out
    assert "A→B" in out
    assert "hello" in out


def test_port_b_passthrough_returns_line_unchanged(capsys):
    import filters.port_b as pb
    pb.set_logger(Logger(_LOG_CFG))
    result = pb.PORT_B_FILTERS[0].process_line(b"resp\n", "B")
    assert result == b"resp\n"


def test_port_b_passthrough_logs_to_terminal(capsys):
    import filters.port_b as pb
    pb.set_logger(Logger(_LOG_CFG))
    pb.PORT_B_FILTERS[0].process_line(b"resp\n", "B")
    out = capsys.readouterr().out
    assert "B→A" in out
    assert "resp" in out


def test_passthrough_with_no_logger_set_does_not_crash():
    import filters.port_a as pa
    pa.set_logger(None)
    result = pa.PORT_A_FILTERS[0].process_line(b"x\n", "A")
    assert result == b"x\n"
