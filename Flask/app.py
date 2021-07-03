from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/xposypos/<string:pos>', methods=['POST'])
def processPos(pos):
    position = json.loads(pos)
    print()
    print("x position: " + str(position['x']))
    print("y position: " + str(position['y']))
    print()

    with open('pos.txt', 'a') as f:
        f.write("position: " + str(position['x']) + ", " + str(position['y']))
        f.close()

    return "done"

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
