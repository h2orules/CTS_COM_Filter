import utime
import pytest
from line_buffer import LineBuffer


def test_complete_line_lf():
    lines = LineBuffer().feed(b"hello\n")
    assert lines == [b"hello\n"]


def test_complete_line_crlf():
    lines = LineBuffer().feed(b"hello\r\n")
    assert lines == [b"hello\r\n"]


def test_multiple_lines_single_feed():
    lines = LineBuffer().feed(b"a\nb\nc\n")
    assert lines == [b"a\n", b"b\n", b"c\n"]


def test_partial_line_not_flushed_immediately():
    utime.set_mock_ms(0)
    buf = LineBuffer(flush_timeout_ms=100)
    lines = buf.feed(b"partial")
    assert lines == []


def test_partial_line_flushed_on_timeout():
    utime.set_mock_ms(0)
    buf = LineBuffer(flush_timeout_ms=100)
    buf.feed(b"partial")
    utime.set_mock_ms(200)          # advance past timeout
    lines = buf.feed(b"")           # empty feed triggers timeout check
    assert lines == [b"partial"]


def test_partial_line_not_flushed_before_timeout():
    utime.set_mock_ms(0)
    buf = LineBuffer(flush_timeout_ms=100)
    buf.feed(b"partial")
    utime.set_mock_ms(50)           # only halfway to timeout
    lines = buf.feed(b"")
    assert lines == []


def test_overflow_flush():
    buf = LineBuffer(max_size=10)
    lines = buf.feed(b"a" * 10)     # exactly at limit, no newline
    assert lines == [b"a" * 10]


def test_overflow_does_not_flush_below_limit():
    buf = LineBuffer(max_size=10)
    lines = buf.feed(b"a" * 9)
    assert lines == []


def test_incremental_line_assembly():
    buf = LineBuffer()
    assert buf.feed(b"hel") == []
    assert buf.feed(b"lo") == []
    assert buf.feed(b"\n") == [b"hello\n"]


def test_line_then_partial():
    buf = LineBuffer()
    lines = buf.feed(b"done\nstill_going")
    assert lines == [b"done\n"]


def test_reset_clears_buffer():
    utime.set_mock_ms(0)
    buf = LineBuffer(flush_timeout_ms=100)
    buf.feed(b"partial")
    buf.reset()
    utime.set_mock_ms(200)
    lines = buf.feed(b"")
    assert lines == []              # cleared, nothing to flush


def test_empty_input_no_output():
    buf = LineBuffer()
    assert buf.feed(b"") == []
