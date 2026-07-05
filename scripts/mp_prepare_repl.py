#!/usr/bin/env python3
"""Interrupt the stock MicroPython app and print the serial port to use."""

from __future__ import annotations

import fnmatch
import sys
import time
from pathlib import Path

import serial
from serial.tools import list_ports


BAUDRATE = 115200
INTERRUPT_COUNT = 5
INTERRUPT_DELAY_S = 0.12
SETTLE_DELAY_S = 0.25


def main() -> int:
    requested = sys.argv[1] if len(sys.argv) > 1 else "auto"
    port = resolve_port(requested)
    interrupt_to_repl(port)
    print(port)
    return 0


def resolve_port(requested: str) -> str:
    if requested != "auto":
        return requested

    ports = [port.device for port in list_ports.comports()]
    preferred = sorted(
        port
        for port in ports
        if fnmatch.fnmatch(Path(port).name, "cu.usbmodem*")
        or fnmatch.fnmatch(Path(port).name, "tty.usbmodem*")
    )
    if preferred:
        return preferred[0]

    fallback = sorted(
        port
        for port in ports
        if "Bluetooth" not in port and "debug-console" not in port
    )
    if fallback:
        return fallback[0]

    raise SystemExit(
        "No USB MicroPython serial device found. "
        "Connect the board or set DEVICE=/dev/cu.usbmodem..."
    )


def interrupt_to_repl(port: str) -> None:
    try:
        with serial.Serial(port, BAUDRATE, timeout=0.2, write_timeout=1) as stream:
            for _ in range(INTERRUPT_COUNT):
                stream.write(b"\x03")
                stream.flush()
                time.sleep(INTERRUPT_DELAY_S)
            time.sleep(SETTLE_DELAY_S)
            stream.read(4096)
    except serial.SerialException as exc:
        raise SystemExit(f"Could not interrupt MicroPython app on {port}: {exc}") from exc


if __name__ == "__main__":
    raise SystemExit(main())
