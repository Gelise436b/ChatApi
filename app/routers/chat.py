from fastapi import APIRouter
from app.models.chat import ChatMessage,ChatRequest,ChatResponse
from app.services.llm import ask_llm

router = APIRouter(prefix = "/chat",tags = ["chat"])

@router.post("",response_model=ChatResponse)
def chat(req:ChatRequest):
    payload =[{"role":m.role,"content":m.content} for m in req.messages] #req.messages 是pydantic 转为dict
    answer =ask_llm(payload)
    return ChatResponse(answer=answer)

