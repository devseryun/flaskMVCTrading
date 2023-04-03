import os
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
        # self.tradingStatus = {'BUY': 1, 'BUY_REQUESTING': 2, '매수취소': 3, '매도취소': 4}   
# READY = 2 BUY = 3 BUY_REQUESTING = 4 BUY_CANCELING = 5 SELL = 6 SELL_REQUESTING = 7 SELL_CANCELING = 8
        # 하나의 종목만 관리하는 상태값
        self.OneTrStatus ={
            "trCode":None,
            "nowTrPrice":None,
            "nowTrName":None,
            "stockNumber":None,
            "startStatus":"", 
            "status":"", # 거래시작/ 거래중지
            "tradingStatus":"", # 6개의 스테이터스 BUY = 3 BUY_REQUESTING = 4 BUY_CANCELING = 5 SELL = 6 SELL_REQUESTING = 7 SELL_CANCELING = 8
            # 8개 아닌가? sell 완료, buy 완료
            "buyStatus":{
            "buyReqGoPrice":None,
            "buyPrice":None,
            "buyReqWithdrawPrice":None,
            },
            "sellStatus":{
            "sellReqGoPrice":None,
            "sellPrice":None,
            "sellReqWitdrawPrice":None,
            },
            "portfolio_stock_dict":{},
            "체결시간":"",
            "현재가":"",
            "전일대비":"",
            "등락율":"",
            "(최우선)매도호가":"",
            "(최우선)매수호가":"",
            "거래량":"",
            "누적거래량":"",
            "고가":"",
            "시가":"",
            "저가":"",
        }

        # 키움증권 실시간 코드 목록
        self.realType = RealType() 

        ########### 전체 종목 관리
        self.all_stock_dict = {}

        ####### 계좌 관련된 변수
        self.account_stock_dict = {}
        self.not_account_stock_dict = {}
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

        ####키움증권 로그인 하기                 
        self.event_slots() 
        self.signal_login_commConnect()
        self.real_event_slot()  
        ####이벤트 생성 및 진행
        self.call_account.clicked.connect(self.accountInterface) # 계좌정보 가져오기
        self.trSearchSettingBtn.clicked.connect(self.tr_searchSetting) # 종목정보 가져와서 셋팅
        self.tradingStartBtn.clicked.connect(self.startTrading) #거래시작
        self.tradingStopBtn.clicked.connect(self.stopTradingReal) #거래중지



        QTest.qWait(1000)       
        self.screen_number_setting()        
        
        print("mode: init Setting 완")

        # Timer2
        # self.timer2 = QTimer(self)
        # self.timer2.start(1000 * 3) #3초에 한 번 갱신.
        # self.timer2.timeout.connect(self.check_balance)

    #     QTimer.singleShot(5000, self.not_concluded_account) #5초 뒤에 미체결 종목들 가져오기 실행
    #     #########################################

    # def not_concluded_account(self, sPrevNext="0"):
    #     print("미체결 종목 요청")
    #     self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
    #     self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "체결구분", "1")
    #     self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "매매구분", "0")
    #     self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "실시간미체결요청", "opt10075", sPrevNext, self.screen_my_info)

    #     self.detail_account_info_event_loop.exec_()

    def setUI(self):
        self.setupUi(self)                  # UI 초기값 셋업

    def signal_login_commConnect(self):
        self.k.kiwoom.dynamicCall("CommConnect()")  
        self.login_event_loop.exec_()  
        print("mode: signal_login_commConnect")

    def event_slots(self):
        print("mode: event_slots")
        self.k.kiwoom.OnEventConnect.connect(self.login_slot)  #통신연결 상태 변경시 이벤트
        self.k.kiwoom.OnReceiveTrData.connect(self.trdata_slot) # 트랜 수신시이벤트
        self.k.kiwoom.OnReceiveMsg.connect(self.msg_slot) #수신메시지 이벤트

    def real_event_slot(self):
        print("mode:real_event_slot")        
        self.k.kiwoom.OnReceiveRealData.connect(self.realdata_slot) # 실시간 시세 이벤트 연결
        self.k.kiwoom.OnReceiveChejanData.connect(self.chejan_slot) # 주문 접수/확인 수신시 이벤트

