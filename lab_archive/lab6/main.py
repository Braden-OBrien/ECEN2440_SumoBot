import machine
from machine import Pin, Timer
import time


time.sleep(0.1)
start = time.ticks_ms()
start_freq = machine.freq()


led = Pin(25, Pin.OUT)

tim = Timer()
def tick(timer):
    #print("currently toggling")
    global led
    led.toggle()


tim.init(freq=2, mode=Timer.PERIODIC, callback=tick)

while True:
    continue