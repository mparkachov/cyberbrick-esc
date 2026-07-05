---
id: m-1
title: "Stock MicroPython ESC simulator PoC"
---

## Description

Prove that the stock CyberBrick MicroPython runtime can host a narrow ESC simulator PoC without replacing the encrypted stock firmware. The milestone starts with a persistent onboard RGB LED blink and then adds two-channel PWM input capture, center-neutral safety mapping, failsafe behavior, and RGB LED feedback for final safe ESC commands. Real H-bridge motor output is intentionally excluded.
