from flask import Flask
from flask_restful import Resource, Api, reqparse
from flask_cors import CORS
from service.kiwoomService import KiwoomAPI

app = Flask(__name__)
CORS(app)
api = Api(app)

kiwoomServiceApi = KiwoomAPI()

class Login(Resource):
    def get(self):
        result = kiwoomServiceApi.login()
        return result

class Balance(Resource):
    def get(self):
        result = kiwoomServiceApi.get_balance()
        return result

class Portfolio(Resource):
    def get(self):
        result = kiwoomServiceApi.get_portfolio()
        return result

class Stock(Resource):
    def get(self, code):
        result = kiwoomServiceApi.get_stock_info(code)
        return result

class Buy(Resource):
    def post(self):
        # reqparse 모듈을 사용하여 전달받은 파라미터를 파싱합니다.
        parser = reqparse.RequestParser()
        parser.add_argument('code', type=str)
        parser.add_argument('price', type=int)
        parser.add_argument('quantity', type=int)
        args = parser.parse_args()
        result = kiwoomServiceApi.buy_order(args['code'], args['price'], args['quantity'])
        if result == 0:
            return {'result': 'success', 'message': '매수 주문이 정상적으로 처리되었습니다.'}
        else:
            return {'result': 'fail', 'message': '매수 주문이 처리되지 않았습니다.'}            
        return result

    # def post(self):
    #     data = request.get_json()
    #     code = data.get('code')
    #     quantity = data.get('quantity')
    #     result = api.buy_order(code, quantity)
    #     return result
    
class Sell(Resource):
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('code', type=str)
        parser.add_argument('quantity', type=int)
        args = parser.parse_args()
        result = kiwoomServiceApi.sell_order(args['code'], args['quantity'])
        if result == 0:
            return {'result': 'success', 'message': '매도 주문이 정상적으로 처리되었습니다.'}
        else:
            return {'result': 'fail', 'message': '매도 주문이 처리되지 않았습니다.'}            
        return result

    # def post(self):
    #     data = request.get_json()
    #     code = data.get('code')
    #     quantity = data.get('quantity')
    #     result = api.sell_order(code, quantity)
    #     return result

class Slack(Resource):
    def post(self):
        data = request.get_json()
        message = data.get('message')
        result = api.send_slack_message(message)
        return result
        
api.add_resource(Login, '/api/login')
api.add_resource(Balance, '/api/balance')
api.add_resource(Portfolio, '/api/portfolio')
api.add_resource(Stock, '/api/stock/<string:code>')
api.add_resource(Buy, '/api/buy')
api.add_resource(Sell, '/api/sell')

if __name__ == '__main__':
    app.run()
