import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pywinauto
import time
import requests
import json

class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()
        self.order_number = ''
        self.slack_webhook_url = 'https://slack.com/api/chat.postMessage' # Slack Incoming Webhook URL을 입력해주세요.

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        self.OnReceiveRealData.connect(self._receive_real_data)
        self.OnReceiveChejanData.connect(self._receive_chejan_data)

    def login(self):
        self.dynamicCall("CommConnect()")
        while self.getConnectState() != 1:
            time.sleep(0.1)
        return {'message': '로그인 성공'}

    def get_balance(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", "계좌번호 입력") # 자신의 계좌번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "비밀번호 입력") # 자신의 비밀번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00001_req", "opw00001", 0, "0101")
        while True:
            if self.tr_balance_event.is_set():
                self.tr_balance_event.clear()
                break
            QApplication.processEvents()
        account_info = self.account_info
        return account_info

    def get_portfolio(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", "계좌번호 입력") # 자신의 계좌번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "비밀번호 입력") # 자신의 비밀번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")
        while True:
            if self.tr_portfolio_event.is_set():
                self.tr_portfolio_event.clear()
                break
            QApplication.processEvents()
        portfolio = self.portfolio
        return portfolio

    def get_stock(self, code):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")
        while True:
            if self.tr_stock_event.is_set():
                self.tr_stock_event.clear()
                break
            QApplication.processEvents()
        stock_info = self.stock_info
        return stock_info

    def buy_order(self, code, quantity):
        self.order_number = ''
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["주문번호", "계좌번호", "주문유형", "주문수량", "종목코드", "주문가격", "거래구분", "원주문번호", ""])
        while not self.order_number:
            time.sleep(0.1)
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매수주문", "계좌번호", "2", quantity, code, 0, "1", self.order_number, ""])
        while True:
            if self.buy_order_event.is_set():
                self.buy_order_event.clear()
                break
            QApplication.processEvents()
        order_result = self.order_result
        return order_result

    def sell_order(self, code, quantity):
        self.order_number = ''
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["주문번호", "계좌번호", "주문유형", "주문수량", "종목코드", "주문가격", "거래구분", "원주문번호", ""])
        while not self.order_number:
            time.sleep(0.1)
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매도주문", "계좌번호", "1", quantity, code, 0, "1", self.order_number, ""])
        while True:
            if self.sell_order_event.is_set():
                self.sell_order_event.clear()
                break
            QApplication.processEvents()
        order_result = self.order_result
        return order_result

    def send_slack_message(self, channel, token, message):
        # 토큰이 널이 아니면 
        SLACK_BOT_TOKEN = "xoxb-4184524433281-5008927392563-qZQ6oS6GFDi2A8DyWSKqCeNg"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + SLACK_BOT_TOKEN
        }
        payload = {
            'channel': channel,
            'text': message
        }
        response = requests.post(self.slack_webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return {'message': 'Slack 메시지 전송 성공'}
        else:
            return {'message': 'Slack 메시지 전송 실패'}
    
    def _event_connect(self, err_code):
        if err_code == 0:
            print("로그인 성공")
        else:
            print("로그인 실패")

    def _receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, error_code, message, splm_msg):
        if rqname == "opw00001_req":
            self.account_info = {}
            total_purchase_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "총매입금액")
            total_purchase_price = int(total_purchase_price)
            self.account_info['total_purchase_price'] = total_purchase_price
            print("예수금: ", total_purchase_price)
            self.tr_balance_event.set()
        elif rqname == "opw00018_req":
            self.portfolio = []
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
            for i in range(rows):
                code = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목번호").strip()[1:]
                name = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명").strip()
                quantity = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "보유수량").strip()
                purchase_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "매입가").strip()
                current_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가").strip()
                profit_loss = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "손익금
            self.portfolio.append({
                'code': code,
                'name': name,
                'quantity': quantity,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'profit_loss': profit_loss
            })
            print("종목명: ", name, " 보유수량: ", quantity)
            self.tr_portfolio_event.set()
        elif rqname == "opt10001_req":
            self.stock_info = {}
            name = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "종목명").strip()
            current_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "현재가").strip()
            self.stock_info['name'] = name
            self.stock_info['current_price'] = current_price
            print("종목명: ", name, " 현재가: ", current_price)
            self.tr_stock_event.set()

    def _receive_real_data(self, code, real_type, real_data):
        pass

    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        if gubun == "0":
            order_number = self.dynamicCall("GetChejanData(int)", 9203).strip()
            if order_number:
                self.order_number = order_number
        elif gubun == "1":
            code = self.dynamicCall("GetChejanData(int)", 9001).strip()
            name = self.dynamicCall("GetChejanData(int)", 302).strip()
            order_status = self.dynamicCall("GetChejanData(int)", 913).strip()
            order_quantity = self.dynamicCall("GetChejanData(int)", 900).strip()
            order_price = self.dynamicCall("GetChejanData(int)", 901).strip()
            executed_quantity = self.dynamicCall("GetChejanData(int)", 911).strip()
            if self.order_number == self.dynamicCall("GetChejanData(int)", 9203).strip():
                if order_status == "접수":
                    message = f"{name}({code}) {order_status}되었습니다. 주문 수량: {order_quantity}, 주문 가격: {order_price}"
                elif order_status == "체결":
                    message = f"{name}({code}) {order_status}되었습니다. 주문 수량: {order_quantity}, 체결 수량: {executed_quantity}, 주문 가격: {order_price}"
                elif order_status == "확인":
                    message = f"{name}({code}) {order_status}되었습니다."
                self.send_slack_message(message)
        elif gubun == "4":
            pass

       
