from machine import Pin, PWM
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging
#from ir_tx.nec import NEC
import time


time.sleep(0.1)

#IR Transmitter Testing
#addr = 0x21
#commands = [0x1]
#ir_transmitter = NEC(Pin(16, Pin.OUT, value=0))


#Global constants
debounce_time = 100 #50ms debounce timer
pwm_rate = 2000
pwm = min(max(int(2**16 * abs(1)), 0), 65535)
curr_motor_cond = -1

#Assigning Pinouts
rf_inputs = [Pin(i, Pin.IN) for i in [11, 12, 15, 14]]
ir_input = Pin(13, Pin.IN, Pin.PULL_UP)
input_toggle_btn = Pin(10, Pin.IN, Pin.PULL_DOWN)
leds = [Pin(i, Pin.OUT) for i in [21, 18, 19, 20]]

ph = [Pin(9, Pin.OUT), Pin(7, Pin.OUT)]
en = [PWM(8, freq=pwm_rate, duty_u16 = 0), PWM(6, freq=pwm_rate, duty_u16 = 0)]

#Interrupt flags
rf_interrupt_flags = []
ir_interrupt_flags = []
input_toggle = 1 # 1 - RF Receiver | 0 - IR Receiver

#Defining ISRs
def rf_ISR(input):
    global rf_interrupt_flags, rf_inputs, input_toggle
    
    if input_toggle:
        index = rf_inputs.index(input)
        print('RF input received on', index)
        rf_interrupt_flags.append(index)
    else:
        print('RF input received on IR Mode. Input Ignored.')
    
def ir_ISR(data, addr_, _):
    global ir_interrupt_flags, rf_inputs, input_toggle
    
    if not input_toggle:
        if addr_ != 0x21:
            print('IR input received on improper address. Input Ignored.')
            return
        else:
            print('IR input received on', addr_, 'with data', data)
            ir_interrupt_flags.append(int(data))
    else:
        print('IR input received on RF Mode. Input Ignored.')

debounce = 0
def input_toggle_ISR(btn):
    global input_toggle, debounce
    
    if (time.ticks_ms() - debounce > debounce_time):
        input_toggle = not input_toggle
        if input_toggle:
            print('Now in RF Mode')
        else:
            print('Now in IR Mode')
        debounce = time.ticks_ms()

#Assigning IRQs
for input in rf_inputs:
    input.irq(trigger=input.IRQ_RISING, handler=rf_ISR)
    
ir_receiver = NEC_8(ir_input, callback=ir_ISR)

input_toggle_btn.irq(trigger=input_toggle_btn.IRQ_FALLING, handler=input_toggle_ISR)

#Motor Control
def set_motor(motor, cond):
    global ph, en
    if cond == -1:    #Stop
        en[motor].duty_u16(0)
    elif cond == 0:   #Forwards
        ph[motor].low()
        en[motor].duty_u16(pwm)
    elif cond == 1:   #Backwards
        ph[motor].high()
        en[motor].duty_u16(pwm)
        
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
            
            print('Acting on flag_type', flag_type)
            
            print('toggling led on', command)
            leds[command].toggle()
            
            print('setting motors to condition', command)
            motor_control(command)
                
        flag_type.clear()
   # ir_transmitter.transmit(addr, commands[0])
   # print('ir signal transmitted addr', addr, 'command', commands[0])
   # time.sleep(3)
    continue