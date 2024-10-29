import machine
from machine import Pin, Timer
import time


time.sleep(0.1)

inputs = [Pin(i, Pin.IN) for i in [11, 12, 15, 14]]
leds = [Pin(i, Pin.OUT) for i in [21, 18, 19, 20]]

interrupt_flags = [0 for i in range(len(inputs))]

def callback(input):
    global interrupt_flags
    global inputs
    
    index = inputs.index(input)
    print('input received on', index)
    interrupt_flags[index] = 1


for input in inputs:
    input.irq(trigger=input.IRQ_RISING, handler=callback)


while True:
    if sum(interrupt_flags) != 0:
        for i in range(len(interrupt_flags)):
            if interrupt_flags[i] == 1:
                print('toggling led on', i)
                leds[i].toggle()
                interrupt_flags[i] = 0
    continue