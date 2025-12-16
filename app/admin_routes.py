from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from auth import hash_password, verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_user_role
from models import UserRole
from crud import get_user_by_email, get_all_users, get_all_reviews_with_user_info
from routes import get_current_user_with_role
from datetime import timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Remove the admin login page and endpoint since we're using unified login

# Dependency to get current admin
def get_current_admin(request: Request):
    user, role = get_current_user_with_role(request)
    if user is None or role != "admin":
        raise HTTPException(status_code=302, detail="Not authenticated", headers={"Location": "/login"})
    return user

# Admin dashboard
@router.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin: str = Depends(get_current_admin)):
    users = get_all_users()
    
    reviews = get_all_reviews_with_user_info()
    
    response = templates.TemplateResponse(
        "admin_dashboard.html", 
        {
            "request": request, 
            "admin": admin,
            "users": users,
            "reviews": reviews
        }
    )
    
    # Set cache control headers to prevent caching
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# Admin logout - now uses the unified logout
@router.get("/admin/logout")
async def admin_logout(request: Request):
    # Clear session
    request.session.clear()
    response = RedirectResponse(url="/login")
    
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response