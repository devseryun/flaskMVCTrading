import os
import requests
import json
import sys
sys.path.append("./")
 
from PyQt5 import uic             # ui 파일을 가져오기위한 함수
# from PyQt5.QtCore import *        # eventloop/스레드를 사용 할 수 있는 함수 가져옴.
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QUrl, QByteArray, QDataStream, pyqtSignal, QObject, QIODevice
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest, QNetworkReply
from PyQt5.QAxContainer import *              # 키움증권의 클레스를 사용할 수 있게 한다.(QAxWidget)
from PyQt5Singleton import Singleton

import pytz
import datetime
from kiwoomRelated.errorCode import *
from kiwoomRelated.kiwoomType import *  

class viewLikeGuiOperaing():
    def __init__(self, *args, **kwargs):
        print("")