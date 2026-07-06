---
id: m-1
title: "Stock MicroPython ESC simulator PoC"
---

## Description

Prove that the stock CyberBrick MicroPython runtime can host a narrow ESC
simulator PoC without replacing the encrypted stock firmware. The milestone
uses a stock-tool workflow: manual REPL recovery when needed, `uv run
mpremote`, RAM blink, persistent boot blink, simulator deploy, and
restore-to-stock. Hardware validation confirms two-channel PWM input capture,
center-neutral safety mapping, failsafe behavior, and RGB LED feedback derived
from final safe ESC commands. Real H-bridge motor output is intentionally
excluded.
