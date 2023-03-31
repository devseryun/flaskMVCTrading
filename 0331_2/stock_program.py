# stock_program.py
import time
import redis
from fakeKiwoom import Kiwoom
# from pykiwoom.kiwoom import Kiwoom

# 로그인 및 이벤트 핸들러 설정
class KiwoomEventHandler:
    def __init__(self):
        self.kiwoom = Kiwoom()
        self.kiwoom.CommConnect(block=True)  # 로그인

    def handle_account_info(self):
        print("handle_account_info")
        account_list = self.kiwoom.GetLoginInfo("ACCNO")
        return account_list[1]  # 두 번째 계좌 정보를 반환합니다.

    def handle_select_account(self,account_num):   #계좌평가 잔고내역
        print("handle_select_account")
        msg = f"Selected account {account_num}" 
        self.kiwoom.account_num = account_num
        result = self.kiwoom.sampleRemain()
        print(result) 
        return result

    def handle_my_balance_check(self):             #예수금상세현황 
        print("handle_my_balance_check")
        result = self.kiwoom.block_request("opw00001",
                            계좌번호=self.kiwoom.account_num,
                            비밀번호="0000",
                            비밀번호입력매체구분="00",
                            조회구분=2,
                            output="예수금상세현황",
                            next=0)
        print(result)         
        return result  

    def handle_single_code_Info(self,scode):             #한 종목 정보 
        print("handle_my_balance_check")
        corp = self.kiwoom.GetMasterCodeName(scode)
        con = self.kiwoom.GetMasterConstruction(scode)
        listed_d = self.kiwoom.GetMasterListedStockDate(scode)
        prev_price = self.kiwoom.GetMasterLastPrice(scode)
        state = self.kiwoom.GetMasterStockState(scode)
        print("geSingleCodeInfo")
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
        print(result)         
        return result  
             
    def handle_start_trading(self):
        return "Trading started"

    def handle_stop_trading(self):
        return "Trading stopped"        


kiwoom_event_handler = KiwoomEventHandler()

db = redis.StrictRedis(host='localhost', port=5000, db=0)
request_types = ['account_info', 'select_account', 'start_trading', 'stop_trading']

while True:
    for request_type in request_types:
        data = db.get(request_type)
        if data is not None:
            data = data.decode('utf-8')
            if request_type == 'account_info':
                result = kiwoom_event_handler.handle_account_info()
            elif request_type == 'my_balance_check':
                result = kiwoom_event_handler.handle_my_balance_check()
            elif request_type == 'select_account':
                result = kiwoom_event_handler.handle_select_account(data)
            elif request_type == 'get_single_codeInfo':
                result = kiwoom_event_handler.handle_single_code_Info(data)
            # elif request_type == 'my_balance_check':
            #     result = kiwoom_event_handler.handle_my_balance_check() 
            # elif request_type == 'my_balance_check':
            #     result = kiwoom_event_handler.handle_my_balance_check()
            # elif request_type == 'my_balance_check':
            #     result = kiwoom_event_handler.handle_my_balance_check()

            db.set(request_type + '_result', result)
            db.set(request_type, None)

    time.sleep(1)
