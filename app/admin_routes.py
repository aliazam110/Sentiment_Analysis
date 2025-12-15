from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException
from auth import hash_password, verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES, get_user_role
from models import UserRole
from crud import get_user_by_email, get_all_users, get_all_reviews_with_user_info
from datetime import timedelta

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    return templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/admin/login")
async def admin_login(request: Request):
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    user = get_user_by_email(email)
    
    if not user or not verify_password(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    # Check if user is admin
    if user["role"] != UserRole.ADMIN.value:
        raise HTTPException(status_code=403, detail="Access denied: Not an admin")
    
    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    # Store token in session
    request.session["admin_access_token"] = access_token
    
    # Redirect to admin dashboard
    return RedirectResponse(url="/admin/dashboard", status_code=303)

# Dependency to get current admin
def get_current_admin(request: Request):
    token = request.session.get("admin_access_token")
    if not token:
        raise HTTPException(status_code=302, detail="Not authenticated", headers={"Location": "/admin/login"})
    
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=302, detail="Invalid token", headers={"Location": "/admin/login"})
    
    # Check if user is admin
    role = get_user_role(email)
    if role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied: Not an admin")
    
    return email

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

# Admin logout
@router.get("/admin/logout")
async def admin_logout(request: Request):
    request.session.pop("admin_access_token", None)
    response = RedirectResponse(url="/admin/login")
    
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response