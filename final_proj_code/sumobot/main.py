from machine import Pin, PWM, ADC, Timer
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error
#from ir_rx.print_error import print_error # for debugging
import adc_conv
import time
import os

time.sleep(0.1)

#IR Transmitter Testing
#addr = 0x21
#commands = [0x1]
#ir_transmitter = NEC(Pin(16, Pin.OUT, value=0))


#Global constants
but_debounce_time = 100 #50ms debounce timer
rf_deb_tim = Timer()
bat_sample_time = 100
pwm_rate = 2000
pwm = [min(max(int(2**16 * abs(1)), 0), 60000), min(max(int(2**16 * abs(1)), 0), 60000)]
curr_motor_cond = -1

#Assigning Pinouts
rf_inputs = [Pin(i, Pin.IN) for i in [6, 4, 7, 5]] #6, 4, 7, 5
ir_input = Pin(18, Pin.IN, Pin.PULL_UP)
bat_low_led = Pin(3, Pin.OUT)
#input_toggle_btn = Pin(10, Pin.IN, Pin.PULL_DOWN)
#leds = [Pin(i, Pin.OUT) for i in [21, 18, 19, 20]]
bat_pin_in = ADC(Pin(28, Pin.IN))

ph = [Pin(12, Pin.OUT), Pin(14, Pin.OUT)]
en = [PWM(13, freq=pwm_rate, duty_u16 = 0), PWM(15, freq=pwm_rate, duty_u16 = 0)]

#Battery Vars
min_bat_volt = 6.8  #Going below 3.2V/cell is dangerous, set to 3.4V/cell for safety
operating = True
bat_low_led.value(0)

#Interrupt flags
rf_interrupt_flags = []
ir_interrupt_flags = []
input_toggle = 1 # 1 - RF Receiver | 0 - IR Receiver

def send_command(input):
    global rf_interrupt_flags, ir_interrupt_flags, rf_inputs, input_toggle
    if (input_toggle):
        index = rf_inputs.index(input)
        print('RF input received on', index)
        rf_interrupt_flags.append(index)
    else:
        print('IR signal is', input)
        ir_interrupt_flags.append(int(input))


rf_debounce = 0
def rf_deb_callback(t, rf_in):
    global rf_debounce
    print('timer callback')
    print(rf_in.value())
    if (rf_in.value() == 0):
        send_command(rf_in)
        rf_debounce = 0

#Defining ISRs
def rf_ISR(input):
    global input_toggle, rf_debounce
    
    print(input.value())
    if (input.value() == 0):
        print('falling edge received, starting debounce timer')
        rf_debounce = 1
        rf_deb_tim.init(mode=Timer.ONE_SHOT, period=100, callback=lambda t: rf_deb_callback(t, input))
        return
    
    if (rf_debounce):
        print('skipping op')
        return
    
    if input_toggle:
        send_command(input)
    else:
        print('RF input received on IR Mode. Input Ignored.')
    
def ir_ISR(data, addr_, _):
    global ir_interrupt_flags, rf_inputs, input_toggle
    
    if not input_toggle:
        if addr_ != 0x21:
            print('IR input received on improper address. Input Ignored.')
            return
        else:
            send_command(data)
    else:
        print('IR input received on RF Mode. Input Ignored.')

but_debounce = 0
def input_toggle_ISR(btn):
    global input_toggle, debounce
    
    if (time.ticks_ms() - but_debounce > but_debounce_time):
        input_toggle = not input_toggle
        if input_toggle:
            print('Now in RF Mode')
        else:
            print('Now in IR Mode')
        debounce = time.ticks_ms()

#Assigning IRQs
for input in rf_inputs:
    input.irq(trigger=(input.IRQ_RISING | input.IRQ_FALLING), handler=rf_ISR)
    
ir_receiver = NEC_8(ir_input, callback=ir_ISR)
ir_receiver.error_function(print_error)


#input_toggle_btn.irq(trigger=input_toggle_btn.IRQ_FALLING, handler=input_toggle_ISR)

#Motor Control
def set_motor(motor, cond):
    global ph, en
    if cond == -1:    #Stop
        en[motor].duty_u16(0)
    elif cond == 0:   #Forwards
        ph[motor].low()
        en[motor].duty_u16(pwm[motor])
    elif cond == 1:   #Backwards
        ph[motor].high()
        en[motor].duty_u16(pwm[motor])
        
def motor_control(cond):
    global curr_motor_cond
    if (curr_motor_cond == cond):
        print('Motors Stopped')
        set_motor(0, -1)
        set_motor(1, -1)
        curr_motor_cond = -1
        return
    curr_motor_cond = cond
    set_motor(0, -1)
    set_motor(1, -1)
    time.sleep(0.1) #Add delay to reduce back EMF
    if cond == 0:   #Forwards
        print('Motors Forward')
        set_motor(0,0)
        set_motor(1,0)
    elif cond == 1: #Backwards
        print('Motors Backward')
        set_motor(0,1)
        set_motor(1,1)
    elif cond == 2: #Turn Left
        print('Motors Left')
        set_motor(0,1)
        set_motor(1,0)
    elif cond == 3: #Turn Right
        print('Motors Right')
        set_motor(0,0)
        set_motor(1,1)

#Main loop
while True:
    for flag_type in [rf_interrupt_flags, ir_interrupt_flags]:
        for command in flag_type:
            #Input handler
            
            #print('Acting on flag_type', flag_type)
            
            #print('toggling led on', command)
            #leds[command].toggle()
            
            #print('setting motors to condition', command)
            motor_control(command)
                
        flag_type.clear()
    
    if (adc_conv.sample_battery(bat_sample_time=75, pin=bat_pin_in) < min_bat_volt):
        #Prevents further operation of robot while battery voltage is too low. Discourages pushing the limits.
        #operating = False
        bat_low_led.value(1)
        #print("Battery Voltage Low")
        #while True:
        #    continue