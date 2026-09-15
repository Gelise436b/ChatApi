from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"],deprecated = "auto")
fake_users_db = {
    "zhangsan":{
        "username":"zhangsan",
        "hashed_password": pwd_context.hash("123456"),
        "role" : "admin"
    }
}

def authenticate_user(username:str,password:str):
    user = fake_users_db.get(username)
    if not user:
        return None
    if not pwd_context.verify(password,user["hashed_password"]):
        return None

    return username