from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_jsglue import JSGlue
from plotter import Plotter

app = Flask(__name__)
jsglue = JSGlue(app)

s1 = Stepper(2, 3, 23, 1600, (1,7,8), "Full")
s2 = Stepper(16, 20, 24, 1600, (1,7,8), "Full")
p = Plotter(s1, s2, 5, 6, 160)

@app.route('/', methods=['POST', 'GET'])
def index():    
    return render_template("index.html")

@app.route('/buttton', methods=['POST', 'GET'])
def checkButtons():
    if request.method == 'POST':
        if request.form.get('homebtn') == 'Home':
            print("Starting Homing...")
            #p.home()            
            print("Successfully Homed.")
            return redirect(url_for('checkButtons'))

        if request.form.get('drawbtn') == 'Draw':
            print("starting draw")
            p.draw()
            print("drawing done")
            return redirect(url_for('checkButtons'))

        if request.form.get('resetbtn') == 'Reset':
            print("reset")
            p.reset_path()
            return redirect(url_for('checkButtons'))

    

    elif request.method == 'GET':
        return render_template('index.html')


@app.route('/position', methods=['POST', 'GET'])
def getPosition():
    if request.method == 'POST':
        position = request.get_json()
        #p.update_pos(position['x'], position['y'])
        p.collect_pos(position)
        return position

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)

