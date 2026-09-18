import time
from fastapi import Request

async def access_log_middleware(request : Request,call_next):
    start = time.time()
    response = await call_next(request)
    cost = time.time()-start
    print(f"[访问] {request.method} {request.url.path} -> {response.status_code} {cost:.3f}s")
    response.headers["X-Process-TIme"] = f"{cost:.3f}"
    return response