import board
from adafruit_pca9685 import PCA9685
i2c = board.I2C()
pca = PCA9685(i2c)
pca.frequency = 120
pca.channels[0].duty_cycle = 0x7fff
import time
while True:
    pca.channels[0].duty_cycle = 0
    time.sleep(1)
    pca.channels[0].duty_cycle = 0x7fff
    time.sleep(1)
    pca.channels[0].duty_cycle = 0xffff
    time.sleep(1)
