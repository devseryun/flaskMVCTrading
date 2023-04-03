from flask import Flask
from flask_cors import CORS, cross_origin
from flask import Flask, request,  jsonify
# from pykiwoom.kiwoom import *
# kiwoom = Kiwoom()
from app.connections.fakeKiwoom import *



app = Flask(__name__)
CORS(app)

kiwoom = KiwoomYo()
kiwoom.CommConnect(block=True)
df = kiwoom.block_request("opt10001",
                        종목코드="005930",
                        output="주식기본정보",
                        next=0)
print(df)
# return jsonify({"result": df})

@app.route("/getSinlgeTrInfo", methods=["GET"])
def getSinlgeTrInfo():
    print(" 확인")


if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=True)



#     from flask import Flask
# from flask_cors import CORS, cross_origin
# from flask import Flask, request,  jsonify
# from flask_socketio import SocketIO, emit
# from pykiwoom.kiwoom import *

# socketio = SocketIO(logger=True,engineio_logger=True)
    

# app = Flask(__name__)
# CORS(app)
# socketio.init_app(app)
# kiwoom = Kiwoom()
# kiwoom.CommConnect(block=True)


# @app.route("/savings", methods=["GET"])
# def savings():
#     df = kiwoom.block_request("opw00001",
#                         계좌번호="8043856211",
#                         비밀번호="",
#                         비밀번호입력매체구분="00",
#                         조회구분=2,
#                         output="예수금상세현황",
#                         next=0)
#     return jsonify(df.to_dict())


# if __name__ == '__main__':
#     app.run('0.0.0.0',port=5000, debug=False)