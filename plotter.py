import math
from step_functions import Stepper, Equal_Step
import RPi.GPIO as GPIO

class Plotter:

    def __init__(self, stepper1, stepper2, limit1_pin, limit2_pin, arm_length):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.arm_length = arm_length
        self.stepper1 = stepper1
        self.stepper2 = stepper2
        self.limit1_pin = limit1_pin
        self.limit2_pin = limit2_pin
        
        GPIO.setup(self.limit1_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.limit2_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        self.left_angle = 30
        self.right_angle = 150

        self.delay = 1 / 2000

        self.path = []

        self.es = Equal_Step(self.stepper1, self.stepper2)
    
    def home(self):
        self.stepper1.set_direction(0)
        self.stepper2.set_direction(0)

        while GPIO.input(self.limit1_pin) == False:
            self.stepper1.step(self.delay)
            self.stepper2.step(self.delay)

        print("homed s1")
            
        self.stepper1.set_direction(1)
        self.stepper2.set_direction(1)

        while self.left_angle < 30:
            self.stepper1.step(self.delay)
            self.stepper2.step(self.delay)
            self.left_angle += 0.45

        while GPIO.input(self.limit2_pin) == False:
            self.stepper2.step(self.delay)

        print("homed s2")
            
        self.stepper2.set_direction(0)

        while self.right_angle > 150:
            self.stepper2.step(self.delay)
            self.right_angle -= .45

        return "home"

    def collect_pos(self, pos):
        #if pos != self.path[len(self.path) - 1]:
        self.path.append(pos)

    def get_path(self):
        return self.path

    def reset_path(self):
        self.path = [];

    def update_pos(self, x_pos, y_pos):
        x_pos = int(x_pos)
        y_pos = int(y_pos)
        r = math.sqrt(x_pos ** 2 + y_pos ** 2)

        if x_pos == 0:
            theta = 90
        else:
            theta = math.degrees(math.atan(y_pos / x_pos))
            if theta < 0:
                theta *= -1
            else:
                theta = 180 - theta

        inner_angle_raw = (self.arm_length ** 2 + r ** 2 - self.arm_length ** 2) / (2 * self.arm_length * r)

        if inner_angle_raw > 1:
            inner_angle_raw = .99

        inner_angle = math.degrees(math.acos(inner_angle_raw))
        
        current_la = theta - inner_angle
        current_ra = theta + inner_angle

        la_dif = current_la - self.left_angle
        ra_dif = current_ra - self.right_angle

        la_steps = round(la_dif / 0.45) * -1
        ra_steps = round(ra_dif / 0.45) * -1

        self.es.equal_step(la_steps, ra_steps)        
        
        self.left_angle = round(current_la, 5)
        self.right_angle = round(current_ra, 5)
        
        '''
        print('\nposition: ', x_pos, y_pos)
        print('theta: ', theta, ' left_angle: ', self.left_angle, ' right_angle: ', self.right_angle)
        print('stepped ', la_steps, ' on left, ', ra_steps, ' on right')
        '''

    def draw(self):
        for x in range(0, len(self.path)):
            #self.update_pos(self.path[x][0], self.path[x][1])
            print(self.path[x])

