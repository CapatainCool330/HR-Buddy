from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from engine import ChatEngine

app = FastAPI(title="HR Buddy API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Chat Engine
chat_engine = ChatEngine()

class ChatRequest(BaseModel):
    message: str
    session_id: str = "default"

class ChatResponse(BaseModel):
    response: str
    type: str # text or action

@app.get("/")
def health_check():
    return {"status": "ok", "service": "HR Buddy Bot"}

@app.post("/chat")
def chat(request: ChatRequest):
    try:
        if not request.message:
            raise HTTPException(status_code=400, detail="Message cannot be empty")

        response_data = chat_engine.process_message(request.message, request.session_id)
        
        return {
            "response": response_data["content"],
            "type": response_data["type"],
            "action": response_data.get("action") # Optional action identifier
        }
    except Exception as e:
        print(f"Error processing message: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
