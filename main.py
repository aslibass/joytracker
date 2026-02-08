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
@app.get("/login/google")
async def login_google(request: Request):
    # Ensure redirect URI uses https when on production domain
    redirect_uri = str(request.url_for("auth_callback"))
    if "localhost" not in redirect_uri:
        redirect_uri = redirect_uri.replace("http://", "https://")
        
    async with auth.google_sso:
        return await auth.google_sso.get_login_redirect(
            redirect_uri=redirect_uri
        )

@app.get("/auth/callback")
async def auth_callback(request: Request, db: Session = Depends(get_db)):
    print(f"DEBUG: Auth callback started. URL: {request.url}")
    try:
        async with auth.google_sso:
            user_info = await auth.google_sso.verify_and_process(request)
        print(f"DEBUG: Google verify success. User info: {user_info}")
        
        user = await auth.get_or_create_user(db, user_info)
        print(f"DEBUG: User get_or_create success. User ID: {user.id}")
        
        response = RedirectResponse(url="/")
        response.set_cookie(
            key="user_id", 
            value=str(user.id), 
            max_age=31536000,
            httponly=True,
            samesite="lax"
        )
        return response
    except Exception as e:
        print(f"ERROR in auth_callback: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))

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
        return templates.TemplateResponse("index.html", {"request": request})
    
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
