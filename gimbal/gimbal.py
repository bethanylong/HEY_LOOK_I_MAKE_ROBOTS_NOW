from adafruit_servokit import ServoKit
import random
import sys
import threading
import time


class Gimbal:
    def __init__(
        self,
        pan_index=0,  # ServoKit index of the pan servo
        pan_lower_bound=0,  # Degrees
        pan_upper_bound=180,  # Degrees
        tilt_index=1,  # ServoKit index of the tilt servo
        tilt_lower_bound=52,  # Degrees
        tilt_upper_bound=156  # Degrees
    ):
        self._pca = ServoKit(channels=16)
        self._hw = {
            "pan": {
                "index": pan_index,
                "lower_bound": pan_lower_bound,
                "upper_bound": pan_upper_bound,
            },
            "tilt": {
                "index": tilt_index,
                "lower_bound": tilt_lower_bound,
                "upper_bound": tilt_upper_bound,
            }
        }
        self._pan = 50
        self._tilt = 50
        self.pan = self._pan
        self.tilt = self._tilt

    def _actuate(self, servo, percent):
        """Set given servo to given percentage of its safe swing angle."""
        if servo not in self._hw:
            raise ValueError("Don't know what '" + servo + "' is")
        if percent < 0 or percent > 100:
            raise ValueError("Give a `percent` value from 0 to 100 dummy")
        index = self._hw[servo]["index"]
        lower_bound = self._hw[servo]["lower_bound"]
        upper_bound = self._hw[servo]["upper_bound"]
        swing_angle = upper_bound - lower_bound
        desired_angle = lower_bound + (percent / 100) * swing_angle
        self._pca.servo[index].angle = desired_angle

    @property
    def pan(self):
        return self._pan

    @pan.setter
    def pan(self, angle):
        self._pan = angle
        self._actuate("pan", angle)

    @property
    def tilt(self):
        return self._tilt

    @tilt.setter
    def tilt(self, angle):
        self._tilt = angle
        self._actuate("tilt", angle)


def crazy_pan(gimbal, watch):
    for _ in range(1000):
        if watch["exit"]:
            return
        pan_angle = random.randint(0, 100)
        delay = random.randint(2, 20) / 10
        gimbal.pan = pan_angle
        time.sleep(delay)


def crazy_tilt(gimbal, watch):
    for _ in range(1000):
        if watch["exit"]:
            return
        tilt_angle = random.randint(0, 100)
        delay = random.randint(2, 20) / 10
        gimbal.tilt = tilt_angle
        time.sleep(delay)


def print_usage():
    print(f"usage: {sys.argv[0]} [random|reset]")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print_usage()
        sys.exit(1)

    gimbal = Gimbal()
    if sys.argv[1] == "random":
        watch = {"exit": False}
        try:
            pan_thread = threading.Thread(target=crazy_pan, name="pan thread", args=(gimbal, watch))
            tilt_thread = threading.Thread(target=crazy_tilt, name="tilt thread", args=(gimbal, watch))
            pan_thread.start()
            tilt_thread.start()
        except KeyboardInterrupt:
            watch["exit"] = True
            pan_thread.join()
            tilt_thread.join()
    elif sys.argv[1] == "reset":
        gimbal.pan = 50
        gimbal.tilt = 50
    else:
        print_usage()
        sys.exit(1)
