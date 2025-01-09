#!/usr/bin/env python3

"""Debug note: run `pinctrl` to make sure the SDA/SCL pins (2 and 3) are actually in I2C mode, not GPIO mode."""

from adafruit_servokit import ServoKit
import random
import time

pca = ServoKit(channels=16)

interval = 15
#interval = 90
#swing = 180
swing_begin = 60
swing_range = 60
#delay = 0.2
delay = 2

#while True:
#    for angle in range(0, swing, interval):
#        for servo_num in range(16):
#            pca.servo[servo_num].angle = angle
#        time.sleep(delay)
#    for angle in reversed(range(0, swing, interval)):
#        for servo_num in range(16):
#            pca.servo[servo_num].angle = angle
#        time.sleep(delay)

"""
while True:
    angle = random.randint(swing_begin, swing_begin + swing_range)
    delay = random.randrange(5, 30) / 10
    #for servo_num in range(16):
    #    pca.servo[servo_num].angle = angle
    pca.servo[0].angle = angle
    time.sleep(delay)
"""

"""
midpoint = 90
pca.servo[0].angle = midpoint
for deviation in range(10, 90, 5):
    left_angle = midpoint - deviation
    right_angle = midpoint + deviation
    input(f"Hit enter to check angle of {left_angle} degrees")
    pca.servo[0].angle = left_angle
    input(f"Hit enter to check angle of {right_angle} degrees")
    pca.servo[0].angle = right_angle
"""

theoretical_midpoint = 90
theoretical_left_bound = 0
theoretical_right_bound = 180

BINARY_SEARCH = "binary search"
STEP_SEARCH = "step search"
mode = BINARY_SEARCH  # this should be an enum or something but whatever
last_angle = None

LEFT = "left side"
RIGHT = "right side"
YES = "yes"
NO = "no"

def next_angle(last_angle, lower, upper, mode, side):
    if side == LEFT:
        step_amount = 1
    elif side == RIGHT:
        step_amount = -1
    else:
        raise ValueError(f"Don't know how to handle side {side} :(")

    if mode == BINARY_SEARCH:
        angle = lower + (upper - lower) // 2
        if angle == last_angle:
            mode = STEP_SEARCH
            angle += step_amount
    elif mode == STEP_SEARCH:
        angle = last_angle + step_amount
    else:
        raise ValueError(f"Don't know how to handle mode {mode} :(")
    return angle

def was_accidental_single_step(angle, last_angle, side):
    if side == LEFT and angle == last_angle + 1:
        return True
    elif side == RIGHT and angle == last_angle - 1:
        return True
    else:
        return False


def get_response(angle):
    patience = 5
    for _ in range(patience):
        raw_response = input(f"Current angle is {angle} degrees. Is the servo happy with this? (y/n) ")
        if raw_response.lower().startswith("n"):
            return NO
        elif raw_response.lower().startswith("y"):
            return YES
        else:
            print("Say y or n")
    raise ValueError("User is illiterate")


def handle_no_response(angle, last_angle, lower, upper, mode, side):
    """If the user answered "no", that means we moved the servo too far, into a sad position."""
    new_lower = lower
    new_upper = upper
    new_mode = mode

    if side == LEFT:
        if lower == angle:
            new_mode = STEP_SEARCH
        else:
            new_lower = angle
    elif side == RIGHT:
        if upper == angle:
            new_mode = STEP_SEARCH
        else:
            new_upper = angle
    else:
        raise ValueError("bleh")

    return new_lower, new_upper, new_mode


def handle_yes_response(angle, last_angle, lower, upper, mode, side):
    """Either we were too timid and need to push our limits more, or we found a good bound."""
    new_lower = lower
    new_upper = upper
    finished = False

    if mode == STEP_SEARCH or was_accidental_single_step(angle, last_angle, side):
        # Gottem :)
        finished = True

    # Otherwise: too timid
    if side == LEFT:
        new_upper = angle
    elif side == RIGHT:
        new_lower = angle
    else:
        raise ValueError

    return new_lower, new_upper, finished

actual_left_bound = None
actual_right_bound = None

try:
    good_history = {LEFT: [], RIGHT: []}
    for side in (LEFT, RIGHT):
        print(f"\nCurrent side: {side}")
        if side == LEFT:
            # this is dorky
            lower = theoretical_left_bound
            upper = theoretical_midpoint
        elif side == RIGHT:
            lower = theoretical_midpoint
            upper = theoretical_right_bound

        for _ in range(30):  # reasonable limit
            angle = next_angle(last_angle, lower, upper, mode, side)

            print(f"{mode=} {lower=} {upper=} {angle=} {last_angle=}")
            pca.servo[0].angle = angle
            response = get_response(angle)
            if response == NO:
                lower, upper, mode = handle_no_response(angle, last_angle, lower, upper, mode, side)
            elif response == YES:
                good_history[side].append(angle)
                lower, upper, finished = handle_yes_response(angle, last_angle, lower, upper, mode, side)
                if finished:
                    break
            else:
                raise ValueError("Programmer is illiterate")
            last_angle = angle

        if side == LEFT:
            #actual_left_bound = angle
            actual_left_bound = min(good_history[side])
        if side == RIGHT:
            #actual_right_bound = angle
            actual_right_bound = max(good_history[side])

except KeyboardInterrupt:
    print()


if actual_left_bound is not None and actual_right_bound is not None:
    print(f"\nBound for left side: {actual_left_bound} degrees")
    print(f"\nBound for right side: {actual_right_bound} degrees")
    span = actual_right_bound - actual_left_bound
    actual_midpoint = actual_left_bound + (span / 2)
    print(f"\nActual midpoint: {actual_midpoint} degrees")
    pca.servo[0].angle = actual_midpoint
else:
    pca.servo[0].angle = 90
