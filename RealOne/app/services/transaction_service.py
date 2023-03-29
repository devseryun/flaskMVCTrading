from PyQt5.QtCore import *       
from PyQt5.QtTest import *

class TranService:
    def __init__(self, slack_service, kiwoom):
        self.slack_service = slack_service
        self.kiwoom = kiwoom

    # def detail_account_mystock(self, sPrevNext="0"):
    #     print("detail_account_mystock")
    #     self.kiwoom.GyeJa()        
    #     res = self.kiwoom.GetTempGyeJaRecord()
    #     print(res)
    #     return res
    
    def getLoginInfo(self):
        account_num = self.kiwoom.GetLoginInfo("ACCOUNT_CNT")        # 전체 계좌수
        accounts = self.kiwoom.GetLoginInfo("ACCNO")                 # 전체 계좌 리스트
        user_id = self.kiwoom.GetLoginInfo("USER_ID")                # 사용자 ID
        user_name = self.kiwoom.GetLoginInfo("USER_NAME")            # 사용자명
        keyboard = self.kiwoom.GetLoginInfo("KEY_BSECGB")            # 키보드보안 해지여부
        firewall = self.kiwoom.GetLoginInfo("FIREW_SECGB")           # 방화벽 설정 여부
        print("fsdfsfsfsfdsfdsffd")
        return {"account_num": account_num,
                         "accounts": accounts,
                         "user_id": user_id,
                         "user_name": user_name,
                         "keyboard": keyboard,
                         "firewall":firewall,
                         }


    def getSingleCodeData(self, scode):
        # 카카오 : 035720
        print("scode,", scode)
        corp = self.kiwoom.GetMasterCodeName(scode)
        con = self.kiwoom.GetMasterConstruction(scode)
        listed_d = self.kiwoom.GetMasterListedStockDate(scode)
        prev_price = self.kiwoom.GetMasterLastPrice(scode)
        state = self.kiwoom.GetMasterStockState(scode)

        print('기업 : {}'.format(corp))
        print('감리구분 : {}'.format(con))
        print('최초상장일 : {}'.format(listed_d))
        print('전일가 : {}'.format(prev_price))
        print('종목상태 : {}'.format(state))
        res ={"기업":corp,
              "감리구분":con,
              "최초상장일":listed_d,
              "전일가":prev_price,
              "종목상태":state,}
        return res    

        # opt10001 : (TR)주식기본정보요청

        
    # def getSingleCodeData(self, scode):
    #     # 카카오 : 035720
    #     corp = self.kiwoom.GetMasterCodeName(scode)
    #     con = self.kiwoom.GetMasterConstruction(scode)
    #     listed_d = self.kiwoom.GetMasterListedStockDate(scode)
    #     prev_price = self.kiwoom.GetMasterLastPrice(scode)
    #     state = self.kiwoom.GetMasterStockState(scode)

    #     print('기업 : {}'.format(corp))
    #     print('감리구분 : {}'.format(con))
    #     print('최초상장일 : {}'.format(listed_d))
    #     print('전일가 : {}'.format(prev_price))
    #     print('종목상태 : {}'.format(state))    

    def stockFundamentalsRequest_opt10001(self):
        print("ddd")

        df = self.kiwoom.block_request("opw00001",
                                계좌번호="8043856211",
                                비밀번호="",
                                비밀번호입력매체구분="00",
                                조회구분=2,
                                output="예수금상세현황",
                                next=0)
        print(df)
        return df

