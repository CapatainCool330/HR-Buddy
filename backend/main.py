from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from engine import ChatEngine
import json

app = FastAPI(title="HR Buddy API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Chat Engine
chat_engine = ChatEngine()

# Connection Manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

manager = ConnectionManager()

@app.get("/")
def health_check():
    return {"status": "ok", "service": "HR Buddy Bot (WebSocket Enabled)"}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            # Parse message if it's JSON, or treat as raw string
            try:
                message_data = json.loads(data)
                user_message = message_data.get("message", "")
            except json.JSONDecodeError:
                user_message = data

            if not user_message:
                continue

            # Process with Engine
            response_data = chat_engine.process_message(user_message, client_id)
            
            # Send back structured response
            await manager.send_message(json.dumps(response_data), websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)

if __name__ == "__main__":
    import uvicorn
    # Trust Proxy Config: proxy_headers=True, forwarded_allow_ips="*"
    uvicorn.run(app, host="0.0.0.0", port=8000, proxy_headers=True, forwarded_allow_ips="*")
