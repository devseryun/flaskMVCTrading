import os
import requests
import json
import sys
sys.path.append("./")
from PyQt5.QtWidgets import *     
from PyQt5 import uic             # ui 파일을 가져오기위한 함수
from PyQt5.QtCore import *        # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from PyQt5.QtTest import *
from kiwoom import *         # 키움증권 함수/공용 방 (싱글턴)
import pytz
import datetime
from errorCode import *

form_class = uic.loadUiType("./UpperLimitPriceTrading.ui")[0]             # 만들어 놓은 ui 불러오기

class Login_Machnine(QMainWindow, QWidget, form_class):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, *args, **kwargs):                      # Main class의 self를 초기화 한다.
        super(Login_Machnine, self).__init__(*args, **kwargs)
        form_class.__init__(self)                            # 상속 받은 from_class를 실행하기 위한 초기값(초기화)
        self.setUI() 
        self.k = Kiwoom()  
        # READY = 2 BUY = 3 BUY_REQUESTING = 4 BUY_CANCELING = 5 SELL = 6 SELL_REQUESTING = 7 SELL_CANCELING = 8
        # 하나의 종목만 관리하는 상태값
        self.OneTrStatus ={
            "trCode":None,
            "nowTrPrice":None,
            "status":"", # 거래시작/ 거래중지
            "tradingStatus":"", # 6개의 스테이터스 BUY BUY_REQUESTING BUY_CANCELING SELL SELL_REQUESTING SELL_CANCELING
            "buyStatus":{
            "buyReqGoPrice":None,
            "buyPrice":None,
            "buyReqWithdrawPrice":None,
            },
            "sellStatus":{
            "sellReqGoPrice":None,
            "sellPrice":None,
            "sellReqWitdrawPrice":None,
            }
        }

        # 키움증권 실시간 코드 목록
        self.realType = RealType() 

        ########### 전체 종목 관리
        self.all_stock_dict = {}  # 코스피, 코스닥 전체 코드넘버 입력

        ####### 계좌 관련된 변수
        self.acc_portfolio = {}   # 내계좌에 들어있는 종목의 코드, 수익률 등등 입력        
        self.not_account_portfolio = {}
        self.account_num = None #계좌번호 담아줄 변수
        self.deposit = 0 #예수금
        self.use_money = 0 #실제 투자에 사용할 금액
        self.use_money_percent = 0.5 #예수금에서 실제 사용할 비율
        self.output_deposit = 0 #출력가능 금액
        self.total_profit_loss_money = 0 #총평가손익금액
        self.total_profit_loss_rate = 0.0 #총수익률(%)


        ####### event loop를 실행하기 위한 변수 모음
        self.login_event_loop = QEventLoop() # 로그인 요청용 이벤트 루프
        self.detail_account_info_event_loop = QEventLoop() # 예수금 요청용 이벤트 루프
        self.calculator_event_loop = QEventLoop()
        self.jang = QEventLoop()
        #########################################

        ######## 종목 정보 가져오기
        self.portfolio_stock_dict = {}
        self.jango_dict = {}

        ########### 종목 분석 용
        self.calcul_data = []
        ##########################################

        ####### 요청 스크린 번호
        self.screen_my_info = "2000" #계좌 관련한 스크린 번호
        self.screen_calculation_stock = "4000" #계산용 스크린 번호
        self.screen_real_stock = "5000" #종목별 할당할 스크린 번호
        self.screen_meme_stock = "6000" #종목별 할당할 주문용 스크린 번호
        self.screen_start_stop_real = "1000" #장 시작/종료 실시간 스크린 번호
        self.screen_realData ="1010"
             
        ####키움증권 로그인 하기                 
        self.event_slots()
        self.real_event_slot() 
        self.signal_login_commConnect()

        ####이벤트 생성 및 진행
        self.call_account.clicked.connect(self.detail_account_mystock) # 계좌정보 가져오기
        self.trSearchSettingBtn.clicked.connect(self.stockSearchAndSetting) # 종목정보 가져와서 셋팅
        self.tradingStartBtn.clicked.connect(self.startTrading) #거래시작
        self.tradingStopBtn.clicked.connect(self.stopTradingReal) #거래중지

        QTest.qWait(1000)       
        # self.screen_number_setting()        
        print("# mode:  init Setting 완")

    #     # Timer2
    #     self.timer2 = QTimer(self)
    #     self.timer2.start(5000) #5초에 한 번 갱신.
    #     self.timer2.timeout.connect(self.timeout2)

    # def timeout2(self):
    #     # print("5초에 한번씩 갱신")
    #     self.detail_account_mystock()

    def setUI(self):
        self.setupUi(self)                

    def signal_login_commConnect(self):

        self.k.kiwoom.dynamicCall("CommConnect()")  
        self.login_event_loop.exec_()  
        print("# mode:  signal_login_commConnect")

    def event_slots(self):
        print("# mode:  event_slots")
        self.k.kiwoom.OnEventConnect.connect(self.login_slot)  #통신연결 상태 변경시 이벤트
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot) # 트랜 수신시이벤트
        self.k.kiwoom.OnReceiveMsg.connect(self.msg_slot) #수신메시지 이벤트

    def real_event_slot(self):
        print("# mode: real_event_slot")        
        self.k.kiwoom.OnReceiveRealData.connect(self.realdata_slot) # 실시간 시세 이벤트 연결
        self.k.kiwoom.OnReceiveChejanData.connect(self.chejan_slot) # 주문 접수/확인 수신시 이벤트

    def post_message(self,channel, text):
        
        SLACK_BOT_TOKEN = "xoxb-4184524433281-5008927392563-qZQ6oS6GFDi2A8DyWSKqCeNg"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + SLACK_BOT_TOKEN
        }
        payload = {
            'channel': channel,
            'text': text
        }
        r = requests.post('https://slack.com/api/chat.postMessage',
                        headers=headers,
                        data=json.dumps(payload)
                        )
    
