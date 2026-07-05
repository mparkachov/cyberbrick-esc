# AGENTS.md

This file defines how coding agents should work on CyberBrick ESC.

The project must stay narrow and safety-first.

CyberBrick ESC is a proof of concept. Do not describe it as production-ready,
safety-certified, or suitable for unattended use.

## Current development stream

`main` is now the stock-firmware MicroPython PoC stream.

The previous Zephyr implementation is preserved on `origin/backup/zephyr`. It
is technically feasible and builds on macOS, but the observed stock CyberBrick
ESP32-C3 board reports Secure Download Mode with flash encryption enabled and is
not usable for plaintext Zephyr flashing.

Do not force-flash plaintext firmware to such a board. Treat it as not
Zephyr-flashable unless a maintainer provides an approved signed/encrypted or
vendor-compatible update flow.

This MicroPython stream must use the existing stock REPL/filesystem. It must not
be presented as the Zephyr firmware path.

## Mission

CyberBrick ESC turns CyberBrick Mini Tank hardware into a standard
bidirectional dual brushed ESC controlled by normal hobby PWM input signals from
a flight controller.

The current MicroPython milestone simulates that ESC behavior visually:

```text
Two center-neutral RC PWM inputs -> safe command mapping -> RGB LED feedback
```

Default public signal behavior:

```text
1000 us -> full reverse
1500 us -> stop / neutral
2000 us -> full forward
```

Do not turn the project into a rover controller, a serial protocol bridge, a
CyberBrick clone, or a general robotics stack.

## Hard scope boundaries

Implement only the stock MicroPython visual ESC simulator unless a human
maintainer explicitly changes scope.

The current milestone must not drive real motor outputs. GPIO4-GPIO7 are
reserved for later H-bridge work and must remain unused by the MicroPython app.

Do not implement these features by default:

- Plaintext firmware flashing to locked stock boards.
- Real motor output from the MicroPython simulator.
- MAVLink.
- MSP.
- CRSF.
- SBUS.
- iBUS.
- UART command input.
- DShot input.
- OneShot input.
- Multishot input.
- Wi-Fi control.
- Bluetooth control.
- Web UI.
- OTA update logic.
- CyberBrick stock protocol compatibility.
- Autonomous rover behavior.
- Navigation, odometry, stabilization, or path planning.

It is acceptable to structure code so future protocols or real motor output can
be added later, but do not add those features now.

## Tooling policy

Use stock MicroPython tooling against the existing REPL/filesystem.

Preferred tools and mechanisms:

- `mpremote` for REPL, filesystem copy, reset, backup, and restore.
- A host-side serial helper for inspection and stop operations when mpremote
  cannot reliably enter raw REPL after USB reconnects.
- `just` as the thin project command runner.
- `python3 -m unittest` for host checks of pure logic.
- Persistent app deployment by preserving stock `boot.py`, then copying a
  reversible PoC `boot.py`, `main.py`, and library files to the MicroPython
  filesystem.
- The PoC `boot.py` must keep a sticky double-reset safe REPL mode using
  `cyberbrick_boot_pending.txt` and `cyberbrick_safe_repl.txt`, so recovery does
  not depend on a fast Ctrl-C race. Safe mode may rename deployed `main.py` to
  `main.poc.py` to prevent MicroPython from auto-running it after `boot.py`
  returns.

Avoid:

- `esptool` writes or force-flashing.
- `west flash` or any Zephyr flashing flow on stock locked boards.
- Arduino framework.
- PlatformIO project structure.
- ESP-IDF application structure.
- MicroPython firmware replacement.
- External dependencies beyond `mpremote` unless clearly justified and approved.

## Hardware contract

Known target hardware:

- MCU: ESP32-C3 on CyberBrick Multi-Function Core Board.
- Runtime: stock CyberBrick MicroPython firmware with REPL access.
- Motor board: CyberBrick receiver and motor-driver board from the Mini Tank.
- Motor driver: dual brushed H-bridge interface, two logic inputs per motor.

Default input pins:

| Function | Connector | GPIO |
| --- | --- | ---: |
| ESC input 1 | Servo S3 signal | GPIO1 |
| ESC input 2 | Servo S4 signal | GPIO0 |

Default status LED:

| Function | GPIO |
| --- | ---: |
| Onboard RGB LED WS2812/NeoPixel | GPIO8 |

Reserved motor pins:

| Function | GPIO |
| --- | ---: |
| Motor 1 input A | GPIO4 |
| Motor 1 input B | GPIO5 |
| Motor 2 input A | GPIO6 |
| Motor 2 input B | GPIO7 |

Avoid using these pins in normal MicroPython development:

- GPIO2, because it is an ESP32-C3 strapping pin.
- GPIO4 to GPIO7, because they are reserved for later motor output work.
- GPIO18 and GPIO19, because they are USB pins.
- GPIO20 and GPIO21 for ESC input, because they may be tied to debug, UART,
  LED, or buzzer functions on CyberBrick-related hardware.

Keep hardware pin assignments centralized in `micropython/lib/cyberbrick_esc/config.py`.

## Input signal rule

