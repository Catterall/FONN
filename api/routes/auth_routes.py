import uuid

from argon2 import PasswordHasher, exceptions
from fastapi import APIRouter, HTTPException, status

from data.database import FONNDB
from models.models import LoginAttempt, SessionKey

router = APIRouter()
db = FONNDB()


@router.post("/login")
def login(login_attempt: LoginAttempt):
    """Logs a user in and returns a session key"""
    email = login_attempt.email
    if not db.select("SELECT COUNT(*) FROM [User] WHERE [Email] = ?", email)[0][0]:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Email not found")
    
    password = login_attempt.password
    user_id, stored_password = db.select("SELECT [UserID], [Password] FROM [User] WHERE [Email] = ?", email)[0]

    ph = PasswordHasher(time_cost=2, memory_cost=80, parallelism=10, hash_len=16, salt_len=16)
    try:
        ph.verify(stored_password, password)
    except exceptions.VerifyMismatchError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password")
    
    session_key = str(uuid.uuid4())
    db.nonselect("""
        INSERT INTO Session 
            (SessionKey, UserID, CreationDate, ExpiryDate) 
        VALUES 
            (?, ?, GETDATE(), DATEADD(day, 1, GETDATE()))""", session_key, user_id)
    
    return {
        "authenticated": True,
        "user_id": user_id,
        "session_key": session_key
    }


@router.post("/logout")
def logout(session_key: SessionKey):
    "Logs a user out by setting the session key expiry date to the current datetime"
    session_key = session_key.session_key
    if not db.session_key_exists(session_key):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Session key not found")
    
    if db.session_key_expired(session_key):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Session key expired")
    
    db.nonselect("""
        UPDATE Session
        SET ExpiryDate = GETDATE()
        WHERE SessionKey = ?""", session_key)
    
    return {
        "logged_out": True
    }
