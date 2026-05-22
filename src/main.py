import uasyncio as asyncio
import config
import relay
import usb_bridge
from logger import Logger

MODES = {
    "relay_two_port": relay.run,
    "usb_bridge": usb_bridge.run,
}


def main():
    try:
        cfg = config.load()
    except Exception as e:
        # Print raw — Logger not available yet
        print("[BOOT] Config error: {}".format(e))
        return

    log = Logger(cfg)
    log.info("RS232 Logger/Relay starting")
    log.info("Mode: {}".format(cfg["mode"]))

    runner = MODES.get(cfg["mode"])
    if runner is None:
        log.info("Unknown mode '{}' — halting".format(cfg["mode"]))
        return

    try:
        asyncio.run(runner(cfg, log))
    except KeyboardInterrupt:
        log.info("Interrupted — dropping to REPL")


main()
