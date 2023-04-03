from flask import Blueprint, Flask, jsonify, request
# from app.connections.fakeKiwoom import *
from app.entity.kiwoomEntity import *
from app.connections.realKiwoom import Kiwoom            # 로그인을 위한 클래스
import threading
from app.Thread3 import Thread3       # 계좌관리 
from PyQt5.QtWidgets import *
app = Flask(__name__)

# kiwoomyo = KiwoomYo()
# kiwoomyo.CommConnect()
# state = kiwoomyo.GetConnectState()
# if state == 0:
#     print("미연결")
# elif state == 1:
#     print("연결완료")
    
dto = DataTransferObject()
# kk = Kiwoom()





# def fetch_data(result_queue):
#     df = kiwoom.block_request("opt10001",
#                               종목코드="005930",
#                               output="주식기본정보",
#                               next=0)
#     result_queue.put(df)



# @app.route("/Login", methods=["GET"])
# def logo():
#     # result_queue = queue.Queue()
#     # worker = threading.Thread(target=fetch_data, args=(result_queue,))
#     # worker.start()
#     # worker.join()

#     # df = result_queue.get()
#     # print(df)
#     # return jsonify(df.to_dict())
#     res = kiwoomyo.GetLoginInfo()
#     print(res)
#     return jsonify({"res":dto})

# @app.route("/singgleTr", methods=["GET"])
# def smapleidaissakieya():


#     # h3 = Thread3()
#     # thread = threading.Thread(target=h3)

#     # # 스레드 시작
#     # thread.start()

#     # # 스레드가 종료될 때까지 대기
#     # thread.join()

#     # print(dto)
#     # return jsonify({"res":dto})



# app.register_blueprint(stock_bp)

if __name__ == '__main__':
    app = QApplication(sys.argv)  # QApplication 객체 생성
    h3 = Thread3()
    print("#############0")
    thread = threading.Thread(target=h3.run)  
    print("#############1")
    # 스레드 시작
    thread.start()
    print("#############2")
    # 스레드가 종료될 때까지 대기
    thread.join()
    print("#############3")
    print(dto)


    app.run('0.0.0.0',port=5000, debug=True)

# if __name__ == "__main__":

