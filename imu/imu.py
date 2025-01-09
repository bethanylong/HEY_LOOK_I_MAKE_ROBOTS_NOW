import adafruit_mpu6050
import board
import statistics
import time

I2C = board.I2C()
MPU = adafruit_mpu6050.MPU6050(I2C)

def calibrate_gyro(duration=10):
    time.sleep(1)
    print("Calibrating gyro. Hold still...")
    gyro_values = {"x": [], "y": [], "z": []}
    start_time = time.time()
    while time.time() < start_time + duration:
        x, y, z = MPU.gyro
        gyro_values["x"].append(x)
        gyro_values["y"].append(y)
        gyro_values["z"].append(z)
        if len(gyro_values["x"]) % 100 == 0:
            duration_remaining = round(duration - (time.time() - start_time), 2)
            print(f"Progress: gathered {len(gyro_values['x'])} values ({duration_remaining} seconds to go)")
    average_values = [statistics.mean(gyro_values[dim]) for dim in gyro_values]
    return average_values


def get_gyro(calibrations):
    raw = MPU.gyro
    assert len(raw) == len(calibrations) == 3
    calibrated = [raw[dim] - calibrations[dim] for dim in range(len(raw))]
    return calibrated


def print_gyro(calibrated_measurement, precision=1):
    rounded = [round(measurement, precision) + 0.0 for measurement in calibrated_measurement]
    print(f"x {rounded[0]}°/sec\ty {rounded[1]}°/sec\tz {rounded[2]}°/sec")


if __name__ == "__main__":
    calibrations = calibrate_gyro()
    MPU.cycle_rate = adafruit_mpu6050.Rate.CYCLE_1_25_HZ
    while True:
        calibrated_measurement = get_gyro(calibrations)
        print_gyro(calibrated_measurement)
        time.sleep(0.5)
