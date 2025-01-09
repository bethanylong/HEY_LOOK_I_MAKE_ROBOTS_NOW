"""Common anode RGB led (long leg shared electricity go in ooga booga)
PCA9685 red pin -> 220Ohm resistor -> common anode -> three legs, each to their own yellow pin
"""
import board
from adafruit_pca9685 import PCA9685
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 500

def set_color(fraction, color):
    print(f"{fraction=} {color=}")
    if color == "red":
        ch = 0
    elif color == "green":
        ch = 2
    elif color == "blue":
        ch = 1
    else:
        raise ValueError
    desired_duty_cycle = int(65535 * (1 - fraction))
    #desired_duty_cycle = 0x7fff
    print(f"{desired_duty_cycle=}")
    pca.channels[ch].duty_cycle = desired_duty_cycle
    #pca.channels[0].duty_cycle = desired_duty_cycle

def set_red(fraction):
    set_color(fraction, "red")

def set_green(fraction):
    set_color(fraction, "green")

def set_blue(fraction):
    set_color(fraction, "blue")

set_red(1)
set_green(0.7)
set_blue(0.2)
