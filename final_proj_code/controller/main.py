import ir_tx, machine, time, seesaw
from ir_tx.nec import NEC
from machine import I2C, Pin

# Initialize ADC pin (GPIO Pin 26 / ADC 0)
adc = machine.ADC(26) 

# Initialize battery voltage indicator LED's
fullBatteryLED = Pin(22, Pin.OUT, Pin.PULL_DOWN)
medBatteryLED = Pin(19, Pin.OUT, Pin.PULL_DOWN)
lowBatteryLED = Pin(18, Pin.OUT, Pin.PULL_DOWN)

# Initialize Remote-Mode LED's (Green = IR; Blue = RF)
IR_Mode_LED = Pin(0, Pin.OUT, Pin.PULL_DOWN)
RF_Mode_LED = Pin(1, Pin.OUT, Pin.PULL_DOWN)

# Initialize Mode Button
mode_toggle_button = Pin(4, Pin.IN, Pin.PULL_UP)

# Initialize I2C
i2c = I2C(0, scl=Pin(21), sda=Pin(20))

# Initialize the Seesaw driver with the I2C interface
seesaw_device = seesaw.Seesaw(i2c, addr=0x50)

# Initialize IR Transmitter pin
tx_pin = Pin(16, Pin.OUT, value = 0)
device_addr = 0x21
transmitter = NEC(tx_pin)
commands = [0x00, 0x01, 0x02, 0x03]

# Define button mappings
BUTTONS = {
    "A": 5,
    "B": 1,
    "X": 6,
    "Y": 2,
    "START": 16,
    "SELECT": 0,
}
BUTTONS_MASK = (1 << BUTTONS["X"]) | (1 << BUTTONS["Y"]) | (1 << BUTTONS["A"]) | (1 << BUTTONS["B"]) | (1 << BUTTONS["SELECT"]) | (1 << BUTTONS["START"])

# Initialize IR Emitter states
emitter_states = {
   BUTTONS["A"]: False,
   BUTTONS["B"]: False,
   BUTTONS["X"]: False,
   BUTTONS["Y"]: False,
   BUTTONS["START"]: False,
   BUTTONS["SELECT"]: False
}

# Initialize RF Transmitter pins
RF_pins = {
    "RF1": Pin(10, Pin.OUT),
    "RF2": Pin(11, Pin.OUT),
    "RF3": Pin(12, Pin.OUT),
    "RF4": Pin(13, Pin.OUT),
}

# Define joystick mappings
JOYSTICK_X_PIN = 14
JOYSTICK_Y_PIN = 15
joystick_threshold = 50

# Initialize joystick center position (calibrate during setup)
joystick_center_x = seesaw_device.analog_read(JOYSTICK_X_PIN)
joystick_center_y = seesaw_device.analog_read(JOYSTICK_Y_PIN)

# Mode selection (0 = IR, 1 = RF)
mode = 0
print("Default Transmission Mode: IR")
RF_Mode_LED.value(0)
IR_Mode_LED.value(1)
last_toggle_time = 0

# Checks the voltage of the battery
def read_battery_voltage():
    raw = adc.read_u16()  # 16-bit ADC value
    scaled_voltage = (raw / 65535.0) * 3.56  # Convert to ADC voltage
    battery_voltage = scaled_voltage / 0.319  # Reverse the voltage divider scaling
    return battery_voltage

# Changes the LEDS for the ADC Battery Indicator
def update_leds(voltage):
    if voltage >= 7.54:  # Fully charged
        fullBatteryLED.value(1)
        medBatteryLED.value(0)
        lowBatteryLED.value(0)
    elif 7.0 <= voltage < 7.54:  # Medium battery
        fullBatteryLED.value(0)
        medBatteryLED.value(1)
        lowBatteryLED.value(0)
    elif 6.8 <= voltage < 7.0:  # Low battery
        fullBatteryLED.value(0)
        medBatteryLED.value(0)
        lowBatteryLED.value(1)
    else:  # Super low battery
        fullBatteryLED.value(0)
        medBatteryLED.value(0)
        # Flash the red LED
        for _ in range(5):  # Flash 5 times
            lowBatteryLED.value(1)
            time.sleep_ms(100)
            lowBatteryLED.value(0)
            time.sleep_ms(100)

# Configure the pin modes for buttons.
def setup_buttons():
    seesaw_device.pin_mode_bulk(BUTTONS_MASK, seesaw_device.INPUT_PULLUP)
    
# Set as input to release the pin (high-impedance)
def turn_off_RFpins():
    RF_pins["RF1"].init(Pin.IN)  
    RF_pins["RF2"].init(Pin.IN)
    RF_pins["RF3"].init(Pin.IN)
    RF_pins["RF4"].init(Pin.IN)

# Interrupt handler for mode toggle button
def mode_toggle_handler(pin):
    global mode, last_toggle_time
    turn_off_RFpins()
    current_time = time.ticks_ms()
    if time.ticks_diff(current_time, last_toggle_time) > 200:  # 200ms debounce
        mode = 1 - mode
        if mode == 0:
            IR_Mode_LED.value(1)
            RF_Mode_LED.value(0)
            print("Mode switched to IR.")
        else:
            IR_Mode_LED.value(0)
            RF_Mode_LED.value(1)
            print("Mode switched to RF.")
        last_toggle_time = current_time

