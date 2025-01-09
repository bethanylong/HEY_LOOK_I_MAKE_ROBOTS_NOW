"""BMP388 barometric altimeter (thx bosch)

Wiring: 3V -> Vin, GND -> GND, SCL -> SCK, SDA -> SDI

Can be used on the same pins as other I2C sensors (such as gyro) because it's a bus.
"""
import adafruit_bmp3xx
import board
import time

I2C = board.I2C()
BMP = adafruit_bmp3xx.BMP3XX_I2C(I2C)
FEET_PER_METER = 3.28
LOCAL_SEA_LEVEL_PRESSURE_HPA = 1025.3  # right now
BMP.sea_level_pressure = LOCAL_SEA_LEVEL_PRESSURE_HPA 

for _ in range(1000):
    altitude_meters = BMP.altitude
    altitude_feet = altitude_meters * FEET_PER_METER
    print(f"Altitude above sea level: {int(altitude_feet)}")
    time.sleep(0.5)
