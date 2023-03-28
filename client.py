import os
import requests
import json
import sys
sys.path.append("./")
from PyQt5.QtWidgets import *     
from PyQt5 import uic             # ui 파일을 가져오기위한 함수
from PyQt5.QtCore import *        # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from PyQt5.QtTest import *
from PyQt5.QtWidgets import *                 # GUI의 그래픽적 요소를 제어
from PyQt5.QAxContainer import *              # 키움증권의 클레스를 사용할 수 있게 한다.(QAxWidget)
from PyQt5Singleton import Singleton
import pytz
import datetime
from server.kiwoomRelated.errorCode import *
from server.kiwoomRelated.kiwoomType import *  

form_class = uic.loadUiType("./UpperLimitPriceTrading.ui")[0]             # 만들어 놓은 ui 불러오기

class KiwoomOperating(QMainWindow, QWidget, form_class):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, *args, **kwargs):                      # Main class의 self를 초기화 한다.
        super(KiwoomOperating, self).__init__(*args, **kwargs)
        form_class.__init__(self)                            # 상속 받은 from_class를 실행하기 위한 초기값(초기화)
        self.setUI() 

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

        self.kiwoomReal = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')  

        ####### event loop를 실행하기 위한 변수 모음
        self.login_event_loop = QEventLoop() # 로그인 요청용 이벤트 루프
        self.detail_account_info_event_loop = QEventLoop() # 예수금 요청용 이벤트 루프
        self.calculator_event_loop = QEventLoop()
        self.jang = QEventLoop()


        ####이벤트 생성 및 진행
        self.call_account.clicked.connect(self.detail_account_mystock) # 계좌정보 가져오기
        self.trSearchSettingBtn.clicked.connect(self.stockSearchAndSetting) # 종목정보 가져와서 셋팅
        self.tradingStartBtn.clicked.connect(self.startTrading) #거래시작
        self.tradingStopBtn.clicked.connect(self.stopTradingReal) #거래중지

    def setUI(self):
        self.setupUi(self)                


    def detail_account_mystock(self, sPrevNext="0"): #계좌평가잔고내역 조회 함수
        print("# mode: 계좌평가잔고내역 조회")


    # 종목코드로 조회 및 셋팅
    def stockSearchAndSetting(self, sPrevNext="0"):  
        print("# mode:  stockSearchAndSetting code: ",code )

    def startTrading(self, sPrevNext="0"):
        print("# mode:  거래시작")       

    # 주식거래중지
    def stopTradingReal(self):
        print("# mode:  거래중지")

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


    # 거래중지 버튼을 눌렀을 때 실행되는 함수
    def stop_trading():
        url = 'http://localhost:5000/stop_trading'
        response = requests.post(url)
        if response.status_code == 200:
            print(response.text)
        else:
            print('Failed to stop trading.')

    # 클라이언트 GUI 코드
    # ...

    # 거래중지 버튼에 이벤트 핸들러 등록
    stop_trading_button.clicked.connect(stop_trading)

