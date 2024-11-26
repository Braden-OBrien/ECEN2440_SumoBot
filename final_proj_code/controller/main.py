import ir_tx, machine, time, seesaw
from ir_tx.nec import NEC
from machine import I2C, Pin

# Initialze Remote-Mode LED's (Green = IR; Blue = RF)
IR_Mode_LED = Pin(0, Pin.OUT, Pin.PULL_DOWN)
RF_Mode_LED = Pin(1, Pin.OUT, Pin.PULL_DOWN)

# Initialize Mode Button
mode_toggle_button = Pin(4, Pin.IN, Pin.PULL_UP)

# Initialize I2C. Adjust pin numbers based on your Pico's configuration
i2c = I2C(0, scl=Pin(21), sda=Pin(20))

# Initialize the Seesaw driver with the I2C interface
# Use the Gamepad QT's I2C address from the Arduino code (0x50)
seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

# Initialize IR Transmitter pin
tx_pin = Pin(16, Pin.OUT, value = 0)
device_addr = 0x01                      # Example address
transmitter = NEC(tx_pin)               # List of commands to send
commands = [0x01,0x02,0x03,0x04,0x05,0x06]

# Initialize RF Transmitter pins
RF4emitter = Pin(13, Pin.OUT, Pin.PULL_DOWN)
RF3emitter = Pin(12, Pin.OUT, Pin.PULL_DOWN)
RF2emitter = Pin(11, Pin.OUT, Pin.PULL_DOWN)
RF1emitter = Pin(10, Pin.OUT, Pin.PULL_DOWN)

# Define button and joystick pin numbers as per the Arduino code
BUTTON_A = 5
BUTTON_B = 1
BUTTON_X = 6
BUTTON_Y = 2
BUTTON_START = 16
BUTTON_SELECT = 0
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15
BUTTONS_MASK = (1 << BUTTON_X) | (1 << BUTTON_Y) | (1 << BUTTON_A) | (1 << BUTTON_B) | (1 << BUTTON_SELECT) | (1 << BUTTON_START)

# Initialize IR Emitter states
emitter_states = {
   BUTTON_A: False,
   BUTTON_B: False,
   BUTTON_X: False,
   BUTTON_Y: False,
   BUTTON_START: False,
   BUTTON_SELECT: False
}

# Initialize last button states
last_buttons = 0

# Initialize joystick center position
joystick_center_x = 511
joystick_center_y = 497

# Mode selection (0 = IR, 1 = RF)
mode = 0  # Default to IR mode
IR_Mode_LED.value(1)
RF_Mode_LED.value(0)

# Interrupt handler for mode toggle button press
def mode_toggle_press(pin):
     global mode
     mode = 1 - mode  # Toggle between 0 (IR) and 1 (RF)
    
     if mode == 0:
          IR_Mode_LED.value(1)  # Turn on IR LED (green)
          RF_Mode_LED.value(0)  # Turn off RF LED (blue)
          print("Mode switched to IR.")
     else:
          IR_Mode_LED.value(0)  # Turn off IR LED (green)
          RF_Mode_LED.value(1)  # Turn on RF LED (blue)
          print("Mode switched to RF.")

# Attach interrupt handler to pin
mode_toggle_button.irq(trigger=Pin.IRQ_FALLING, handler=mode_toggle_press)      

def setup_buttons():               # Configure the pin modes for buttons.    
     seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)
     # Debugging to check the setup of BUTTON_SELECT
     # print(f"BUTTON_SELECT pin mode: {seesaw_device.pin_mode(BUTTON_SELECT)}")

def read_buttons():                # Read and return the state of each button.
     return seesaw_device.digital_read_bulk(BUTTONS_MASK)
     print(f"Read buttons: {bin(button_state)}")  # Debug print of all buttons' states
     
def turn_off_RFpins():             # Resets all RF emitter pins to 0V
     RF1emitter.value(0)
     RF2emitter.value(0)
     RF3emitter.value(0)
     RF4emitter.value(0)

