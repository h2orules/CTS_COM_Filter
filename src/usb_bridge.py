import uasyncio as asyncio


async def run(cfg, log):
    """
    USB bridge mode: relay between one RS232 port (Port A) and the USB CDC
    virtual COM port presented to the attached computer.

    Not yet implemented — reserved for a future variant where the second
    physical DB9 connector is replaced by USB.
    """
    log.info("usb_bridge mode is not yet implemented")
    log.info("Change settings.json 'mode' to 'relay_two_port' to use the device")

    # Keep the event loop alive so Ctrl+C still drops to REPL
    while True:
        await asyncio.sleep_ms(1000)
