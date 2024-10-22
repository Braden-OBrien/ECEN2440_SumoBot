import time
from machine import Pin
import random

time.sleep(0.1)

leds = [Pin(i, Pin.OUT) for i in range(18,22)]
buttons = [Pin(i, Pin.IN, Pin.PULL_UP) for i in range (10,14)]

IRQ_requests = [0, 0, 0, 0]

def button_press_isr(button):
    global IRQ_requests
    global buttons
    index = buttons.index(button)
    IRQ_requests[index] = 1
    
for i in range(len(buttons)):
    buttons[i].irq(trigger=buttons[i].IRQ_FALLING, handler=button_press_isr)


def reset():
    print("Restarting Game...")
    global current_stage
    global led_seq
    current_stage = 0
    led_seq = [-1, -1, -1, -1]
     
print("game start")
    
current_stage = 0
led_seq = [-1, -1, -1, -1]
reset_flag = 0
    
#Game Loop    
while True:    
    led_seq[current_stage] = random.randint(0, 3)
    print("led selected is", led_seq[current_stage])
    #Display LEDs
    for i in range(current_stage+1):
        print("displaying on LED", i)
        leds[led_seq[i]].toggle
        time.sleep(0.25)
        leds[led_seq[i]].toggle
        time.sleep(0.25)
    
    #Check buttons pressed
    currently_checking = 0
    for i in range(current_stage+1):
        while(sum(IRQ_requests) < 1):
            continue
    
        button_pressed = IRQ_requests.index(1)
        if button_pressed == led_seq[currently_checking]:
            currently_checking+=1
            continue
        else:
            reset_flag = 1
            break
    
    if reset_flag == 1:
        print("Game Over! You chose the wrong value!")
        reset()
    else:
        print("Stage", current_stage, "complete! Continuing to stage", current_stage+1,"!")
        current_stage += 1
    
    time.sleep(5)