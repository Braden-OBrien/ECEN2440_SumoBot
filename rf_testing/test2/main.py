from machine import Pin
from rx import RX
from tx import TX
import uasyncio as asyncio
import time

example = {"on": [111, 541, 111, 542, 113, 541, 109, 543, 111, 541, 110, 543, 112, 541, 438, 217, 110, 542, 438, 216, 110, 544, 436, 216, 112, 542, 437, 216, 111, 542, 436, 216, 111, 543, 110, 542, 438, 215, 439, 215, 112, 541, 112, 544, 436, 215, 437, 217, 110, 5112], 
           "off": [110, 542, 111, 541, 111, 543, 109, 542, 111, 542, 110, 541, 112, 542, 436, 216, 111, 543, 435, 217, 110, 542, 437, 218, 110, 542, 437, 216, 109, 543, 437, 216, 109, 543, 110, 544, 434, 219, 436, 215, 437, 218, 435, 218, 109, 544, 110, 542, 110, 5108]}


#receiver = RX(Pin(16, Pin.IN), example)
receiver = RX(Pin(17, Pin.IN), example)
#receiver = Pin(16, Pin.IN)
#receiver2 = Pin(20, Pin.IN)
button = Pin(12, Pin.IN, Pin.PULL_UP)

transmitter = TX(Pin(15, Pin.OUT), example)
transmitter_queue = asyncio.TaskQueue()

def received(pin):
    print('received')
    
def button_isr(pin):
    print(transmitter.keys())
    transmitter('on')

#receiver.irq(handler=received, trigger=(receiver.IRQ_FALLING | receiver.IRQ_RISING))
button.irq(handler=button_isr, trigger=button.IRQ_FALLING)

async def send_queued():
    delay = transmitter.latency()
    while True:
        to_send = await transmitter_queue.pop()
        transmitter(to_send)
        await asyncio.sleep_ms(delay)
        
        
def create_key_pair(rx, tx, key):
    #for i in range(5):
    #    transmitter_queue.push(key)
    #await send_queued()
    transmitter(key)
    print('sending')
    receiver(key)
    print('received')
    
create_key_pair(receiver, transmitter, 'on')
#print(a)
    
while True:
    pass