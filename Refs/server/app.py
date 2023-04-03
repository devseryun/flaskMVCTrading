from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
sys.path.append("./")
from PyQt5.QtWidgets import *     
from PyQt5 import uic             # ui 파일을 가져오기위한 함수
from PyQt5.QtCore import *        # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from PyQt5.QtTest import *
from PyQt5.QtWidgets import *                 # GUI의 그래픽적 요소를 제어
from PyQt5.QAxContainer import *              # 키움증권의 클레스를 사용할 수 있게 한다.(QAxWidget)
from PyQt5Singleton import Singleton
from config.kiwoomType import *  
from kiwoomRelated.errorCode import *
from kiwoomRelated.kiwoomServer import KiwoomServer

app = Flask(__name__)
CORS(app)

ks = KiwoomServer()

form_class = uic.loadUiType("./UpperLimitPriceTrading.ui")[0]

class KiwoomOperating(QMainWindow, QWidget, form_class):

    def __init__(self, *args, **kwargs):
        super(KiwoomOperating, self).__init__(*args, **kwargs)
        form_class.__init__(self)
        self.setUI() 
        self.kiwoomReal = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')  


        # 코드 생략

    def setUI(self):
        self.setupUi(self)  

@app.route("/")
def main():
    return render_template('index.html')

@app.route("/login")
def login():
    kiwoom_operating = KiwoomOperating()
    return "로그인 성공"

@app.route('/api/comm_connect', methods=['POST'])
def comm_connect():
    ks.comm_connect()
    return jsonify(success=True)

@app.route('/api/get_login_info', methods=['GET'])
def get_login_info():
    tag = request.args.get('tag')
    result = ks.get_login_info(tag)
    return jsonify(result=result)

# POST 메소드로 매매 요청을 받음
@app.route('/order', methods=['POST'])
def process_order():
    try:
        code = request.form['code']
        price = request.form['price']
        quantity = request.form['quantity']

        # Kiwoom API를 통해 매매 실행
        result = kiwoom.buy_order(code, int(price), int(quantity))
        if result:
            print("매수 체결되었습니다.")
            result = kiwoom.sell_order(code, int(price), int(quantity))
            if result:
                print("매도 체결되었습니다.")
                return "Success"
            else:
                print("매도 체결 실패하였습니다.")
                return "Failure"
        else:
            print("매수 체결 실패하였습니다.")
            return "Failure"
    except Exception as e:
        print(e)
        return "Failure"


if __name__ == '__main__':
    # app.run(debug=True)       
    app.run(host='127.0.0.1', port=9999)    