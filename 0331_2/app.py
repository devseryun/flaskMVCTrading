# app.py
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
import redis
import json
import time
import requests

app = Flask(__name__)
socketio = SocketIO(app)

app = Flask(__name__)
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

def post_message(channel, text):
    
    SLACK_BOT_TOKEN = "xoxb-4184524433281-5008927392563-qZQ6oS6GFDi2A8DyWSKqCeNg"
    headers = {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer ' + SLACK_BOT_TOKEN
    }
    payload = {
        'channel': channel,
        'text': text
    }
    r = requests.post('https://slack.com/api/chat.postMessage',
                    headers=headers,
                    data=json.dumps(payload)
                    )
        
@app.route('/test')
def test():
    print("test")
    return jsonify({'test': "test"})

@app.route('/account_info')
def account_info():
    print("account_info")
    result = send_request_to_stock_program('account_info', '')
    return jsonify({'account_info': result})

@app.route('/my_balance_check')
def my_balance_check():
    print("my_balance_check")    
    result = send_request_to_stock_program('my_balance_check', '')
    return jsonify({'my_balance_check': result})

@app.route('/select_account', methods=['GET'])
def select_account():
    print("select_account")
    # account_num = request.form['account_num']
    account_num = request.args.get("account_num")
    print("account_number",account_num)
    result = send_request_to_stock_program('select_account', account_num)
    retrieved_data =  json.loads(result)
    print(retrieved_data)
    post_message("#autobot",retrieved_data) #슬랙으로 메시지 전송
    return jsonify({'result': retrieved_data})

# #종목조회 정보(단순정보)
@app.route("/get_single_codeInfo", methods=["GET"])
def getSingleCodeInfo():
    scode = request.args.get("scode")
    print("scode: ",scode)
    result = send_request_to_stock_program('get_single_codeInfo', scode)
    print(result)
    return jsonify({"result": result})

# #종목조회및 셋팅 ===> 사실상 안씀
@app.route("/get_single_codeInfo_and_setting", methods=["GET"])
def getSingleCodeInfoAndSetting():
    scode = request.args.get("scode")
    print("scode: ",scode)
    result = send_request_to_stock_program('get_single_codeInfo_and_setting', scode)
    print(result)
    # return 값으로 현재가를 전달.
    return jsonify({"result": result})

@app.route('/start_trading', methods=['POST'])
def start_trading():
    data = request.get_json() # 포스트로 유저의 6가지값 받아옴
    result = send_request_to_stock_program('start_trading', data)
    return jsonify({'start_trading': result})

@app.route('/stop_trading') # 구현해야함
def stop_trading():
    result = send_request_to_stock_program('stop_trading', '')
    return jsonify({'stop_trading': result})


# 실시간 주가 정보 SocketIO 이벤트 핸들러 추가
@socketio.on('subscribe_stock_price')
def handle_subscribe_stock_price(stock_code):
    # 여기에 실시간 주가 정보를 받아오는 코드를 작성하세요.
    # 주기적으로 주가 정보를 클라이언트에게 전송
    # scode = data['code']
    while True:
        price = send_request_to_stock_program('handle_realtime_stock_price', stock_code)
        emit('stock_price', {'price': price})
        time.sleep(1)  # Adjust this value to set the update interval    


# 주문 체결 결과 이벤트 핸들러
@socketio.on('subscribe_order_execution')
def handle_subscribe_order_execution(order_info):
    # 여기에 주문 체결 결과를 받아오는 코드를 작성하세요.
    # 주기적으로 주문 체결 결과를 클라이언트에게 전송
    pass



# 실시간 주가 요청을 처리하는 로직을 구현합니다.
# 여기서는 예시로 무작위 값을 사용합니다.
# import random
# stock_real_time_price = random.randint(1000, 10000)

# 클라이언트에게 실시간 주가 정보를 전달합니다.
# emit('stock_real_time_price', {'scode': scode, 'price': stock_real_time_price})

######################## 아래는 클라이언트 코드
# <!-- Add these elements -->
# <input type="text" id="stock_code" placeholder="Enter stock code">
# <button id="subscribe_stock">Subscribe</button>
# <p>Realtime price: <span id="price"></span></p>

# <!-- Add these scripts -->
# <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.3.2/socket.io.min.js"></script>
# <script>
#     const socket = io();

#     $("#subscribe_stock").click(function() {
#         const stock_code = $("#stock_code").val();
#         socket.emit('subscribe_stock', {code: stock_code});
#     });

#     socket.on('stock_price', function(data) {
#         $("#price").text(data.price);
#     });
# </script>
########################

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=True)