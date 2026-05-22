import uasyncio as asyncio
from machine import UART, Pin
from line_buffer import LineBuffer
from filters import run_filter_chain
import filters.port_a as port_a_mod
import filters.port_b as port_b_mod


def _make_uart(port_cfg):
    parity = port_cfg["parity"]
    return UART(
        port_cfg["uart_id"],
        baudrate=port_cfg["baud"],
        bits=port_cfg["bits"],
        parity=parity,
        stop=port_cfg["stop"],
        tx=Pin(port_cfg["tx_pin"]),
        rx=Pin(port_cfg["rx_pin"]),
        rxbuf=1024,
    )


async def _relay_direction(src_uart, dst_uart, source_label, buf, filters, log):
    log.debug("relay direction {} started".format(source_label))
    while True:
        n = src_uart.any()
        if n:
            raw = src_uart.read(n)
            if raw:
                log.debug("{} {} bytes".format(source_label, len(raw)))
                for line in buf.feed(raw):
                    out = run_filter_chain(line, source_label, filters)
                    if out is not None:
                        dst_uart.write(out)
        else:
            # Pass empty feed so LineBuffer can check for timeout-based flush
            for line in buf.feed(b""):
                out = run_filter_chain(line, source_label, filters)
                if out is not None:
                    dst_uart.write(out)

        await asyncio.sleep_ms(1)


async def run(cfg, log):
    log.info("relay_two_port mode initialising")

    uart_a = _make_uart(cfg["port_a"])
    uart_b = _make_uart(cfg["port_b"])

    log.info(
        "Port A: UART{} TX=GPIO{} RX=GPIO{} {}bd".format(
            cfg["port_a"]["uart_id"],
            cfg["port_a"]["tx_pin"],
            cfg["port_a"]["rx_pin"],
            cfg["port_a"]["baud"],
        )
    )
    log.info(
        "Port B: UART{} TX=GPIO{} RX=GPIO{} {}bd".format(
            cfg["port_b"]["uart_id"],
            cfg["port_b"]["tx_pin"],
            cfg["port_b"]["rx_pin"],
            cfg["port_b"]["baud"],
        )
    )

    # Inject logger into filter modules so they can emit log lines
    port_a_mod.set_logger(log)
    port_b_mod.set_logger(log)

    buf_a = LineBuffer()
    buf_b = LineBuffer()

    log.info("Relay running — Ctrl+C to drop to REPL")

    await asyncio.gather(
        _relay_direction(uart_a, uart_b, "A", buf_a, port_a_mod.PORT_A_FILTERS, log),
        _relay_direction(uart_b, uart_a, "B", buf_b, port_b_mod.PORT_B_FILTERS, log),
    )
