from PyQt5.QtCore import *           # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from kiwoom import Kiwoom            # 로그인을 위한 클래스
from PyQt5.QtWidgets import *        # PyQt import
from PyQt5.QtTest import *           # 시간관련 함수
from datetime import datetime, timedelta    # 특정 일자를 조회

class Thread3(QThread):
    def __init__(self, parent):     # 부모의 윈도우 창을 가져올 수 있다.
        super().__init__(parent)    # 부모의 윈도우 창을 초기화 한다.
        self.parent = parent        # 부모의 윈도우를 사용하기 위한 조건

        ################## 키움서버 함수를 사용하기 위해서 kiwoom의 능력을 상속 받는다.
        self.kw = Kiwoom()
        ################## 사용되는 변수
        self.search_Screen = "1300"  # 계좌평가잔고내역을 받기위한 스크린
        
        ###### 슬롯
        self.kw.kiwoom.OnReceiveTrData.connect(self.trdata_slot)  # 내가 알고 있는 Tr 슬롯에다 특정 값을 던져 준다.

        ###### EventLoop
        self.searchTr_loop = QEventLoop()  # 계좌 이벤트루프
        self.parent.pteSearchLog.setDisabled(False) 
        ###### 검색 종목값 가져오기
        self.searchClass()
       

    #종목코드로 조회
    def searchClass(self, sPrevNext="0"):  # 조회 버튼 클릭 시 실행되는 함수
        code = self.parent.lineEditCode.text() # ui 파일을 생성할때 작성한 종목코드 입력란의 objectName 으로 사용자가 입력한 종목코드의 텍스트를 가져옴
        self.parent.pteSearchLog.appendPlainText("종목코드: " + code)    # ui 파일을 생성할때 작성한 plainTextEdit의 objectName 으로 해당 plainTextEdit에 텍스트를 추가함
        # 키움 dynamicCall 함수를 통해 SetInputValue 함수를 호출하여 종목코드를 셋팅함
        self.kw.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        # 키움 dynamicCall 함수를 통해 CommRqData 함수를 호출하여 opt10001 API를 구분명 opt10001_req, 화면번호 0101으로 호출함
        self.kw.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "종목검색요청", "opt10001", 0, self.search_Screen)   
        self.searchTr_loop.exec_() # 이벤트 루프 실행

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        if sRQName == "종목검색요청":    # 수신된 데이터 구분명이 종목검색요청 일 경우
            name =  self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, 0, "종목명")    # 구분명 opt10001_req 의 종목명을 가져와서 name에 셋팅
            volume =  self.kw.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, 0, "거래량")  # 구분명 opt10001_req 의 거래량을 가져와서 volume에 셋팅
            self.parent.pteSearchLog.setPlainText("종목명: " + name.strip()+"  거래량: " + volume.strip()) # 종목명을 공백 제거해서 plainTextEdit에 텍스트를 추가함
            #self.parent.pteSearchLog.appendPlainText("종목명: " + name.strip()+"  거래량: " + volume.strip()) # 종목명을 공백 제거해서 plainTextEdit에 텍스트를 추가함
           # self.parent.pteSearchLog.appendPlainText("거래량: " + volume.strip())   # 거래량을 공백 제거해서 plainTextEdit에 텍스트를 추가함
            self.searchTr_loop.exit() # 이벤트 루프 종료