######################################## 인터페이스 like 함수 목록 ########################################
    def accountInterface(self):
        print("mode: 선택된 계좌 정보 가져오기")
        self.getItemList()               # 종목 이름 받아오기
        self.detail_acount_mystock()     # 계좌평가잔고내역 가져오기
    
    # def a_logOut(self):
    #     print("mode: 로그아웃")  # 키움증권 이제 로그아웃 에이이파아이 제공 안함.                
    
    def tr_searchSetting(self): # 종목조회
        print("mode: tr_searchSetting")
        self.stockSearchAndSetting() 

    def SetRealReg(self, screen_no, code_list, fid_list, real_type):
        print('mode: SetRealReg')        
        print('mode: self', self, 'screen_no',screen_no, 'code_list',code_list,'fid_list',fid_list,'real_type',real_type)
        self.k.kiwoom.dynamicCall("SetRealReg(QString, QString, QString, QString)", 
                              screen_no, code_list, fid_list, real_type)

    def GetCommData(self, trCode,recordeName, index, itemname):
        print('mode: GetCommData') 
        result = self.k.kiwoom.dynamicCall("GetCommData( QString, QString, int, QString)",trCode,recordeName, index, itemname)   

    def GetCommRealData(self, code, fid):
        print('mode: GetCommRealData')         
        data = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", code, fid) 
        return data

    def sendOrderFunc(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no):
        result = self.k.kiwoom.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no])
        return result

    def get_chejan_data(self, fid):
        print('mode: get_chejan_data')         
        ret = self.k.kiwoom.dynamicCall("GetChejanData(int)", fid)
        return ret

    def receive_chejan_data(self, gubun, item_cnt, fid_list):
        print('mode: receive_chejan_data')          
        print(gubun)
        print(self.get_chejan_data(9203))
        print(self.get_chejan_data(302))
        print(self.get_chejan_data(900))
        print(self.get_chejan_data(901))


