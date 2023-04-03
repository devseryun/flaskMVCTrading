from PyQt5.QAxContainer import *
from PyQt5.QtWidgets import *        # PyQt import
from PyQt5.QtTest import *           # 시간관련 함수
# from PyQt5.QtCore import *           # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from app.entity.kiwoomEntity import *


dto = DataTransferObject()

class Thread3():
    def __init__(self):    

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.CommConnect()
        ################## 사용되는 변수
        self.search_Screen = "1300"  # 계좌평가잔고내역을 받기위한 스크린
        
        ###### 슬롯
        self.kiwoom.OnReceiveTrData.connect(self.trdata_slot)  # 내가 알고 있는 Tr 슬롯에다 특정 값을 던져 준다.
        self.kiwoom.OnReceiveRealData.connect(self.OnReceiveRealData)
        self.kiwoom.OnEventConnect.connect(self.OnEventConnect)
        # ###### EventLoop
        # self.searchTr_loop = QEventLoop()  # 계좌 이벤트루프
        
        ###### 검색 종목값 가져오기
        self.ampleRemain()

    def OnEventConnect(self, err_code):
        print("OnEventConnect", err_code)
        """Login Event

        Args:
            err_code (int): 0: login success
        """
        if err_code == 0:
            self.connected = True
        elif err_code == 100:
            print("err_code:사용자 정보교환 실패")

        elif err_code == 101:
            print("err_code:서버접속 실패")

        elif err_code == 102:
            print("err_code: 버전처리 실패")

        elif err_code == -106:
            print(err_code)          

    def CommConnect(self, block=True):
        """
        로그인 윈도우를 실행합니다.
        :param block: True: 로그인완료까지 블록킹 됨, False: 블록킹 하지 않음
        :return: None
        """
        self.kiwoom.dynamicCall("CommConnect()")     

    def GetConnectState(self):
        print("GetConnectState")
        """
        현재접속 상태를 반환하는 메서드
        :return: 0:미연결, 1: 연결완료
        """
        ret = self.kiwoom.dynamicCall("GetConnectState()")
        return ret
    
    #sampleRemain0 조회
    def ampleRemain(self, sPrevNext="0"):  # 조회 버튼 클릭 시 실행되는 함수
        print("sampleRemain0")       
        res = self.GetConnectState() 
        print("상태", res) 
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)","계좌번호", "8043856211")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)","비밀번호", "0000")  # 모의투자 0000
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)","비밀번호입력매체구분", "00")
        self.kiwoom.dynamicCall("SetInputValue(QString, QString)","조회구분", "2")
        print("sampleRemain1")         
        self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)","계좌평가잔고내역요청", "opw00018", next, "2000")
        print("sampleRemain2")   
        # self.kiwoom.dynamicCall("SetInputValue(QString, QString)", "종목코드", "005930")
        # self.kiwoom.dynamicCall("CommRqData(QString, QString, int, QString)", "종목검색요청", "opt10001", 0, self.search_Screen)   
        # self.searchTr_loop.exec_() # 이벤트 루프 실행

    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext):
        print("와라")
        if sRQName == "계좌평가잔고내역요청":    # 수신된 데이터 구분명이 종목검색요청 일 경우
            name =  self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, 0, "종목명")    # 구분명 opt10001_req 의 종목명을 가져와서 name에 셋팅
            volume =  self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)", sTrCode, "", sRQName, 0, "거래량")  # 구분명 opt10001_req 의 거래량을 가져와서 volume에 셋팅
            totalBuyingPrice = int(self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총매입금액"))
            currentTotalPrice = int(self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총평가금액"))
            balanceAsset = int(self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "추정예탁자산"))
            totalEstimateProfit = int(self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총평가손익금액"))
            total_profit_loss_rate = float(self.kiwoom.dynamicCall("CommGetData(QString, QString, QString, int, QString)",sTrCode, sRQName, 0, "총수익률(%)")) 
            print("totalBuyingPrice %s" % totalBuyingPrice)
            dto = totalBuyingPrice
            # self.searchTr_loop.exit() # 이벤트 루프 종료

    def OnReceiveRealData(self, code, rtype, data):
        print("OnReceiveRealData")

if not QApplication.instance():
    app = QApplication(sys.argv)

if __name__ == "__main__":
    pass


