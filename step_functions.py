import time
import RPi.GPIO as GPIO
GPIO.setwarnings(False)

class Stepper:

    def __init__(self, dir_pin, step_pin, slp_pin, spr, mode_pins, step_type):
        self.dir_pin = dir_pin
        self.step_pin = step_pin
        self.slp_pin = slp_pin
        self.spr = spr
        self.mode_pins = mode_pins
        self.step_type = step_type
        self.delay = 1 / 2000
        self.cw = 1
        self.ccw = 0
        
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.dir_pin, GPIO.OUT)
        GPIO.setup(self.step_pin, GPIO.OUT)
        GPIO.setup(self.slp_pin, 0)
        GPIO.output(self.dir_pin, self.cw)

        GPIO.setup(self.mode_pins, GPIO.OUT)
        resolution = {"Full": (0,0,0),
                      "Half": (1,0,0),
                      "1/4": (0,1,0),
                      "1/8": (1,1,0),
                      "1/16": (0,0,1),
                      "1/32": (1,0,1)}
        GPIO.output(self.mode_pins, resolution[self.step_type]) 
    
    def step(self, delay):
        GPIO.output(self.step_pin, GPIO.HIGH)
        time.sleep(delay)
        GPIO.output(self.step_pin, GPIO.LOW)
        time.sleep(delay)

    def set_direction(self, direction):
        GPIO.output(self.dir_pin, direction)

    def Rotate(self, rotations, d):
        GPIO.setmode(GPIO.BCM)
        GPIO.output(self.dir_pin, d)
        
        for x in range(self.spr * rotations):
           self.step(self.delay)

    def Accel(self, accel_point, accel_delay, d, s):
        increment = (self.delay / accel_delay) ** (1 / (accel_point - 1))

        for x in range(s):
            if x < accel_point - 1 or x > s - accel_point:
                self.step(accel_delay)
                    
                if x < accel_point - 1:
                    accel_delay = accel_delay * increment
                    print("Accelerated", str(round(accel_delay, 4)), str(d))
                else: 
                    accel_delay = accel_delay / increment
                    print("De-accelerated", str(round(accel_delay, 4)), str(d))
            else:
                self.step(accel_delay)
                print("Constant", str(round(accel_delay, 4)), str(d))

    def Rotate_Ramp_Up_Down(self, rotations, d):
        GPIO.output(self.dir_pin, d)
        accel_point = self.spr / 64 * rotations 
        accel_delay = 0.05
        self.Accel(accel_point, accel_delay, d, self.spr * rotations)
        
    def Oscilate(self, instances):
        GPIO.output(self.dir_pin, self.ccw)
        accel_point = self.spr / 200
        accel_delay = 0.05
        increment = (self.delay / accel_delay) ** (1 / (accel_point - 1))
        direction = self.ccw
        print(accel_delay, increment)
        self.Accel(accel_point, accel_delay, direction, int(self.spr / 32))

        accel_delay = 0.05
        GPIO.output(self.dir_pin, self.cw)
        direction = self.cw

        print("done with first")
 
        for x in range(instances):
            self.Accel(accel_point, accel_delay, direction, int(self.spr / 16))

            if direction == self.ccw:
                direction = self.cw
                GPIO.output(self.dir_pin, self.cw)
            else:
                direction = self.ccw
                GPIO.output(self.dir_pin, self.ccw)

        self.Accel(accel_point, accel_delay, direction, int(self.spr / 32))

class Equal_Step:
    
    def __init__(self, s1, s2):
        self.s1 = s1
        self.s2 = s2
        self.delay = 1 / 2000 

    def equal_step(self, steps1, dir1, steps2, dir2):
        ma = max(steps1, steps2)
        mi = min(steps1, steps2)
        s_ma = 0
        s_mi = 0

        self.s1.set_direction(dir1)
        self.s2.set_direction(dir2)
    
        if ma == steps1:
            s_ma = self.s1
            s_mi = self.s2
        else:
            s_ma = self.s2
            s_mi = self.s1

        if mi == 0:
            for x in range(ma):
                s_ma.step(self.delay)
            return 'done'

        ratio = int(ma / mi)
        leftover = ma % mi

        for x in range(ma - leftover):
            s_ma.step(self.delay)
            if x % ratio == 0:
                s_mi.step(self.delay)

        for x in range(leftover):
            s_ma.step(self.delay)

        return 'done'
            

if __name__ == "__main__":
    # dir, step, sleep, spr, (mode pins), mode 
    stepper1 = Stepper(20, 21, 16, 3200, (1,7,8), "Full")
    #stepper1 = Stepper(2, 3, 23, 1600, (1,7,8), "Full")
    #stepper2  Stepper(16, 20, 24, 1600, (1,7,8), "Full")
    #stepper1.Rotate(1, 1)
    #stepper1.equal_step(473, 39)

    equal = Equal_Step(stepper1, stepper2)
    equal.equal_step(473, 0, 39, 1)

    #es(stepper1, 200, stepper2, 10)

    #stepper2.Rotate(1, 1)
    #stepper1.Rotate_Ramp_Up_Down(1, 1)
    #stepper1.Oscilate(4)


