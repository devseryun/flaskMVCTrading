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
    print('send_request_to_stock_program')
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

tickerPrice = None
isTradingStop = False
@app.route("/")
def index():
    return render_template("index.html")

@app.route('/test')
def test():
    print("test")
    return jsonify({'test': "test"})

# #내 계좌정보 전달
# @socketio.on('request_account_list')
# def handle_request_account_list():
#     account_list = send_request_to_stock_program('account_info','')
#     emit('account_list', {'account_list': account_list})


@app.route('/account_list', methods=["GET"])
def get_account_list():
    account_list = account_list = send_request_to_stock_program('account_info','')
    account_list = account_list.split(';')
    return jsonify({'account_list': account_list})

@app.route('/my_balance_check')
def my_balance_check():
    print("my_balance_check")    
    result = send_request_to_stock_program('my_balance_check', '')
    return jsonify({'my_balance_check': result})


# 소켓으로 선택 계좌 정보 받아와서 kiwoom.account_num 상태값변경만 함.
@socketio.on('select_account')
def handle_select_account(data):
    account = data['account']
    # do something with the selected account
    print(f"Selected account: {account}")
    result = send_request_to_stock_program('select_account', account)
    print(result)
    post_message("#autobot",result) #슬랙으로 메시지 전송


# #종목조회 정보(단순정보)
@app.route("/get_single_codeInfo", methods=["GET"])
def getSingleCodeInfo():
    scode = request.args.get("scode")
    print("scode: ",scode)
    result = send_request_to_stock_program('get_single_codeInfo', scode)
    print(result)
    return jsonify({"result": result})

# 실시간 계좌평가잔고내역 보여주는  SocketIO 이벤트 핸들러 추가
@socketio.on('request_account_balance')
def handle_realtime_account_info(data):
    selectedAccount = data['selectedAccount']
    balance = send_request_to_stock_program('handle_realtime_account_info',selectedAccount)
    balance = json.loads(balance)
    print(balance)
    arr = list(balance.values())
    print(arr)
    emit('account_balance', {'balance': arr})


# 실시간 주가 정보 SocketIO 이벤트 핸들러 추가
@socketio.on('subscribe_stock')
def handle_subscribe_stock_price(data):
    print('subscribe_stock: ',data)
    scode = data['code']
    while True:
        price = send_request_to_stock_program('handle_realtime_stock_price', scode)
        print('price', price)
        tickerPrice = price 
        emit('stock_price', {'price': price})
        time.sleep(1)  # Adjust this value to set the update interval    

# 매도매수 SocketIO 이벤트 핸들러 추가
@socketio.on('start_buying')
def handle_start_buying(data):
    forSendingData={
        "trCode":None,
        "nowTrPrice":None,
        "status":"", # 거래시작/ 거래중지
        "tradingStatus":"", # 6개의 스테이터스 BUY BUY_REQUESTING BUY_CANCELING SELL SELL_REQUESTING SELL_CANCELING
        "buyStatus":{
        "buyReqGoPrice":int(data['buyReqGoPrice']),
        "buyPrice":int(data['buyPrice']),
        "buyReqWithdrawPrice":int(data['buyReqWithdrawPrice']),
        },
        "sellStatus":{
        "sellReqGoPrice":int(data['sellReqGoPrice']),
        "sellPrice":int(data['sellPrice']),
        "sellReqWitdrawPrice":int(data['sellReqWitdrawPrice']),
    }}
    print("handle_start_buying tickerPrice:", tickerPrice)
    if tickerPrice is not None:
        # Start buying logic
        if isTradingStop is not True:
            while True:
                status = send_request_to_stock_program('start_trading', forSendingData)
                print(status)
                emit('trade_result', {'result': status})
                time.sleep(1)  # Adjust this value to set the update interval

@app.route('/stop_trading') # 구현해야함
def stop_trading():
    result = send_request_to_stock_program('stop_trading', '')
    isTradingStop =True
    print(result)
    return jsonify({'result': result})


# 주문 체결 결과 이벤트 핸들러
@socketio.on('subscribe_order_execution')
def handle_subscribe_order_execution(order_info):
    # 여기에 주문 체결 결과를 받아오는 코드를 작성하세요.
    # 주기적으로 주문 체결 결과를 클라이언트에게 전송
    pass

if __name__ == '__main__':
    socketio.run(app,'0.0.0.0',port=5000, debug=True)