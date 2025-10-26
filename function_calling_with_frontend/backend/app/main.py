from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.ai import call_llm
app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:5173",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Data(BaseModel):
    user_query : str

@app.get('/')
async def home():
    return {"msg" : "Hare Krsna"}

headers = {
    'Content-Type' : 'text/event-stream',
    'Cache-Control' : 'no-cache',
    'Connection' : 'keep-alive',
}
@app.post('/api/v1/ai/chat')
async def ai_chat_endpoint(data : Data):
    return StreamingResponse(
        content=call_llm(user_input = data.user_query),
        headers= headers,
        media_type='text/event-stream'
    )