# opt10081 : (TR)주식일봉차트조회요청
# multi-data (has multiple rows)
    def opt10081(self, scode):
        df_multi = self.kiwoom.block_request('opt10081',
                                종목코드=scode,
                                기준일자='20230327', # 기준일로부터 
                                수정주가구분=1, # 수정주가 적용(액분 등 반영)
                                output='주식일봉차트조회', # multi-data
                                next=0 # 0 : single transaction(단일 요청)
                                )
        print(df_multi)        

    def GetData_10081(self, itemInfo):
        trCode = 'opt10081'
        print(trCode, ' :', itemInfo['code'], ' ... ', )
        Data_10081 = []
        itemCode = itemInfo['code']
        time1 = time.time()
        time1 = self.WaitRequestInterval(time1)
        df = self.kiwoom.block_request(trCode,
                                    종목코드=itemCode,
                                    #기준일자= '20190101',
                                    output="주식일봉차트조회요청",
                                    next=0
        )
        print(df.head())
        rets1 = self.ExtractData_10081(df)
        for ret1 in rets1:
            Data_10081.append(ret1)

        #print("[Length : 10081]", len(Data_10081))
        #print("[Data0]", Data_10081[0])
        #print("[DataFinal]", Data_10081[len(Data_10081)-1])
        if itemInfo: return Data_10081

        while self.kiwoom.tr_remained:
            time1 = self.WaitRequestInterval(time1)
            #print("[time1]", time1)
            df = self.kiwoom.block_request(trCode,
                                        종목코드=itemCode,
                                        #기준일자= '20190101',
                                        output="주식일봉차트조회요청",
                                        next=0
            )
            #print(df.head())
            try:
                rets1 = self.ExtractData_10081(df)
            except:
                break;
            for ret1 in rets1:
                Data_10081.append(ret1)

        print('length :', len(Data_10081))

        return Data_10081

    def ExtractData_10081(seslf, data0):
        codes = data0['종목코드'] # 종목코드
        currents = data0['현재가'] # 현재가
        amounts = data0['거래량'] # 거래량
        moneys = data0['거래대금'] # 거래대금
        dates = data0['일자'] # 일자
        starts = data0['시가'] # 시가
        highs = data0['고가'] # 고가
        lows = data0['저가'] # 저가
        corr1s = data0['수정주가구분'] # 대업종구분
        corrRatios = data0['수정비율'] # 소업종구분
        upjongDaes = data0['대업종구분'] # 종목정보
        upjongSos = data0['소업종구분'] # 수정주가이벤트
        itemInfos = data0['종목정보'] # 전일종가
        corrEvents = data0['수정주가이벤트'] # 수정주가이벤트
        yesters = data0['전일종가'] # 전일종가

        index1 = 0
        values = []
        for curr1 in currents:
            try:
                value1 = {
                    'Da': dates[index1], # date
                    'St':  abs(int(starts[index1])), # Start price
                    'Hi': abs(int(highs[index1])), # High price
                    'Lo':  abs(int(lows[index1])), # Low price
                    'CP':  abs(int(currents[index1])), # current price
                    'TQ':  abs(int(amounts[index1])), # Trade quantity
                    'YP': yesters[index1] # Final price yesterday
                    }
            except:
                continue
            #print(value1)
            values.append(value1)
            index1 += 1


        return values


    def SetItems(self):
        kospiCode = '0'
        kosdaqCode = '10'

        itemCodes_KOSPI = self.kiwoom.GetCodeListByMarket(kospiCode)
        itemCodes_KOSDAQ = self.kiwoom.GetCodeListByMarket(kosdaqCode)
        print('KOSPI:', len(itemCodes_KOSPI))
        itemIndex1 = -1
        for itemCode in itemCodes_KOSPI:
            itemIndex1 += 1
            name = self.kiwoom.GetMasterCodeName(itemCode)
            stockCount = self.kiwoom.GetMasterListedStockCnt(itemCode)
            listedDate = self.kiwoom.GetMasterListedStockDate(itemCode)
            print(itemCode, ' : ', name)
            itemInfo = {
                'market': 'KOSPI',
                'code': str(itemCode),
                'name': name,
                'stockCount': stockCount,
                'listedDate': listedDate
                }
            self.KospiItems.append(itemInfo)

        for itemCode in itemCodes_KOSDAQ:
            itemIndex1 += 1
            name = self.kiwoom.GetMasterCodeName(itemCode)
            stockCount = self.kiwoom.GetMasterListedStockCnt(itemCode)
            listedDate = self.kiwoom.GetMasterListedStockDate(itemCode)
            print(itemCode, ' : ', name)
            itemInfo = {
                'market': 'KOSDAQ',
                'code': itemCode,
                'name': name,
                'stockCount': stockCount,
                'listedDate': listedDate
                }
            self.KosdaqItems.append(itemInfo)
            
        # self.UpdateItems2Server(self.KospiItems, self.Tablename_KOSPI)
        # self.UpdateItems2Server(self.KosdaqItems, self.Tablename_KOSDAQ)        