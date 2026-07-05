# CyberBrick ESC

CyberBrick ESC is an open source Zephyr firmware project that repurposes CyberBrick Mini Tank hardware as a standard bidirectional brushed ESC interface.

The project goal is narrow: make the CyberBrick ESP32-C3 board and its onboard dual brushed motor driver behave like two standard center-neutral RC ESC channels for a flight controller or RC-style PWM source.

This project is a proof of concept. It is not intended for production deployment, unattended operation, or safety-certified use.

This is not CyberBrick stock firmware. It is not a rover controller, not a Bluetooth controller, not a UART motor adapter, and not a DShot or BLHeli ESC implementation.

## Current target

CyberBrick ESC targets this hardware combination:

- CyberBrick Multi-Function Core Board based on ESP32-C3.
- CyberBrick receiver and motor-driver board used in the Mini Tank.
- Onboard dual brushed H-bridge motor driver.
- Two standard RC PWM input signals from a flight controller.
- Two bidirectional brushed motor outputs, one per tank motor.

The firmware is intended to be built with stock Zephyr and stock Zephyr tooling wherever possible.

## Build, flash, and log workflow

The project uses `just` as a thin command runner around stock Zephyr tools.
Python tooling is installed into a local virtual environment with `uv`.

Required host commands before setup:

- `python3`
- `uv`
- `git`
- `just`
- `dtc`
- `screen`

Install the local Zephyr workspace, ESP-IDF checkout, Espressif tools, and Python tooling:

```sh
just install
```

`just install` resolves the latest stable non-release-candidate Zephyr and ESP-IDF tags from the official upstream repositories, creates `.venv`, initializes gitignored `.zephyr/` and `.esp-idf/` workspaces, installs Espressif tools into `.espressif/`, installs local ESP-IDF CMake and Ninja binaries, installs Python requirements with `uv pip`, and verifies that the local ESP32-C3 RISC-V toolchain is available.

Build the firmware:

```sh
just build
```

This runs:

```sh
cd .zephyr && IDF_PATH=../.esp-idf IDF_TOOLS_PATH=../.espressif ZEPHYR_TOOLCHAIN_VARIANT=cross-compile CROSS_COMPILE=<local-riscv32-esp-elf-prefix> ../.venv/bin/west -z zephyr build -p auto -b esp32c3_devkitm -d ../build ..
```

The build recipe exports ESP-IDF's local tool paths first, so CMake, Ninja, OpenOCD, esptool, and the ESP32-C3 RISC-V compiler come from gitignored project folders after setup. Zephyr still needs the devicetree compiler executable `dtc` from the host environment.

Remove generated build and test output while keeping installed toolchains and workspaces:

```sh
just clean
```

This removes `build/` and build-only ccache data, but leaves `.venv/`, `.zephyr/`, `.esp-idf/`, and `.espressif/` intact.

Flash the connected board:

```sh
just flash
```

The default flash device is:

```text
/dev/tty.usbmodem1101
```

Read firmware logs:

```sh
just log
```

This opens:

```sh
screen /dev/tty.usbmodem1101 115200
```

At this proof-of-concept stage, the required software validation is that the firmware builds on macOS with `just build`. Twister tests are not part of the active workflow.

## What it does

CyberBrick ESC reads standard hobby RC PWM signals and drives the CyberBrick brushed motor outputs as a dual bidirectional ESC.

Default behavior:

- Input 1 controls ESC channel 1.
- Input 2 controls ESC channel 2.
- Each input is a normal servo or ESC pulse signal.
- 1000 us means full reverse.
- 1500 us means stop / neutral.
- 2000 us means full forward.
- A configurable deadband around 1500 us is treated as stop.
- Values outside the configured valid range are rejected.
- If input is lost, both motors enter a safe stop state.

This makes the board useful as a small dual brushed ESC for flight controllers that can output normal center-neutral PWM motor or servo signals.

## Project direction

The development stream is forward-only, not the motor direction.

In this project, forward-only development means:

