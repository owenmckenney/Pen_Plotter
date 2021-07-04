from flask import Flask, render_template, request, jsonify
from flask_jsglue import JSGlue

app = Flask(__name__)
jsglue = JSGlue(app)

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/position', methods=['POST', 'GET'])
def getPosition():
    if request.method == 'POST':
        position = request.get_json()
        print(position)

        return jsonify(status="success", position=position)
    else:
        return render_template("index.html")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
