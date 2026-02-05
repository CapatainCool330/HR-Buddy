import asyncio
import websockets
import json

async def test_websocket():
    uri = "ws://localhost:8000/ws/test_client"
    print(f"Connecting to {uri}...")
    try:
        async with websockets.connect(uri) as websocket:
            print("Connected!")
            
            # Test 1: Hello
            msg = {"message": "Hello"}
            await websocket.send(json.dumps(msg))
            response = await websocket.recv()
            print(f"Sent: Hello, Received: {response}")
            
            # Test 2: Apply for leave (Intent)
            msg = {"message": "Apply for leave"}
            await websocket.send(json.dumps(msg))
            response = await websocket.recv()
            print(f"Sent: Apply for leave, Received: {response}")

            print("WebSocket Test Passed! ✅")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_websocket())
