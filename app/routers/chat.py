from fastapi import APIRouter,Depends
from app.models.chat import ChatMessage,ChatRequest,ChatResponse
from app.services.llm import ask_llm
from app.dependencies import get_current_user
from typing import Annotated
from uuid import uuid4
from app.services.storage import get_history,save_message

router = APIRouter(prefix = "/chat",tags = ["chat"])

@router.post("",response_model=ChatResponse)
def chat(
    req:ChatRequest,
    current_user : Annotated[str,Depends(get_current_user)]

):
    conversation_id = req.conversation_id or str(uuid4())

    history = get_history(conversation_id=conversation_id)
    search = history + [{"role" : "user","content":req.message}]
    answer = ask_llm(search)
    save_message(conversation_id,"user",req.message)
    save_message(conversation_id,"assistant",answer)
    return ChatResponse(conversation_id=conversation_id,answer=answer)
        

