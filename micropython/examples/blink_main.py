from machine import Pin
from neopixel import NeoPixel
from time import sleep_ms


LED_PIN = 8
LED_COUNT = 1
STEP_MS = 300


def show(pixel, color):
    pixel[0] = color
    pixel.write()


pixel = NeoPixel(Pin(LED_PIN, Pin.OUT), LED_COUNT)

while True:
    show(pixel, (32, 0, 0))
    sleep_ms(STEP_MS)
    show(pixel, (0, 32, 0))
    sleep_ms(STEP_MS)
    show(pixel, (0, 0, 32))
    sleep_ms(STEP_MS)
    show(pixel, (0, 0, 0))
    sleep_ms(STEP_MS)
