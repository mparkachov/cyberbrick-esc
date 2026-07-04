#!/usr/bin/env python3
"""Print the local ESP-IDF RISC-V toolchain prefix for Zephyr cross-compile."""

from __future__ import annotations

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = PROJECT_ROOT / ".espressif"


def main() -> int:
    candidates = sorted(
        TOOLS_DIR.glob(
            "tools/riscv32-esp-elf/*/riscv32-esp-elf/bin/riscv32-esp-elf-gcc"
        )
    )
    if not candidates:
        print(
            "No local ESP32-C3 RISC-V compiler found. Run 'just install' first.",
            flush=True,
        )
        return 1

    compiler = candidates[-1]
    print(compiler.with_name("riscv32-esp-elf-"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

