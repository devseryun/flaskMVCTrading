from flask import Flask, request, jsonify, Response
from flask_cors import CORS
from websocket import create_connection
import json

app = Flask(__name__)
CORS(app)

current_price = None


@app.route("/current_price", methods=["POST"])
def update_current_price():
    global current_price
    current_price = request.json.get("value")
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

