from machine import Pin
from ir_rx.nec import NEC_8 # Use the NEC 8-bit class
from ir_rx.print_error import print_error # for debugging
import uasyncio as asyncio
from ir_tx.nec import NEC

# Callback function to execute when an IR code is received
def ir_callback(data, addr, _):
    print(f"Received NEC command! Data: 0x{data:02X}, Addr: 0x{addr:02X}")

# Setup the IR receiver
ir_pin = Pin(13, Pin.IN, Pin.PULL_UP) # Adjust the pin number based on your wiring

ir_receiver = NEC_8(ir_pin, callback=ir_callback)

# Optional: Use the print_error function for debugging
ir_receiver.error_function(print_error)

# Define an asynchronous function to handle IR transmission
async def transmit_ir():
    ir_transmitter = NEC(Pin(16, Pin.OUT, value=0)) # Initialize IR transmitter on Pin 17
    addr = 0x01 # Example device address
    commands = [0x01, 0x02, 0x03, 0x04] # List of commands to send
    
    while True:
        for command in commands:
            ir_transmitter.transmit(addr, command) # Send each command
            print(f"IR signal transmitted: Addr {addr}, Command {command}")
            await asyncio.sleep(3) # Wait for 3 seconds before sending the next command

# Main function to run the transmitter
async def main():
    await transmit_ir() # Call the transmit function

if __name__ == "__main__":
    asyncio.run(main()) # Start the asynchronous event loop
    
# Main loop to keep the script running
while True:
    pass # Execution is interrupt-driven, so just keep the script alive