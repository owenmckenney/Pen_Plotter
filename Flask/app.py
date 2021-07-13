from flask import Flask, render_template, request, jsonify
from flask_jsglue import JSGlue

app = Flask(__name__)
jsglue = JSGlue(app)

import math
from step_functions import Stepper
import RPi.GPIO as GPIO

class Plotter:

    def __init__(self, stepper1, stepper2, limit1_pin, limit2_pin, arm_length):
        self.arm_length = arm_length
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)

        self.current_top_angle = 60
        self.current_bottom_angle = 60

    
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

    def track_pos(self):
        

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

        inner_angle = math.degrees(math.acos(left_angle_raw))

        left_angle = theta - inner_angle
        right_angle = theta + inner_angle

        start_angle = 60
        start_distance = self.arm_length




        
        #return r, theta, math.degrees(inner_angle)

s1 = Stepper(2, 3, 23, 1600, (1,7,8), "Full")
s2 = Stepper(16, 20, 24, 1600, (1,7,8), "Full")
p = Plotter(s1, s2, 5, 6, 160)

@app.route('/')
def index():
    return render_template("index.html")

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

