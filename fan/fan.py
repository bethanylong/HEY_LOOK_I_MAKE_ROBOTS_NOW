"""
oops it's a 12v fan and the PCA9685 only supports 6v max lol
"""
import board
from adafruit_pca9685 import PCA9685
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 30

def set_speed(fraction):
    print(f"{fraction=}")
    desired_duty_cycle = int(65535 * (1 - fraction))
    #desired_duty_cycle = 0x7fff
    print(f"{desired_duty_cycle=}")
    pca.channels[0].duty_cycle = desired_duty_cycle

set_speed(0.2)