Input is standard hobby PWM pulse timing.

Default interpretation:

- Valid pulse range: 900 us to 2100 us.
- Command range: 1000 us to 2000 us.
- Reverse command: below neutral.
- Neutral command: 1500 us.
- Forward command: above neutral.
- Input lower than minimum valid is invalid.
- Input higher than maximum valid is invalid.
- Invalid pulses do not update the last-valid timestamp.

Default mapping:

```text
1000 us -> -1000
1500 us -> 0
2000 us -> +1000
```

Use a neutral deadband around 1500 us. The default deadband is 50 us.

Use GPIO interrupts on both rising and falling edges. Interrupt handlers must be
short and non-blocking.

Do not implement input decoding by busy-waiting in the main loop.

## Visual feedback rule

The onboard RGB LED is proof-of-concept visual feedback for testing while
motors are disconnected or the vehicle is physically safe.

Default LED behavior:

- Blue means powered and neutral, so motors should not move.
- Green means the dominant final command is forward. Intensity reflects the
  largest forward command magnitude.
- Red means the dominant final command is reverse. Intensity reflects the
  largest reverse command magnitude.
- If channels disagree, dominant absolute command wins; an exact opposing tie
  returns to blue.

The LED must be derived from final safe commands after safety processing. It
must not affect arming, failsafe, input capture, or any future motor output
commands.

## Safety invariants

These rules are mandatory and should be protected by host tests where practical.

- On boot, simulated output commands are zero before input capture starts.
- On initialization failure, the app must not command motor pins.
- On missing input, final commands return to zero after the failsafe timeout.
- On invalid pulse width, the pulse is ignored.
- On failsafe recovery, input must be valid and neutral before arming again.
- On startup, input must be valid and neutral before first arming.
- No IRQ directly changes LED feedback or any future motor output.
- No malformed input can produce nonzero final commands.
- No default should allow unexpected movement at boot.

## Architecture expectations

Keep the application modular.

Expected layout:

```text
justfile
requirements.txt
micropython/
  boot.py
  main.py
  examples/
    blink_boot.py
    blink_main.py
  lib/
    cyberbrick_esc/
      app.py
      config.py
      led.py
      pwm_input.py
      safety.py
tests/
  test_safety.py
README.md
AGENTS.md
```

Module responsibilities:

### `pwm_input`

- Owns GPIO configuration and callbacks.
- Measures pulse widths.
- Publishes validated pulse-width samples.
- Does not know about motor pins.
- Does not know about arming policy.

### `safety`

- Owns arming and failsafe state.
- Owns command mapping from pulse width to normalized signed command.
- Applies neutral deadband.
- Applies clamping.
- Applies neutral-before-arm rules.
- Provides final safe commands for LED feedback.

### `led`

- Owns visual-only RGB LED updates.
- Derives LED color and intensity from final safe commands.
- Does not change safety, input capture, or future motor output state.

### `app`

- Initializes modules.
- Runs the control loop.
- Contains no hardware pin numbers outside config.

## Coding style

Follow normal embedded MicroPython practices.

- Use clear, small functions.
- Prefer integer arithmetic for timing and command calculations.
- Avoid dynamic allocation in IRQ handlers.
- Keep IRQ handlers short.
- Avoid unnecessary global mutable state.
- Keep target-specific imports (`machine`, `neopixel`) out of pure host-testable
  modules when practical.
- Keep public module surfaces minimal.
- Document units in names, for example `_us`, `_ms`, `_hz`.

## Testing requirements

The required host validation gate for now is:

```sh
just test
```

Hardware validation remains manual:

```sh
just install
just mp-list
just mp-backup
just deploy-blink
just mp-stop
just deploy
```

Do not add Twister metadata, `testcase.yaml`, or Ztest scaffolding for this
MicroPython milestone.

## Definition of done

A change is not complete unless:

- It keeps stock-board work on the MicroPython REPL/filesystem path.
- It does not introduce firmware flashing for locked stock boards.
- It preserves center-neutral ESC simulator behavior.
- It preserves safe boot and failsafe behavior.
- It keeps GPIO4-GPIO7 unused unless a maintainer explicitly approves real
  motor output work.
- It updates README documentation when user-visible behavior changes.
- `just test` passes, or the reason it could not be run is documented.

## Documentation expectations

Documentation should be explicit about:

- Required wiring.
- 3.3 V signal limits.
- PWM timing expectations.
- Center-neutral behavior.
- Failsafe behavior.
- Which pins are used.
- Which pins are intentionally reserved and unused.
- Which features are intentionally unsupported.
- Backup, deploy, stop, and restore workflows.

Do not describe this project as a complete BLHeli, DShot, or universal ESC
replacement.

## When uncertain

Choose the safer and narrower behavior.

If hardware behavior is unknown, document the uncertainty and require
measurement. Do not make assumptions that could put 5 V on an ESP32-C3 GPIO or
start a motor unexpectedly.

If a requested change expands scope, implement the smallest preparatory refactor
only if it improves the current stock MicroPython visual ESC simulator. Otherwise
leave it for a future scope decision.
