from fastapi import FastAPI
from pydantic import BaseModel

from agent import DeepSeekAgent

app = FastAPI(title="DeepSeek Minimal Agent API", version="0.1.0")
agent = DeepSeekAgent()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    answer: str

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    answer = agent.run(req.message)
    return ChatResponse(answer=answer)
