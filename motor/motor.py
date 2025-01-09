from gpiozero import PWMOutputDevice, DigitalOutputDevice
import time

"""Debug note: don't forget to connect the STBY pin to VCC (3.3v)

Number of times I forgot anyway: 2
(^ Increment whenever I forget)
"""

pin_pwm = 13
#pin_fwd = 16
#pin_rev = 26
pin_fwd = 26
pin_rev = 16
dev_drive = PWMOutputDevice(pin=pin_pwm, active_high=True, initial_value=0, frequency=1000)
dev_fwd = DigitalOutputDevice(pin_fwd)
dev_rev = DigitalOutputDevice(pin_rev)

go_interval = 0.5
stop_interval = 0.5

"""
while True:
    print("Forward")
    dev_fwd.on()
    dev_rev.off()
    dev_drive.value = 1.0
    time.sleep(go_interval)

    print("Stop")
    dev_drive.value = 0.0
    time.sleep(stop_interval)

    print("Reverse")
    dev_fwd.off()
    dev_rev.on()
    dev_drive.value = 1.0
    time.sleep(go_interval)

    print("Stop")
    dev_drive.value = 0.0
    time.sleep(stop_interval)
"""
STEP = 0.01
target_value = 0
dev_fwd.on()
dev_rev.off()
dev_drive.value = 0.0
while dev_drive.value < 1:
    target_value += STEP
    dev_drive.value = target_value
    input(f"Current target output value: {target_value}")
