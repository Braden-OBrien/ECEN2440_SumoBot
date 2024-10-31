import time
# load the MicroPython pulse-width-modulation module for driving hardware
from machine import PWM, Pin

time.sleep(1) # Wait for USB to become ready

pwm_rate = 2000
ph = [Pin(9, Pin.OUT), Pin(7, Pin.OUT)]
en = [PWM(8, freq=pwm_rate, duty_u16 = 0), PWM(6, freq=pwm_rate, duty_u16 = 0)]

pwm = min(max(int(2**16 * abs(1)), 0), 65535)

while True:
    print("Motors Forward") # Print to REPL
    ph[0].low()
    ph[1].low()
    en[0].duty_u16(pwm)
    en[1].duty_u16(pwm)
    time.sleep(2)
    print("Motors OFF") # Print to REPL
    en[0].duty_u16(0)
    en[1].duty_u16(0)
    time.sleep(2)
    print("Motors Backward") # Print to REPL
    ph[0].high()
    ph[1].high()
    en[0].duty_u16(pwm)
    en[1].duty_u16(pwm)
    time.sleep(2)
    print("Motors OFF") # Print to REPL
    en[0].duty_u16(0)
    en[1].duty_u16(0)
    time.sleep(2)
    
    print("Motors Forward") # Print to REPL
    ph[0].low()
    ph[1].low()
    en[0].duty_u16(pwm)
    en[1].duty_u16(pwm)
    time.sleep(30)