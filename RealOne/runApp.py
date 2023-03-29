import time
import json
from collections import defaultdict
from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from pykiwoom.kiwoom import *

app = Flask(__name__)
CORS(app)
# 키움증권 API 객체 생성

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

state = kiwoom.GetConnectState()
if state == 0:
    print("미연결")
elif state == 1:
    print("연결완료")

# 결과를 저장하기 위한 딕셔너리
code_data_result = defaultdict(dict)

# # 이벤트 핸들러
# def handle_opt10001(tr_code, rq_name, record_name, prev_next, data):
#     code_data_result[data['종목코드']] = data

# # 이벤트 핸들러 등록
# kiwoom.connect_event("OPT10001", "tr_data_received", handle_opt10001)

@app.route('/savings', methods=['GET'])
def get_stock_price():
    code = "005930"  # 삼성전자 주식 코드
    result = kiwoom.GetMasterLastPrice(code)  # 주식 현재가 가져오기

    if result is not None:
        price = int(result)
        return jsonify({"code": code, "price": price})
    else:
        return jsonify({"error": "주가 정보를 가져오는 데 실패했습니다."}), 500

def get_account_info(account_number):
    # kiwoom.SetInputValue("계좌번호", account_number)
    # kiwoom.SetInputValue("비밀번호", "")  # 사용자의 비밀번호를 입력하세요
    # kiwoom.SetInputValue("비밀번호입력매체구분", "00")
    # kiwoom.SetInputValue("조회구분", "2")
    # kiwoom.CommRqData("opw00018_req", "opw00018", 0, "2000")

    # while kiwoom.remained_data:
    #     time.sleep(0.2)
    #     kiwoom.CommRqData("opw00018_req", "opw00018", 2, "2000")
    df = kiwoom.block_request("opw00001",
                        계좌번호=account_number,
                        비밀번호="",
                        비밀번호입력매체구분="00",
                        조회구분=2,
                        output="예수금상세현황",
                        next=0)

    return df

@app.route('/getAccountInfo', methods=['GET'])
def get_account_info_route():
    account_number = kiwoom.GetLoginInfo("ACCNO")[1]  # 첫 번째 계좌번호를 가져옵니다. 필요한 경우 계좌번호를 변경하세요.
    print(account_number)
    account_info = get_account_info(account_number)

    if account_info:
        return jsonify(account_info)
    else:
        return jsonify({"error": "계좌 평가 잔고 내역을 가져오는 데 실패했습니다."}), 500

def get_single_code_data(code):
    kiwoom.SetInputValue("종목코드", code)
    kiwoom.CommRqData("opt10001_req", "opt10001", 0, "0101")

    while code not in code_data_result:
        time.sleep(0.2)

    return code_data_result.pop(code)



@app.route('/getSingleCodeData/<code>', methods=['GET'])
def get_single_code_data_route(code):
    if not code:
        return jsonify({"error": "종목 코드를 입력해주세요."}), 400

    code_data = get_single_code_data(code)

    if code_data:
        return jsonify(code_data)
    else:
        return jsonify({"error": "주가 정보를 가져오는 데 실패했습니다."}), 500

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=False)