####################################### 실제 실행 함수 ######################################

    def get_account_info(self): #계좌정보 가져오는 함수
        account_list = self.k.kiwoom.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        print(account_list)

        for n in account_list.split(';'):
            self.accComboBox.addItem(n)

    def getItemList(self): # 전체 주식장 종목 정보 가져오는 함수
        marketList = ["0", "10"]

        for market in marketList:
            codeList = self.k.kiwoom.dynamicCall("GetCodeListByMarket(QString)", market).split(";")[:-1]

            for code in codeList:
                name = self.k.kiwoom.dynamicCall("GetMasterCodeName(QString)", code)
                self.k.All_Stock_Code.update({code: {"종목명": name}})

    def detail_account_info(self, sPrevNext="0"):
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "계좌번호", self.account_num)
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "0000")
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)

        self.detail_account_info_event_loop.exec_()

    def detail_acount_mystock(self, sPrevNext="0"): #계좌평가잔고내역 조회 함수
        print("mode:계좌평가잔고내역 조회")
        account = self.accComboBox.currentText()  # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        print("최종 선택 계좌는 %s" % self.account_num)

        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", account)
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")  # 모의투자 0000
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
        self.detail_account_info_event_loop.exec_()

    def reset_opw00018_output(self):
        self.opw00018_output = {'single': [], 'multi': []}

    def check_balance(self):
        self.reset_opw00018_output()
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", 0, self.screen_my_info)    

        # while self.kiwoom.remained_data: #한 번에 최대 20개 가져오므로 남은 데이터 처리.
        #     time.sleep(0.2)
        #     self.kiwoom.set_input_value("계좌번호", account_number)
        #     self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.k.kiwoom.dynamicCall("SetInputValue(String, String)", "계좌번호", self.account_num)
        self.k.kiwoom.dynamicCall("CommRqData(String, String, int, String)", "예수금상세현황요청", "opw00001", 0, self.screen_my_info)    

        # # balance
        # item = QTableWidgetItem(self.kiwoom.d2_deposit) # QTableWidget에 출력하기 위해 먼저 self.kiwoom.d2_deposit에 저장된 예수금 데이터를 QTableWidgetItem 객체로 변환.
        # item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        # self.tableWidget.setItem(0, 0, item)

        # for i in range(1, 6):
        #     item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][0][i-1])
        #     item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        #     self.tableWidget.setItem(0, i, item)
        # self.tableWidget.resizeRowsToContents() #아이템의 크기에 맞춰 행의 높이 조절.

        # # Item list
        # item_count = len(self.kiwoom.opw00018_output['multi']) #앞에 tablewidget도 이런식으로 소스파일에서 코딩해보기.
        # self.tableWidget_2.setRowCount(item_count)

        # for i in range(item_count):
        #     row = self.kiwoom.opw00018_output['multi'][i]
        #     for j in range(len(row)):
        #         item = QTableWidgetItem(row[j])
        #         item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        #         self.tableWidget_2.setItem(i, j, item)
        # self.tableWidget_2.resizeRowsToContents()


    # 종목코드로 조회 및 셋팅
    def stockSearchAndSetting(self, sPrevNext="0"):  
        code = self.trSearchText.text() 
        print(" # 종목코드로 조회 및 셋팅. code: ",code )
        self.OneTrStatus["trCode"] = code
        self.k.acc_portfolio[self.OneTrStatus["trCode"]].update({"selectedTrcode": code})
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "종목조회셋팅", "opt10001", 0, self.screen_my_info)   

    # 거래시작과 합께 트레이딩 정보 셋팅
    def startTrading(self, sPrevNext="0"):
        print("mode: 거래시작")       
        self.OneTrStatus["buyStatus"]["buyReqGoPrice"]  = self.buyReqGoPrice.text()
        self.OneTrStatus["buyStatus"]["buyPrice"] = self.buyPrice.text()
        self.OneTrStatus["buyStatus"]["buyReqWithdrawPrice"] = self.buyReqWithdrawPrice.text()
        self.OneTrStatus["sellStatus"]["sellReqGoPrice"] = self.sellReqGoPrice.text()
        self.OneTrStatus["sellStatus"]["sellPrice"] = self.sellPrice.text()
        self.OneTrStatus["sellStatus"]["sellReqWitdrawPrice"] = self.sellReqWitdrawPrice.text()
        sCode =self.OneTrStatus["trCode"]
        print('trCode:',self.OneTrStatus["trCode"])       
        self.OneTrStatus["status"] = "거래시작"
        self.GetCommRealData(sCode, self.realType.REALTYPE["주식체결"]['현재가'])
        print("called\n")        

   
    # 거래중지
    def stopTradingReal(self, screenNo):
        print("mode: 거래중지")
        self.OneTrStatus["status"] = "거래중지"
        self.k.kiwoom.dynamicCall("SetRealRemove(QString, QString)","ALL", self.OneTrStatus["trCode"])
        self.detail_acount_mystock()        
        QTest.qWait(1000) 


    def tradingStatusSetting(self):

        if self.OneTrStatus["tradingStatus"] =="BUY":
            if int(self.OneTrStatus["buyStatus"]["buyReqGoPrice"]) > int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="BUY_REQUESTING" # 주문요청상태로

        elif self.OneTrStatus["tradingStatus"] =="BUY_REQUESTING":
            if int(self.OneTrStatus["buyStatus"]["buyReqWitdrawPrice"]) < int (self.OneTrStatus["nowTrPrice"]):
                self.OneTrStatus["tradingStatus"] =="BUY_CANCELING" 
                # BUY_REQUESTING / BUY_CANCELING

        elif self.OneTrStatus["tradingStatus"] =="BUY_CANCELING":
                self.OneTrStatus["tradingStatus"] ="BUY" # 주문취소상태면 다시 BUY로
                # BUY/  BUY_CANCELING
        # elif self.OneTrStatus["tradingStatus"] =="BUY_ACCEPTED":
        #         self.OneTrStatus["tradingStatus"] ="SELL" # BUY INIT 초기화

        elif self.OneTrStatus["tradingStatus"] =="SELL":
            if int(self.OneTrStatus["sellStatus"]["sellReqGoPrice"]) < int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="SELL_REQUESTING" 
                #SELL_REQUESTING /SELL

        elif self.OneTrStatus["tradingStatus"] =="SELL_REQUESTING":
            print("")
            if int(self.OneTrStatus["sellStatus"]["sellReqWitdrawPrice"]) > int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="SELL_CANCELING" 
                #SELL_REQUESTING /SELL_CANCELING

        elif self.OneTrStatus["tradingStatus"] =="SELL_CANCELING":
            if int(self.OneTrStatus["sellStatus"]["sellReqGoPrice"]) > int (self.OneTrStatus["nowTrPrice"]) :
                self.OneTrStatus["tradingStatus"] ="SELL"
                # SELL /  SELL_CANCELING
        # elif self.OneTrStatus["tradingStatus"] =="SELL_ACCEPTED":
        #         self.OneTrStatus["tradingStatus"] ="BUY" # BUY INIT 초기화

    # tradingStatus 값 셋팅
    def tradingExcecute(self, tradingStatus, sCode, sRealType, sRealData):
        print("mode: tradingStatus- ", tradingStatus)
        order_type_lookup = {'신규매수': 1, '신규매도': 2, '매수취소': 3, '매도취소': 4} 
        hoga_lookup = {'지정가': "00", '시장가': "03"}
        # 실제 매매 주문(매수/매도) 이행하는 구간이랑 별도로 둘 것.
        # BUYREQ, BUYCANCEL, SELLREQ, SELLCACEL만 다룰것.

        if self.OneTrStatus["tradingStatus"] =="BUY_REQUESTING": # 매수요청
                order_success = self.sendOrderFunc("매수", "0101", self.account_num, order_type_lookup["신규매수"], sCode, 1, self.OneTrStatus["buyStatus"]["buyPrice"], hoga_lookup["지정가"], "")

                if order_success == 0:
                    print("매수주문 전달 성공")
                    self.OneTrStatus["tradingStatus"] ="SELL" #BUY_ACCEPTED
                else:
                    print("매수주문 전달 실패")
                    self.OneTrStatus["tradingStatus"] ="BUY_REQUESTING"

        elif self.OneTrStatus["tradingStatus"] =="BUY_CANCELING": # 매수취소
                order_success =  self.sendOrderFunc("매수취소", "0101", self.account_num, order_type_lookup["매수취소"], sCode, 1, self.OneTrStatus["buyStatus"]["buyPrice"], hoga_lookup["지정가"], "")
                if order_success == 0:
                    print("매수취소 전달 성공")
                    self.OneTrStatus["tradingStatus"] ="BUY"
                else:
                    print("매수취소 전달 실패")
                    self.OneTrStatus["tradingStatus"] ="SELL"
        elif self.OneTrStatus["tradingStatus"] =="SELL_REQUESTING": # 매도요청
                order_success =  self.sendOrderFunc("매도", "0101", self.account_num, order_type_lookup["신규매도"], sCode, 1, self.OneTrStatus["sellStatus"]["sellPrice"], hoga_lookup["지정가"], "")

                if order_success == 0:
                    print("매도주문 전달 성공")
                    self.OneTrStatus["tradingStatus"] ="BUY"  #BUY_ACCEPTED               
                else:
                    print("매도주문 전달 실패")
                    self.OneTrStatus["tradingStatus"] ="SELL_REQUESTING"
        elif self.OneTrStatus["tradingStatus"] =="SELL_CANCELING": # 매도취소
                order_success =  self.sendOrderFunc("매도취소", "0101", self.account_num, order_type_lookup["매도취소"], sCode, 1, self.OneTrStatus["sellStatus"]["sellPrice"], hoga_lookup["지정가"], "")
                if order_success == 0:
                    print("매도취소 전달 성공")
                    self.OneTrStatus["tradingStatus"] ="SELL"
                else:
                    print("매도취소 전달 실패")
                    self.OneTrStatus["tradingStatus"] ="BUY"

        print("끝")


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
        QTest.qWait(3600) #3.6초마다 딜레이를 준다.

        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "수정주가구분", "1")
        if date != None:
            self.k.kiwoom.dynamicCall("SetInputValue(QString, QString)", "기준일자", date)
        self.k.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "주식일봉차트조회", "opt10081", sPrevNext, self.screen_calculation_stock)
        self.calculator_event_loop.exec_()

    def merge_dict(self):
        self.all_stock_dict.update({"계좌평가잔고내역": self.account_stock_dict})
        self.all_stock_dict.update({'미체결종목': self.not_account_stock_dict})
        self.all_stock_dict.update({'포트폴리오종목': self.portfolio_stock_dict})

    def screen_number_setting(self):
        screen_overwrite = []

        #계좌평가잔고내역에 있는 종목들
        for code in self.account_stock_dict.keys():
            if code not in screen_overwrite:
                screen_overwrite.append(code)

        #미체결에 있는 종목들
        for order_number in self.not_account_stock_dict.keys():
            code = self.not_account_stock_dict[order_number]['종목코드']

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



