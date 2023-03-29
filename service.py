import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pywinauto
import time
import requests
import json

class KiwoomAPI(QAxWidget):
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()
        self.order_number = ''
        self.slack_webhook_url = 'https://slack.com/api/chat.postMessage' # Slack Incoming Webhook URL을 입력해주세요.

    def _create_kiwoom_instance(self):
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)
        self.OnReceiveRealData.connect(self._receive_real_data)
        self.OnReceiveChejanData.connect(self._receive_chejan_data)

    def login(self):
        self.dynamicCall("CommConnect()")
        while self.getConnectState() != 1:
            time.sleep(0.1)
        return {'message': '로그인 성공'}

    def get_balance(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", "계좌번호 입력") # 자신의 계좌번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "비밀번호 입력") # 자신의 비밀번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("SetInputValue(QString, QString)", "조회구분", "1")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00001_req", "opw00001", 0, "0101")
        while True:
            if self.tr_balance_event.is_set():
                self.tr_balance_event.clear()
                break
            QApplication.processEvents()
        account_info = self.account_info
        return account_info

    def get_portfolio(self):
        self.dynamicCall("SetInputValue(QString, QString)", "계좌번호", "계좌번호 입력") # 자신의 계좌번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호", "비밀번호 입력") # 자신의 비밀번호 입력
        self.dynamicCall("SetInputValue(QString, QString)", "비밀번호입력매체구분", "00")
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opw00018_req", "opw00018", 0, "0101")
        while True:
            if self.tr_portfolio_event.is_set():
                self.tr_portfolio_event.clear()
                break
            QApplication.processEvents()
        portfolio = self.portfolio
        return portfolio

    def get_stock(self, code):
        self.dynamicCall("SetInputValue(QString, QString)", "종목코드", code)
        self.dynamicCall("CommRqData(QString, QString, int, QString)", "opt10001_req", "opt10001", 0, "0101")
        while True:
            if self.tr_stock_event.is_set():
                self.tr_stock_event.clear()
                break
            QApplication.processEvents()
        stock_info = self.stock_info
        return stock_info

    def buy_order(self, code, quantity):
        self.order_number = ''
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["주문번호", "계좌번호", "주문유형", "주문수량", "종목코드", "주문가격", "거래구분", "원주문번호", ""])
        while not self.order_number:
            time.sleep(0.1)
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매수주문", "계좌번호", "2", quantity, code, 0, "1", self.order_number, ""])
        while True:
            if self.buy_order_event.is_set():
                self.buy_order_event.clear()
                break
            QApplication.processEvents()
        order_result = self.order_result
        return order_result

    def sell_order(self, code, quantity):
        self.order_number = ''
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["주문번호", "계좌번호", "주문유형", "주문수량", "종목코드", "주문가격", "거래구분", "원주문번호", ""])
        while not self.order_number:
            time.sleep(0.1)
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)", ["매도주문", "계좌번호", "1", quantity, code, 0, "1", self.order_number, ""])
        while True:
            if self.sell_order_event.is_set():
                self.sell_order_event.clear()
                break
            QApplication.processEvents()
        order_result = self.order_result
        return order_result

    def send_slack_message(self, channel, token, message):
        # 토큰이 널이 아니면 
        SLACK_BOT_TOKEN = "xoxb-4184524433281-5008927392563-qZQ6oS6GFDi2A8DyWSKqCeNg"
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer ' + SLACK_BOT_TOKEN
        }
        payload = {
            'channel': channel,
            'text': message
        }
        response = requests.post(self.slack_webhook_url, data=json.dumps(payload), headers=headers)
        if response.status_code == 200:
            return {'message': 'Slack 메시지 전송 성공'}
        else:
            return {'message': 'Slack 메시지 전송 실패'}
    
    def _event_connect(self, err_code):
        if err_code == 0:
            print("로그인 성공")
        else:
            print("로그인 실패")

    def _receive_tr_data(self, screen_no, rqname, trcode, recordname, prev_next, data_len, error_code, message, splm_msg):
        if rqname == "opw00001_req":
            self.account_info = {}
            total_purchase_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "총매입금액")
            total_purchase_price = int(total_purchase_price)
            self.account_info['total_purchase_price'] = total_purchase_price
            print("예수금: ", total_purchase_price)
            self.tr_balance_event.set()
        elif rqname == "opw00018_req":
            self.portfolio = []
            rows = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
            for i in range(rows):
                code = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목번호").strip()[1:]
                name = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "종목명").strip()
                quantity = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "보유수량").strip()
                purchase_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "매입가").strip()
                current_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "현재가").strip()
                profit_loss = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, i, "손익금
            self.portfolio.append({
                'code': code,
                'name': name,
                'quantity': quantity,
                'purchase_price': purchase_price,
                'current_price': current_price,
                'profit_loss': profit_loss
            })
            print("종목명: ", name, " 보유수량: ", quantity)
            self.tr_portfolio_event.set()
        elif rqname == "opt10001_req":
            self.stock_info = {}
            name = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "종목명").strip()
            current_price = self.dynamicCall("CommGetData(QString, QString, QString, int, QString)", trcode, "", rqname, 0, "현재가").strip()
            self.stock_info['name'] = name
            self.stock_info['current_price'] = current_price
            print("종목명: ", name, " 현재가: ", current_price)
            self.tr_stock_event.set()

    def _receive_real_data(self, code, real_type, real_data):
        pass

    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        if gubun == "0":
            order_number = self.dynamicCall("GetChejanData(int)", 9203).strip()
            if order_number:
                self.order_number = order_number
        elif gubun == "1":
            code = self.dynamicCall("GetChejanData(int)", 9001).strip()
            name = self.dynamicCall("GetChejanData(int)", 302).strip()
            order_status = self.dynamicCall("GetChejanData(int)", 913).strip()
            order_quantity = self.dynamicCall("GetChejanData(int)", 900).strip()
            order_price = self.dynamicCall("GetChejanData(int)", 901).strip()
            executed_quantity = self.dynamicCall("GetChejanData(int)", 911).strip()
            if self.order_number == self.dynamicCall("GetChejanData(int)", 9203).strip():
                if order_status == "접수":
                    message = f"{name}({code}) {order_status}되었습니다. 주문 수량: {order_quantity}, 주문 가격: {order_price}"
                elif order_status == "체결":
                    message = f"{name}({code}) {order_status}되었습니다. 주문 수량: {order_quantity}, 체결 수량: {executed_quantity}, 주문 가격: {order_price}"
                elif order_status == "확인":
                    message = f"{name}({code}) {order_status}되었습니다."
                self.send_slack_message(message)
        elif gubun == "4":
            pass

       

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
            rowCount = self.kiwoomReal.dynamicCall("GetRepeatCnt(QString, QString)", sTrCode, sRQName)
            self.stocklistTableWidget_2.setColumnCount(colCount)                 # 행 갯수
            self.stocklistTableWidget_2.setRowCount(rowCount)                    # 열 갯수 (종목 수)
            self.stocklistTableWidget_2.setHorizontalHeaderLabels(column_head)   # 행의 이름 삽입

            self.rowCount = rowCount
            print("계좌에 들어있는 종목 수 %s" % rowCount)

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
            
            for index in range(rowCount):
                itemCode = self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목번호").strip(" ").strip("A")
                itemName = self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "종목명")
                amount = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "보유수량"))
                buyingPrice = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매입가"))
                currentPrice = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "현재가"))
                estimateProfit = int(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "평가손익"))
                profitRate = float(self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "수익률(%)"))
                total_chegual_price = self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매입금액")
                total_chegual_price = int(total_chegual_price.strip())
                possible_quantity = self.kiwoomReal.dynamicCall("GetCommData(QString, QString, int, QString)", sTrCode, sRQName, index, "매매가능수량")
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
            value = self.kiwoomReal.dynamicCall("GetCommRealData(QString, int)", sCode, fid)
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
                    self.kiwoomReal.dynamicCall("SetRealRemove(QString, QString)", self.portfolio_stock_dict[code]['스크린번호'], code)
                self.calculator_fnc()
                sys.exit()
            elif value == "8": #시간외
                pass

        elif sRealType == "주식체결":
            b = self.kiwoomReal.dynamicCall("GetCommRealData(QString, int)", sCode, self.realType.REALTYPE[sRealType]['현재가']) # 출력 : +(-)2520
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
            price = self.kiwoomReal.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결가']).strip()
            if price == '':
                return
            sCode = self.kiwoomReal.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목코드']).strip()[1:]
            ctime = self.kiwoomReal.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['주문/체결시간']).strip()[1:]
            name = self.kiwoomReal.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['종목명']).strip()
            quantity = self.kiwoomReal.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['체결량']).strip()
            status = self.kiwoomReal.dynamicCall("GetChejanData(int)", self.realType.REALTYPE['주문체결']['매도수구분']).strip()
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
