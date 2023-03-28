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
from kiwoomRelated.kiwoomType import *  
from kiwoomRelated.errorCode import *

form_class = uic.loadUiType("./UpperLimitPriceTrading.ui")[0]             # 만들어 놓은 ui 불러오기

class KiwoomOperating(QMainWindow, QWidget, form_class):       # QMainWindow : PyQt5에서 윈도우 생성시 필요한 함수

    def __init__(self, *args, **kwargs):                     
        super(KiwoomOperating, self).__init__(*args, **kwargs)
        form_class.__init__(self)                          
        self.setUI() 
        self.kiwoomReal = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')  
        self.login_event_loop = QEventLoop() 
        self.detail_account_info_event_loop = QEventLoop() 
        self.screen_my_info = "2000" #계좌 관련한 스크린 번호
        ####키움증권 로그인 하기                 
        self.event_slots()
        self.signal_login_commConnect()
        self.call_account.clicked.connect(self.detail_account_mystock) # 계좌정보 가져오기
        QTest.qWait(1000)       

    def setUI(self):
        self.setupUi(self)                

    def signal_login_commConnect(self):
        self.kiwoomReal.dynamicCall("CommConnect()")  
        self.login_event_loop.exec_()  
        self.post_message("채널이름", "# mode:  signal_login_commConnect")

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

    def event_slots(self):
        print("# mode:  event_slots")
        self.kiwoomReal.OnEventConnect.connect(self.login_slot)  #통신연결 상태 변경시 이벤트
        self.kiwoomReal.OnReceiveTrData.connect(self.trdata_slot) # 트랜 수신시이벤트

    def get_account_info(self): #계좌정보 가져오는 함수
        account_list = self.kiwoomReal.dynamicCall("GetLoginInfo(QString)", "ACCNO")
        for n in account_list.split(';'):
            self.accComboBox.addItem(n)

    def detail_account_info(self, sPrevNext="0"):
        self.SetInputValue( "계좌번호", self.account_num)
        self.SetInputValue( "비밀번호", "0000")
        self.SetInputValue( "비밀번호입력매체구분", "00")
        self.SetInputValue( "조회구분", "1")
        self.CommRqData( "예수금상세현황요청", "opw00001", sPrevNext, self.screen_my_info)

    def detail_account_mystock(self, sPrevNext="0"): #계좌평가잔고내역 조회 함수
        account = self.accComboBox.currentText()  # 콤보박스 안에서 가져오는 부분
        self.account_num = account
        self.kiwoomReal.dynamicCall("SetInputValue(String, String)", "계좌번호", account)
        self.kiwoomReal.dynamicCall("SetInputValue(String, String)", "비밀번호", "0000")  # 모의투자 0000
        self.kiwoomReal.dynamicCall("SetInputValue(String, String)", "비밀번호입력매체구분", "00")
        self.kiwoomReal.dynamicCall("SetInputValue(String, String)", "조회구분", "2")
        self.kiwoomReal.dynamicCall("CommRqData(String, String, int, String)", "계좌평가잔고내역요청", "opw00018", sPrevNext, self.screen_my_info)
        self.detail_account_info_event_loop.exec_()
    
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
            self.post_message("#autobot", errors(errCode)[1]) 
        self.login_event_loop.exit()  # 로그인이 완료되면 로그인 창을 닫는다.  

    # Tran 수신 콜백
    def trdata_slot(self, sScrNo, sRQName, sTrCode, sRecordName, sPrevNext): 
        if sRQName == "예수금상세현황요청":
            deposit = self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "예수금")
            self.deposit = int(deposit)
            use_money = float(self.deposit) * self.use_money_percent
            self.use_money = int(use_money)
            self.use_money = self.use_money / 4
            output_deposit =self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "출금가능금액")
            self.output_deposit = int(output_deposit)
            self.detail_account_info_event_loop.exit()
          
        elif sRQName == "계좌평가잔고내역요청":
            column_head = ["종목번호", "종목명", "보유수량", "매입가", "현재가", "평가손익", "수익률(%)"]
            colCount = len(column_head)
            rowCount = self.kiwoomReal.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.stocklistTableWidget_2.setColumnCount(colCount)                 # 행 갯수
            self.stocklistTableWidget_2.setRowCount(rowCount)                    # 열 갯수 (종목 수)
            self.stocklistTableWidget_2.setHorizontalHeaderLabels(column_head)   # 행의 이름 삽입
            self.rowCount = rowCount
            totalBuyingPrice = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총매입금액"))
            currentTotalPrice = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가금액"))
            balanceAsset = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "추정예탁자산"))
            totalEstimateProfit = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, 0, "총평가손익금액"))
            total_profit_loss_rate = float(self.kiwoomReal.dynamicCall("GetCommData(String, String, int, String)", sTrCode, sRQName, 0, "총수익률(%)")) 
            self.label_1.setText(str(totalBuyingPrice))
            self.label_2.setText(str(currentTotalPrice))
            self.label_3.setText(str(balanceAsset))
            self.label_4.setText(str(totalEstimateProfit))
            self.label_5.setText(str(total_profit_loss_rate))      

if __name__=='__main__':                                                
    app = QApplication(sys.argv)     
    CH = KiwoomOperating()            
    CH.show()                        
    app.exec_()           