
from pydantic import BaseModel

class ChatMessage(BaseModel):
    role:str
    content:str

class ChatRequest(BaseModel):
    conversation_id : str | None = None
    message : str

class ChatResponse(BaseModel):
    conversation_id : str
    answer : str