---
id: TASK-2.10
title: Unloaded H-Bridge Motor Voltage Check
status: In Progress
assignee: []
created_date: '2026-07-08 21:00'
updated_date: '2026-07-08 21:00'
labels:
  - micropython
  - hardware
  - output
dependencies:
  - TASK-2.9
modified_files:
  - AGENTS.md
  - README.md
  - micropython/lib/cyberbrick_esc/app.py
  - micropython/lib/cyberbrick_esc/config.py
  - micropython/lib/cyberbrick_esc/motor_output.py
  - host/raspi_s3_s4_output_sequence.py
  - justfile
  - tests/test_app_skeleton.py
  - tests/test_led.py
  - tests/test_motor_output.py
parent_task_id: TASK-2
milestone: m-1
priority: high
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Generate unloaded H-bridge input PWM from the final safe command stream so the
software output state can be inspected in logs and the H-bridge motor output
terminals can be measured with a multimeter before any motor load is attached.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Config defines Motor 1 output pins GPIO4/GPIO5 and Motor 2 output pins GPIO6/GPIO7.
- [x] #2 Output PWM is driven only from final safe commands after arming, failsafe, and command confirmation.
- [x] #3 Vehicle-positive command drives Motor 1 input A and Motor 2 input B; vehicle-negative command drives Motor 1 input B and Motor 2 input A, matching Mini Tank polarity.
- [x] #4 Neutral, stale input, input loss, and hard-fault states drive both pins low for each motor.
- [x] #5 Diagnostics print `out=` duty_u16 values for GPIO4-GPIO7.
- [x] #6 Host tests cover output pin config, command-to-duty mapping, neutral/malformed safe output, direction changes, and app dataflow.
- [x] #7 Raspberry Pi output sequence exercises left/right forward, left/right reverse, neutral/off, both-forward, both-reverse, and pivot patterns.
- [ ] #8 Hardware validation confirms unloaded motor terminal voltage matches diagnostics with no motor attached.
- [x] #9 Published Mini Tank configuration is documented as Motor 1/right positive polarity and Motor 2/left negative polarity.
- [ ] #10 Restrained motor validation confirms both-forward, both-reverse, pivot-left, and pivot-right vehicle motion.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
This task intentionally starts with unloaded H-bridge validation. Do not attach
motors until the motor output terminal pairs have been measured with a DC
multimeter and the results match the `out=` diagnostics. Attached-motor checks
must keep tracks lifted or otherwise prevent vehicle movement.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implementation is complete in the repo. `motor_output` initializes GPIO4-GPIO7
as 20 kHz PWM outputs, drives only one side of each H-bridge input pair at a
time, maps command magnitude to duty_u16, skips redundant steady-state PWM
writes, and falls back to both-low output for neutral or malformed command
values. `app` applies output PWM immediately after `Safety.update(...)` and
before LED debug feedback, then prints the applied output duty values in
`ESC diag ... out=...`.

Deployed hardware diagnostics confirm the software output state follows final
safe commands with no motor attached: neutral and waiting states report all
zeros, `cmd=1000,0` reports `m0:a4=65535/b5=0,m1:a6=0/b7=0`, `cmd=-1000,0`
reports `m0:a4=0/b5=65535,m1:a6=0/b7=0`, and loss-pending and latched
input-loss states report all zeros.

Full command output is back to duty_u16 `65535` for the final unloaded voltage
check. `host/raspi_s3_s4_output_sequence.py` provides a Raspberry Pi sequence
and dry-run output covering left/right forward, left/right reverse,
both-forward, both-reverse, neutral/off, and pivot patterns.

Attached-motor testing showed the original identical electrical polarity made
the mirrored Mini Tank tracks rotate in opposite vehicle directions for equal
commands. The published Mini Tank configuration maps Motor 1/right positive and
Motor 2/left negative. `MOTOR_OUTPUT_INVERTED=(False, True)` now preserves
vehicle-level command semantics while translating Motor 2 polarity:
`cmd=0,1000` reports `m1:a6=0/b7=65535`, `cmd=0,-1000` reports
`m1:a6=65535/b7=0`, `cmd=1000,1000` reports
`m0:a4=65535/b5=0,m1:a6=0/b7=65535`, and `cmd=-1000,-1000` reports
`m0:a4=0/b5=65535,m1:a6=65535/b7=0`. Restrained physical direction validation
remains open.
<!-- SECTION:FINAL_SUMMARY:END -->
