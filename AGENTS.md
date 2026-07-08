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

The active phase is stock-tool ESC simulator deployment on top of the validated
Phase 1 workflow. Keep the board workflow on `uv`, stock `mpremote`, manual
miniterm recovery when needed, and restore-to-stock through `boot.stock.py`.

## Mission And Scope

The long-term mission is a center-neutral dual brushed ESC path:

```text
Two center-neutral RC PWM inputs -> safe command mapping -> final safe commands
```

Future motor output must be driven from the final safe commands. The current
visual PoC taps those final safe commands into the RGB LED only as debug
feedback.

Default future simulator signal behavior:

```text
1000 us -> full reverse
1500 us -> stop / neutral
2000 us -> full forward
```

The active MicroPython path alternates native `machine.time_pulse_us` polling
between both channels, nominally evaluates safety at 50 Hz, and samples each
channel at 25 Hz. It uses a 50 us neutral deadband, 150 us endpoint deadband,
three-sample PWM median filter, and 80 ms command-change confirmation. These
are part of the final command stream, not LED display workarounds.

Hardware testing showed that scheduled Python `Pin.irq` callbacks do not
provide edge timestamps on this ESP32 port. Native polling is much more
accurate but still has rare preemption outliers and is not hardware capture.
Treat the expected roughly 160 ms command-transition latency and non-
deterministic capture timing as stock-runtime PoC limitations.

Active hardware work is still visual-only: stock-tool blink/restore and the
MicroPython ESC simulator. The simulator reads inputs and drives only the RGB
LED feedback path.

## Output Priority

The final safe command stream is the behavioral contract. Design and validation
must prioritize commands that are stable enough for future motor output and that
faithfully reflect valid RC PWM inputs after safety processing.

The RGB LED is debug feedback only. LED appearance, flicker, smoothness, or
brightness stability must not drive changes to input capture, safety mapping,
arming, failsafe, or future motor-output behavior. If LED output looks unstable
but diagnostics show the final safe commands are changing, preserve command
fidelity and investigate the input/safety path rather than hiding it in the LED.

LED code may format or display final safe commands, but it must remain
downstream-only:

- Do not feed LED state back into safety, input capture, or command generation.
- Do not change command semantics to make LED colors look steadier.
- Do not use LED stability as evidence that future motor output would be
  stable; validate final safe commands directly through logs/tests and later
  hardware measurements.
- Any smoothing or filtering intended for motor output must be explicit in the
  command/output path, documented as such, and protected by tests.

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

Allowed board commands:

- `uv sync`
- `uv run mpremote connect list`
- `uv run mpremote connect <device> resume repl`
- `uv run mpremote connect <device> resume run micropython/examples/blink_main.py`
- `uv run mpremote connect <device> resume run micropython/examples/pwm_timing_ram.py`
- `uv run mpremote connect <device> resume fs ...`
- `uv run python -m serial.tools.miniterm --raw --dtr 0 --rts 0 <device> 115200`
- `DEVICE=<device> just miniterm`
- `just deploy`
- `just restore-stock`

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
    esc_boot.py
    pwm_timing_ram.py
  lib/
    cyberbrick_esc/
tests/
README.md
AGENTS.md
```

The blink examples remain the first hardware proof. The simulator modules are
deployed by `just deploy` and remain modular:

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

Manual hardware validation:

```sh
uv run mpremote connect list
just run-blink
just run-pwm-timing
just deploy-blink
just deploy
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
- ESC simulator deploy and visual RGB command behavior.
- 3.3 V signal limits and reserved motor pins.
- Which features are intentionally unsupported.

Do not describe this project as a complete BLHeli, DShot, or universal ESC
replacement.

## When Uncertain

Choose the safer and narrower behavior.

If hardware behavior is unknown, document the uncertainty and require
measurement. Do not make assumptions that could put 5 V on an ESP32-C3 GPIO or
start a motor unexpectedly.
