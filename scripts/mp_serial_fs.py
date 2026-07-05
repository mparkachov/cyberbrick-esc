#!/usr/bin/env python3
"""MicroPython filesystem helpers for CyberBrick stock USB serial quirks."""

from __future__ import annotations

import argparse
import sys
import time

import serial
from serial import SerialException
from mpremote.transport import TransportError
from mpremote.transport_serial import SerialTransport

from mp_prepare_repl import resolve_port


BAUDRATE = 115200
CTRL_C_INTERVAL_S = 0.2
CTRL_C_TIMEOUT_S = 25.0
RAW_REPL_TIMEOUT_S = 4.0
READ_CHUNK_BYTES = 4096
RECONNECT_DELAY_S = 0.25


class CyberBrickSerialTransport(SerialTransport):
    def __init__(self, requested_device: str):
        self.in_raw_repl = False
        self.use_raw_paste = True
        self.requested_device = requested_device
        self.device_name = None
        self.mounted = False
        self.serial = None
        self.open()

    def open(self):
        port = resolve_port(self.requested_device)
        self.device_name = port
        self.serial = serial.serial_for_url(
            port,
            baudrate=BAUDRATE,
            timeout=0.1,
            write_timeout=0.5,
            do_not_open=True,
        )
        self.serial.dtr = False
        self.serial.rts = False
        self.serial.open()

    def reopen(self):
        self.close()
        deadline = time.monotonic() + CTRL_C_TIMEOUT_S
        last_error = None
        while time.monotonic() < deadline:
            try:
                self.open()
                return
            except (OSError, SerialException, SystemExit) as exc:
                last_error = exc
                time.sleep(RECONNECT_DELAY_S)

        raise SystemExit(f"Could not reopen USB serial device after reset: {last_error}")

    def close(self):
        if self.serial is None:
            return

        try:
            if self.serial.is_open:
                try:
                    self.serial.rts = False
                    self.serial.dtr = False
                except (OSError, SerialException):
                    pass
                self.serial.close()
        except (OSError, SerialException):
            pass
        finally:
            self.serial = None


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--device", default="auto")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("tree")
    cat_parser = subparsers.add_parser("cat")
    cat_parser.add_argument("path")
    subparsers.add_parser("stop")
    args = parser.parse_args()

    transport = CyberBrickSerialTransport(args.device)
    try:
        enter_raw_repl(transport)
        if args.command == "tree":
            print_tree(transport)
        elif args.command == "cat":
            data = transport.fs_readfile(strip_remote_prefix(args.path))
            sys.stdout.buffer.write(data)
        elif args.command == "stop":
            stop_app(transport)
    finally:
        transport.close()

    return 0


def enter_raw_repl(transport: CyberBrickSerialTransport) -> None:
    prompt_data = interrupt_to_friendly_repl(transport)
    transport.serial.write(b"\r\x01")
    data = transport.read_until(
        1,
        b"raw REPL; CTRL-B to exit\r\n",
        timeout_overall=RAW_REPL_TIMEOUT_S,
    )
    if not data.endswith(b"raw REPL; CTRL-B to exit\r\n"):
        raise SystemExit(
            "Could not enter raw REPL after Ctrl-C.\n"
            f"Last friendly-REPL data: {prompt_data!r}\n"
            f"Raw-REPL data: {data!r}"
        )
    transport.in_raw_repl = True


def interrupt_to_friendly_repl(transport: CyberBrickSerialTransport) -> bytes:
    deadline = time.monotonic() + CTRL_C_TIMEOUT_S
    data = bytearray()
    saw_micropython = False
    next_interrupt_at = 0.0
    while time.monotonic() < deadline:
        now = time.monotonic()
        try:
            chunk = transport.serial.read(READ_CHUNK_BYTES)
        except (OSError, SerialException):
            transport.reopen()
            continue

        if chunk:
            data.extend(chunk)
            if b">>> " in data:
                return bytes(data)
            if b"MicroPython " in data or b"Type \"help()\"" in data:
                saw_micropython = True

        if saw_micropython or now >= next_interrupt_at:
            try:
                transport.serial.write(b"\x03")
            except (OSError, SerialException):
                transport.reopen()
                continue
            next_interrupt_at = now + CTRL_C_INTERVAL_S

        time.sleep(0.02)
        try:
            data.extend(transport.serial.read(READ_CHUNK_BYTES))
        except (OSError, SerialException):
            transport.reopen()
            continue
        if b">>> " in data:
            return bytes(data)

    raise SystemExit(
        "Could not reach friendly REPL with Ctrl-C. "
        "Reset or power-cycle the board while running this command; "
        "do not press BOOT. "
        "or use miniterm manual recovery.\n"
        f"Captured data: {bytes(data)!r}"
    )


def print_tree(transport: CyberBrickSerialTransport) -> None:
    print(":/")
    print_tree_entries(transport, "", "")


def print_tree_entries(transport: CyberBrickSerialTransport, path: str, prefix: str) -> None:
    entries = sorted(transport.fs_listdir(path), key=lambda entry: entry.name)
    for idx, entry in enumerate(entries):
        is_last = idx == len(entries) - 1
        connector = "`-- " if is_last else "|-- "
        print(prefix + connector + entry.name)
        if entry.st_mode & 0x4000:
            child_path = remote_join(path, entry.name)
            child_prefix = prefix + ("    " if is_last else "|   ")
            print_tree_entries(transport, child_path, child_prefix)


def stop_app(transport: CyberBrickSerialTransport) -> None:
    transport.exec_raw_no_follow(
        """
import os, machine
for path in ("cyberbrick_boot_pending.txt", "cyberbrick_safe_repl.txt", "main.poc.py"):
    try:
        os.remove(path)
    except OSError:
        pass
try:
    os.remove("boot.py")
except OSError:
    pass
try:
    os.rename("boot.stock.py", "boot.py")
except OSError:
    pass
try:
    os.remove("main.py")
except OSError:
    pass
machine.reset()
"""
    )
    print("Requested stock boot restore and reset.")


def strip_remote_prefix(path: str) -> str:
    if path.startswith(":"):
        return path[1:]
    return path


def remote_join(parent: str, child: str) -> str:
    if not parent:
        return child
    return parent.rstrip("/") + "/" + child


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except TransportError as exc:
        raise SystemExit(str(exc)) from exc
