import time
from machine import PWM, Pin


# Motor Driver Setup
pwm_rate = 2000  # PWM frequency in Hz


# Motor A setup (AIN1, AIN2)
ain1_ph = Pin(12, Pin.OUT)  # Phase control (GP12)
ain2_en = PWM(Pin(13), freq=pwm_rate, duty_u16=0)  # Enable control (GP13)


# Motor B setup (BIN1, BIN2)
bin1_ph = Pin(14, Pin.OUT)  # Phase control (GP14)
bin2_en = PWM(Pin(15), freq=pwm_rate, duty_u16=0)  # Enable control (GP15)


# Set the PWM value for motor control
pwm = min(max(int(2**16 * abs(1)), 0), 65535)


# Main control loop
while True:
    for _ in range(2):
        # ------------------- Motor A Control ---------------------
        print("Motor A - Forward")  # AIN1 low, AIN2 PWM active
        ain1_ph.low()  # Set phase low for forward motion
        ain2_en.duty_u16(pwm)  # Apply PWM signal


        print("Measure voltage at AO1, AO2 during Motor A Forward.")
        time.sleep(2)


        print("Motor A - Backward")  # AIN1 high, AIN2 PWM active
        ain1_ph.high()  # Set phase high for reverse motion
        ain2_en.duty_u16(pwm)  # Maintain PWM signal


        print("Measure voltage at AO1, AO2 during Motor A Backward.")
        time.sleep(2)


        print("Motor A OFF")  # Stop Motor A
        ain1_ph.low()
        ain2_en.duty_u16(0)  # Disable PWM


        print("Check for voltage spikes at AO1, AO2 after Motor A OFF.")
        time.sleep(1)


        # ------------------- Motor B Control ---------------------
        print("Motor B - Forward")  # BIN1 low, BIN2 PWM active
        bin1_ph.low()  # Set phase low for forward motion
        bin2_en.duty_u16(pwm)  # Apply PWM signal


        print("Measure voltage at BO1, BO2 during Motor B Forward.")
        time.sleep(2)


        print("Motor B - Backward")  # BIN1 high, BIN2 PWM active
        bin1_ph.high()  # Set phase high for reverse motion
        bin2_en.duty_u16(pwm)  # Maintain PWM signal


        print("Measure voltage at BO1, BO2 during Motor B Backward.")
        time.sleep(2)


        print("Motor B OFF")  # Stop Motor B
        bin1_ph.low()
        bin2_en.duty_u16(0)  # Disable PWM


        print("Check for voltage spikes at BO1, BO2 after Motor B OFF.")
        time.sleep(1)


    print("Sequence Finished. Press 'CTRL' + 'C' to stop.")
    time.sleep(10)