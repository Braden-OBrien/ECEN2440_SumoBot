from machine import Pin
import time

counter = 0
debounce = 0
button = Pin(5, Pin.IN, Pin.PULL_UP)

while True:
    if (button.value() == 0) and ((time.ticks_ms()-debounce) > 500):
        print("Button Pressed")
        counter += 1
        debounce = time.ticks_ms()
        print("counter =", counter)