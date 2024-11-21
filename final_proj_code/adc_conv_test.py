from machine import Pin, ADC
import time
import adc_conv

time.sleep(0.1)

bat_pin_in = ADC(Pin(26, Pin.IN))
#gnd_pin_in = ADC(Pin(27, Pin.IN))
#ref_pin_in = ADC(Pin(27, Pin.IN))

while True:
    time.sleep(5)
    print('current battery sample is', adc_conv.sample_battery(bat_sample_time=0.1, pin=bat_pin_in))
    #print('current ref sample is', adc_conv.sample_battery(bat_sample_time=0.1, pin=ref_pin_in))
    #print('current gnd sample is', adc_conv.sample_battery(bat_sample_time=0.1, pin=gnd_pin_in))