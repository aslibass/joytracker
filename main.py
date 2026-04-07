from fastapi import FastAPI, Depends, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from sqlalchemy.orm import Session
import models, database, auth, ai_service, notifications
from database import get_db, settings
import uvicorn
from datetime import datetime
import traceback

# Initialize Database
models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(title="JoyBucket")
app.add_middleware(SessionMiddleware, secret_key=settings.secret_key)
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    tb = traceback.format_exc()
    print(f"UNHANDLED EXCEPTION on {request.url}:\n{tb}")
    return JSONResponse(status_code=500, content={"detail": str(exc), "traceback": tb})

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
        return templates.TemplateResponse("index.html", context={
            "request": request,
            "google_client_id": settings.google_client_id
        })
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    entries = db.query(models.JoyEntry).filter(models.JoyEntry.user_id == user.id).order_by(models.JoyEntry.created_at.desc()).all()
    return templates.TemplateResponse("feed.html", context={"request": request, "user": user, "entries": entries})

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        return RedirectResponse(url="/")
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or not user.is_admin:
        return RedirectResponse(url="/")
    
    # Aggregated Stats
    entries = db.query(models.JoyEntry).order_by(models.JoyEntry.created_at.desc()).all()
    total_joy = len(entries)
    
    # Calculate Average Sentiment
    scored_entries = [e for e in entries if e.sentiment_score is not None]
    avg_sentiment = sum(e.sentiment_score for e in scored_entries) / len(scored_entries) if scored_entries else 0
    
    # Category Distribution
    categories = {}
    for e in entries:
        cat = e.category or "Pending"
        categories[cat] = categories.get(cat, 0) + 1
        
    # Urgent Count
    urgent_count = sum(1 for e in entries if e.is_urgent)
    
    # Recent Alerts (Top 5)
    recent_alerts = [e for e in entries if e.is_urgent][:5]
    
    # Member-Specific Trends
    users = db.query(models.User).all()
    member_stats = []
    for u in users:
        # Get sentiment history for this user (last 10 entries)
        user_entries = [e for e in entries if e.user_id == u.id and e.sentiment_score is not None]
        user_entries.reverse() # Chronological order for sparkline
        
        recent_scores = [e.sentiment_score for e in user_entries][-10:]
        
        if not recent_scores:
            continue
            
        current_avg = sum(recent_scores[-3:]) / len(recent_scores[-3:]) if len(recent_scores) >= 3 else sum(recent_scores) / len(recent_scores)
        prev_avg = sum(recent_scores[-6:-3]) / len(recent_scores[-6:-3]) if len(recent_scores) >= 6 else current_avg
        
        trend = "stable"
        if current_avg > prev_avg + 0.5: trend = "up"
        elif current_avg < prev_avg - 0.5: trend = "down"
        
        member_stats.append({
            "user": u,
            "recent_scores": recent_scores,
            "avg_sentiment": round(current_avg, 1),
            "trend": trend,
            "last_active": user_entries[-1].created_at if user_entries else u.created_at
        })

    # Sort members by health (lowest sentiment first for pastoral priority)
    member_stats.sort(key=lambda x: x['avg_sentiment'])
    
    return templates.TemplateResponse("admin.html", context={
        "request": request, 
        "user": user, 
        "entries": entries,
        "member_stats": member_stats,
        "stats": {
            "total_joy": total_joy,
            "avg_sentiment": round(avg_sentiment, 1),
            "categories": categories,
            "urgent_count": urgent_count,
            "recent_alerts": recent_alerts
        }
    })

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
    return templates.TemplateResponse("components/joy_entry_card.html", context={"request": request, "entry": new_entry})

@app.get("/entry/{entry_id}/status", response_class=HTMLResponse)
async def get_entry_status(request: Request, entry_id: int, db: Session = Depends(get_db)):
    entry = db.query(models.JoyEntry).filter(models.JoyEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404)
    return templates.TemplateResponse("components/joy_entry_card.html", context={"request": request, "entry": entry})

# Helper function to get current admin user
def get_current_admin_user(request: Request, db: Session = Depends(get_db)):
    user_id = request.cookies.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    user = db.query(models.User).filter(models.User.id == int(user_id)).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return user

@app.get("/admin/users", response_class=HTMLResponse)
async def admin_users(request: Request, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin_user)):
    users = db.query(models.User).order_by(models.User.created_at.desc()).all()
    return templates.TemplateResponse("admin_users.html", context={
        "request": request,
        "user": admin,
        "users": users
    })

@app.post("/admin/users/{user_id}/toggle-admin", response_class=HTMLResponse)
async def toggle_admin(request: Request, user_id: int, db: Session = Depends(get_db), admin: models.User = Depends(get_current_admin_user)):
    target_user = db.query(models.User).filter(models.User.id == user_id).first()
    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Toggle admin status
    target_user.is_admin = not target_user.is_admin
    db.commit()
    db.refresh(target_user)
    
    # Return updated user row component
    return templates.TemplateResponse("components/user_row.html", context={
        "request": request,
        "u": target_user
    })

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=settings.port, reload=True)
