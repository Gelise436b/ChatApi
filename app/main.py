from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routers import chat,auth
from app.middleware.rate_limit import rate_limit_middleware 
from app.middleware.access_log import access_log_middleware

app = FastAPI(title = "Chat API")
app.include_router(chat.router)
app.include_router(auth.router)
app.middleware("http")(access_log_middleware)
app.middleware("http")(rate_limit_middleware)

@app.get("/health")
def health():
    return {"status":"OK"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials = True,
    allow_methods = ["*"],
    allow_headers = ["*"]

)