- Build one Zephyr-native firmware path.
- Prefer stock Zephyr APIs and tooling.
- Do not maintain parallel Arduino, ESP-IDF application, MicroPython, or CyberBrick-stock-compatible implementations.
- Do not add compatibility shims for obsolete internal designs unless they directly support the current Zephyr ESC architecture.

Motor control itself is bidirectional.

## What it does not do

CyberBrick ESC intentionally does not implement these features in the initial scope:

- MAVLink.
- MSP.
- CRSF.
- SBUS.
- iBUS.
- UART command input.
- DShot input.
- OneShot input.
- Multishot input.
- BLHeli compatibility.
- Wi-Fi or Bluetooth control.
- CyberBrick stock protocol compatibility.
- Autonomous rover logic.
- Navigation, stabilization, odometry, or path planning.

Those features can be discussed later, but the first project shape is a bidirectional center-neutral PWM ESC.

## Hardware pin map

### PWM input pins

Use the CyberBrick receiver shield servo signal pins as input from the flight controller.

| Function | CyberBrick connector | ESP32-C3 GPIO | Notes |
| --- | --- | ---: | --- |
| ESC input 1 | Servo S3 signal | GPIO1 | Recommended default input |
| ESC input 2 | Servo S4 signal | GPIO0 | Recommended default input |
| Optional input | Servo S1 signal | GPIO3 | Usable if needed |
| Avoid by default | Servo S2 signal | GPIO2 | ESP32-C3 strapping pin |

Recommended wiring:

```text
Flight controller OUT1 signal -> CyberBrick S3 signal -> GPIO1
Flight controller OUT2 signal -> CyberBrick S4 signal -> GPIO0
Flight controller GND         -> CyberBrick GND
Flight controller 5V/red wire  -> not connected
```

Use signal and ground only unless the power topology has been verified.

The servo header has a 5 V power rail for servos, but the ESP32-C3 GPIO signal pins are 3.3 V logic. Do not feed a 5 V PWM signal into an ESP32-C3 GPIO. If the flight controller output is 5 V, use a level shifter or resistor divider.

### Motor output pins

The onboard brushed motor driver is controlled by two GPIO/PWM inputs per motor.

| Function | ESP32-C3 GPIO | Direction in this firmware |
| --- | ---: | --- |
| Motor 1 input A | GPIO4 | PWM output or static level |
| Motor 1 input B | GPIO5 | PWM output or static level |
| Motor 2 input A | GPIO6 | PWM output or static level |
| Motor 2 input B | GPIO7 | PWM output or static level |

Each motor uses a two-input H-bridge model:

| Command | Input A | Input B |
| --- | --- | --- |
| Forward | PWM | Low |
| Reverse | Low | PWM |
| Brake stop | High | High |
| Coast stop | Low | Low |

If a motor spins in the wrong physical direction, fix it with the configured motor inversion option or swap the motor wires. Do not change the public input convention. The default public convention remains 1000 us reverse, 1500 us stop, and 2000 us forward.

## ESC signal model

CyberBrick ESC uses normal hobby PWM timing, not UART.

Default input interpretation:

| Pulse width | Meaning |
| ---: | --- |
| less than 900 us | invalid |
| 1000 us | full reverse |
| 1000 to 1500 us | proportional reverse command |
| 1500 us | neutral / stop |
| 1500 to 2000 us | proportional forward command |
| 2000 us | full forward |
| greater than 2100 us | invalid |

Suggested defaults:

- Minimum valid pulse: 900 us.
- Maximum valid pulse: 2100 us.
- Minimum command pulse: 1000 us.
- Neutral command pulse: 1500 us.
- Maximum command pulse: 2000 us.
- Neutral deadband: 25 us to 50 us.
- Input timeout: 100 ms to 250 ms.
- Control loop rate: 100 Hz to 400 Hz.
- Motor PWM output frequency: start at 1 kHz, allow configuration up to ultrasonic ranges after testing.

Normalized command mapping:

```text
1000 us -> -1000
1500 us -> 0
2000 us -> +1000
```

