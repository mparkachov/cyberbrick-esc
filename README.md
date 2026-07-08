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

The current phase validates Mini Tank motor direction on the stock-tool
workflow after the unloaded H-bridge output check:

```text
stock firmware -> manual REPL when needed -> uv run mpremote -> ESC simulator -> restrained motor-direction check -> restore stock
```

The simulator reads two RC PWM inputs, applies the center-neutral safety
mapping, drives H-bridge input PWM on GPIO4-GPIO7 from the final safe commands,
and shows the same final safe command state on the onboard RGB LED. The
published Mini Tank configuration uses positive polarity for Motor 1 and
negative polarity for Motor 2; this project applies the same vehicle-relative
mapping.

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

H-bridge input PWM pins:

| Function | GPIO |
| --- | ---: |
| Motor 1/right input A | GPIO4 |
| Motor 1/right input B | GPIO5 |
| Motor 2/left input A | GPIO6 |
| Motor 2/left input B | GPIO7 |

Motor 1/right uses normal polarity. Motor 2/left is inverted so equal positive
commands move both tracks forward despite the mirrored drivetrain mounting.
Keep tracks lifted or the vehicle physically unable to move during attached
motor checks. Confirm external signals are 3.3 V safe before connecting them to
ESP32-C3 GPIO pins.