####################################################################################
############################컨트롤이벤트 slot 목록(콜백) 시작 ################################
    # 로그인 반환값 다루는 이벤트 핸들러
    def login_slot(self, errCode):         
        print("mode: login_slot")
        if errCode == 0:
            print("mode:로그인 성공")
            self.statusbar.showMessage("mode:로그인 성공")           
            self.get_account_info()
            
        elif errCode == 100:
            print("errCode:사용자 정보교환 실패")
        elif errCode == 101:
            print("errCode:서버접속 실패")
        elif errCode == 102:
            print("errCode: 버전처리 실패")
        elif errCode == -106:
            os.system('cls')
            print(errors(errCode)[1])

        self.login_event_loop.exit()  # 로그인이 완료되면 로그인 창을 닫는다.  

    #Tran 수신 이벤트
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): 
        print("mode: trdata_slot.")
        if sRQName == "예수금상세현황요청":
            print("mode: 예수금상세현황요청.")
            deposit = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)

            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4

            output_deposit = self.k.kiwoom.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)

            print("예수금 : %s" % self.output_deposit)

            self.stop_screen_cancel(self.screen_my_info)

            self.detail_account_info_event_loop.exit()

        elif sRQName == "종목조회셋팅":
            print("mode: 종목조회셋팅.")    
            self.OneTrStatus["nowTrPrice"]  = self.GetCommRealData(sTrCode, 10) #현재가
            # 종목조회와 동시에 c초기 스테이터스 셋팅
            if int(self.k.acc_portfolio[self.OneTrStatus["trCode"]]["보유수량"]) > 0:
                self.k.acc_portfolio[self.OneTrStatus["trCode"]].update({"tradingStatus": "SELL"})
                self.OneTrStatus["tradingStatus"] = "BUY"
            else:
                self.k.acc_portfolio[self.OneTrStatus["trCode"]].update({"tradingStatus": "SELL"})
                self.OneTrStatus["tradingStatus"] = "BUY"
        

        elif sRQName == "계좌평가잔고내역요청":
            print("mode:계좌평가잔고내역요청.")
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

                if itemCode in self.k.acc_portfolio:
                    pass
                else:
                    self.k.acc_portfolio.update({itemCode:{}})     
                self.k.acc_portfolio[itemCode].update({"종목번호":itemCode})
                self.k.acc_portfolio[itemCode].update({"종목명": itemName.strip()})
                self.k.acc_portfolio[itemCode].update({"보유수량": amount})
                self.k.acc_portfolio[itemCode].update({"매입가": buyingPrice})
                self.k.acc_portfolio[itemCode].update({"수익률(%)": profitRate})
                self.k.acc_portfolio[itemCode].update({"현재가": currentPrice})
                self.k.acc_portfolio[itemCode].update({"매입금액": total_chegual_price})
                self.k.acc_portfolio[itemCode].update({"매매가능수량": possible_quantity})
                print("#####",self.k.acc_portfolio[itemCode])
                print("#####",self.k.acc_portfolio)

                self.stocklistTableWidget_2.setItem(index, 0, QTableWidgetItem(str(itemCode)))
                self.stocklistTableWidget_2.setItem(index, 1, QTableWidgetItem(str(itemName)))
                self.stocklistTableWidget_2.setItem(index, 2, QTableWidgetItem(str(amount)))
                self.stocklistTableWidget_2.setItem(index, 3, QTableWidgetItem(str(buyingPrice)))
                self.stocklistTableWidget_2.setItem(index, 4, QTableWidgetItem(str(currentPrice)))
                self.stocklistTableWidget_2.setItem(index, 5, QTableWidgetItem(str(estimateProfit)))
                self.stocklistTableWidget_2.setItem(index, 6, QTableWidgetItem(str(profitRate)))

            if sPrevNext == "2":
                self.detail_acount_mystock(sPrevNext="2")  # 다음 페이지가 있으면 전부 검색한다.
            else:
                self.detail_account_info_event_loop.exit()  # 끊어 준다.         
        else:
            print(" trdata_slot, sRQName:", sRQName)

    def realdata_slot(self, sCode, sRealType, sRealData):
        # print("mode: realdata_slot")
        if sRealType == "장시작시간":
            print("장시작 시간대\n")
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

                QTest.qWait(5000)
                # self.file_delete()
                self.calculator_fnc()
                sys.exit()
            elif value == "8": #시간외
                pass

        elif sRealType == "주식체결":
            # print("mode: 주식체결")
            # 현재가 
            b = self.k.kiwoom.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) # 출력 : +(-)2520
            b = abs(int(b))
            self.OneTrStatus["nowTrPrice"] = b  # 종목검색 정보 윗줄의 현재가도 실시간 업데이트
            self.tempText = " 현재가:"+str(b)
            self.realTimeTrInfo.clear
            self.realTimeTrInfo.setPlainText(self.tempText) # 종목검색 정보 실시간 업데이트.

            self.kst = pytz.timezone('Asia/Seoul')
            self.current_time = datetime.datetime.now(self.kst).time()
            if self.current_time > datetime.time(9, 0) or self.current_time <= datetime.time(15, 30):
                if self.OneTrStatus["status"] =="거래시작":
                    print("========================tradingExcecute===================")  
                    self.tradingStatusSetting()  
                    self.tradingExcecute(self.OneTrStatus["tradingStatus"] , sCode, sRealType, sRealData)
            # QTest.qWait(2000)
        else:
            print("realdata_slot, sRealType: ", sRealType)     

    def chejan_slot(self, sGubun, nItemCnt, sFidList):  #실시간 주문 접수/확인 이벤트
        print("mode: chejan_slot")
        if int(sGubun) == 0:
            print("mode: chejan_slot-주문체결통보") 
            price = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가']).strip()
            if price == '':
                return
            sCode = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드']).strip()[1:]
            ctime = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간']).strip()[1:]
            name = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명']).strip()
            quantity = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량']).strip()
            status = self.k.kiwoom.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['매도수구분']).strip()
            if status == '2':  # 매수
                
                self.k.acc_portfolio[sCode].update({"종목명": name})
                self.k.acc_portfolio[sCode].update({"보유수량": int(quantity)})
                self.k.acc_portfolio[sCode].update({"체결가": price})
              
                
                msg = "[매수]" + name + " 체결가 : " + price + " 수량 : " + quantity+" 체결시간:"+ctime
                print(msg)
                print(self.k.acc_portfolio[sCode])
                self.pteLog.appendPlainText(msg+"\n") 
                self.OneTrStatus["tradingStatus"] ="SELL"

            elif status == '1':  # 매도
    
                print(self.k.acc_portfolio[sCode])
                msg = "[매도]" + name + " 체결가 : " + price + " 수량 : " + quantity+" 체결시간:"+ctime
                print(msg)
                self.pteLog.setPlainText(msg)

                self.k.acc_portfolio[sCode]['보유수량'] -= int(quantity)

                    
                self.OneTrStatus["tradingStatus"] ="BUY"
                self.pteLog.appendPlainText(msg+"\n") 
            # self.accountInterface()
        else:
            print("chejan_slot, else: ", sGubun)                            

    def msg_slot(self, sScrNo, sRQName, sTrCode, msg):
        print("스크린: %s, 요청이름: %s, tr코드: %s --- %s" %(sScrNo, sRQName, sTrCode, msg))


if __name__=='__main__':             
                                    
    app = QApplication(sys.argv)     
    CH = Login_Machnine()            
    CH.show()                        
    app.exec_()           