Values between those points are mapped linearly. Values inside the neutral deadband are mapped to zero.

## Operating modes

### Direct dual ESC mode

Direct mode is the default.

```text
Input 1 -> Motor 1 command
Input 2 -> Motor 2 command
```

This is the best default for a flight controller that already performs skid-steer, differential-drive, or rover mixing.

### Optional throttle / steering mode

Throttle / steering mode may be added as a configuration option, but it is not required for the first bring-up.

```text
Input 1 -> throttle
Input 2 -> steering
left  = throttle + steering
right = throttle - steering
```

The mixed result must be clamped to the normalized command range of -1000 to +1000.

This mode is convenience logic only. CyberBrick ESC should still remain an ESC-style firmware, not a rover controller.

## Safety behavior

The firmware must be safe before it is useful.

Required safety behavior:

- Motors are stopped before PWM input capture is enabled.
- Motors are stopped if hardware initialization fails.
- Motors are stopped if no valid pulse is received within the configured timeout.
- Motors remain stopped after boot until both inputs have been valid and neutral for the configured arming time.
- Motors remain stopped after failsafe until the same neutral arming condition is met again.
- Malformed, missing, or out-of-range input pulses do not refresh the failsafe timer.
- Stop behavior is configurable as coast or brake.
- The default stop behavior should be conservative and documented.
- Motor inversion must not change the public input meaning. It only changes physical output polarity.

Bench testing should be done with the tank lifted, tracks removed, or motors disconnected.

## Hardware validation

Use `/dev/tty.usbmodem1101` for the currently connected device unless `DEVICE` is overridden:

```sh
DEVICE=/dev/tty.usbmodem1101 just flash
DEVICE=/dev/tty.usbmodem1101 just log
```

Before flashing or sending input signals, make the motor outputs physically safe:

- Disconnect motors, remove tracks, or lift the tank so the tracks cannot move the vehicle.
- Use a current-limited supply during bring-up.
- Confirm the flight-controller PWM signal is 3.3 V safe before connecting it to GPIO0 or GPIO1.
- Start with both inputs at neutral and verify the firmware logs an armed state only after the neutral arming delay.
- Verify input loss and invalid pulse widths stop both motors before testing nonzero commands.

## Software architecture

Expected modules:

```text
src/main.c
src/pwm_input.c
src/motor_output.c
src/safety.c
include/pwm_input.h
include/motor_output.h
include/safety.h
boards/
app.overlay
prj.conf
CMakeLists.txt
```

### `pwm_input`

Responsibilities:

- Configure GPIO inputs for ESC pulse capture.
- Use GPIO interrupts on rising and falling edges.
- Measure high pulse width in microseconds.
- Reject invalid pulses.
- Publish the latest valid pulse width for each channel.
- Avoid blocking work inside interrupt handlers.

### `motor_output`

Responsibilities:

- Configure four motor-driver pins.
- Use Zephyr PWM APIs for motor speed output where practical.
- Support signed bidirectional motor commands in the normalized range -1000 to +1000.
- Support per-channel inversion.
- Support per-channel scaling and limiting.
- Support coast and brake stop modes.
- Never leave motor pins floating.

### `safety`

Responsibilities:

- Enforce arming.
- Enforce failsafe timeout.
- Enforce neutral-before-arm.
- Convert pulse widths to signed normalized commands.
- Clamp commands.
- Apply deadband.
- Apply slew-rate limits if enabled.

## Zephyr tooling

Use stock Zephyr tooling first.

Expected tools:

- Local `.zephyr/` West workspace installed by `just install`.
- Local `.esp-idf/` checkout and `.espressif/` Espressif tools installed by `just install`.
- `west` in the project `.venv` for workspace management, build, flash, and debug.
- CMake and Ninja through Zephyr or locally installed Espressif tools.
- Devicetree overlays for pin assignments.
- Kconfig for firmware options.
- Zephyr GPIO API for PWM input edge interrupts.
- Zephyr PWM API for ESP32-C3 LEDC motor output.
- macOS firmware build validation with `just build`.

