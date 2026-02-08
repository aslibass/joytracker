from fastapi import FastAPI, Depends, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import models, database, auth, ai_service, notifications
from database import get_db, settings
import uvicorn
from datetime import datetime

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="JoyBucket")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return RedirectResponse(url="/static/icons/icon-192x192.png")

templates = Jinja2Templates(directory="templates")

# Auth Routes
@app.post("/auth/google")
async def auth_google(request: Request, db: Session = Depends(get_db)):
    data = await request.json()
    token = data.get("token")
    if not token:
        raise HTTPException(status_code=400, detail="Token missing")
    
    try:
        user_info = auth.verify_google_id_token(token)
        user = await auth.get_or_create_user(db, user_info)
        
        response = RedirectResponse(url="/", status_code=200)
        response.set_cookie(
            key="user_id", 
            value=str(user.id), 
            max_age=31536000,
            httponly=True,
            samesite="lax"
        )
        return response
    except Exception as e:
        print(f"ERROR in auth_google: {str(e)}")
        raise HTTPException(status_code=401, detail="Authentication failed")

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user_id")
    return response

# Background Task for AI Analysis
def process_joy_entry(entry_id: int, db: Session):
    entry = db.query(models.JoyEntry).filter(models.JoyEntry.id == entry_id).first()
    if not entry:
        return
    
    analysis = ai_service.analyze_joy_entry(entry.content)
    if analysis:
        entry.category = analysis.category
        entry.sentiment_score = analysis.sentiment_score
        entry.is_urgent = analysis.is_urgent
        entry.tags = analysis.tags
        entry.pastor_summary = analysis.pastor_summary
        db.commit()
        
        if entry.is_urgent:
            user = db.query(models.User).filter(models.User.id == entry.user_id).first()
            notifications.send_crisis_email(user.email, entry.content)
            notifications.send_crisis_sms(user.email)

@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: Session = Depends(get_db)):
    # Check for session cookie (Placeholder logic)
    user_id = request.cookies.get("user_id")
    if not user_id:
        return templates.TemplateResponse("index.html", {
            "request": request,
            "google_client_id": settings.google_client_id
        })
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    entries = db.query(models.JoyEntry).filter(models.JoyEntry.user_id == user.id).order_by(models.JoyEntry.created_at.desc()).all()
    return templates.TemplateResponse("feed.html", {"request": request, "user": user, "entries": entries})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/")
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user.is_admin:
        return RedirectResponse(url="/")
    
    entries = db.query(models.JoyEntry).order_by(models.JoyEntry.created_at.desc()).limit(100).all()
    return templates.TemplateResponse("admin.html", {"request": request, "user": user, "entries": entries})

@app.post("/log", response_class=HTMLResponse)
async def log_joy(request: Request, background_tasks: BackgroundTasks, content: str = Form(...), db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401)
    
    new_entry = models.JoyEntry(user_id=int(user_id), content=content)
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    
    background_tasks.add_task(process_joy_entry, new_entry.id, db)
    
    # Return HTMX snippet for the new entry
    return templates.TemplateResponse("components/joy_entry_card.html", {"request": request, "entry": new_entry})

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
