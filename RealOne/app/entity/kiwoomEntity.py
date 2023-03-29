from app.config.kiwoomType import *  
import os
import requests
import json
import sys
sys.path.append("./")
from PyQt5.QtWidgets import *     
from PyQt5 import uic             # ui 파일을 가져오기위한 함수
from PyQt5.QtCore import *        # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from PyQt5.QtTest import *

class DataTransferObject :
    def __init__(self):                      # Main class의 self를 초기화 한다.
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

