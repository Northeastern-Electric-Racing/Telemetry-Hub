import asyncio
import websockets


# async def ping(websocket):
#     while True:
#         await websocket.send('{"message":"PING"}')
#         print('------ ping')
#         await asyncio.sleep(5)

async def hello():
    count = 1
    async with websockets.connect("ws://127.0.0.1:8765", timeout=10, ping_interval=None) as websocket:
        # task = asyncio.create_task(ping(websocket))
        while True:
            await websocket.send(f"Peter ${count}")
            data = await websocket.recv()
            print(data)
            count += 1
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(hello())
