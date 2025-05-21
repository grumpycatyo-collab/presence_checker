import asyncio
import websockets

async def listen(uri):
    async with websockets.connect(uri) as websocket:
        print(f"Connected to {uri}")
        while True:
            message = await websocket.recv()
            print(f"Received message: {message}")

uri = "ws://localhost:8000/api/attendances/ws"
asyncio.run(listen(uri))