from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jsglue import JSGlue

app = Flask(__name__)
jsglue = JSGlue(app)

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
        
        self.left_angle = -30
        self.right_angle = 210

        self.delay = 1 / 2000

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

    def update_pos(self, x_pos, y_pos):
        x_pos /= 2
        y_pos /= 2
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

        la = theta - inner_angle
        ra = theta + inner_angle
        la_dif = la - self.left_angle
        ra_dif = ra - self.right_angle

        start_angle = 60
        start_distance = self.arm_length

        self.es.equal_step(la_dif, ra_dif)        
            
        
        #return r, theta, math.degrees(inner_angle)

s1 = Stepper(2, 3, 23, 1600, (1,7,8), "Full")
s2 = Stepper(16, 20, 24, 1600, (1,7,8), "Full")
p = Plotter(s1, s2, 5, 6, 160)

@app.route('/', methods=['POST', 'GET'])
def index():    
    return render_template("index.html")

@app.route('/home', methods=['POST', 'GET'])
def checkButtons():
    if request.method == 'POST':
        if request.form.get('homebtn') == 'home':
            print("Starting Homing...")
            #p.home()            
            print("Successfully Homed.")
            return redirect(url_for('checkButtons'))
        else:
            pass

    elif request.method == 'GET':
        return render_template('index.html')

@app.route('/position', methods=['POST', 'GET'])
def getPosition():
    if request.method == 'POST':
        position = request.get_json()
        #print(position)
        print()
        print(p.update_pos(position['x'], position['y']))
        print()
        return position
        #return jsonify(status="success", position=position)
    #else:
        #return render_template("index.html")

#def return_position():

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

