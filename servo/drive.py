#!/usr/bin/env python3
"""
if "RuntimeError: Cannot determine SOC peripheral base address":
    https://forums.raspberrypi.com/viewtopic.php?t=361218
    (servo) pi@charli:~/code/servo $ pip install rpi-lgpio
"""

from adafruit_servokit import ServoKit
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import random
import time

STEERING_LEFT_MAX = 58  # degrees
STEERING_RIGHT_MAX = 133  # degrees
STEERING_MIDPOINT = 95.5  # degrees
STEERING_I2C_SERVO_INDEX = 0

MOTOR_MIN_SPEED = 0.35
MOTOR_MAX_SPEED = 1
MOTOR_PIN_PWM = 13  # pin for amount of speed we're commanding
MOTOR_PIN_FORWARD = 26  # pin saying we're going forward
MOTOR_PIN_REVERSE = 16  # pin saying we're going in reverse


#pca = ServoKit(channels=16)
steering_servo = ServoKit(channels=16).servo[STEERING_I2C_SERVO_INDEX]
steering_servo.angle = STEERING_MIDPOINT

motor_speed = PWMOutputDevice(pin=MOTOR_PIN_PWM, active_high=True, initial_value=0, frequency=1000)
motor_speed.value = 0
motor_forward = DigitalOutputDevice(MOTOR_PIN_FORWARD)
motor_forward.on()
motor_reverse = DigitalOutputDevice(MOTOR_PIN_REVERSE)
motor_reverse.off()

SAFE_STEERING_RANGE = 35
try:
    forward = True
    for _ in range(100):
        if forward:
            motor_forward.on()
            motor_reverse.off()
        else:
            motor_forward.off()
            motor_reverse.on()

        next_turn = random.randrange(-SAFE_STEERING_RANGE, SAFE_STEERING_RANGE)
        speed = random.uniform(0.4, 0.95)
        go_interval = random.uniform(0.25, 0.75)
        wait_interval = random.uniform(0.5, 3)

        steering_servo.angle = STEERING_MIDPOINT + next_turn
        motor_speed.value = speed
        time.sleep(go_interval)

        motor_speed.value = 0
        time.sleep(wait_interval)

        forward = not forward
except KeyboardInterrupt:
    pass
steering_servo.angle = STEERING_MIDPOINT
