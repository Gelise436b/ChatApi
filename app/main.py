from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from app.routers import chat,auth
app = FastAPI(title = "Chat API")
app.include_router(chat.router)
app.include_router(auth.router)
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