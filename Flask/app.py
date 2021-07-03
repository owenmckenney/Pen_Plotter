from flask import Flask, render_template, request, redirect, session
import json
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/xposypos/<string:pos>', methods=['POST'])
def processPos(pos):
    pos = json.loads(pos)
    print()
    print("x position: " + str(pos['x']))
    print("y position: " + str(pos['y']))
    print()

    with open('pos.txt', 'a') as f:
        f.write("position: " + str(pos['x']) + ", " + str(pos['y']))
        f.close()

    return "done"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