Avoid project-specific build scripts unless they wrap standard Zephyr commands and remain optional.

Example commands:

```sh
just install
just build
just clean
just flash
just log
```

A custom board definition can be added later as `cyberbrick_esc_esp32c3`, but early development may use an existing ESP32-C3 Zephyr board target plus an application overlay.

## Configuration

Initial firmware configuration should be exposed through Kconfig and devicetree rather than hard-coded constants.

Suggested Kconfig options:

```text
CONFIG_CYBERBRICK_ESC_INPUT_TIMEOUT_MS
CONFIG_CYBERBRICK_ESC_ARMING_TIME_MS
CONFIG_CYBERBRICK_ESC_MIN_VALID_US
CONFIG_CYBERBRICK_ESC_MAX_VALID_US
CONFIG_CYBERBRICK_ESC_MIN_COMMAND_US
CONFIG_CYBERBRICK_ESC_NEUTRAL_US
CONFIG_CYBERBRICK_ESC_MAX_COMMAND_US
CONFIG_CYBERBRICK_ESC_DEADBAND_US
CONFIG_CYBERBRICK_ESC_OUTPUT_PWM_HZ
CONFIG_CYBERBRICK_ESC_STOP_MODE_BRAKE
CONFIG_CYBERBRICK_ESC_STOP_MODE_COAST
CONFIG_CYBERBRICK_ESC_MOTOR1_INVERT
CONFIG_CYBERBRICK_ESC_MOTOR2_INVERT
CONFIG_CYBERBRICK_ESC_SLEW_LIMIT_ENABLE
CONFIG_CYBERBRICK_ESC_MIXING_MODE_DIRECT
CONFIG_CYBERBRICK_ESC_MIXING_MODE_THROTTLE_STEERING
```

## Development milestones

### Milestone 0: Board bring-up

- Build a minimal Zephyr application for ESP32-C3.
- Disable conflicting console or logging pins.
- Confirm safe GPIO startup state.
- Confirm flashing and recovery workflow.

### Milestone 1: Motor output only

- Drive Motor 1 and Motor 2 in both directions under controlled test commands.
- Implement brake and coast stop modes.
- Validate output polarity with motors unloaded.
- Validate motor inversion settings.

### Milestone 2: PWM input only

- Capture pulse width on GPIO1 and GPIO0.
- Print or inspect measured pulse widths through a safe debug path.
- Validate input timeout behavior.
- Validate neutral detection.

### Milestone 3: Closed ESC behavior

- Map valid input pulse widths to signed motor commands.
- Add neutral-before-arm logic.
- Add failsafe logic.
- Add command clamping and deadband.
- Confirm 1000 us reverse, 1500 us stop, and 2000 us forward.

### Milestone 4: Tests and documentation

- Add unit tests for pulse mapping and safety state transitions.
- Add integration notes for common flight controller configurations.
- Document measured electrical behavior of servo headers.

## Flight controller setup notes

Configure the flight controller output protocol as normal PWM or servo PWM with center-neutral bidirectional behavior.

Do not use DShot, OneShot, Multishot, or a digital ESC protocol with this firmware. CyberBrick ESC expects timed PWM pulses on GPIO inputs.

For ArduPilot Rover or another rover-capable flight controller, a skid-steer setup can output separate left and right motor commands. In that case, use direct mode: one flight controller output per CyberBrick ESC input.

Confirm that the output signal voltage is safe for 3.3 V ESP32-C3 GPIO.

## License

Pick an open source license before accepting contributions. Recommended options:

- Apache-2.0 if you want alignment with Zephyr's licensing style.
- MIT if you want a shorter permissive license.

## Disclaimer

CyberBrick ESC is an independent open source firmware project. It is not affiliated with, endorsed by, or supported by Bambu Lab or the CyberBrick product team.

Flashing third-party firmware can make the board unusable without recovery tools. Motors can start unexpectedly during firmware development. Test with the vehicle restrained and use a current-limited power source during bring-up.
