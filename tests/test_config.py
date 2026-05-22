import json
import pytest
import config


def test_load_returns_defaults_when_file_missing(tmp_path):
    cfg = config.load(str(tmp_path / "no_such_file.json"))
    assert cfg["mode"] == "relay_two_port"
    assert cfg["port_a"]["baud"] == 9600
    assert cfg["port_b"]["uart_id"] == 2
    assert cfg["log"]["show_timestamps"] is True


def test_load_merges_top_level_override(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"mode": "usb_bridge"}))
    cfg = config.load(str(p))
    assert cfg["mode"] == "usb_bridge"
    # unmentioned keys still carry defaults
    assert cfg["port_a"]["baud"] == 9600


def test_load_merges_nested_override(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"port_a": {"baud": 115200}}))
    cfg = config.load(str(p))
    assert cfg["port_a"]["baud"] == 115200
    assert cfg["port_a"]["tx_pin"] == 1   # default preserved


def test_load_merges_log_override(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"log": {"show_hex": True, "verbose": True}}))
    cfg = config.load(str(p))
    assert cfg["log"]["show_hex"] is True
    assert cfg["log"]["verbose"] is True
    assert cfg["log"]["show_timestamps"] is True  # untouched default


def test_load_invalid_mode_raises(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"mode": "unknown_mode"}))
    with pytest.raises(ValueError, match="mode"):
        config.load(str(p))


def test_load_invalid_bits_raises(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"port_a": {"bits": 9}}))
    with pytest.raises(ValueError, match="bits"):
        config.load(str(p))


def test_load_invalid_stop_raises(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"port_b": {"stop": 3}}))
    with pytest.raises(ValueError, match="stop"):
        config.load(str(p))


def test_load_invalid_parity_raises(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"port_a": {"parity": 5}}))
    with pytest.raises(ValueError, match="parity"):
        config.load(str(p))


def test_load_null_parity_is_valid(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"port_a": {"parity": None}}))
    cfg = config.load(str(p))
    assert cfg["port_a"]["parity"] is None


def test_load_even_parity_is_valid(tmp_path):
    p = tmp_path / "s.json"
    p.write_text(json.dumps({"port_a": {"parity": 0}}))
    cfg = config.load(str(p))
    assert cfg["port_a"]["parity"] == 0
