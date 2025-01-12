from enum import StrEnum
import evdev
from gpiozero import PWMOutputDevice, DigitalOutputDevice
import sys


VERBOSE = False


class Motor():
    def __init__(self, pwm_pin, forward_pin, reverse_pin):
        self.drive_dev = PWMOutputDevice(pin=pwm_pin, active_high=True, initial_value=0, frequency=1000)
        self.forward_dev = DigitalOutputDevice(forward_pin)
        self.reverse_dev = DigitalOutputDevice(reverse_pin)
        self.drive_dev.value = 0
        self.forward_dev.on()
        self.reverse_dev.off()

    def set(self, speed_fraction, forward=True):
        if speed_fraction < 0 or speed_fraction > 1:
            raise ValueError("Programmer doesn't know what a fraction is")

        if forward:
            self.forward_dev.on()
            self.reverse_dev.off()
        else:
            self.forward_dev.off()
            self.reverse_dev.on()

        self.drive_dev.value = speed_fraction


class GamecubeButton(StrEnum):
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


class GamecubeController():
    def __init__(self, state_callback_fn=None, state_callback_args=[], state_callback_kwargs={}):
        input_devices = [evdev.InputDevice(path) for path in evdev.list_devices()]
        gamecube_controllers = [dev for dev in input_devices if "gamecube" in dev.name.lower()]
        if not gamecube_controllers:
            for dev in input_devices:
                print(dev.path, dev.name, dev.phys)
            raise Exception("No gamecube controllers detected.")
        self.controller_dev = gamecube_controllers[0]

        # Forward button mapping
        self.input_name_to_code = {
            GamecubeButton.CATEGORY_BUTTONS: {
                GamecubeButton.BUTTON_START: 297,
                GamecubeButton.BUTTON_A: 289,
                GamecubeButton.BUTTON_B: 290,
                GamecubeButton.BUTTON_X: 288,
                GamecubeButton.BUTTON_Y: 291,
                GamecubeButton.BUTTON_Z: 295,
                GamecubeButton.BUTTON_L: 292,
                GamecubeButton.BUTTON_R: 293,
                GamecubeButton.BUTTON_DPAD_UP: 300,
                GamecubeButton.BUTTON_DPAD_RIGHT: 301,
                GamecubeButton.BUTTON_DPAD_DOWN: 302,
                GamecubeButton.BUTTON_DPAD_LEFT: 303,
            },
            GamecubeButton.CATEGORY_AXES: {  # yes I know axes aren't buttons but whatever
                GamecubeButton.AXIS_ANALOG_X: 0,
                GamecubeButton.AXIS_ANALOG_Y: 1,
                GamecubeButton.AXIS_CSTICK_X: 5,
                GamecubeButton.AXIS_CSTICK_Y: 2,
                GamecubeButton.AXIS_L_SQUISH: 3,
                GamecubeButton.AXIS_R_SQUISH: 4,
            },
        }

        # Reverse button mapping
        self.input_code_to_name = {}
        for input_type in self.input_name_to_code:
            for input_item in self.input_name_to_code[input_type]:
                name = input_item
                value = self.input_name_to_code[input_type][input_item]
                self.input_code_to_name[value] = name

        self.button_state = {
            GamecubeButton.BUTTON_START: 0,
            GamecubeButton.BUTTON_A: 0,
            GamecubeButton.BUTTON_B: 0,
            GamecubeButton.BUTTON_X: 0,
            GamecubeButton.BUTTON_Y: 0,
            GamecubeButton.BUTTON_Z: 0,
            GamecubeButton.BUTTON_L: 0,
            GamecubeButton.BUTTON_R: 0,
            GamecubeButton.BUTTON_DPAD_UP: 0,
            GamecubeButton.BUTTON_DPAD_RIGHT: 0,
            GamecubeButton.BUTTON_DPAD_DOWN: 0,
            GamecubeButton.BUTTON_DPAD_LEFT: 0,
            GamecubeButton.AXIS_ANALOG_X: 127,
            GamecubeButton.AXIS_ANALOG_Y: 127,
            GamecubeButton.AXIS_CSTICK_X: 127,
            GamecubeButton.AXIS_CSTICK_Y: 127,
            GamecubeButton.AXIS_L_SQUISH: 0,
            GamecubeButton.AXIS_R_SQUISH: 0,
        }

        self.state_callback_fn = state_callback_fn
        self.state_callback_args = state_callback_args
        self.state_callback_kwargs = state_callback_kwargs
        if state_callback_fn is not None:
            assert callable(state_callback_fn)

    def blocking_read(self):
        for event in self.controller_dev.read_loop():
            if event.code not in self.input_code_to_name:
                continue

            item = self.input_code_to_name[event.code]
            self.button_state[item] = event.value
            if event.type == evdev.ecodes.EV_KEY:
                # Button press
                if VERBOSE:
                    print(f"Got button {item}, value {event.value}")
                if item == GamecubeButton.BUTTON_START and event.value == 1:
                    sys.exit(0)
            elif event.type == evdev.ecodes.EV_ABS:
                # Axis
                if VERBOSE:
                    print(f"Got axis {item}, value {event.value}")
            else:
                continue

            if self.state_callback_fn is not None:
                self.state_callback_fn(
                    self.button_state,
                    *self.state_callback_args,
                    **self.state_callback_kwargs
                )


def squish_button_to_motor_value(squish_button_value):
    if not squish_button_value:
        return 0
    motor_min = 0.4
    motor_max = 1
    motor_range = motor_max - motor_min
    squish_max = 255
    squish_fraction = squish_button_value / squish_max
    return motor_min + squish_fraction * motor_range


def callback(state, left_motor, right_motor):
    left_motor_speed = right_motor_speed = 0
    l_squish = state[GamecubeButton.AXIS_L_SQUISH]
    r_squish = state[GamecubeButton.AXIS_R_SQUISH]

    if l_squish is not None and 0 <= l_squish <= 255:
        left_motor_speed = squish_button_to_motor_value(l_squish)
        left_motor.set(left_motor_speed)
    if r_squish is not None and 0 <= r_squish <= 255:
        right_motor_speed = squish_button_to_motor_value(r_squish)
        right_motor.set(right_motor_speed)


if __name__ == "__main__":
    L_PWM = 12
    L_FWD = 5
    L_REV = 6
    R_PWM = 13
    R_FWD = 16
    R_REV = 26

    left = Motor(L_PWM, L_FWD, L_REV)
    right = Motor(R_PWM, R_FWD, R_REV)
    gc = GamecubeController(state_callback_fn=callback, state_callback_args=[left, right])
    print("CAT BOTHERER 3002 ready to bother. Steer with L and R; press Start to end.")
    gc.blocking_read()
