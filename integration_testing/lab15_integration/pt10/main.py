from machine import Pin
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging
import time


time.sleep(0.1)

#Global constants
debounce_time = 100 #50ms debounce timer

#Assigning Pinouts
rf_inputs = [Pin(i, Pin.IN) for i in [11, 12, 15, 14]]
ir_input = Pin(13, Pin.IN, Pin.PULL_UP)
input_toggle_btn = Pin(10, Pin.IN, Pin.PULL_DOWN)
leds = [Pin(i, Pin.OUT) for i in [21, 18, 19, 20]]


#Interrupt flags
led_interrupt_flags = [0 for i in range(len(rf_inputs))]
input_toggle = 1 # 1 - RF Receiver | 0 - IR Receiver

#Defining ISRs
def rf_ISR(input):
    global interrupt_flags
    global inputs
    
    index = rf_inputs.index(input)
    print('rf input received on', index)
    led_interrupt_flags[index] = 1
    
def ir_ISR(data, addr_, _):
    global led_interrupt_flags
    
    if addr_ > range(len(rf_inputs)):
        return
    else:
        print('ir input received on', addr_, 'with data', data)
        led_interrupt_flags[int(addr_)] = data

debounce = 0
def input_toggle_ISR(btn):
    global input_toggle
    global debounce
    
    if (time.ticks_ms() - debounce > debounce_time):
        input_toggle = not input_toggle
        print('input toggle is now', input_toggle)
        debounce = time.ticks_ms()

#Assigning IRQs
for input in rf_inputs:
    input.irq(trigger=input.IRQ_RISING, handler=rf_ISR)
    
ir_receiver = NEC_8(ir_input, callback=ir_ISR)

input_toggle_btn.irq(trigger=input_toggle_btn.IRQ_FALLING, handler=input_toggle_ISR)

#Main loop
while True:
    if sum(led_interrupt_flags) != 0:
        for i in range(len(led_interrupt_flags)):
            if led_interrupt_flags[i] != 0:
                if input_toggle:
                    #RF handler
                    print('toggling led on', i)
                    leds[i].toggle()
                    led_interrupt_flags[i] = 0
                else:
                    #IR handler
                    print('toggling led on', i)
                    print('ir data is', led_interrupt_flags[i])
                    leds[i].toggle()
                    led_interrupt_flags[i] = 0
    continue