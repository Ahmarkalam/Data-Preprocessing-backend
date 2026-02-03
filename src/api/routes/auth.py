from fastapi import APIRouter, Depends, HTTPException, status, Response, Cookie, Header
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from src.database.models import Client, AccessToken
from src.api.dependencies import get_db
import uuid
from datetime import datetime, timedelta
import secrets
import re
import hmac
import hashlib
import base64
from config.settings import settings
from src.utils.email import send_access_email
from src.database.crud.client_crud import get_client_by_email, generate_api_key

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/guest")
async def create_guest_session(db: Session = Depends(get_db)):
    guest_id = f"guest_{uuid.uuid4().hex[:8]}"
    api_key = f"dp_guest_{uuid.uuid4().hex[:16]}"
    
    while db.query(Client).filter(Client.api_key == api_key).first():
        api_key = f"dp_guest_{uuid.uuid4().hex[:16]}"
    
    new_guest = Client(
        id=guest_id,
        name="Guest User",
        email=f"{guest_id}@temp.local",
        company="Guest Session",
        api_key=api_key,
        plan_type="guest",
        monthly_quota_mb=50,
        expires_at=datetime.utcnow() + timedelta(hours=24)
    )
    
    db.add(new_guest)
    db.commit()
    db.refresh(new_guest)
    
    return {
        "api_key": new_guest.api_key,
        "expires_at": new_guest.expires_at,
        "quota_mb": new_guest.monthly_quota_mb
    }

@router.post("/request-access")
async def request_access(email: str, db: Session = Depends(get_db)):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_regex, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid email")
    
    client = get_client_by_email(db, email)
    if not client:
        client_id = f"user_{uuid.uuid4().hex[:8]}"
        api_key = generate_api_key(32)
        client = Client(
            id=client_id,
            name=email.split("@")[0],
            email=email,
            api_key=api_key,
            plan_type="free",
            monthly_quota_mb=1000
        )
        db.add(client)
        db.commit()
        db.refresh(client)
    
    one_hour_ago = datetime.utcnow() - timedelta(hours=1)
    recent_count = db.query(AccessToken).filter(AccessToken.email == email, AccessToken.created_at >= one_hour_ago).count()
    if recent_count >= 3:
        raise HTTPException(status_code=429, detail="Too many requests. Try again later.")
    
    token = secrets.token_urlsafe(32)
    access = AccessToken(
        token=token,
        email=email,
        expires_at=datetime.utcnow() + timedelta(hours=24),
        used=False
    )
    db.add(access)
    db.commit()
    
    link = f"http://localhost:8000/auth/access?token={token}"
    message = f"Your API key: {client.api_key}\nAccess your dashboard: {link}"
    sent_ok = send_access_email(email, client.api_key, link)
    return {
        "message": "Access link sent" if sent_ok else "Access link prepared (email not configured)",
        "preview": {"to": email, "api_key": client.api_key, "link": link, "text": message}
    }

@router.post("/register")
async def register_client(email: str, name: str, company: str = None, db: Session = Depends(get_db)):
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not email or not re.match(email_regex, email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid email address"
        )
    
    if not name or len(name.strip()) < 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide a valid name"
        )
        
    client_id = f"client_{uuid.uuid4().hex[:8]}"
    api_key = f"dp_live_{uuid.uuid4().hex[:24]}"
    
    # Check if email exists
    if db.query(Client).filter(Client.email == email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered. Please sign in."
        )

    new_client = Client(
        id=client_id,
        name=name.strip(),
        email=email,
        company=company or "Independent",
        api_key=api_key,
        plan_type="free",
        monthly_quota_mb=1000  # 1GB for free tier
    )
    
    db.add(new_client)
    db.commit()
    db.refresh(new_client)
    
    return {
        "client_id": new_client.id,
        "name": new_client.name,
        "api_key": new_client.api_key,
        "quota_mb": new_client.monthly_quota_mb,
        "plan": new_client.plan_type
    }

@router.get("/access")
async def access_with_token(token: str, db: Session = Depends(get_db)):
    rec = db.query(AccessToken).filter(AccessToken.token == token).first()
    if not rec:
        raise HTTPException(status_code=401, detail="Invalid token")
    if rec.used:
        raise HTTPException(status_code=401, detail="Token already used")
    if rec.expires_at < datetime.utcnow():
        raise HTTPException(status_code=401, detail="Token expired")
    client = get_client_by_email(db, rec.email)
    if not client:
        raise HTTPException(status_code=404, detail="Account not found")
    rec.used = True
    rec.used_at = datetime.utcnow()
    db.commit()
    exp = int((datetime.utcnow() + timedelta(days=7)).timestamp())
    msg = f"{client.id}:{exp}".encode("utf-8")
    sig = hmac.new(settings.SESSION_SECRET.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    raw = f"{client.id}:{exp}:{sig}".encode("utf-8")
    cookie_value = base64.urlsafe_b64encode(raw).decode("utf-8")
    response = RedirectResponse(url=f"{settings.FRONTEND_URL}/dashboard", status_code=302)
    response.set_cookie(
        key="dp_session",
        value=cookie_value,
        httponly=True,
        secure=False,
        samesite="lax",
        max_age=7*24*3600,
        path="/"
    )
    return response

@router.get("/me")
async def me(x_api_key: str = Header(None), dp_session: str = Cookie(None), db: Session = Depends(get_db)):
    client = None
    if x_api_key:
        client = db.query(Client).filter(Client.api_key == x_api_key).first()
    if not client and dp_session:
        try:
            raw = base64.urlsafe_b64decode(dp_session.encode("utf-8")).decode("utf-8")
            parts = raw.split(":")
            if len(parts) == 3:
                client_id = parts[0]
                client = db.query(Client).filter(Client.id == client_id).first()
        except Exception:
            client = None
    if not client:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"id": client.id, "email": client.email, "name": client.name, "plan": client.plan_type}
