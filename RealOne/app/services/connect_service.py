from PyQt5.QtCore import *        # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from PyQt5.QtTest import *
import sys
from flask import Blueprint,Flask, jsonify, request
from app.connections.kiwoomConn2 import *

kiwoom = Kiwoom()
kiwoom.CommConnect()

class ConnectService:
    def __init__(self):
        # kiwoom = kiwoom
        print('kiwoom:',kiwoom)

    def getLoginInfo(self):
        account_num = kiwoom.GetLoginInfo("ACCOUNT_CNT")        # 전체 계좌수
        accounts = kiwoom.GetLoginInfo("ACCNO")                 # 전체 계좌 리스트
        user_id = kiwoom.GetLoginInfo("USER_ID")                # 사용자 ID
        user_name = kiwoom.GetLoginInfo("USER_NAME")            # 사용자명
        keyboard = kiwoom.GetLoginInfo("KEY_BSECGB")            # 키보드보안 해지여부
        firewall = kiwoom.GetLoginInfo("FIREW_SECGB")           # 방화벽 설정 여부
        print("fsdfsfsfsfdsfdsffd")
        return {"account_num": account_num,
                         "accounts": accounts,
                         "user_id": user_id,
                         "user_name": user_name,
                         "keyboard": keyboard,
                         "firewall":firewall,
                         }
        


        