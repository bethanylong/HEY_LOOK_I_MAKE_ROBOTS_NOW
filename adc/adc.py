"""Connections:

3.3V, GND, SDA, SCL between RPi and ADS1115

Potentiometer:
    left leg -> VDD (3.3V)
    middle leg (wiper) -> A0
    right leg -> GND

Photoresistor:
    VDD -> photoresistor left leg
    photoresistor right leg -> A0 -> 10k resistor left leg
    10k resistor right leg -> GND
More light == more voltage passes.
    - Phone flashlight: 3.1V
    - Ambient: 1.7V
    - Finger over photoresistor: 0.7V
    - Whole hand over photoresistor: 0.1V

holy shit this is awesome
"""

import adafruit_ads1x15.ads1115 as ADS
from adafruit_ads1x15.analog_in import AnalogIn
import board
import busio
import time

i2c = busio.I2C(board.SCL, board.SDA)
ads = ADS.ADS1115(i2c)
chan = AnalogIn(ads, ADS.P0)

while True:
    pretty_voltage = round(chan.voltage, 3)
    print(pretty_voltage)
    time.sleep(1)
