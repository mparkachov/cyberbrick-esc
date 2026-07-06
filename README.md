# CyberBrick ESC

CyberBrick ESC is a proof-of-concept project for making CyberBrick Mini Tank
hardware behave like a standard center-neutral dual brushed ESC.

This project is not production-ready, not safety-certified, and not suitable for
unattended operation.

## Current Stream

`main` is the stock-firmware MicroPython PoC stream. It uses the existing stock
MicroPython REPL and filesystem on the observed CyberBrick ESP32-C3 board.

The previous Zephyr implementation is preserved on `origin/backup/zephyr`. The
observed stock CyberBrick board reports Secure Download Mode with flash
encryption enabled, so do not force-flash plaintext firmware to that board.

The current phase is a workflow reset:

```text
stock firmware -> manual REPL when needed -> uv run mpremote -> blink -> restore stock
```

The ESC simulator library remains in the repo for a later phase, but simulator
deployment is intentionally disabled until blink and restore are reliable.

## Hardware Contract

Known target hardware:

- MCU: ESP32-C3 on CyberBrick Multi-Function Core Board.
- Runtime: stock CyberBrick MicroPython firmware with REPL access.
- LED: onboard WS2812/NeoPixel on GPIO8.
- Future inputs: standard hobby PWM signal pins from a flight controller or
  signal generator.

Default future simulator pins:

| Function | Connector | GPIO |
| --- | --- | ---: |
| ESC input 1 | Servo S3 signal | GPIO1 |
| ESC input 2 | Servo S4 signal | GPIO0 |
| Onboard RGB LED | Board LED | GPIO8 |

Reserved motor pins remain unused in this phase:

| Function | GPIO |
| --- | ---: |
| Motor 1 input A | GPIO4 |
| Motor 1 input B | GPIO5 |
| Motor 2 input A | GPIO6 |
| Motor 2 input B | GPIO7 |

Keep motors disconnected, tracks removed, or the vehicle physically unable to
move during bring-up. Confirm external signals are 3.3 V safe before connecting
them to ESP32-C3 GPIO pins.

## Tooling

Install the local environment:

```sh
uv sync
```

List devices:

```sh
uv run mpremote connect list
```

The `justfile` contains thin aliases over the same stock tools:

```sh
just install
just mp-list
just mp-repl
just miniterm
just run-blink
just deploy-blink
just restore-stock
just test
```

The default device is `auto`. Override it when needed:

```sh
DEVICE=/dev/cu.usbmodem1101 just mp-repl
```

No custom serial recovery helpers are part of the active workflow. If the board
is already running the stock solid-green app, `mpremote` may not interrupt it.
Use the manual REPL procedure below first, then rerun the `uv run mpremote ...`
or `just ...` command.

After manual recovery, filesystem and RAM-run recipes use stock `mpremote
resume` so `mpremote` does not soft-reset back into the stock app before the
operation.

## Manual REPL Recovery

Use this when the board is running stock firmware and showing solid green.

```sh
uv run python -m serial.tools.miniterm --raw --dtr 0 --rts 0 /dev/cu.usbmodem1101 115200
```

Equivalent `just` alias:

```sh
DEVICE=/dev/cu.usbmodem1101 just miniterm
```

Reliable sequence observed on the board:

1. Press physical RESET.
2. While the LED is in early boot, start the miniterm command.
3. Press Ctrl-C before the stock app takes over.
4. If the LED reaches solid green first, close miniterm and repeat from RESET.

Expected result:

```text
>>>
```

Exit miniterm with `Ctrl-]`.

## Phase 1 Blink Workflow

Back up the current filesystem from a REPL-reachable board:

```sh
just mp-backup
```

Backups are saved under gitignored `device-backups/` and use stock
`uv run mpremote ... fs` commands.

Run blink from RAM without changing board files:

```sh
just run-blink
```

Equivalent stock command:

```sh
uv run mpremote connect auto resume run micropython/examples/blink_main.py
```

Acceptance: the onboard LED on GPIO8 blinks while the command is running. Stop
with Ctrl-C; this command intentionally keeps running because the RAM script
loops forever. A board reset returns to stock behavior.

Deploy persistent boot blink:

```sh
just deploy-blink
```

This backs up the filesystem, preserves remote `boot.py` as `boot.stock.py` if
needed, copies `micropython/examples/blink_boot.py` to remote `boot.py`, and
resets the board. The boot-file override is required because the observed stock
CyberBrick `boot.py` runs the stock app directly.

Acceptance: after reset or power-cycle, the onboard LED blinks without a host
command.

Restore stock boot:

```sh
just restore-stock
```

This copies remote `boot.stock.py` back to `boot.py`, removes old PoC auto-main
files if present, and resets the board.

Acceptance: after reset or power-cycle, the board returns to the stock
solid-green behavior.

## Phase 2 Direction

Only after Phase 1 is stable, resume ESC simulator deployment. Use the same
`uv` plus stock `mpremote` approach. The simulator modules under
`micropython/lib/cyberbrick_esc/` and host tests are kept for that later phase,
but they are not part of the active deploy workflow.

Phase 2 still must preserve these safety boundaries:

- No plaintext firmware flashing to locked stock boards.
- No real motor output in the visual simulator milestone.
- GPIO4-GPIO7 remain unused until a later approved motor-output task.
- Startup and failsafe recovery require valid neutral input before commands.

## Host Checks

```sh
uv sync
uv run python -m unittest discover -s tests
just test
just --list
```

## Layout

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
      app.py
      config.py
      led.py
      pixels.py
      pwm_input.py
      safety.py
tests/
README.md
AGENTS.md
```

## References

- [MicroPython mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [MicroPython reset and boot sequence](https://docs.micropython.org/en/latest/reference/reset_boot.html)
- [MicroPython NeoPixel](https://docs.micropython.org/en/latest/library/neopixel.html)
- [MicroPython Pin IRQ](https://docs.micropython.org/en/latest/library/machine.Pin.html)
