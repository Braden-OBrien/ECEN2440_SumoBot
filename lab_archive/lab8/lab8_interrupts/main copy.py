import time
from machine import Pin

button = Pin(2, Pin.IN, Pin.PULL_DOWN)
interrupt_flag = 0

def callback(button):
    global interrupt_flag 
    interrupt_flag = 1
    
button.irq(trigger=button.IRQ_FALLING, handler=callback)

while True:
    if interrupt_flag == 1:
        print("Interrupt Occurred, Button Pressed!")
        interrupt_flag = 0