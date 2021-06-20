from step_functions import Stepper
import math
import time
import RPi.GPIO as GPIO

class Plotter:

    def __init__(self, stepper1, stepper2, limit1_pin, limit2_pin):
        self.arm_length = arm_length

        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
    
    def home(self):
        stepper1.set_direction(1)
        stepper2.set_direction(0)

        while GPIO.input(limit1_pin) == False:
            stepper1.step()
        # start position tracking for stepper1

        while GPIO.input(limit2_pin) == False:
            stepper2.step()

        # start position tracking for stepper2

        # return to 'home' position