######################################## API 호출 함수 목록 ########################################
    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        print('# mode:  SetRealReg')        
        print('# mode: screen_no',screen_no, 'code_list',code_list,'fid_list',fid_list,'real_type',real_type)
        self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                              screen_no, code_list, fid_list, real_type)

    def GetCommData(self, trCode,recordeName, index, itemname):
        print('# mode:  GetCommData') 
        result = self.k.kiwoom.dynamicCall("GetCommData( QString, QString, int, QString)",trCode,recordeName, index, itemname)   

    def sendOrderFunc(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no):
        result = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no])
        return result   

    def SetInputValue(self,id,value):
        self.k.kiwoom.dynamicCall("SetInputValue(Qstring, Qstring)",id,value)

    def CommRqData(self, rqname, trcode, next, screen_no):
        self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString", rqname, trcode, next, screen_no)
        self.detail_account_info_event_loop.exec_()

####################################### 기능 함수 ######################################

    def get_account_info(self): #계좌정보 가져오는 함수
        account_list = self.k.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        # print(account_list)

        for n in account_list.split(';'):
            self.accComboBox.addItem(n)

    def detail_account_info(self, sPrevNext="0"):
        self.SetInputValue( "계좌번호", self.account_num)
        self.SetInputValue( "비밀번호", "0000")
        self.SetInputValue( "비밀번호입력매체구분", "00")
        self.SetInputValue( "조회구분", "1")
        self.CommRqData( "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)

    def detail_account_mystock(self, sPrevNext="0"): #계좌평가잔고내역 조회 함수
        print("# mode: 계좌평가잔고내역 조회")
        account = self.accComboBox.currentText()  # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        print("최종 선택 계좌는 %s" % self.account_num)

        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", account)
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")  # 모의투자 0000
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
        self.detail_account_info_event_loop.exec_()

    def screen_number_setting(self):
        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.acc_portfolio.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        for order_number in self.not_account_portfolio.keys():
            code = self.not_account_portfolio[order_number]['종목코드']

            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #포트폴리오에 있는 종목들
        for code in self.portfolio_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        # 스크린 번호 할당
        cnt = 0
        for code in screen_overwrite:
            temp_screen = int(self.screen_real_stock)
            meme_screen = int(self.screen_meme_stock)

            if (cnt % 50) == 0:
                temp_screen += 1
                self.screen_real_stock = str(temp_screen)

            if (cnt % 50) == 0:
                meme_screen += 1
                self.screen_meme_stock = str(meme_screen)

            if code in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict[code].update({"스크린번호": str(self.screen_real_stock)})
                self.portfolio_stock_dict[code].update({"주문용스크린번호": str(self.screen_meme_stock)})

            elif code not in self.portfolio_stock_dict.keys():
                self.portfolio_stock_dict.update({code: {"스크린번호": str(self.screen_real_stock), "주문용스크린번호": str(self.screen_meme_stock)}})

            cnt += 1

        print(self.portfolio_stock_dict)


    # 종목코드로 조회 및 셋팅
    def stockSearchAndSetting(self, sPrevNext="0"):  
        code = self.trSearchText.text()        
        self.OneTrStatus["trCode"] = code.strip()
        if self.OneTrStatus["trCode"] in self.acc_portfolio:
            pass
        else:
            self.acc_portfolio.update({self.OneTrStatus["trCode"]:{"보유수량": 0}})
        self.acc_portfolio[self.OneTrStatus["trCode"]].update({"selectedTrcode": code})
        self.SetInputValue( "종목코드", code)
        self.CommRqData( "종목선택완료", "opt10001", 0, self.screen_my_info)   
        print("# mode:  stockSearchAndSetting code: ",code )


    def update_trading_status(self, key, value):
        self.OneTrStatus[key].update(value)

    def startTrading(self, sPrevNext="0"):
        print("# mode:  거래시작")       
        self.update_trading_status("buyStatus", {
            "buyReqGoPrice": self.buyReqGoPrice.text(),
            "buyPrice": self.buyPrice.text(),
            "buyReqWithdrawPrice": self.buyReqWithdrawPrice.text()
        })

        self.update_trading_status("sellStatus", {
            "sellReqGoPrice": self.sellReqGoPrice.text(),
            "sellPrice": self.sellPrice.text(),
            "sellReqWitdrawPrice": self.sellReqWitdrawPrice.text()
        })

        self.OneTrStatus["status"] = "거래시작"
        self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)",self.OneTrStatus["trCode"], self.realType.REALTYPE["주식체결"]['현재가'])
        print("called\n")  


    # 주식거래중지
    def stopTradingReal(self):
        print("# mode:  거래중지")
        self.OneTrStatus["status"] = "거래중지"
        self.k.kiwoom.dynamicCall("SetRealRemove(QString, QString)","ALL", self.OneTrStatus["trCode"])  
        QTest.qWait(1000) 

    def fliterdOrderSuccessReturn(self, result):
        tempOrderSucess = 1
        if(result == 0):
            tempOrderSucess = 0
        else:
            tempOrderSucess = 1
        return tempOrderSucess  

    #주식매매 주문 전달 후 메시지 값 설정 및 노티 전송
    def tradingExcecuteResultMsgSend(self, orderSucess, tradingStatus, channelName ):
        fliterdOrderSuccess = self.fliterdOrderSuccessReturn(orderSucess)
        settingTradingStatusAndMsg = {
            0:{
            "BUY_REQUESTING":{"msg":"매수주문 전달 성공","status":"SELL"},
            "BUY_CANCELING":{"msg":"매수취소 전달 성공","status":"BUY"},
            "SELL_REQUESTING":{"msg":"매도주문 전달 성공","status":"BUY"},
            "SELL_CANCELING":{"msg":"","매도취소 전달 성공":"SELL"},
            },
            1:{
            "BUY_REQUESTING":{"msg":"매수주문 전달 실패","status":"BUY_REQUESTING"},
            "BUY_CANCELING":{"msg":"매수취소 전달 실패","status":"SELL"},
            "SELL_REQUESTING":{"msg":"매도주문 전달 실패","status":"SELL_REQUESTING"},
            "SELL_CANCELING":{"msg":"매도취소 전달 실패","status":"BUY"},
            }            
        }

        print(settingTradingStatusAndMsg[fliterdOrderSuccess][tradingStatus]["msg"])
        self.post_message(channelName, settingTradingStatusAndMsg[fliterdOrderSuccess][tradingStatus]["msg"])
        self.OneTrStatus["tradingStatus"] =settingTradingStatusAndMsg[fliterdOrderSuccess][tradingStatus]["status"]        
     

    # 주식매매 시작
    def tradingExcecute(self, tradingStatus, sCode ):
        print("# mode:  tradingExcecute- ", tradingStatus)
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4} 
        hoga_lookup = {'지정가': "00", '시장가': "03"}

        # 매수요청
        if self.OneTrStatus["tradingStatus"] =="BUY_REQUESTING": 
                order_success = self.sendOrderFunc("매수", "0101", self.account_num, order_type_lookup["신규매수"], sCode, 1, self.OneTrStatus["buyStatus"]["buyPrice"], hoga_lookup["지정가"], "")
                self.tradingExcecuteResultMsgSend(order_success,"BUY_REQUESTING","#autobot")
       
        # 매수취소
        elif self.OneTrStatus["tradingStatus"] =="BUY_CANCELING": 
                order_success =  self.sendOrderFunc("매수취소", "0101", self.account_num, order_type_lookup["매수취소"], sCode, 1, self.OneTrStatus["buyStatus"]["buyPrice"], hoga_lookup["지정가"], "")
                self.tradingExcecuteResultMsgSend(order_success,"BUY_CANCELING","#autobot")

        # 매도요청
        elif self.OneTrStatus["tradingStatus"] =="SELL_REQUESTING": 
                order_success =  self.sendOrderFunc("매도", "0101", self.account_num, order_type_lookup["신규매도"], sCode, 1, self.OneTrStatus["sellStatus"]["sellPrice"], hoga_lookup["지정가"], "")
                self.tradingExcecuteResultMsgSend(order_success,"SELL_REQUESTING","#autobot")

        # 매도취소            
        elif self.OneTrStatus["tradingStatus"] =="SELL_CANCELING": 
                order_success =  self.sendOrderFunc("매도취소", "0101", self.account_num, order_type_lookup["매도취소"], sCode, 1, self.OneTrStatus["sellStatus"]["sellPrice"], hoga_lookup["지정가"], "")
                self.tradingExcecuteResultMsgSend(order_success,"SELL_CANCELING","#autobot")

        print("called\n")   

    # 주식매매전 트레이딩 Status 설정 6가지
    def tradingStatusSetting(self):
        print("========================tradingExcecute===================")  
        print("# mode:  tradingStatusSetting- ",  self.OneTrStatus["tradingStatus"])
        if self.OneTrStatus["tradingStatus"] =="BUY":
            if int(self.OneTrStatus["buyStatus"]["buyReqGoPrice"]) > int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="BUY_REQUESTING" # 주문요청상태로

        elif self.OneTrStatus["tradingStatus"] =="BUY_REQUESTING":
            if int(self.OneTrStatus["buyStatus"]["buyReqWithdrawPrice"]) < int (self.OneTrStatus["nowTrPrice"]):
                self.OneTrStatus["tradingStatus"] =="BUY_CANCELING" 
                # BUY_REQUESTING / BUY_CANCELING

        elif self.OneTrStatus["tradingStatus"] =="BUY_CANCELING":
                self.OneTrStatus["tradingStatus"] ="BUY" # 주문취소상태면 다시 BUY로
                # BUY/  BUY_CANCELING

        elif self.OneTrStatus["tradingStatus"] =="SELL":
            if int(self.OneTrStatus["sellStatus"]["sellReqGoPrice"]) < int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="SELL_REQUESTING" 
                #SELL_REQUESTING /SELL

        elif self.OneTrStatus["tradingStatus"] =="SELL_REQUESTING":         
            if int(self.OneTrStatus["sellStatus"]["sellReqWitdrawPrice"]) > int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="SELL_CANCELING" 
                #SELL_REQUESTING /SELL_CANCELING

        elif self.OneTrStatus["tradingStatus"] =="SELL_CANCELING":
            if int(self.OneTrStatus["sellStatus"]["sellReqGoPrice"]) > int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="SELL"
                # SELL /  SELL_CANCELING       


    # 스크린 번호 연결 끊기
    def stop_screen_cancel(self, sScrNo=None):
        self.k.kiwoom.dynamicCall("DisconnectRealData(QString)", sScrNo) 


    # 마켓에 따른 코드정보들 소환 함수
    def get_code_list_by_market(self, market_code):
        code_list = self.k.kiwoom.dynamicCall("GetCodeListByMarket(QString)", market_code)
        code_list = code_list.split(';')[:-1]
        return code_list


    # 장 종료와 함께 계산하는 함수
    def calculator_fnc(self):
        code_list = self.get_code_list_by_market("10")
        print("코스닥 갯수 %s " % len(code_list))
        for idx, code in enumerate(code_list):
            self.k.kiwoom.dynamicCall("DisconnectRealData(QString)", self.screen_calculation_stock) # 스크린 연결 끊기

            print("%s / %s : KOSDAQ Stock Code : %s is updating... " % (idx + 1, len(code_list), code))
            self.day_kiwoom_db(code=code)


    def day_kiwoom_db(self, code=None, date=None, sPrevNext="0"):
        QTest.qWait(3600) 

        self.SetInputValue( "종목코드", code)
        self.SetInputValue( "수정주가구분", "1")
        if date != None:
            self.SetInputValue( "기준일자", date)
        self.CommRqData( "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
        self.calculator_event_loop.exec_()


    def merge_dict(self):
        self.all_stock_dict.update({"계좌평가잔고내역": self.acc_portfolio})
        self.all_stock_dict.update({'미체결종목': self.not_account_portfolio})
        self.all_stock_dict.update({'포트폴리오종목': self.portfolio_stock_dict})




####################################################################################
############################콜백 이벤트 Slot 목록 ##################################
    
    # 로그인 콜백
    def login_slot(self, errCode):         
        print("# mode:  login_slot")
        if errCode == 0:
            print("# mode: 로그인 성공")
            self.post_message("#autobot", "로그인 성공")          
            self.get_account_info()
            
        elif errCode == 100:
            print("errCode:사용자 정보교환 실패")
            self.post_message("#autobot", "errCode:사용자 정보교환 실패") 
        elif errCode == 101:
            print("errCode:서버접속 실패")
            self.post_message("#autobot","errCode:서버접속 실패") 
        elif errCode == 102:
            print("errCode: 버전처리 실패")
            self.post_message("#autobot", "errCode: 버전처리 실패") 
        elif errCode == -106:
            os.system('cls')
            print(errors(errCode)[1])
            self.post_message("#autobot", errors(errCode)[1]) 

        self.login_event_loop.exit()  # 로그인이 완료되면 로그인 창을 닫는다.  

    # Tran 수신 콜백
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): 
        print("# mode: :  trdata_slot.")
        if sRQName == "예수금상세현황요청":
            print("# mode:  예수금상세현황요청.")
            deposit = self.GetCommData( sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4

            output_deposit = self.GetCommData( sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)

            print("예수금 : %s" % self.output_deposit)

            self.stop_screen_cancel(self.screen_my_info)
            self.detail_account_info_event_loop.exit()
          

        elif sRQName == "종목선택완료":
            print("# mode:  : 종목선택완료.")    
            # 종목조회와 동시에 초기 스테이터스 셋팅
            if int(self.acc_portfolio[self.OneTrStatus["trCode"]]["보유수량"]) > 0:
                self.acc_portfolio[self.OneTrStatus["trCode"]].update({"tradingStatus": "SELL"})
                self.OneTrStatus["tradingStatus"] = "SELL"
            else:
                self.acc_portfolio[self.OneTrStatus["trCode"]].update({"tradingStatus": "BUY"})
                self.OneTrStatus["tradingStatus"] = "BUY"
            # 종목새로 셋팅할 때 마다, 이전거래 요청 초기화 및 거래중지 상태로 변경
            self.stopTradingReal()     
            # 종목새로 셋팅할 때 마다, 값 정보 초기화    
            self.update_trading_status("buyStatus", {
                "buyReqGoPrice": None,
                "buyPrice": None,
                "buyReqWithdrawPrice": None
            })

            self.update_trading_status("sellStatus", {
                "sellReqGoPrice": None,
                "sellPrice": None,
                "sellReqWitdrawPrice": None
            })        
            self.buyReqGoPrice.clear()
            self.buyPrice.clear()
            self.buyReqWithdrawPrice.clear()
            self.sellReqGoPrice.clear(),
            self.sellPrice.clear(),
            self.sellReqWitdrawPrice.clear()
            

        elif sRQName == "계좌평가잔고내역요청":
            print("# mode: 계좌평가잔고내역요청.")
            column_head = ["종목번호", "종목명", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"]
            colCount = len(column_head)
            rowCount = self.k.kiwoom.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.stocklistTableWidget_2.setColumnCount(colCount)                 # 행 갯수
            self.stocklistTableWidget_2.setRowCount(rowCount)                    # 열 갯수 (종목 수)
            self.stocklistTableWidget_2.setHorizontalHeaderLabels(column_head)   # 행의 이름 삽입

            self.rowCount = rowCount
            print("계좌에 들어있는 종목 수 %s" % rowCount)

            totalBuyingPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액"))
            currentTotalPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
            balanceAsset = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "추정예탁자산"))
            totalEstimateProfit = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
            total_profit_loss_rate = float(self.k.kiwoom.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")) 


            self.label_1.setText(str(totalBuyingPrice))
            self.label_2.setText(str(currentTotalPrice))
            self.label_3.setText(str(balanceAsset))
            self.label_4.setText(str(totalEstimateProfit))
            self.label_5.setText(str(total_profit_loss_rate))      
            
            for index in range(rowCount):
                itemCode = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목번호").strip(" ").strip("A")
                itemName = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목명")
                amount = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "보유수량"))
                buyingPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매입가"))
                currentPrice = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "현재가"))
                estimateProfit = int(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "평가손익"))
                profitRate = float(self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "수익률(%)"))
                total_chegual_price = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매입금액")
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매매가능수량")
                possible_quantity = int(possible_quantity.strip())

                if itemCode in self.acc_portfolio:
                    pass
                else:
                    self.acc_portfolio.update({itemCode:{}})     
                self.acc_portfolio[itemCode].update({"종목번호":itemCode,
                                                     "종목명": itemName.strip(),
                                                     "보유수량": amount,
                                                     "매입가": buyingPrice,
                                                     "수익률(%)": profitRate,
                                                     "현재가": currentPrice,
                                                     "매입금액": total_chegual_price,
                                                     "매매가능수량": possible_quantity})

                # print("#####",self.acc_portfolio[itemCode])
                # print("#####",self.acc_portfolio)

                self.stocklistTableWidget_2.setItem(index, 0, QTableWidgetItem(str(itemCode)))
                self.stocklistTableWidget_2.setItem(index, 1, QTableWidgetItem(str(itemName)))
                self.stocklistTableWidget_2.setItem(index, 2, QTableWidgetItem(str(amount)))
                self.stocklistTableWidget_2.setItem(index, 3, QTableWidgetItem(str(buyingPrice)))
                self.stocklistTableWidget_2.setItem(index, 4, QTableWidgetItem(str(currentPrice)))
                self.stocklistTableWidget_2.setItem(index, 5, QTableWidgetItem(str(estimateProfit)))
                self.stocklistTableWidget_2.setItem(index, 6, QTableWidgetItem(str(profitRate)))

            self.screen_number_setting()

            if sPrevNext == "2":
                self.detail_account_mystock(sPrevNext="2")  # 다음 페이지가 있으면 전부 검색한다.
            else:
                 
                self.detail_account_info_event_loop.exit()      
        else:
            print("# mode: trdata_slot -sRQName:", sRQName)


    def realdata_slot(self, sCode, sRealType, sRealData):
        # print("# mode:  realdata_slot", sRealData)
        if sRealType == "장시작시간":
            fid = self.realType.REALTYPE[sRealType]['장운영구분'] # (0:장시작전, 2:장종료전(20분), 3:장시작, 4,8:장종료(30분), 9:장마감)
            value = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, fid)
            self.jang.exit()

            if value == '0':
                print("장 시작 전\n")

            elif value == '3':
                print("정규장 시작\n")

            elif value == "2":
                print("장 종료, 동시호가로 넘어감\n")

            elif value == '4':  # 장시간외 거래 시작
                print("3시30분 장 종료\n")
                self.OneTrStatus["status"] = "거래중지"
                for code in self.portfolio_stock_dict.keys():
                    self.k.kiwoom.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)
                self.calculator_fnc()
                sys.exit()
            elif value == "8": #시간외
                pass

        elif sRealType == "주식체결":
            b = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) # 출력 : +(-)2520
            b = abs(int(b))
            
            self.OneTrStatus["nowTrPrice"] = b  # 종목검색 정보 윗줄의 현재가도 실시간 업데이트
            self.tempText = "현재가:"+str(b)
            self.realTimeTrInfo.clear()
            self.realTimeTrInfo.setPlainText(self.tempText) # 종목검색 정보 실시간 업데이트.

            self.kst = pytz.timezone('Asia/Seoul')
            self.current_time = datetime.datetime.now(self.kst).time()

            if self.current_time > datetime.time(9, 0) or self.current_time <= datetime.time(15, 30):
                if self.OneTrStatus["status"] =="거래시작":
                    self.tradingStatusSetting()  
                    self.tradingExcecute(self.OneTrStatus["tradingStatus"] , sCode)
        else:
            print("# mode:  realdata_slot - sRealType: ", sRealType)     

    #실시간 주문 접수/확인 이벤트
    def chejan_slot(self, sGubun, nItemCnt, sFidList):  
        # sGubun – 0: 주문체결통보, 1: 국내주식 잔고통보, 4: 파생상품 잔고통보
        # sFidList – 데이터 구분은 ‘;’

        if int(sGubun) == 0:
            print("# mode:  chejan_slot-주문체결통보") 
            price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가']).strip()
            if price == '':
                return
            sCode = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드']).strip()[1:]
            ctime = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간']).strip()[1:]
            name = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명']).strip()
            quantity = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량']).strip()
            status = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['매도수구분']).strip()
            print("status:",status)
            if status == '2':  # 매수              
                self.acc_portfolio[sCode].update({"종목명": name})
                self.acc_portfolio[sCode].update({"보유수량": int(quantity)})
                self.acc_portfolio[sCode].update({"체결가": price})                
                msg = "[매수]" + name + " 체결가 : " + price + " 수량 : " + quantity+" 체결시간:"+ctime
                # print(msg)
                # print(self.acc_portfolio[sCode])
                self.post_message("#autobot", msg) 
                self.pteLog.appendPlainText(msg+"\n") 
                self.OneTrStatus["tradingStatus"] ="SELL"

            elif status == '1':  # 매도   
                print(self.acc_portfolio[sCode])
                msg = "[매도]" + name + " 체결가 : " + price + " 수량 : " + quantity+" 체결시간:"+ctime
                # print(msg)
                self.post_message("#autobot", msg) 
                self.pteLog.setPlainText(msg)
                self.acc_portfolio[sCode]['보유수량'] -= int(quantity)                    
                self.OneTrStatus["tradingStatus"] ="BUY"
                self.pteLog.appendPlainText(msg+"\n") 
            
        else:
            print("chejan_slot, else: ", sGubun)                            

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
       # print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))
        self.post_message("#autobot", "스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg)) 


if __name__=='__main__':             
                                    
    app = QApplication(sys.argv)     
    CH = Login_Machnine()            
    CH.show()                        
    app.exec_()           