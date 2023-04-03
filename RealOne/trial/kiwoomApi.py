from PyQt5.QtWidgets import QApplication
from PyQt5.QAxContainer import QAxWidget
import json
import websocket
import requests
import sys

class KiwoomAPI:
    def __init__(self):   
        self.ocx = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.ocx.dynamicCall("CommConnect()")  # 로그인
        self.ocx.OnEventConnect.connect(self.on_login)  # 로그인 이벤트 연결

        # 웹소켓 서버 설정
        self.ws_url = "ws://localhost:8000/ws/"
        self.ws = websocket.WebSocketApp(self.ws_url, on_message=self.on_ws_message)

        # Flask 웹서버 설정
        self.flask_url = "http://localhost:5000"



    def on_login(self, err_code):
        if err_code == 0:  # 로그인 성공
            print("로그인 성공")
            self.ocx.dynamicCall("SetRealReg(QString, QString, QString, QString)", "1000", "", "215;20", "0")  # 실시간 시세 구독
            # "1000": 화면번호, "" : 종목코드 리스트, "215;20": 실시간 시세 구독항목, "0": 출력여부

            # 웹소켓 연결 시작
            self.ws.run_forever()

    def on_ws_message(self, message):
        data = json.loads(message)
        if data["type"] == "current_price":
            current_price = data["value"]
            print(f"현재가: {current_price}")

            # Flask 웹서버로 현재가 보내기
            self.send_to_flask(current_price)

    def send_to_flask(self, current_price):
        url = f"{self.flask_url}/current_price"
        headers = {"Content-Type": "application/json"}
        data = {"value": current_price}
        response = requests.post(url, data=json.dumps(data), headers=headers)
        print(f"Flask 웹서버 응답 코드: {response.status_code}")

    def receive_real_data(self, code, real_type, real_data):
        if real_type == "주식체결":
            items = real_data.split(";")
            curr_price = int(items[1])
            print(f"현재가: {curr_price}")

            # WebSocket 서버로 현재가 보내기
            data = {"type": "current_price", "value": curr_price}
            self.send_to_websocket(data)

    def send_to_websocket(self, data):
        url = "ws://localhost:8000/ws/"
        ws = websocket.create_connection(url)
        ws.send(json.dumps(data))
        ws.close()

if not QApplication.instance():
    app = QApplication(sys.argv)


if __name__ == "__main__":

    kiwoom_api = KiwoomAPI()
