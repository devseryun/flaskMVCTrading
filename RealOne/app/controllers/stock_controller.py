from flask import Blueprint, jsonify, request
from pykiwoom.kiwoom import *

kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

stock_blueprint = Blueprint('stock', __name__)

@stock_blueprint.route("/getSinlgeTrInfo", methods=["GET"])
def getSinlgeTrInfo():
    print(" 확인")
    df = kiwoom.block_request("opt10001",
                            종목코드="005930",
                            output="주식기본정보",
                            next=0)
    print(df)
    return jsonify({"result": df})





# from app.connections.fakeKiwoom import *
# kiwoom = KiwoomYo()
# #커넥션 상태 확인
# @stock_bp.route("/login", methods=["GET"])
# def login():
#     print
#     if kiwoom.GetConnectState() == 1:
#         print("로그인 성공\n")
#         return jsonify({"result": "로그인 성공"})
#     else:
#         print("로그인 실패")
#         return jsonify({"result": "fail"})

# #종목조회 정보
# @stock_bp.route("/geSingleCodeInfo", methods=["GET"])
# def getSingleCodeInfo():
#     scode = request.args.get("scode")
#     corp = kiwoom.GetMasterCodeName(scode)
#     con = kiwoom.GetMasterConstruction(scode)
#     listed_d = kiwoom.GetMasterListedStockDate(scode)
#     prev_price = kiwoom.GetMasterLastPrice(scode)
#     state = kiwoom.GetMasterStockState(scode)
#     print("geSingleCodeInfo")
#     print('기업 : {}'.format(corp))
#     print('감리구분 : {}'.format(con))
#     print('최초상장일 : {}'.format(listed_d))
#     print('전일가 : {}'.format(prev_price))
#     print('종목상태 : {}'.format(state))
#     res ={"기업":corp,
#             "감리구분":con,
#             "최초상장일":listed_d,
#             "전일가":prev_price,
#             "종목상태":state,}
#     return jsonify({"result": res})

# # #종목조회 정보
# # @stock_bp.route("/singgleTr", methods=["GET"])
# # def smapleidaissakieya():
# #     df = kiwoom.block_request("opt10001",
# #                             종목코드="005930",
# #                             output="주식기본정보",
# #                             next=0)
# #     print(df)      
        
        


# #내계좌정보
# @stock_bp.route("/selectAccount", methods=["GET"])
# def selectAccountAndGetAccountInfo():
#         account_num =kiwoom.GetLoginInfo("ACCOUNT_CNT")        # 전체 계좌수
#         accounts = kiwoom.GetLoginInfo("ACCNO")                 # 전체 계좌 리스트
#         user_id = kiwoom.GetLoginInfo("USER_ID")                # 사용자 ID
#         user_name = kiwoom.GetLoginInfo("USER_NAME")            # 사용자명
#         keyboard = kiwoom.GetLoginInfo("KEY_BSECGB")            # 키보드보안 해지여부
#         firewall = kiwoom.GetLoginInfo("FIREW_SECGB")           # 방화벽 설정 여부
#         print("selectAccount")
#         return jsonify({"account_num": account_num,
#                          "accounts": accounts,
#                          "user_id": user_id,
#                          "user_name": user_name,
#                          "keyboard": keyboard,
#                          "firewall":firewall,
#                          })


# @stock_bp.route("/savings", methods=["GET"])
# def savings():
#     # kiwoom.account_num = request.args.get("account_number")
#     # print("계좌 %s" % kiwoom.account_num)
#     print("----")
#     df = kiwoom.block_request("opw00001",
#                         계좌번호="8043856211",
#                         비밀번호="0000",
#                         비밀번호입력매체구분="00",
#                         조회구분=2,
#                         output="예수금상세현황",
#                         next=0)
#     print(df)
#     return df

# @stock_bp.route("/remains")
# def remains():
#     # kiwoom.account_num = request.args.get("account_number")
#     # print("계좌 %s" % kiwoom.account_num)
#     print("----remains")

#     kiwoom.sampleRemain()
#     print("----res")
#     # return jsonify({"res": res})

# # @stock_bp.route('/echo_call/<param>') #get echo api
# # def get_echo_call(param):
# #     return jsonify({"param": param})




# # @stock_bp.route("/stock/code", methods=["GET"])
# # def stock_code_info():
# #     stock_code = request.args.get("stock_code")
# #     stock_info = kiwoom.get_code_info(stock_code)
# #     return jsonify(stock_info)

# # @stock_bp.route("/stock/real", methods=["GET"])
# # def stock_real_info():
# #     stock_code = request.args.get("stock_code")
# #     stock_info = kiwoom.get_real_info(stock_code)
# #     return jsonify(stock_info)

# # @stock_bp.route("/stock/order", methods=["POST"])
# # def stock_order():
# #     account_number = request.json.get("account_number")
# #     stock_code = request.json.get("stock_code")
# #     order_type = request.json.get("order_type")
# #     quantity = request.json.get("quantity")
# #     price = request.json.get("price")
# #     order_result = kiwoom.send_order(account_number, stock_code, order_type, quantity, price)
# #     return jsonify({"result": order_result})

