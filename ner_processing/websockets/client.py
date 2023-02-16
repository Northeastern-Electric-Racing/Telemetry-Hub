import asyncio
import websockets


async def hello():
    async with websockets.connect("ws://127.0.0.1:8765") as websocket:
        await websocket.send("Peter")
        while True:
            data = await websocket.recv()
            print(data)

if __name__ == "__main__":
    asyncio.run(hello())