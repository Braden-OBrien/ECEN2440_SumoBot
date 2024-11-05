import math, time
import machine
# load the MicroPython pulse-width-modulation module for driving hardware
from machine import PWM
from machine import Pin
# IR Receiver Library
import ir_rx
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging


# Callback function to execute when an IR code is received
def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")  
   
# Setup the IR receiver
ir_pin = Pin(10, Pin.IN, Pin.PULL_UP) # Adjust the pin number based on your wiring
ir_receiver = NEC_8(ir_pin, callback=ir_callback)


# Optional: Use the print_error function for debugging
ir_receiver.error_function(print_error)




time.sleep(1) # Wait for USB to become ready
led = Pin(18, Pin.OUT)


pwm_rate = 2000
ain1_ph = Pin(12, Pin.OUT) # Initialize GP12 as an OUTPUT
ain2_en = PWM(Pin(15), freq = pwm_rate, duty_u16 = 0)
bin1_ph = Pin(13, Pin.OUT) # Initialize GP14 as an OUTPUT
bin2_en = PWM(Pin(14), freq = pwm_rate, duty_u16 = 0)




pwm = min(max(int(2**16 * abs(1)), 0), 65535)


while True:
    pass # Execution is interrupt-driven, so just keep the script alive
    for i in range(2):
        # time.sleep(2)
        print("Motor A - Forward") # Print to REPL
        ain1_ph.low()
        ain2_en.duty_u16(pwm)
        led.value(1)
        time.sleep(2)
       
        print("Motor A - Backward") # Print to REPL
        ain1_ph.high()
        ain2_en.duty_u16(pwm)
        time.sleep(2)
       
        print("Motor A OFF") # Print to REPL
        ain1_ph.low()
        ain2_en.duty_u16(0)
        led.value(0)
        time.sleep(1)
       
        print("Motor B - Forward") # Print to REPL
        bin1_ph.low()
        bin2_en.duty_u16(pwm)
        led.value(1)
        time.sleep(2)
       
        print("Motor B - Backward") # Print to REPL
        bin1_ph.high()
        bin2_en.duty_u16(pwm)
        time.sleep(2)
       
        print("Motor B OFF") # Print to REPL
        bin1_ph.low()
        bin2_en.duty_u16(0)
        led.value(0)
        time.sleep(1)
       
    print("Sequence Finished. Press 'CTRL' + 'C'")
    time.sleep(10)