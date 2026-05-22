# CTS_COM_Filter — RS232 Logger / Relay

An RS232 bidirectional relay and logger running MicroPython on the Seeed Studio XIAO ESP32-S3.
The device sits between two RS232 serial devices, relays bytes in both directions, and streams a timestamped log of all traffic to the USB terminal.

---

## Hardware

### Components

- Seeed Studio XIAO ESP32-S3
- MAX3232 level-shifter IC (converts 3.3 V logic ↔ RS232 ±12 V)
- Two DB9 connectors (male or female depending on target devices)
- 4 × 100 nF capacitors (MAX3232 charge pump — C1+, C1−, C2+, C2−)

### Wiring

```text
XIAO ESP32-S3         MAX3232                DB9 Port A
─────────────         ──────────────         ─────────────────
D0 / GPIO1  ──TX──►  T1IN  T1OUT ──RS232──►  Pin 3 (RXD)
D1 / GPIO2  ◄─RX──   R1OUT  R1IN ◄─RS232──   Pin 2 (TXD)
                                              Pin 5 (GND) ─┐
                                                            │
XIAO ESP32-S3         MAX3232                DB9 Port B    │
─────────────         ──────────────         ──────────────┤
D2 / GPIO3  ──TX──►  T2IN  T2OUT ──RS232──►  Pin 3 (RXD)  │
D3 / GPIO4  ◄─RX──   R2OUT  R2IN ◄─RS232──   Pin 2 (TXD)  │
                                              Pin 5 (GND) ─┘
                                                            │
3V3 ──────────────►  VCC                                   │
GND ──────────────►  GND ◄─────────────────────────────────┘
```

**DB9 pin convention:**

- Pin 2 = RXD, Pin 3 = TXD, Pin 5 = GND for DTE devices (PCs, controllers).
- Swap pins 2 & 3 if connecting to a DCE device (modem, some sensors).

---

## Prerequisites

### 1. Flash MicroPython firmware

