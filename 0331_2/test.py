# app.py
from flask import Flask, jsonify, request,render_template
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import redis
import json
import time
import requests

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app)
db = redis.StrictRedis(host='localhost', port=6379, db=0)
db.flushdb()

def send_request_to_stock_program(request_type, data):
    print('request_type: ',request_type,'\n')
    print('data: ',data,'\n')

    db.set(request_type, data)
    db.delete(request_type + '_result')

    while db.get(request_type + '_result') is None:
        pass

    result = db.get(request_type + '_result')
    if result is not None:
        result = result.decode("utf-8")
        db.delete(request_type + '_result')
    else:
        result = "No result found"
    return result

@app.route("/")
def index():
    return render_template("index.html")



# 실시간 주가 정보 SocketIO 이벤트 핸들러 추가
@socketio.on('subscribe_stock')
def handle_subscribe_stock_price(data):
    print(data)
    scode = data['code']
    while True:
        price = send_request_to_stock_program('handle_realtime_stock_price', scode)
        print('price', price) 
        emit('stock_price', {'price': price})
        time.sleep(1)  # Adjust this value to set the update interval    

if __name__ == '__main__':
    socketio.run(app,'0.0.0.0',port=5000, debug=True)