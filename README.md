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

The current phase runs the visual ESC simulator on the validated stock-tool
workflow:

```text
stock firmware -> manual REPL when needed -> uv run mpremote -> ESC simulator -> restore stock
```

The simulator is visual-only. It reads two RC PWM inputs, applies the
center-neutral safety mapping, and shows the final safe command state on the
onboard RGB LED. It does not drive GPIO4-GPIO7 motor outputs.

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
just deploy
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

This copies remote `boot.stock.py` back to `boot.py`, removes deployed PoC
startup/library files if present, and resets the board.

Acceptance: after reset or power-cycle, the board returns to the stock
solid-green behavior.

## ESC Simulator Workflow

From a REPL-reachable stock board, deploy the simulator:

```sh
just deploy
```

This backs up the filesystem, preserves remote `boot.py` as `boot.stock.py` if
needed, creates remote `lib/cyberbrick_esc/`, copies
`micropython/examples/esc_boot.py` to remote `boot.py`, copies
`micropython/main.py` to remote `main.py`, copies the simulator library, and
resets the board.

The boot-file override is required because the observed stock CyberBrick
`boot.py` runs the stock app directly and does not reliably hand off to
`main.py`.

Expected simulator behavior:

- Missing input or stale input: blue neutral.
- Both channels valid and neutral for at least 1000 ms: armed, still blue.
- Brief non-neutral glitches up to 300 ms during arming are tolerated, but
  output remains zero until arming completes.
- Input loss after arming outputs zero while stale, but does not latch a full
  disarm unless the loss persists for another 1500 ms.
- Dominant forward command: green, with intensity based on command magnitude.
- Dominant reverse command: red, with intensity based on command magnitude.
- Exact opposing direction tie: blue.
- Endpoint captures within 150 us of the 1000 us or 2000 us command endpoints
  are treated as full command. This keeps near-endpoint RC PWM captures stable
  in the final command stream instead of hiding imbalance in the LED layer.
- PWM input capture uses a three-sample median filter to reject isolated valid
  pulse-width spikes.
- Final command changes require 80 ms of confirmation before release. Failsafe
  and hard-fault paths still output zero immediately.

The LED is debug feedback only. Final safe commands in the diagnostic log are
the behavior to validate for future motor output; do not treat LED smoothness as
the motor-output stability signal.

Current hardware state:

- `just deploy` persistently starts the simulator after reset/power-cycle.
- With Raspberry Pi 50 Hz PWM on S3/S4, the simulator arms from neutral and
  releases stable final commands after the 80 ms confirmation window.
- Forward test state holds `cmd=1000,0` and shows green.
- Reverse test state holds `cmd=-1000,0` and shows red.
- Opposing endpoint tie holds `cmd=1000,-1000` and shows blue, including while
  isolated raw captures briefly move away from the endpoint.
- When the Raspberry Pi script disables PWM, stale input immediately outputs
  `cmd=0,0`; if input remains absent, `latch=input_loss` appears after the
  configured 1500 ms latch window.

Observed raw captures still contain occasional valid-width excursions on the
input lines. The current PoC treats those as input-source/capture jitter and
stabilizes the final command stream with the median filter and command
confirmation described above.

Default input behavior:

```text
1000 us -> -1000
1500 us -> 0
2000 us -> +1000
```

The neutral deadband is 50 us around 1500 us. The endpoint deadband is 150 us,
so 900-1150 us maps to full reverse and 1850-2100 us maps to full forward
within the broader 900-2100 us valid-pulse range.

When miniterm is attached, the simulator prints a startup banner and diagnostic
lines every 500 ms:

```text
ESC simulator starting inputs=(1, 0) led=(8,) loop_hz=200 diag_ms=500 valid_us=900-2100 neutral_us=1500 neutral_db_us=50 endpoint_db_us=150 arm_ms=1000 arm_grace_ms=300 loss_latch_ms=1500 cmd_confirm_ms=80 pwm_filter=3
ESC diag t_ms=1234 reason=armed latch= fault= armed=1 failsafe=0 neutral_wait=0 neutral_ms=0 non_neutral_ms=0 loss_ms=0 raw=1000,0 cmd=1000,0 led=0,255,0 ch0=2000us/v1/f1/age3ms,ch1=1500us/v1/f1/age3ms
```

Diagnostic fields:

- `v1` means the last captured pulse width was valid.
- `f1` means the last valid pulse is fresh enough for the failsafe window.
- `raw` is the command that the captured pulses would map to before arming and
  failsafe safety gates.
- `reason=need_neutral` means capture is working but arming is blocked because
  at least one channel is outside the neutral deadband.
- `reason=loss_pending` means the simulator is armed but has seen a short
  stale-input condition; output is zero unless fresh input returns quickly.
- `latch=input_loss` means stale input persisted long enough to require neutral
  re-arming before commands are released again.
- `latch=hard_fault` means malformed input caused an immediate latched safe
  state.
- `fault=future_timestamp` means a captured PWM timestamp was newer than the
  safety time reference. That indicates an input snapshot/timing bug, not a
  normal RC command.
- Other `fault` values describe malformed samples, invalid sample fields, or
  out-of-range pulse widths.
- `armed=0` with `neutral_wait=1` means neutral has been detected but not held
  for the full arming time yet.
- `neutral_ms` is the current neutral-hold duration used for arming.
- `non_neutral_ms` is how long a pre-arm non-neutral glitch has persisted.
- `loss_ms` is how long an armed stale-input condition has persisted before a
  latched disarm.
- `cmd` is the final safe command after arming and failsafe logic.
- `led` is the RGB value written from the final safe command.

Restore stock after simulator testing:

```sh
just restore-stock
```

The simulator must preserve these safety boundaries:

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
    esc_boot.py
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
