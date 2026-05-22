import json

_DEFAULTS = {
    "mode": "relay_two_port",
    "port_a": {
        "uart_id": 1,
        "tx_pin": 1,
        "rx_pin": 2,
        "baud": 9600,
        "bits": 8,
        "parity": None,
        "stop": 1,
    },
    "port_b": {
        "uart_id": 2,
        "tx_pin": 3,
        "rx_pin": 4,
        "baud": 9600,
        "bits": 8,
        "parity": None,
        "stop": 1,
    },
    "log": {
        "show_timestamps": True,
        "show_hex": False,
        "verbose": False,
    },
}

_REQUIRED_PORT_KEYS = ("uart_id", "tx_pin", "rx_pin", "baud", "bits", "stop")


def _merge(base, override):
    result = {}
    for k, v in base.items():
        if k in override:
            if isinstance(v, dict) and isinstance(override[k], dict):
                result[k] = _merge(v, override[k])
            else:
                result[k] = override[k]
        else:
            result[k] = v
    for k in override:
        if k not in result:
            result[k] = override[k]
    return result


def _validate_port(name, port):
    for key in _REQUIRED_PORT_KEYS:
        if key not in port:
            raise ValueError(f"config: {name}.{key} is required")
    if port["bits"] not in (5, 6, 7, 8):
        raise ValueError(f"config: {name}.bits must be 5-8, got {port['bits']}")
    if port["stop"] not in (1, 2):
        raise ValueError(f"config: {name}.stop must be 1 or 2, got {port['stop']}")
    if port.get("parity") not in (None, 0, 1):
        raise ValueError(f"config: {name}.parity must be null, 0 (even), or 1 (odd)")


def load(path="/settings.json"):
    try:
        with open(path) as f:
            user = json.load(f)
    except OSError:
        user = {}

    cfg = _merge(_DEFAULTS, user)
    _validate_port("port_a", cfg["port_a"])
    _validate_port("port_b", cfg["port_b"])

    valid_modes = ("relay_two_port", "usb_bridge")
    if cfg["mode"] not in valid_modes:
        raise ValueError(f"config: mode must be one of {valid_modes}, got '{cfg['mode']}'")

    return cfg
