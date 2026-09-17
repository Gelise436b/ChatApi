from fastapi import APIRouter,Depends
from app.models.chat import ChatMessage,ChatRequest,ChatResponse
from app.services.llm import ask_llm, ask_llm_stream
from app.dependencies import get_current_user
from typing import Annotated
from uuid import uuid4
from app.services.storage import get_history,save_message
from fastapi.responses import StreamingResponse

router = APIRouter(prefix = "/chat",tags = ["chat"])

@router.post("")
def chat(
    req:ChatRequest,
    current_user : Annotated[str,Depends(get_current_user)]

):
    cid = req.conversation_id or str(uuid4())

    search = get_history(conversation_id=cid) + [{"role" : "user","content":req.message}]
    return StreamingResponse(
        stream_and_save(cid,search,req.message),  # ⚠️❌ 两个问题：① 行尾少了逗号（实测 SyntaxError: Perhaps you forgot a comma?） ② 变量名是 search，不是 messages（NameError）
        media_type="text/event-stream",  
        headers = {"X-Conversation-Id":cid}   # 会话 id 走响应头（以后上 nginx 再加 "X-Accel-Buffering": "no"，否则会被缓冲成一次性返回）
    )
    # ↓↓↓ 以下 4 行是 v1.2 的「非流式」旧实现，留作对比（已被上面的流式版替代）
    # answer = ask_llm(search)
    # save_message(conversation_id,"user",req.message)
    # save_message(conversation_id,"assistant",answer)
    # return ChatResponse(conversation_id=conversation_id,answer=answer)
        
def stream_and_save(cid,messages,user_msg):
    full = []
    for piece in ask_llm_stream(messages):
        full.append(piece)
        yield piece
    answer = "".join(full)   # ⚠️❌ 缩进错！这三行必须在 for 循环【外面】：否则每收到一个片段就存一次库（重复插入，而且存的是半截答案）
    save_message(cid,"user",user_msg)
    save_message(cid,"assistant",answer)

