from typing import Annotated
from fastapi import Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError

from app.config import SECRET_KEY,ALGORITHM

oauth2_scheme = OAuth2PasswordBearer(tokenUrl= "token")
async def get_current_user(token : Annotated[str,Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token,SECRET_KEY,ALGORITHM)
        username = payload.get("sub")
        if username is None:
            raise HTTPException(401)
    except JWTError:
        raise HTTPException(401)
    return username