import utime
import pytest
from logger import Logger


_CFG_TS = {"log": {"show_timestamps": True, "show_hex": False, "verbose": False}}
_CFG_NOTS = {"log": {"show_timestamps": False, "show_hex": False, "verbose": False}}
_CFG_HEX = {"log": {"show_timestamps": False, "show_hex": True, "verbose": False}}
_CFG_VERB = {"log": {"show_timestamps": False, "show_hex": False, "verbose": True}}


def test_log_a_to_b_arrow(capsys):
    utime.set_mock_ms(1500)
    Logger(_CFG_TS).log(b"hello\r\n", "A")
    out = capsys.readouterr().out
    assert "A→B" in out  # A→B
    assert "hello" in out


def test_log_b_to_a_arrow(capsys):
    utime.set_mock_ms(0)
    Logger(_CFG_NOTS).log(b"ACK\r\n", "B")
    out = capsys.readouterr().out
    assert "B→A" in out  # B→A


def test_log_timestamp_format(capsys):
    utime.set_mock_ms(42)
    Logger(_CFG_TS).log(b"x\n", "A")
    out = capsys.readouterr().out
    assert "[0000042ms]" in out


def test_log_no_timestamp(capsys):
    Logger(_CFG_NOTS).log(b"x\n", "A")
    out = capsys.readouterr().out
    assert "ms]" not in out


def test_log_escapes_non_printable(capsys):
    Logger(_CFG_NOTS).log(bytes([0x01, 0x7F, 0x80]), "A")
    out = capsys.readouterr().out
    assert "\\x01" in out
    assert "\\x7f" in out
    assert "\\x80" in out


def test_log_cr_lf_escape(capsys):
    Logger(_CFG_NOTS).log(b"hi\r\n", "A")
    out = capsys.readouterr().out
    assert "\\r" in out
    assert "\\n" in out


def test_log_tab_escape(capsys):
    Logger(_CFG_NOTS).log(b"a\tb", "A")
    out = capsys.readouterr().out
    assert "\\t" in out


def test_log_show_hex_emits_hex_line(capsys):
    Logger(_CFG_HEX).log(b"AB", "A")
    out = capsys.readouterr().out
    assert "41 42" in out  # hex for A, B


def test_log_show_hex_false_no_hex_line(capsys):
    Logger(_CFG_NOTS).log(b"AB", "A")
    out = capsys.readouterr().out
    assert "41 42" not in out


def test_info_line(capsys):
    Logger(_CFG_NOTS).info("startup complete")
    out = capsys.readouterr().out
    assert "[INFO]" in out
    assert "startup complete" in out


def test_debug_emits_when_verbose(capsys):
    Logger(_CFG_VERB).debug("internal state")
    out = capsys.readouterr().out
    assert "[DBG]" in out
    assert "internal state" in out


def test_debug_silent_when_not_verbose(capsys):
    Logger(_CFG_NOTS).debug("should not appear")
    out = capsys.readouterr().out
    assert out == ""
