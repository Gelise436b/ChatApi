from typing import Annotated
from fastapi import APIRouter,Depends,HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.services.user import authenticate_user
from app.services.token import create_access_token

router = APIRouter(tags=["auth"])

@router.post("/token")
async def login(form_data : Annotated[OAuth2PasswordRequestForm,Depends()]):
    username = form_data.username
    password = form_data.password
    answer = authenticate_user(username,password)
    if answer is None:
        raise HTTPException(401)
    return {"access_token":create_access_token(username),"token_type":"bearer"}