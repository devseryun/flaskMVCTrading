from PyQt5.QtCore import *           # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from app.connections.realKiwoom import Kiwoom            # 로그인을 위한 클래스
from PyQt5.QtWidgets import *        # PyQt import
from PyQt5.QtTest import *           # 시간관련 함수
from datetime import datetime, timedelta    # 특정 일자를 조회
from app.entity.kiwoomEntity import *

dto = DataTransferObject()
class Thread3():
    def __init__(self):     # 부모의 윈도우 창을 가져올 수 있다.

        self.kw = Kiwoom()
        ################## 사용되는 변수
        self.search_Screen = "1300"  # 계좌평가잔고내역을 받기위한 스크린
        
        ###### 슬롯
        self.kw.kiwoom.OnReceiveTrData.connect(self.trdata_slot)  # 내가 알고 있는 Tr 슬롯에다 특정 값을 던져 준다.
        self.kw.kiwoom.OnReceiveRealData.connect(self.OnReceiveRealData)
        ###### EventLoop
        self.searchTr_loop = QEventLoop()  # 계좌 이벤트루프
        ###### 검색 종목값 가져오기
        self.ampleRemain()
       

    #sampleRemain0 조회
    def ampleRemain(self, sPrevNext="0"):  # 조회 버튼 클릭 시 실행되는 함수
        print("sampleRemain0")         
        self.kw.kiwoom.dynamicCall("SetInputValue(QString, QString)","계좌번호", "8043856211")
        self.kw.kiwoom.dynamicCall("SetInputValue(QString, QString)","비밀번호", "0000")  # 모의투자 0000
        self.kw.kiwoom.dynamicCall("SetInputValue(QString, QString)","비밀번호입력매체구분", "00")
        self.kw.kiwoom.dynamicCall("SetInputValue(QString, QString)","조회구분", "2")
        print("sampleRemain1")         
        self.kw.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)","계좌평가잔고내역요청", "opw00018", next, "2000")
         
        # self.kw.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", "005930")
        # self.kw.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "종목검색요청", "opt10001", 0, self.search_Screen)   
        # self.searchTr_loop.exec_() # 이벤트 루프 실행

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        print("와라")
        if sRQName == "계좌평가잔고내역요청":    # 수신된 데이터 구분명이 종목검색요청 일 경우
            name =  self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, 0, "종목명")    # 구분명 opt10001_req 의 종목명을 가져와서 name에 셋팅
            volume =  self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, 0, "거래량")  # 구분명 opt10001_req 의 거래량을 가져와서 volume에 셋팅
            totalBuyingPrice = int(self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총매입금액"))
            currentTotalPrice = int(self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총평가금액"))
            balanceAsset = int(self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "추정예탁자산"))
            totalEstimateProfit = int(self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총평가손익금액"))
            total_profit_loss_rate = float(self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총수익률(%)")) 
            print("totalBuyingPrice %s" % totalBuyingPrice)
            dto = totalBuyingPrice
            # self.searchTr_loop.exit() # 이벤트 루프 종료

    def OnReceiveRealData(self, code, rtype, data):
        print("OnReceiveRealData")
          