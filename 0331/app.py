# app.py
from flask import Flask, jsonify
import redis

app = Flask(__name__)
db = redis.StrictRedis(host='0.0.0.0', port=5000, db=0)


@app.route('/test', methods=["GET"])
def test():
    print("dddddd")


@app.route('/current_price', methods=["GET"])
def get_current_price():
    current_price = db.get('current_price')
    return jsonify({'current_price': current_price})


# @app.route("/remains")
# def remains():
#     # kiwoom.account_num = request.args.get("account_number")
#     # print("계좌 %s" % kiwoom.account_num)
#     print("----remains")

#     kiwoom.sampleRemain()
#     print("----res")
#     # return jsonify({"res": res})

# if __name__ == '__main__':
#     app.run(debug=True)
if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=True)