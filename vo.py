class dataTransferObject :
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

if __name__ == '__main__':
    dataTransferObject()
