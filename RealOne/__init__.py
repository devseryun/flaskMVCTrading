from flask import Flask
from flask_cors import CORS, cross_origin
from flask import Flask, request,  jsonify

def create_app():
    app = Flask(__name__)
    # CORS(app)

    # 블루프린트 등록
    from app.controllers.stock_controller import stock_bp
    app.register_blueprint(stock_bp, url_prefix='/stock')

    return app

app = create_app()

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=False)



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