def handle_button_press(button):    # Send corresponding NEC command on button press.
   global emitter_states, mode
   emitter_states[button] = not emitter_states[button]
   
   # For IR Mode:
   if mode == 0:
        if button == BUTTON_A:
             transmitter.transmit(device_addr, commands[0])  
             print("COMMANDS",hex(commands[0]),"TRANSMITTED.")
        elif button == BUTTON_B:
             transmitter.transmit(device_addr, commands[1])  
             print("COMMANDS",hex(commands[1]),"TRANSMITTED.")
        elif button == BUTTON_X:
             transmitter.transmit(device_addr, commands[2])  
             print("COMMANDS",hex(commands[2]),"TRANSMITTED.")
        elif button == BUTTON_Y:
             transmitter.transmit(device_addr, commands[3])  
             print("COMMANDS",hex(commands[3]),"TRANSMITTED.")
        print("Button", button, "is", "pressed" if emitter_states[button] else "released")
   # For RF Mode
   elif mode == 1:
        if button == BUTTON_A:
             RF1emitter.value(1)
             print("D0 Active")
        elif button == BUTTON_B:
             RF2emitter.value(1)
             print("D1 Active")
        elif button == BUTTON_X:
             RF3emitter.value(1)
             print("D2 Active")
        elif button == BUTTON_Y:
             RF4emitter.value(1)
             print("D3 Active")                      


# Main Loop
def main():
   global last_buttons  # Ensure last_buttons is recognized as a global variable

   setup_buttons()

   last_x, last_y = seesaw_device.analog_read(JOYSTICK_X_PIN), seesaw_device.analog_read(JOYSTICK_Y_PIN)
   joystick_threshold = 50  # Adjust threshold as needed

   while True:
       current_buttons = read_buttons()
       
       # Check if button state has changed
       for button in emitter_states:
           if current_buttons & (1 << button) and not last_buttons & (1 << button):
               handle_button_press(button)

       # Read joystick values
       current_x = seesaw_device.analog_read(JOYSTICK_X_PIN)
       current_y = seesaw_device.analog_read(JOYSTICK_Y_PIN)

       # Check if joystick position has changed significantly
       if abs(current_x - last_x) > joystick_threshold or abs(current_y - last_y) > joystick_threshold:
           print("Joystick moved - X:", current_x, ", Y:", current_y)
           last_x, last_y = current_x, current_y

           if mode == 0:      # If in IR mode
                # Determine which NEC command to send based on joystick direction
              if current_y < joystick_center_y - joystick_threshold:       # Joystick moved up
                   transmitter.transmit(device_addr, commands[0])  
                   print("COMMANDS",hex(commands[0]),"TRANSMITTED.")
              elif current_y > joystick_center_y + joystick_threshold:     # Joystick moved down
                   transmitter.transmit(device_addr, commands[1])  
                   print("COMMANDS",hex(commands[1]),"TRANSMITTED.")
              elif current_x < joystick_center_x - joystick_threshold:     # Joystick moved left
                   transmitter.transmit(device_addr, commands[2])  
                   print("COMMANDS",hex(commands[2]),"TRANSMITTED.")
              elif current_x > joystick_center_x + joystick_threshold:     # Joystick moved right
                   transmitter.transmit(device_addr, commands[3])  
                   print("COMMANDS",hex(commands[3]),"TRANSMITTED.")
           elif mode == 1:    # If in RF mode
               if current_y < joystick_center_y - joystick_threshold:
                   RF1emitter.value(1)
                   print("Joystick moved up (RF).")
               elif current_y > joystick_center_y + joystick_threshold:
                   RF2emitter.value(1)
                   print("Joystick moved down (RF).")
               elif current_x < joystick_center_x - joystick_threshold:
                   RF3emitter.value(1)
                   print("Joystick moved right (RF).")
               elif current_x > joystick_center_x + joystick_threshold:
                   RF4emitter.value(1)
                   print("Joystick moved left (RF).")

       last_buttons = current_buttons
       time.sleep_ms(100)  # Delay to prevent overwhelming the output

if __name__ == "__main__":
   main()