from datetime import datetime,timedelta,timezone
from jose import jwt 
from app.config import SECRET_KEY,ALGORITHM,ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(username : str)->str:
    expire = datetime.now(timezone.utc)+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {"sub":username,"exp":expire}
    token = jwt.encode(payload,SECRET_KEY,algorithm= ALGORITHM)
    return token
