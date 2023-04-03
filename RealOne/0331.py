import asyncio
from flask import Flask, jsonify
from aiohttp import ClientSession
from pykiwoom.kiwoom import Kiwoom

app = Flask(__name__)
kiwoom = Kiwoom()

async def get_kiwoom_data():
    await kiwoom.CommConnect()
    data = kiwoom.block_request("opt10001", 종목코드="005930", output="주식기본정보", next=0)
    return data.to_dict()

async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()

@app.route("/getSingleTrInfo", methods=["GET"])
async def get_single_tr_info():
    async with ClientSession() as session:
        url = "https://jsonplaceholder.typicode.com/todos/1"
        task = asyncio.ensure_future(get_kiwoom_data())
        await asyncio.gather(task)
        kiwoom_data = task.result()
        print("dd", kiwoom_data)
        data = await fetch(session, url)
        return jsonify({"kiwoom_data": kiwoom_data, "other_data": data})

if __name__ == '__main__':
    app.run('0.0.0.0',port=5000, debug=True)
