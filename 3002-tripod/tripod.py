from gpiozero import PWMOutputDevice, DigitalOutputDevice

L_PWM = 12
L_FWD = 5
L_REV = 6
R_PWM = 13
R_FWD = 16
R_REV = 26

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


if __name__ == "__main__":
    left = Motor(L_PWM, L_FWD, L_REV)
    right = Motor(R_PWM, R_FWD, R_REV)
    left.set(1)
    right.set(1)
    input("Press enter to exit")
