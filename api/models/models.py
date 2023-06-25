from typing import Optional

from pydantic import BaseModel


class LoginAttempt(BaseModel):
    email: str
    password: str
    

class SessionKey(BaseModel):
    session_key: str
