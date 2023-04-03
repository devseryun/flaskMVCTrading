import time
#from pykiwoom.kiwoom import Kiwoom # 키움증권 OpenAPI 라이브러리를 사용하기 위한 예시
from fakeKiwoom import Kiwoom # 키움증권 OpenAPI 라이브러리를 사용하기 위한 예시
import redis

db = redis.StrictRedis(host='0.0.0.0', port=6379, db=0)
kiwoom = Kiwoom()
kiwoom.CommConnect(block=True)

while True:
    # current_price = kiwoom.get_current_price() # 키움증권 OpenAPI를 통해 현재가 정보를 가져오는 예시
    data = kiwoom.sampleRemain()
    # current_price = kiwoom.block_request("opt10001",
    #                     종목코드="005930",
    #                     output="주식기본정보",
    #                     next=0)
    db.set('current_price', data)
    time.sleep(20) # 10초 간격으로 정보를 업데이트하는 예시
