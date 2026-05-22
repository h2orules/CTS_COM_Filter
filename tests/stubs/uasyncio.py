"""Stub for MicroPython uasyncio — delegates to stdlib asyncio."""
import asyncio as _asyncio

sleep = _asyncio.sleep
gather = _asyncio.gather
run = _asyncio.run
create_task = _asyncio.create_task
CancelledError = _asyncio.CancelledError
Event = _asyncio.Event


async def sleep_ms(ms):
    await _asyncio.sleep(ms / 1000)
