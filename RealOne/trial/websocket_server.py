import asyncio
import websockets
import json

current_price = None


async def send_current_price(websocket, path):
    global current_price
    while True:
        if current_price is not None:
            data = {"type": "current_price", "value": current_price}
            await websocket.send(json.dumps(data))
            print(f"WebSocket 클라이언트에게 현재가({current_price}) 전송")
            current_price = None
        await asyncio.sleep(1)


def update_current_price(price):
    global current_price
    current_price = price


if __name__ == "__main__":
    start_server = websockets.serve(send_current_price, "localhost", 8000)
    asyncio.get_event_loop().run_until_complete(start_server)
