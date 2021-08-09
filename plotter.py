import math
import asyncio
from step_functions import Stepper
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
        self.loop = asyncio.get_event_loop()
        self.limit1_hit = False
        self.limit2_hit = False

        self.left_angle = 30
        self.right_angle = 150
        self.delay = 1 / 20
        self.path = []
        self.run = True

        #self.es = Equal_Step(self.stepper1, self.stepper2)
    
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

    def equal_step(self, steps1, steps2):
        
        if steps1 < 0:
            self.stepper1.set_direction(0)
            steps1 *= -1
        else:
            self.stepper1.set_direction(1)

        if steps2 < 0:
            self.stepper2.set_direction(1)
            steps2 *= -1
        else:
            self.stepper2.set_direction(0)

        ma = max(steps1, steps2)
        mi = min(steps1, steps2)
        s_ma = 0
        s_mi = 0
 
        if ma == steps1:
            s_ma = self.stepper1
            s_mi = self.stepper2
        else:
            s_ma = self.stepper2
            s_mi = self.stepper1

        if mi == 0:
            for x in range(ma):
                if self.check_limits(s_ma) != True:
                    s_ma.step(self.delay)
            return 'done'

        ratio = int(ma / mi)
        leftover = ma % mi

        for x in range(ma - leftover):
            if self.check_limits(s_ma) != True:
                s_ma.step(self.delay)
            if x % ratio == 0:
                if self.check_limits(s_mi) != True:
                    s_mi.step(self.delay)

        for x in range(leftover):
            if self.check_limits(s_ma) != True:
                s_ma.step(self.delay)

        return 'done', mi, ma

    def collect_pos(self, pos):
        array_pos = [pos['x'], pos['y']]
        #print(len(self.path))
        if len(self.path) >= 1 and array_pos != self.path[len(self.path) - 1]:
            self.path.append(array_pos)
        elif len(self.path) < 1:
            self.path.append(array_pos)

    def get_path(self):
        return self.path

    def reset_path(self):
        self.path = [];

    def check_limits(self, limit_type):
        if limit_type == self.stepper1:
            if GPIO.input(self.limit1_pin):
                self.limit1_hit = True
            else:
                self.limit1_hit = False
        else:
            if GPIO.input(self.limit2_pin):
                self.limit2_hit = True
            else:
                self.limit2_hit = False

    def update_pos(self, x_pos, y_pos):
        if x_pos == 'pen_down' or x_pos == 'pen_up':
            return

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
         
        #self.es.equal_step(la_steps, ra_steps, limit1)      
        self.equal_step(la_steps, ra_steps)
        
        self.left_angle = round(current_la, 5)
        self.right_angle = round(current_ra, 5)
        
        '''
        print('\nposition: ', x_pos, y_pos)
        print('theta: ', theta, ' left_angle: ', self.left_angle, ' right_angle: ', self.right_angle)
        print('stepped ', la_steps, ' on left, ', ra_steps, ' on right')
        '''

    def draw(self):
        for x in range(0, len(self.path)):
            self.update_pos(self.path[x][0], self.path[x][1])
            print(self.path[x])

