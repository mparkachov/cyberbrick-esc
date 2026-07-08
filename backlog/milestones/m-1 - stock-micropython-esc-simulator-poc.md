---
id: m-1
title: "Stock MicroPython ESC simulator PoC"
---

## Description

Prove that the stock CyberBrick MicroPython runtime can host a narrow ESC
simulator PoC without replacing the encrypted stock firmware. The milestone
uses a stock-tool workflow: manual REPL recovery when needed, `uv run
mpremote`, RAM blink, persistent boot blink, simulator deploy, and
restore-to-stock. Scope and RAM-probe testing established native
`machine.time_pulse_us` polling as more accurate than scheduled Python GPIO
callbacks, while also documenting rare stock-runtime preemption outliers.
Integrated native-capture validation confirms the deployed app starts after
reset/power-cycle and follows neutral, forward, reverse, opposing-tie, and
input-loss behavior through final safe commands and RGB debug feedback. The
milestone is now extended with an unloaded H-bridge input PWM probe on
GPIO4-GPIO7; attached motor-load operation remains excluded until those output
signals are measured and reviewed.
