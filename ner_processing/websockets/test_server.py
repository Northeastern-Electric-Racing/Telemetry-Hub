
import asyncio
import websockets
from threading import Thread

from timeit import default_timer



"""
Messages will just be forwarded in the raspi from the xbee to the clients.
Therefore, the messages will be strings in the format:
    Tttttttttttmmmiiildd...\r

    T = start token (literal 'T')
    tt... = timestamp in seconds (10-digit number)
    mmm = millisecond time
    iii = CAN ID
    l = message length (in bytes)
    dd... = hex data bytes (amount according to length, 2 chars per byte)
    \r
"""

class Message:
    START_TIME = 1654705626000

    def __init__(self):
        self.time = Message.START_TIME
        self.id = 514
        self.len = 8
        self.data = [0, 0, 24, 0, 0, 0, 0, 0]
        self.data_count = 1
        self.time_count = 1
    
    def update_message(self):
        self.time += self.time_count
        self.data[0] = self.data_count % 255
        self.time_count += 1
        self.data_count += 1

    def get_string(self):
        return f"T{self.time}{self.id:03x}{self.len}{self.get_data_string()}\r"

    def get_data_string(self):
        out = ""
        for d in self.data:
            out += f"{d:02x}"
        return out


connections = []


class MessageThread(Thread):
    def __init__(self):
        super().__init__()

    def run(self):
        last_time = default_timer()
        m = Message()
        
        while True:
            dif = default_timer() - last_time
            if dif > 1:
                print("hit timer")
                message = m.get_string()
                for con in connections:
                    print("sending message")
                    con.send(message)
                m.update_message()
                last_time = default_timer()


async def handle(websocket):
    name = await websocket.recv()
    print(f"Received from {name}")
    connections.append(websocket)


if __name__ == "__main__":
    # message_thread = MessageThread()
    # message_thread.start()
    # message_thread.join()

    start_server = websockets.serve(handle, '127.0.0.1', 8765)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()
    
    print("Exit")