# Attach interrupt handler to pin
mode_toggle_button.irq(trigger=Pin.IRQ_FALLING, handler=mode_toggle_handler)

# Handle button press
def handle_button_press(button_name):
    global mode
    print(f"Button {button_name} pressed.")
    if mode == 0:  # IR Mode
        command_map = {5: 3, 1: 1, 6: 0, 2: 2}
        if button_name in command_map:
            transmitter.transmit(device_addr, commands[command_map[button_name]])
            print(f"IR Command {hex(commands[command_map[button_name]])} transmitted.")
    elif mode == 1:  # RF Mode
        RF_pin_map = {5: "RF1", 1: "RF2", 6: "RF3", 2: "RF4"}
        if button_name in RF_pin_map:
            # for pin in RF_pins.values():
                # pin.init(Pin.IN)
            RF_pins[RF_pin_map[button_name]].init(Pin.OUT)
            print(f"{RF_pin_map[button_name]} activated.")
            time.sleep_ms(3000)
            RF_pins[RF_pin_map[button_name]].init(Pin.IN)
            print(f"{RF_pin_map[button_name]} deactivated.")

# Joystick handler (polling, unavoidable for analog input)
def check_joystick():
    global mode
    current_x = seesaw_device.analog_read(JOYSTICK_X_PIN)
    current_y = seesaw_device.analog_read(JOYSTICK_Y_PIN)
    
    # If in IR Mode
    if mode == 0:
        if abs(current_x - joystick_center_x) > joystick_threshold:
            direction = "right" if current_x < joystick_center_x else "left"
            print(f"Joystick moved {direction}.")
            if direction == "right":
                transmitter.transmit(device_addr, commands[2])  
                print("COMMANDS",hex(commands[2]),"TRANSMITTED.")
            elif direction == "left":
                transmitter.transmit(device_addr, commands[3])  
                print("COMMANDS",hex(commands[3]),"TRANSMITTED.")
        if abs(current_y - joystick_center_y) > joystick_threshold:
            direction = "up" if current_y < joystick_center_y else "down"
            print(f"Joystick moved {direction}.")
            if direction == "up":
                transmitter.transmit(device_addr, commands[0])  
                print("COMMANDS",hex(commands[0]),"TRANSMITTED.")
            elif direction == "down":
                transmitter.transmit(device_addr, commands[1])  
                print("COMMANDS",hex(commands[1]),"TRANSMITTED.")
    # If in RF Mode
    elif mode == 1:
        if abs(current_x - joystick_center_x) > joystick_threshold:
            direction = "right" if current_x < joystick_center_x else "left"
            print(f"Joystick moved {direction}.")
            if direction == "right":
                RF_pins["RF1"].init(Pin.OUT)
                print("RF1 activated.")
                time.sleep_ms(3000)
                RF_pins["RF1"].init(Pin.IN)
                print("RF1 deactivated.")
            elif direction == "left":
                RF_pins["RF4"].init(Pin.OUT)
                print("RF4 activated.")
                time.sleep_ms(3000)
                RF_pins["RF4"].init(Pin.IN)
                print("RF4 deactivated.")
        if abs(current_y - joystick_center_y) > joystick_threshold:
            direction = "up" if current_y < joystick_center_y else "down"
            print(f"Joystick moved {direction}.")
            if direction == "up":
                RF_pins["RF3"].init(Pin.OUT)
                print("RF3 activated.")
                time.sleep_ms(3000)
                RF_pins["RF3"].init(Pin.IN)
                print("RF3 deactivated.")
            elif direction == "down":
                RF_pins["RF2"].init(Pin.OUT)
                print("RF2 activated.")
                time.sleep_ms(3000)
                RF_pins["RF2"].init(Pin.IN)
                print("RF2 deactivated.")

# Calibrate joystick center position during setup
def calibrate_joystick():
    global joystick_center_x, joystick_center_y
    joystick_center_x = seesaw_device.analog_read(JOYSTICK_X_PIN)
    joystick_center_y = seesaw_device.analog_read(JOYSTICK_Y_PIN)
    print(f"Joystick calibrated: Center X = {joystick_center_x}, Center Y = {joystick_center_y}")

# Read and return the state of each button.
def read_buttons():                
     return seesaw_device.digital_read_bulk(BUTTONS_MASK)

# Main function
def main():
    global last_buttons     # Ensure last_buttons is recognized as a global variable
    turn_off_RFpins()       # ALso make sure that the RF transmitter is off

    setup_buttons()
    last_buttons = read_buttons()
    
    last_time = time.ticks_ms()  # Record the initial time
    interval = 2000  # 2 seconds in milliseconds
    
    while True:
        # Check if 2 seconds have passed
        if time.ticks_diff(time.ticks_ms(), last_time) >= interval:
            voltage = read_battery_voltage()
            update_leds(voltage)
            print("Battery Voltage: ", voltage)
            last_time = time.ticks_ms()  # Reset the timer
        
        current_buttons = read_buttons()
       
        # Check if button state has changed
        for BUTTONS in emitter_states:
           if current_buttons & (1 << BUTTONS) and not last_buttons & (1 << BUTTONS):
               handle_button_press(BUTTONS)
        
        check_joystick()
        time.sleep_ms(100)  # Adjust delay as necessary
        
        last_buttons = current_buttons
        time.sleep_ms(100)  # Delay to prevent overwhelming the output

if __name__ == "__main__":
    calibrate_joystick()
    main()

