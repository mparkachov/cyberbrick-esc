# CyberBrick ESC

CyberBrick ESC is a proof-of-concept project for making CyberBrick Mini Tank
hardware behave like a standard center-neutral dual brushed ESC.

This branch is now focused on a stock-firmware MicroPython PoC. It uses the
existing MicroPython REPL and filesystem on the observed stock CyberBrick
ESP32-C3 board instead of replacing firmware.

This project is not production-ready, not safety-certified, and not suitable for
unattended operation.

## Current result

The previous Zephyr ESC architecture is technically feasible and is preserved on
`origin/backup/zephyr`. It builds on macOS, but the observed stock CyberBrick
board is not usable for plaintext Zephyr flashing: ESP32-C3 ROM flashing reports
Secure Download Mode with flash encryption enabled, and esptool refuses to write
the plaintext image because doing so can make the board unusable.

For stock CyberBrick boards in that state:

- Do not force-flash plaintext firmware.
- Treat the board as not Zephyr-flashable unless a maintainer provides an
  approved signed/encrypted or vendor-compatible update flow.
- Use this MicroPython PoC only through the existing REPL/filesystem.

The active milestone is `m-1`: stock MicroPython ESC simulator PoC.

## Scope

The current MicroPython milestone is visual-first:

```text
Two center-neutral RC PWM inputs -> safe command mapping -> RGB LED feedback
```

Default public signal behavior:

```text
1000 us -> full reverse
1500 us -> stop / neutral
2000 us -> full forward
```

The MicroPython app does not drive the real H-bridge motor outputs. GPIO4-GPIO7
are intentionally unused in this milestone. Real motor output requires a later
maintainer-approved task after hardware measurements and safety review.

## Hardware contract

Known target hardware:

- MCU: ESP32-C3 on CyberBrick Multi-Function Core Board.
- Runtime: stock CyberBrick MicroPython firmware with REPL access.
- LED: one onboard WS2812/NeoPixel RGB LED, currently treated as GPIO8.
- Inputs: standard hobby PWM signal pins from a flight controller or signal
  generator.

Default pins:

| Function | Connector | GPIO |
| --- | --- | ---: |
| ESC input 1 | Servo S3 signal | GPIO1 |
| ESC input 2 | Servo S4 signal | GPIO0 |
| Onboard RGB LED | Board LED | GPIO8 |

Reserved pins:

| Function | GPIO |
| --- | ---: |
| Motor 1 input A | GPIO4 |
| Motor 1 input B | GPIO5 |
| Motor 2 input A | GPIO6 |
| Motor 2 input B | GPIO7 |

Keep motors disconnected, tracks removed, or the vehicle physically unable to
move during bring-up. Confirm input signals are 3.3 V safe before connecting
them to ESP32-C3 GPIO pins.

## Workflow

Install local MicroPython tooling:

```sh
just install
```

This creates `.venv` and installs `mpremote` from `requirements.txt`.

List available MicroPython devices:

```sh
just mp-list
```

Open the REPL:

```sh
just mp-repl
```

`just mp-repl` sends Ctrl-C first, so it should land at the REPL prompt even
when the stock app is printing startup logs.

The default device is `auto`. Override it when needed:

```sh
DEVICE=/dev/tty.usbmodem1101 just mp-repl
```

Back up the current board filesystem before deploying:

```sh
just mp-backup
```

Backups are saved under gitignored `device-backups/`. Backup, deploy, stop, and
restore recipes first send Ctrl-C to the serial port because the stock
CyberBrick script may be running; this mirrors the manual step needed to drop to
the REPL before raw filesystem operations. The recipes then call `mpremote
resume` so mpremote does not soft-reset the board and restart the stock script
before filesystem access.

Deploy the persistent onboard LED blink:

```sh
just deploy-blink
```

This backs up the board filesystem, copies
`micropython/examples/blink_main.py` to remote `main.py`, and resets the board.
After deployment, the LED should blink after board reset or power-on without any
additional host command.

Deploy the ESC simulator:

```sh
just deploy
```

This backs up the board filesystem, copies `micropython/main.py` and
`micropython/lib/cyberbrick_esc/` to the board, and resets it.

Stop the deployed app and recover REPL startup:

```sh
just mp-stop
```

Restore the latest local backup:

```sh
just mp-restore
```

Run host checks:

```sh
just test
```

## Simulator behavior

Input decoding:

- Valid pulse range: 900 us to 2100 us.
- Command range: 1000 us to 2000 us.
- Neutral: 1500 us.
- Neutral deadband: 50 us on each side of neutral.
- Failsafe timeout: 150 ms.
- Neutral arming time: 1000 ms.
- Control loop: 200 Hz.

Safety behavior:

- Missing, stale, malformed, or invalid input produces safe zero commands.
- Startup requires both channels to be valid and neutral before arming.
- Failsafe recovery also requires valid neutral input before re-arming.
- Invalid pulse widths do not update the last-valid sample timestamp.

RGB LED feedback is derived from final safe commands:

- Blue: neutral or exact opposing direction tie.
- Green: dominant final command is forward.
- Red: dominant final command is reverse.
- Green/red intensity reflects command magnitude.

The LED is visual feedback only. It does not arm the app, change failsafe state,
or control motor outputs.

## Layout

```text
justfile
requirements.txt
micropython/
  main.py
  examples/
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
backlog/
  milestones/
  tasks/
```

## Unsupported

Do not add these features by default:

- Plaintext firmware flashing to locked stock boards.
- Real H-bridge motor output in the current MicroPython milestone.
- MAVLink, MSP, CRSF, SBUS, iBUS, DShot, OneShot, or Multishot input.
- UART command input.
- Wi-Fi control, Bluetooth control, web UI, or OTA update logic.
- CyberBrick stock protocol compatibility.
- Autonomous rover behavior, navigation, odometry, stabilization, or path
  planning.

## References

- [MicroPython mpremote](https://docs.micropython.org/en/latest/reference/mpremote.html)
- [MicroPython reset and boot sequence](https://docs.micropython.org/en/latest/reference/reset_boot.html)
- [MicroPython NeoPixel](https://docs.micropython.org/en/latest/library/neopixel.html)
- [MicroPython Pin IRQ](https://docs.micropython.org/en/latest/library/machine.Pin.html)
