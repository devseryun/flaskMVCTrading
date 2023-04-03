# stock_program.py
import time
import json
import redis
from customKiwoom import Kiwoom
kiwoom = Kiwoom()
kiwoom.CommConnect()  # 로그인


# 슬랙 메시지 보내는 것도 추가할 것
# 로그인 및 이벤트 핸들러 설정
class KiwoomEventHandler:
    def __init__(self):
        pass

    def handle_account_info(self):
        print("handle_account_info")
        account_list = kiwoom.GetLoginInfo("ACCNO")
        return account_list[1]  # 두 번째 계좌 정보를 반환합니다.

    def handle_select_account(self,account_num):   #계좌평가 잔고내역
        print("handle_select_account")
        msg = f"Selected account {account_num}" 
        df = kiwoom.opt10001Req("계좌평가잔고내역요청",
                            계좌번호="8043856211",
                            비밀번호="0000",
                            비밀번호입력매체구분="00",
                            조회구분=2,
                            trcode="opw00018",
                            next=0)                 
        print("result:", df) 
        # dictionary 객체를 JSON 문자열로 변환한 뒤 바이트로 인코딩
        data_string = json.dumps(df).encode('utf-8')              
        return data_string

    def handle_single_codeInfo_and_setting(self, scode):      # 거래시작
        print("handle_single_codeInfo_and_setting")
        # 종목조회와 동시에 초기 스테이터스 셋팅
        kiwoom.OneTrStatus["trCode"] = scode.strip()
        if kiwoom.OneTrStatus["trCode"] in kiwoom.acc_portfolio:
            pass
        else:
            kiwoom.acc_portfolio.update({kiwoom.OneTrStatus["trCode"]:{"보유수량": 0}})
        kiwoom.acc_portfolio[kiwoom.OneTrStatus["trCode"]].update({"selectedTrcode": scode})

        if int(kiwoom.acc_portfolio[kiwoom.OneTrStatus["trCode"]]["보유수량"]) > 0:
            kiwoom.acc_portfolio[kiwoom.OneTrStatus["trCode"]].update({"tradingStatus": "SELL"})
            kiwoom.OneTrStatus["tradingStatus"] = "SELL"
        else:
            kiwoom.acc_portfolio[kiwoom.OneTrStatus["trCode"]].update({"tradingStatus": "BUY"})
            kiwoom.OneTrStatus["tradingStatus"] = "BUY"

        # 종목새로 셋팅할 때 마다, 이전거래 요청 초기화 및 거래중지 상태로 변경
        kiwoom.stopTradingReal()     

        # 종목새로 셋팅할 때 마다, 값 정보 초기화    
        kiwoom.update_trading_status("buyStatus", {
            "buyReqGoPrice": None,
            "buyPrice": None,
            "buyReqWithdrawPrice": None
        })

        kiwoom.update_trading_status("sellStatus", {
            "sellReqGoPrice": None,
            "sellPrice": None,
            "sellReqWitdrawPrice": None
        })  

        result ={"selectedTrcode":scode}        
        return result

    def handle_realtime_stock_price(self, code):
        print("handle_single_codeInfo_and_setting")        
        kiwoom.OneTrStatus["trCode"] = code
        realTimePrice = kiwoom.stockRealTimePrice()
        return int(realTimePrice)       


    def handle_single_codeInfo(self, scode):             #종목단순 조회 
        print("handle_single_code_Info")
        corp = kiwoom.GetMasterCodeName(scode)
        con = kiwoom.GetMasterConstruction(scode)
        listed_d = kiwoom.GetMasterListedStockDate(scode)
        prev_price = kiwoom.GetMasterLastPrice(scode)
        state = kiwoom.GetMasterStockState(scode)
        print("getSingleCodeInfo")
        print('기업 : {}'.format(corp))
        print('감리구분 : {}'.format(con))
        print('최초상장일 : {}'.format(listed_d))
        print('전일가 : {}'.format(prev_price))
        print('종목상태 : {}'.format(state))
        result ={"기업":corp,
                "감리구분":con,
                "최초상장일":listed_d,
                "전일가":prev_price,
                "종목상태":state}
        # print(result)         
        return result  
                 
    def handle_start_trading(self,data):                        # 거래시작
        print("# mode:  거래시작")      
        kiwoom.update_trading_status("buyStatus", {
            "buyReqGoPrice": data.get("buyReqGoPrice"),
            "buyPrice": data.get("buyPrice"),
            "buyReqWithdrawPrice": data.get("buyReqWithdrawPrice")
        })
        kiwoom.update_trading_status("sellStatus", {
            "sellReqGoPrice": data.get("sellReqGoPrice"),
            "sellPrice": data.get("sellPrice"),
            "sellReqWitdrawPrice": data.get("sellReqWitdrawPrice")
        })

        kiwoom.OneTrStatus["status"] = "거래시작"
        kiwoom.GetCommRealData(kiwoom.OneTrStatus["trCode"], kiwoom.realType.REALTYPE["주식체결"]['현재가'])
        print("called\n")  
        return "Trading started"

    def handle_stop_trading(self):
        return "Trading stopped"        
        
    def handle_my_balance_check(self):             #예수금상세현황 
        print("handle_my_balance_check")
        result = kiwoom.block_request("opw00001",
                            계좌번호=kiwoom.account_num,
                            비밀번호="0000",
                            비밀번호입력매체구분="00",
                            조회구분=2,
                            output="예수금상세현황",
                            next=0)
        print(result)         
        return result  


kiwoom_event_handler = KiwoomEventHandler()

db = redis.StrictRedis(host='localhost', port=6379, db=0)
request_types = ['account_info', 'select_account','my_balance_check','get_stock_real_time_price','get_single_codeInfo', 'get_single_codeInfo_and_setting','start_trading', 'stop_trading']

while True:
    for request_type in request_types:
        data = db.get(request_type)
        print('request_type: \n',request_type)
        print('요청확인 data',data)
        if data is not None:
            data = data.decode('utf-8')
            if request_type == 'account_info':
                result = kiwoom_event_handler.handle_account_info()
            elif request_type == 'my_balance_check':
                result = kiwoom_event_handler.handle_my_balance_check()
            elif request_type == 'select_account':
                result = kiwoom_event_handler.handle_select_account(data)
            elif request_type == 'get_stock_real_time_price':
                result = kiwoom_event_handler.handle_realtime_stock_price(data)                
            elif request_type == 'get_single_codeInfo':
                result = kiwoom_event_handler.handle_single_codeInfo(data)
            elif request_type == 'get_single_codeInfo_and_setting':
                result = kiwoom_event_handler.handle_single_codeInfo_and_setting(data)                
            elif request_type == 'start_trading':
                result = kiwoom_event_handler.handle_start_trading(data) 
            elif request_type == 'stop_trading':
                result = kiwoom_event_handler.handle_stop_trading()

            db.set(request_type + '_result', result)
            db.delete(request_type)

    time.sleep(1)