Download the XIAO ESP32-S3 MicroPython firmware (v1.23 or later) from
[https://micropython.org/download/XIAO_ESP32S3/](https://micropython.org/download/XIAO_ESP32S3/)

Flash it using `esptool`:

```bash
pip install esptool
# Put the XIAO into download mode: hold BOOT, press RESET, release BOOT
esptool.py --chip esp32s3 --port /dev/tty.usbmodem* erase_flash
esptool.py --chip esp32s3 --port /dev/tty.usbmodem* write_flash -z 0x0 XIAO_ESP32S3-*.bin
```

### 2. Install VS Code + MicroPico extension

1. Install [Visual Studio Code](https://code.visualstudio.com/)
2. Open this project folder in VS Code — it will prompt to install the recommended **MicroPico** extension (`paulober.pico-w-go`)
3. Accept the recommendation, or install manually from the Extensions panel

---

## Deployment

1. Connect the XIAO ESP32-S3 via USB.
2. VS Code / MicroPico auto-detects the device (status bar shows the port).
3. **Upload:** `Ctrl+Shift+U` — syncs the `src/` folder to the device filesystem.
4. **Run:** Reset the device (press the physical RESET button or use the MicroPico "Reset" command). `main.py` runs automatically on boot.
5. **Monitor:** Open the MicroPico terminal (`Ctrl+Shift+P` → *MicroPico: Toggle REPL*) to see live log output.

### Updating and re-deploying

Edit any file under `src/`, then press `Ctrl+Shift+U` again. Reset the device to pick up changes.

---

## Log Output

All relayed traffic appears in the terminal with the source port and direction:

```text
[0000123ms] [INFO] RS232 Logger/Relay starting
[0000124ms] [INFO] Mode: relay_two_port
[0000125ms] [INFO] Port A: UART1 TX=GPIO1 RX=GPIO2 9600bd
[0000126ms] [INFO] Port B: UART2 TX=GPIO3 RX=GPIO4 9600bd
[0000127ms] [INFO] Relay running — Ctrl+C to drop to REPL
[0001500ms] A→B: Hello from device A\r\n
[0001510ms] B→A: ACK\r\n
```

Non-printable bytes are shown as `\xNN` escapes. Set `"show_hex": true` in `settings.json` for an additional hex dump line per received chunk.

---

## Configuration (`src/settings.json`)

| Key                  | Default             | Description                                              |
| -------------------- | ------------------- | -------------------------------------------------------- |
| `mode`               | `"relay_two_port"`  | Active operating mode (`relay_two_port` or `usb_bridge`) |
| `port_a.uart_id`     | `1`                 | MicroPython UART number for Port A                       |
| `port_a.tx_pin`      | `1`                 | GPIO pin number for Port A TX                            |
| `port_a.rx_pin`      | `2`                 | GPIO pin number for Port A RX                            |
| `port_a.baud`        | `9600`              | Baud rate                                                |
| `port_a.bits`        | `8`                 | Data bits (5–8)                                          |
| `port_a.parity`      | `null`              | `null` = none, `0` = even, `1` = odd                    |
| `port_a.stop`        | `1`                 | Stop bits (1 or 2)                                       |
| `port_b.*`           | (same)              | Same keys for Port B                                     |
| `log.show_timestamps`| `true`              | Prefix each log line with milliseconds since boot        |
| `log.show_hex`       | `false`             | Also emit a hex dump for each received chunk             |
| `log.verbose`        | `false`             | Enable `[DBG]` lines for UART event tracing              |

Edit `src/settings.json`, re-deploy with `Ctrl+Shift+U`, then reset the device.

---

## Adding Filters / Transforms

Filters for each direction live in two files:

| File                                             | Direction | Edit to…                                  |
| ------------------------------------------------ | --------- | ----------------------------------------- |
| [src/filters/port_a.py](src/filters/port_a.py)  | A → B     | Transform or drop lines sent from Port A  |
| [src/filters/port_b.py](src/filters/port_b.py)  | B → A     | Transform or drop lines sent from Port B  |

Each file exposes a `PORT_x_FILTERS` list. Add a subclass of `FilterBase` to the list:

```python
from filters.base import FilterBase

class StripTimestamp(FilterBase):
    def matches(self, line):
        return line.startswith(b"TS:")   # only run on lines that start with "TS:"

    def process_line(self, line, source):
        # Return None to drop, or return bytes to forward (possibly modified)
        return line[10:]                 # strip first 10 bytes and pass through

PORT_A_FILTERS = [
    PassthroughLogFilter(),   # keep the logger
    StripTimestamp(),         # add your filter after
]
```

Filters run in list order. If `process_line` returns `None` the line is dropped and no further filters run.

---

## Modes

| Mode              | Description                                                                          |
| ----------------- | ------------------------------------------------------------------------------------ |
| `relay_two_port`  | **Current.** Relay and log between Port A (UART1) and Port B (UART2) via GPIO + MAX3232 |
| `usb_bridge`      | **Future stub.** Relay between Port A (UART1) and a USB CDC virtual COM port        |

Switch modes by editing `"mode"` in `src/settings.json`.

---

## Debugging

MicroPython does not support VS Code breakpoint debugging. The workflow is:

1. Set `"verbose": true` in `settings.json` for detailed UART event lines.
2. Observe the live log stream in the MicroPico terminal.
3. Press `Ctrl+C` in the terminal at any time to interrupt the relay loop and drop to a MicroPython REPL where you can inspect state interactively.
4. Re-run with `import main` or reset the device.

### Loopback test (no RS232 hardware)

Wire GPIO1 ↔ GPIO4 and GPIO3 ↔ GPIO2 directly (3.3 V logic — do **not** use the MAX3232 for this).
In the REPL, write to UART1 and observe the relay log:

```python
from machine import UART, Pin
u = UART(1, 9600, tx=Pin(1), rx=Pin(2))
u.write(b"test\r\n")
```

You should see `A→B: test\r\n` and `B→A: test\r\n` in the log.

---

## Project Layout

```text
esp32_rs232_logger/
├── .vscode/
│   ├── settings.json        # MicroPico sync folder config
│   └── extensions.json      # Recommends paulober.pico-w-go
├── src/                     # Synced to device root filesystem
│   ├── main.py              # Boot entry point
│   ├── settings.json        # Runtime config
│   ├── config.py            # Config loader with defaults + validation
│   ├── logger.py            # Timestamped USB terminal logger
│   ├── line_buffer.py       # Byte accumulator → line splitter
│   ├── relay.py             # relay_two_port mode (uasyncio)
│   ├── usb_bridge.py        # usb_bridge mode stub
│   └── filters/
│       ├── __init__.py      # run_filter_chain() helper
│       ├── base.py          # FilterBase ABC
│       ├── port_a.py        # A→B filter chain (edit to customise)
│       └── port_b.py        # B→A filter chain (edit to customise)
└── README.md
```
