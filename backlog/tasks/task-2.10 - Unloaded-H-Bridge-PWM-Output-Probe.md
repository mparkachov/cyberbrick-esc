---
id: TASK-2.10
title: Unloaded H-Bridge PWM Output Probe
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
output pins can be inspected in logs and measured with a scope before any motor
load is attached.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Config defines Motor 1 output pins GPIO4/GPIO5 and Motor 2 output pins GPIO6/GPIO7.
- [x] #2 Output PWM is driven only from final safe commands after arming, failsafe, and command confirmation.
- [x] #3 Positive command drives the A pin with PWM and keeps the B pin low; negative command keeps the A pin low and drives the B pin with PWM.
- [x] #4 Neutral, stale input, input loss, and hard-fault states drive both pins low for each motor.
- [x] #5 Diagnostics print `out=` duty_u16 values for GPIO4-GPIO7.
- [x] #6 Host tests cover output pin config, command-to-duty mapping, neutral/malformed safe output, direction changes, and app dataflow.
- [x] #7 Raspberry Pi output sequence exercises left/right forward, left/right reverse, neutral/off, both-forward, both-reverse, and pivot patterns.
- [ ] #8 Hardware scope validation confirms GPIO4-GPIO7 match diagnostics with no motor attached.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
This task intentionally starts with unloaded H-bridge input probing. Do not
attach motors until GPIO4-GPIO7 have been measured relative to CyberBrick GND
and the results match the `out=` diagnostics.
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
reports `m0:a4=0/b5=65535,m1:a6=0/b7=0`, and `cmd=1000,-1000` reports
`m0:a4=65535/b5=0,m1:a6=0/b7=65535`. Loss-pending and latched input-loss states
report all zeros.

For the next scope experiment, full command output is capped at duty_u16
`16384` instead of `65535`, so endpoint commands should visibly pulse at about
25% duty rather than appearing steady high. `host/raspi_s3_s4_output_sequence.py`
now provides a Raspberry Pi sequence and dry-run output covering left/right
forward, left/right reverse, both-forward, both-reverse, neutral/off, and pivot
patterns.

The full sequence diagnostics confirm the expected software output states for
all four pins, including right-motor phases: `cmd=0,1000` reports
`m1:a6=16384/b7=0`, `cmd=0,-1000` reports `m1:a6=0/b7=16384`,
`cmd=1000,1000` reports `m0:a4=16384/b5=0,m1:a6=16384/b7=0`,
`cmd=-1000,-1000` reports `m0:a4=0/b5=16384,m1:a6=0/b7=16384`, and pivot
patterns drive opposite sides as expected. Scope validation has confirmed clear
PWM on GPIO4 and GPIO5 with no motor attached. Hardware scope validation
remains open until GPIO6 and GPIO7 are also measured relative to CyberBrick GND
and confirmed to match these diagnostics.
<!-- SECTION:FINAL_SUMMARY:END -->