This mapping follows the
[published Mini Tank project configuration](https://makerworld.com/en/models/1734120-cyberbrick-mini-t-remote-controlled-mini-tank)
(`MOTOR1` positive, `MOTOR2` negative). The
[official CyberBrick motor driver](https://github.com/CyberBrick-Official/CyberBrick_Controller_Core/blob/b5fc07d44d65143cfef1164ae6234099fcb11d62/src/app_rc/bbl/motors.py)
confirms M1 on GPIO4/GPIO5 and M2 on GPIO6/GPIO7.

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
- PWM input capture alternates GPIO1/GPIO0 through native
  `machine.time_pulse_us` polling. Safety is evaluated nominally at 50 Hz and
  each channel is sampled nominally at 25 Hz.
- A three-sample median filter rejects isolated valid pulse-width spikes.
- Final command changes require 80 ms of confirmation before release. Failsafe
  and hard-fault paths still output zero immediately.
- Final safe commands drive 20 kHz PWM on the H-bridge input pins:
  - Motor 1/right command uses GPIO4/GPIO5 with normal polarity.
  - Motor 2/left command uses GPIO6/GPIO7 with inverted polarity.
  - Positive Motor 1 command drives GPIO4; positive Motor 2 command drives
    GPIO7.
  - Negative Motor 1 command drives GPIO5; negative Motor 2 command drives
    GPIO6.
  - Neutral, failsafe, input-loss, and hard-fault states keep both pins low.
  - Full command maps to duty_u16 `65535`.
  - Half command maps to about duty_u16 `32768`.

The LED is debug feedback only. Final safe commands and `out=` PWM diagnostics
are the behavior to validate before attached-motor work; do not treat LED
smoothness as the motor-output stability signal.

Current hardware state:

- `just deploy` persistently starts the simulator after reset/power-cycle.
- Integrated native-capture hardware validation confirms neutral arming,
  forward, reverse, opposing endpoint tie, and stale-input behavior.
- With Raspberry Pi 50 Hz PWM on S3/S4, the simulator arms from neutral, holds
  `cmd=1000,0` for forward, holds `cmd=-1000,0` for reverse, and holds
  `cmd=1000,-1000` for the opposing endpoint tie.
- GPIO4-GPIO7 output PWM is enabled from those final safe commands for unloaded
  H-bridge validation. LED feedback remains downstream debug: blue neutral,
  green forward, red reverse, and blue for the exact opposing tie.
- Deployed output diagnostics confirm GPIO4-GPIO7 duty values follow final safe
  commands. `cmd=1000,0` drives GPIO4 at `65535`, `cmd=-1000,0` drives GPIO5
  at `65535`, `cmd=1000,-1000` drives GPIO4 and GPIO6 at `65535`, and loss
  states drive all four outputs to zero.
- Earlier scope validation confirmed clear PWM on GPIO4 and GPIO5 with no motor
  attached. Subsequent attached-motor testing exposed the mirrored Mini Tank
  drivetrain polarity; Motor 2 is now explicitly inverted to match the
  published Mini Tank configuration.
- When the Raspberry Pi script disables PWM, stale input immediately outputs
  `cmd=0,0`; if input remains absent, `latch=input_loss` appears after the
  configured 1500 ms latch window.
- The reverse transition may show one diagnostic line where `raw=-1000,0` while
  `cmd=1000,0`; this is the intentional 80 ms command-change confirmation
  window.
- Returning from a non-neutral command to neutral can likewise show a short
  diagnostic interval where `raw=0,0` while the prior `cmd` and `out` remain
  active; this is the same command-change confirmation window. Failsafe and
  persistent input-loss paths still force `out=0` on all four pins.

Timing comparison showed stable electrical inputs while the former scheduled
Python GPIO callbacks reported large deviations. Native `machine.time_pulse_us`
polling normally measured within about 1 us, but still produced rare outliers
when ESP32 runtime work preempted its C polling loop. The current PoC rejects
out-of-range measurements, applies the three-sample median to valid
measurements, and then applies command confirmation. This is a measured
stock-runtime limitation, not input-source jitter.

Native polling is blocking and is not hardware edge capture. It is adequate for
this unloaded output check, but it is not evidence of deterministic timing
suitable for attached motors. On the measured 50 Hz source, expected command
transition latency is approximately 160 ms across alternating capture, median
acceptance, and the 80 ms command confirmation window. Signal-loss evaluation
is also subject to the 30 ms native capture timeout.

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
ESC simulator starting inputs=(1, 0) outputs=((4, 5), (6, 7)) motor_inverted=(False, True) motor_pwm_hz=20000 motor_max_duty_u16=65535 led=(8,) capture=time_pulse_us capture_timeout_us=30000 safety_hz_nominal=50 channel_hz_nominal=25 loop_sleep_ms=0 diag_ms=500 valid_us=900-2100 neutral_us=1500 neutral_db_us=50 endpoint_db_us=150 arm_ms=1000 arm_grace_ms=300 loss_latch_ms=1500 cmd_confirm_ms=80 pwm_filter=3
ESC diag t_ms=1234 reason=armed latch= fault= armed=1 failsafe=0 neutral_wait=0 neutral_ms=0 non_neutral_ms=0 loss_ms=0 raw=1000,0 cmd=1000,0 out=m0:a4=65535/b5=0,m1:a6=0/b7=0 led=0,255,0 ch0=2000us/v1/f1/age3ms/last2000us/cap31/rej0,ch1=1500us/v1/f1/age23ms/last1500us/cap30/rej0
```

Diagnostic fields:

- `v1` means the last captured pulse width was valid.
- `f1` means the last valid pulse is fresh enough for the failsafe window.
- `last` is the latest unfiltered native measurement. It may differ from the
  filtered width shown immediately after `ch0=` or `ch1=`.
- `cap` is the cumulative native capture count and `rej` is the cumulative
  count rejected for timeout or falling outside 900-2100 us.
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
- `out` is the actual H-bridge input PWM state derived from `cmd`. It reports
  duty_u16 for each output pin: `m0` is Motor 1 GPIO4/GPIO5 and `m1` is Motor 2
  GPIO6/GPIO7. Motor 2 is physically inverted, so its positive command appears
  on GPIO7 and its negative command appears on GPIO6.
- `led` is the RGB value written from the final safe command.

Restore stock after simulator testing:

```sh
just restore-stock
```

The simulator must preserve these safety boundaries:

- No plaintext firmware flashing to locked stock boards.
- Attached-motor tests require tracks lifted or the chassis otherwise
  restrained; never leave the PoC running unattended.
- GPIO4-GPIO7 may only be driven by final safe commands through
  `motor_output`; do not write those pins from input capture, LED code, or test
  probes.
- Startup and failsafe recovery require valid neutral input before commands.

### Electrical Measurements

Motors must stay disconnected for this PoC check. Use a multimeter in DC
voltage mode across the H-bridge motor output terminals, not in current mode
and not with a motor attached. Power the H-bridge motor supply through the
board's normal supported power input; USB power alone may not energize the
motor supply. Never apply external power directly to a motor output terminal.

Measure motor terminal voltage differentially:

| Check | Meter red lead | Meter black lead | Expected neutral | Expected full command |
| --- | --- | --- | --- | --- |
| Motor 1 | Motor 1 output terminal A | Motor 1 output terminal B | Near 0 V or floating, driver-dependent | Near motor supply voltage, sign depends on direction |
| Motor 2 | Motor 2 output terminal A | Motor 2 output terminal B | Near 0 V or floating, driver-dependent | Near motor supply voltage, sign depends on direction |

The exact sign depends on which physical terminal is under the red lead. If a
forward command reads negative, swap the meter leads or record that physical
polarity. Measuring either motor terminal relative to CyberBrick GND is less
useful for this check because the motor sees the voltage between the two output
terminals. Do not short the two terminals with a probe tip.

The software neutral contract is GPIO4-GPIO7 at zero duty. The H-bridge IC is
not identified in this repo, so its low/low output mode may be driven low or
high impedance. An unloaded neutral reading can therefore be near 0 V or
unstable/floating; use the full forward/reverse magnitude and polarity changes
as the decisive terminal-output evidence.

Recommended two-run procedure:

1. Keep both motors disconnected and power the board off.
2. Secure the meter leads across the Motor 1 output terminal pair.
3. Power the board through its normal motor-supply input, let the simulator
   start, then run the Raspberry Pi sequence below.
4. Record Motor 1 neutral, right-forward, and right-reverse readings. Forward and
   reverse should have similar magnitude and opposite sign.
5. Power the board off before moving the meter leads.
6. Secure the leads across the Motor 2 output terminal pair, power the board,
   rerun the sequence, and record left-forward and left-reverse readings.

Expected terminal behavior:

| Command state | Motor 1 terminal pair | Motor 2 terminal pair |
| --- | --- | --- |
| Neutral/off | Near 0 V or floating | Near 0 V or floating |
| Right forward | Near supply voltage, A-to-B polarity | About 0 V |
| Right reverse | Near supply voltage, B-to-A polarity | About 0 V |
| Left forward | About 0 V | Near supply voltage, B-to-A polarity |
| Left reverse | About 0 V | Near supply voltage, A-to-B polarity |
| Both forward | Near supply voltage, A-to-B polarity | Near supply voltage, B-to-A polarity |
| Both reverse | Near supply voltage, B-to-A polarity | Near supply voltage, A-to-B polarity |
| Pivot left/right | Near supply voltage | Near supply voltage with the opposite command direction |

The GPIO-level H-bridge input PWM can still be checked with a scope if needed.
Probe GPIO4-GPIO7 relative to CyberBrick GND only; do not attach a scope ground
clip to a motor terminal or any non-ground H-bridge node.

To verify the PWM signals at the CyberBrick input:

| Scope channel | Probe tip | Ground clip |
| --- | --- | --- |
| CH1 | S3 signal / GPIO1 | CyberBrick GND |
| CH2 | S4 signal / GPIO0 | CyberBrick GND |

The Raspberry Pi PWM source and CyberBrick must share that same ground. Use DC
coupling and confirm the high level does not exceed 3.3 V. Do not attach a scope
ground clip to a motor terminal or any non-ground H-bridge node.

GPIO8 is debug output only. Probing GPIO8 relative to CyberBrick GND shows
short WS2812 data bursts when the debug color changes; it does not expose
either numeric ESC command as a conventional PWM output.

Optional GPIO-level output probe points:

| Scope channel | Probe tip | Expected positive command | Expected negative command |
| --- | --- | --- | --- |
| CH1 | GPIO4 / Motor 1 input A | High/full-duty PWM at full command | Low |
| CH2 | GPIO5 / Motor 1 input B | Low | High/full-duty PWM at full command |
| CH3 | GPIO6 / Motor 2 input A | Low | High/full-duty PWM at full command |
| CH4 | GPIO7 / Motor 2 input B | High/full-duty PWM at full command | Low |

For neutral, failsafe, input loss, or a channel with command zero, both pins for
that motor should stay low.

### Raspberry Pi output sequence

Use the host-side sequence to exercise left/right motor directions, neutral
off, both-forward, both-reverse, and pivot patterns:

```sh
python3 host/raspi_s3_s4_output_sequence.py
```

Dry-run prints the expected CyberBrick diagnostics without touching Raspberry
Pi sysfs PWM:

```sh
python3 host/raspi_s3_s4_output_sequence.py --dry-run
```

The sequence covers these expected final command/output states:

| Step | S3 us | S4 us | Expected `cmd` | Expected `out` |
| ---: | ---: | ---: | --- | --- |
| Arm/off | 1500 | 1500 | `0,0` | `m0:a4=0/b5=0,m1:a6=0/b7=0` |
| Right/M1 forward | 2000 | 1500 | `1000,0` | `m0:a4=65535/b5=0,m1:a6=0/b7=0` |
| Right/M1 reverse | 1000 | 1500 | `-1000,0` | `m0:a4=0/b5=65535,m1:a6=0/b7=0` |
| Left/M2 forward | 1500 | 2000 | `0,1000` | `m0:a4=0/b5=0,m1:a6=0/b7=65535` |
| Left/M2 reverse | 1500 | 1000 | `0,-1000` | `m0:a4=0/b5=0,m1:a6=65535/b7=0` |
| Both forward | 2000 | 2000 | `1000,1000` | `m0:a4=65535/b5=0,m1:a6=0/b7=65535` |
| Both reverse | 1000 | 1000 | `-1000,-1000` | `m0:a4=0/b5=65535,m1:a6=65535/b7=0` |
| Pivot left | 2000 | 1000 | `1000,-1000` | `m0:a4=65535/b5=0,m1:a6=65535/b7=0` |
| Pivot right | 1000 | 2000 | `-1000,1000` | `m0:a4=0/b5=65535,m1:a6=0/b7=65535` |

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
host/
  raspi_s3_s4_output_sequence.py
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
      motor_output.py
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
- [MicroPython `machine.time_pulse_us`](https://docs.micropython.org/en/v1.23.0/library/machine.html#machine.time_pulse_us)
- [MicroPython 1.23 ESP32 RMT limitation](https://docs.micropython.org/en/v1.23.0/library/esp32.html#rmt)
