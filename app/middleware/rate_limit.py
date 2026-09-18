import time 
from fastapi import Request
from fastapi.responses import JSONResponse

MAX_REQUEST = 5
WINDOW = 60

_hits = {}

async def rate_limit_middleware(request : Request,call_next):
    ip = request.client.host
    now = time.time()
    stamps = _hits.get(ip,[])
    stamps =[t for t in stamps if now-t<WINDOW]
    if len(stamps) >= MAX_REQUEST:
        return JSONResponse(status_code=429,content={"detail":"请求太频繁，请稍后再试"})   # ⚠️❌ 状态码写错了：限流应该返回 429（Too Many Requests）；404 是“找不到这个资源”
    stamps.append(now)
    _hits[ip] = stamps
    return await call_next(request)  # ⚠️❌ 这里必须是 `return await call_next(request)`：你现在把 Request 对象当响应返回了，而且【没调 call_next → 请求根本不会走到路由】