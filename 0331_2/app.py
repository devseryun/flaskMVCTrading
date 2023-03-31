# app.py
from flask import Flask, jsonify, request
import redis

app = Flask(__name__)
db = redis.StrictRedis(host='localhost', port=6369, db=0)

def send_request_to_stock_program(request_type, data):
    db.set(request_type, data)
    db.set(request_type + '_result', None)

    while db.get(request_type + '_result') is None:
        pass

    result = db.get(request_type + '_result').decode('utf-8')
    db.set(request_type + '_result', None)
    return result

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
    account_num = request.json.get("account_number")
    result = send_request_to_stock_program('select_account', account_num)
    print(result)
    return jsonify({'select_account': result})

# #종목조회 정보
@app.route("/get_single_codeInfo", methods=["GET"])
def getSingleCodeInfo():
    scode = request.args.get("scode")
    result = send_request_to_stock_program('get_single_codeInfo', scode)
    print(result)
    return jsonify({"result": result})

@app.route('/start_trading')
def start_trading():
    result = send_request_to_stock_program('start_trading', '')
    return jsonify({'start_trading': result})

@app.route('/stop_trading')
def stop_trading():
    result = send_request_to_stock_program('stop_trading', '')
    return jsonify({'stop_trading': result})

################################# POST방식############################################
# @app.route('/select_account', methods=['POST'])
# def select_account():
#     print("select_account")
#     account_num = request.form['account_num']
#     result = send_request_to_stock_program('select_account', account_num)
#     print(result)
#     return jsonify({'select_account': result})

# # @app.route("/order", methods=["POST"])
# # def stock_order():
# #     account_number = request.json.get("account_number")
# #     stock_code = request.json.get("stock_code")
# #     order_type = request.json.get("order_type")
# #     quantity = request.json.get("quantity")
# #     price = request.json.get("price")
# #     order_result = kiwoom.send_order(account_number, stock_code, order_type, quantity, price)
# #     return jsonify({"result": order_result})


if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=True)
