from adafruit_servokit import ServoKit
import evdev
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import sys

devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
for device in devices:
   print(device.path, device.name, device.phys)

device = evdev.InputDevice("/dev/input/event5")

# Controller constants
CATEGORY_BUTTONS = "buttons"
CATEGORY_AXES = "axes"
BUTTON_START = "start"
BUTTON_A = "a"
BUTTON_B = "b"
BUTTON_X = "x"
BUTTON_Y = "y"
BUTTON_Z = "z"
BUTTON_L = "l"
BUTTON_R = "r"
BUTTON_DPAD_UP = "dpad up"
BUTTON_DPAD_RIGHT = "dpad right"
BUTTON_DPAD_DOWN = "dpad down"
BUTTON_DPAD_LEFT = "dpad left"
AXIS_ANALOG_X = "analog x"
AXIS_ANALOG_Y = "analog y"
AXIS_CSTICK_X = "cstick x"
AXIS_CSTICK_Y = "cstick y"
AXIS_L_SQUISH = "l squish"
AXIS_R_SQUISH = "r squish"

AXIS_ANALOG_X_MIN = 16
AXIS_ANALOG_X_MAX = 238
AXIS_ANALOG_X_MIDPOINT = 127
AXIS_ANALOG_X_DEADZONE = 3  # in each direction

AXIS_ANALOG_Y_MIN = 17
AXIS_ANALOG_Y_MAX = 239
AXIS_ANALOG_Y_MIDPOINT = 127
AXIS_ANALOG_Y_DEADZONE = 3  # in each direction

# Motor constants
MOTOR_MIN_SPEED = 0.35
MOTOR_MAX_SPEED = 1
MOTOR_PIN_PWM = 13  # pin for amount of speed we're commanding
MOTOR_PIN_FORWARD = 26  # pin saying we're going forward
MOTOR_PIN_REVERSE = 16  # pin saying we're going in reverse

# Servo constants
STEERING_LEFT_MAX = 58  # degrees
STEERING_RIGHT_MAX = 133  # degrees
STEERING_MIDPOINT = 95.5  # degrees
STEERING_I2C_SERVO_INDEX = 0
STEERING_FLIP = True  # in case the engineer forgot to wire up the servo correctly

# Controller setup
inputs = {
    CATEGORY_BUTTONS: {
        BUTTON_START: 297,
        BUTTON_A: 289,
        BUTTON_B: 290,
        BUTTON_X: 288,
        BUTTON_Y: 291,
        BUTTON_Z: 295,
        BUTTON_L: 292,
        BUTTON_R: 293,
        BUTTON_DPAD_UP: 300,
        BUTTON_DPAD_RIGHT: 301,
        BUTTON_DPAD_DOWN: 302,
        BUTTON_DPAD_LEFT: 303,
    },
    CATEGORY_AXES: {
        AXIS_ANALOG_X: 0,
        AXIS_ANALOG_Y: 1,
        AXIS_CSTICK_X: 5,
        AXIS_CSTICK_Y: 2,
        AXIS_L_SQUISH: 3,
        AXIS_R_SQUISH: 4,
    },
}

codes = {}
for input_type in inputs:
    for input_item in inputs[input_type]:
        name = input_item
        value = inputs[input_type][input_item]
        codes[value] = name

# Motor setup
motor_speed = PWMOutputDevice(pin=MOTOR_PIN_PWM, active_high=True, initial_value=0, frequency=1000)
motor_speed.value = 0
motor_forward = DigitalOutputDevice(MOTOR_PIN_FORWARD)
motor_forward.on()
motor_reverse = DigitalOutputDevice(MOTOR_PIN_REVERSE)
motor_reverse.off()

# Servo setup
steering_servo = ServoKit(channels=16).servo[STEERING_I2C_SERVO_INDEX]
steering_servo.angle = STEERING_MIDPOINT


def axis_analog_y_to_throttle(controller_value):
    forward = True
    throttle = 0  # Fractional. 0 <= throttle <= 1
    deadzone_lower_bound = AXIS_ANALOG_Y_MIDPOINT - AXIS_ANALOG_Y_DEADZONE
    deadzone_upper_bound = AXIS_ANALOG_Y_MIDPOINT + AXIS_ANALOG_Y_DEADZONE
    if controller_value > deadzone_upper_bound:
        # We're moving in reverse (thanks Nintendo). By how much?
        forward = False
        span = AXIS_ANALOG_Y_MAX - deadzone_upper_bound
        throttle = (controller_value - deadzone_upper_bound) / span
    elif controller_value < deadzone_lower_bound:
        # Similar, but forward.
        span = deadzone_lower_bound - AXIS_ANALOG_Y_MIN
        throttle = (deadzone_lower_bound - controller_value) / span
    else:
        # Within deadzone. Implicitly fall through with defaults set at top of function.
        pass
    return forward, throttle


def throttle_fraction_to_motor_speed(throttle):
    if not throttle:
        return 0
    span = MOTOR_MAX_SPEED - MOTOR_MIN_SPEED
    linear_speed = throttle * span + MOTOR_MIN_SPEED
    exponential_speed = linear_speed * linear_speed * linear_speed
    return exponential_speed


def axis_analog_x_to_steering(controller_value):
    steering = 0.5
    deadzone_lower_bound = AXIS_ANALOG_X_MIDPOINT - AXIS_ANALOG_X_DEADZONE
    deadzone_upper_bound = AXIS_ANALOG_X_MIDPOINT + AXIS_ANALOG_X_DEADZONE
    if controller_value > deadzone_upper_bound:
        span = AXIS_ANALOG_X_MAX - deadzone_upper_bound
        steering = 0.5 + (controller_value - deadzone_upper_bound) / span / 2
    elif controller_value < deadzone_lower_bound:
        span = deadzone_lower_bound - AXIS_ANALOG_X_MIN
        steering = 0.5 - (deadzone_lower_bound - controller_value) / span / 2
    else:
        # Within deadzone. Implicitly fall through.
        pass
    if STEERING_FLIP:
        steering = 1 - steering
    return steering


def steering_fraction_to_servo_position(steering):
    span = STEERING_RIGHT_MAX - STEERING_LEFT_MAX
    return STEERING_LEFT_MAX + steering * span


try:
    for event in device.read_loop():
        if event.code not in codes:
            continue

        item = codes[event.code]
        if event.type == evdev.ecodes.EV_KEY:
            # Button press
            print(f"Got button {item}, value {event.value}")
            if item == BUTTON_START:
                sys.exit(0)
        elif event.type == evdev.ecodes.EV_ABS:
            # Axis
            print(f"Got axis {item}, value {event.value}")

            if item == AXIS_ANALOG_Y:
                # It's go time!
                forward, throttle = axis_analog_y_to_throttle(event.value)
                speed = throttle_fraction_to_motor_speed(throttle)
                print(f"{forward=} {throttle=}")

                if forward:
                    motor_forward.on()
                    motor_reverse.off()
                else:
                    motor_forward.off()
                    motor_reverse.on()
                motor_speed.value = speed

            elif item == AXIS_ANALOG_X:
                # It's...steer time!
                steering = axis_analog_x_to_steering(event.value)
                servo_position = steering_fraction_to_servo_position(steering)
                steering_servo.angle = servo_position

except KeyboardInterrupt:
    pass
