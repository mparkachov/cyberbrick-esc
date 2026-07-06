# AGENTS.md

This file defines how coding agents should work on CyberBrick ESC.

CyberBrick ESC is a proof of concept. Do not describe it as production-ready,
safety-certified, or suitable for unattended use.

## Current Development Stream

`main` is the stock-firmware MicroPython PoC stream.

The previous Zephyr implementation is preserved on `origin/backup/zephyr`. It
is technically feasible and builds on macOS, but the observed stock CyberBrick
ESP32-C3 board reports Secure Download Mode with flash encryption enabled and is
not usable for plaintext Zephyr flashing.

Do not force-flash plaintext firmware to such a board. Treat it as not
Zephyr-flashable unless a maintainer provides an approved signed/encrypted or
vendor-compatible update flow.

The active phase is a stock-tool workflow reset. First make stock REPL access,
RAM blink, persistent boot blink, and restore-to-stock reliable. Do not resume
ESC simulator deployment until that Phase 1 workflow is validated.

## Mission And Scope

The long-term mission is a center-neutral dual brushed ESC simulator path:

```text
Two center-neutral RC PWM inputs -> safe command mapping -> RGB LED feedback
```

Default future simulator signal behavior:

```text
1000 us -> full reverse
1500 us -> stop / neutral
2000 us -> full forward
```

For Phase 1, active hardware work is limited to stock-tool blink and restore.
Keep `micropython/lib/cyberbrick_esc/` and host tests dormant for Phase 2.

Do not implement these features by default:

- Plaintext firmware flashing to locked stock boards.
- Real motor output from the MicroPython simulator.
- MAVLink, MSP, CRSF, SBUS, iBUS, UART command input, DShot, OneShot, or
  Multishot input.
- Wi-Fi, Bluetooth, web UI, OTA update logic, or CyberBrick stock protocol
  compatibility.
- Autonomous rover behavior, navigation, odometry, stabilization, or path
  planning.

## Tooling Policy

Use stock MicroPython tooling against the existing REPL/filesystem.

Required tooling:

- `uv` manages the Python environment.
- `mpremote` is the only active board automation tool.
- `just` may exist only as thin aliases over `uv run ...`.
- `uv run python -m unittest discover -s tests` is the host test command.

Allowed Phase 1 commands:

- `uv sync`
- `uv run mpremote connect list`
- `uv run mpremote connect <device> resume repl`
- `uv run mpremote connect <device> resume run micropython/examples/blink_main.py`
- `uv run mpremote connect <device> resume fs ...`
- `uv run python -m serial.tools.miniterm --raw --dtr 0 --rts 0 <device> 115200`
- `DEVICE=<device> just miniterm`

Avoid:

- `esptool` writes, `west flash`, Arduino, PlatformIO, ESP-IDF app structure,
  or MicroPython firmware replacement.
- Dependencies beyond `mpremote` unless explicitly justified and approved.

Manual REPL recovery is part of the workflow. If the board is running the stock
solid-green app and `mpremote` cannot interrupt it, use miniterm: press
physical RESET, start miniterm during early boot, and press Ctrl-C before the
stock app takes over.

## Hardware Contract

Known target hardware:

- MCU: ESP32-C3 on CyberBrick Multi-Function Core Board.
- Runtime: stock CyberBrick MicroPython firmware with REPL access.
- Status LED: onboard WS2812/NeoPixel on GPIO8.

Future simulator input pins:

| Function | Connector | GPIO |
| --- | --- | ---: |
| ESC input 1 | Servo S3 signal | GPIO1 |
| ESC input 2 | Servo S4 signal | GPIO0 |

Reserved motor pins:

| Function | GPIO |
| --- | ---: |
| Motor 1 input A | GPIO4 |
| Motor 1 input B | GPIO5 |
| Motor 2 input A | GPIO6 |
| Motor 2 input B | GPIO7 |

GPIO4-GPIO7 must remain unused until a later maintainer-approved motor-output
task. Avoid GPIO2, GPIO18, GPIO19, GPIO20, and GPIO21 unless a maintainer
explicitly changes the hardware contract.

## Architecture Expectations

Expected active layout:

```text
pyproject.toml
uv.lock
justfile
micropython/
  main.py
  examples/
    blink_boot.py
    blink_main.py
  lib/
    cyberbrick_esc/
tests/
README.md
AGENTS.md
```

Phase 1 uses only the blink examples for hardware deployment. The simulator
modules remain modular and host-tested for later work:

- `pwm_input` owns GPIO input capture.
- `safety` owns arming, failsafe, and command mapping.
- `led` owns visual-only RGB feedback.
- `app` wires the simulator modules together.

## Testing Requirements

Required host validation:

```sh
uv sync
uv run python -m unittest discover -s tests
just test
just --list
```

Manual hardware validation for Phase 1:

```sh
uv run mpremote connect list
just run-blink
just deploy-blink
just restore-stock
```

These board commands assume the board is already REPL-reachable. If it is
running the stock app, perform manual miniterm recovery first.

Do not add Twister metadata, `testcase.yaml`, or Ztest scaffolding for this
MicroPython milestone.

## Documentation Expectations

Documentation must be explicit about:

- Manual REPL recovery from stock solid green.
- `uv` and stock `mpremote` as the supported workflow.
- RAM blink, persistent blink, and restore stock.
- 3.3 V signal limits and reserved motor pins.
- Which features are intentionally unsupported.

Do not describe this project as a complete BLHeli, DShot, or universal ESC
replacement.

## When Uncertain

Choose the safer and narrower behavior.

If hardware behavior is unknown, document the uncertainty and require
measurement. Do not make assumptions that could put 5 V on an ESP32-C3 GPIO or
start a motor unexpectedly.
