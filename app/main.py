from fastapi import FastAPI, Request, Response
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
from starlette.middleware.base import BaseHTTPMiddleware    
from database import create_tables
from routes import router
from admin_routes import router as admin_router
import os
from dotenv import load_dotenv

load_dotenv()
app = FastAPI(title="PayFast Sentiment Analysis", description="Sentiment analysis API for PayFast")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    SessionMiddleware, 
    secret_key=os.environ.get("SECRET_KEY"),
    session_cookie="session_id",
    max_age=14 * 24 * 60 * 60,
    https_only=False, 
    same_site="lax"
)

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

# Include routes from the routes module
app.include_router(router)
app.include_router(admin_router)

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Apply cache control to all protected paths
        protected_paths = ["/review", "/api/"]
        if any(path in request.url.path for path in protected_paths):
            # Strict cache control to prevent any caching
            response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0, post-check=0, pre-check=0"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers["Surrogate-Control"] = "no-store"
            
        return response

# Apply the security headers middleware
app.add_middleware(SecurityHeadersMiddleware)

# Root endpoint redirects to the routes module
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Add a route to check authentication status
@app.get("/api/check-auth")
async def check_auth(request: Request):
    # Check if user is in session
    user = request.session.get("user")
    if user:
        return {"authenticated": True, "user": user}
    return {"authenticated": False}, 401