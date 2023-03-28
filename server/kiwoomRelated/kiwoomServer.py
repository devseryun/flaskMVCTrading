from PyQt5.QAxContainer import *
from PyQt5Singleton import Singleton

class KiwoomServer(metaclass=Singleton):
    def __init__(self):
        self.kiwoom = QAxWidget('KHOPENAPI.KHOpenAPICtrl.1')

    def comm_connect(self):
        self.kiwoom.dynamicCall("CommConnect()")

    def get_login_info(self, tag):
        return self.kiwoom.dynamicCall("GetLoginInfo(QString)", tag)
