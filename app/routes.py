from fastapi import FastAPI, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
from starlette.middleware.sessions import SessionMiddleware
from model_loader import load_model_components
from predict import predict_sentiment
from database import get_db_connection, create_tables
from auth import hash_password, verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import UserCreate
import mysql.connector
from mysql.connector import Error
from datetime import timedelta

app = FastAPI(title="PayFast Sentiment Analysis", description="Sentiment analysis API for PayFast")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Add session middleware for storing JWT token in session
app.add_middleware(SessionMiddleware, secret_key="your-session-secret-key")

# Initialize database tables on startup
@app.on_event("startup")
def startup_event():
    create_tables()

model, tokenizer, label_encoder, device, max_len = load_model_components()

# Landing page
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Signup page
@app.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@app.post("/signup")
async def signup(request: Request):
    form_data = await request.form()
    name = form_data.get("name")
    email = form_data.get("email")
    cnic = form_data.get("cnic")
    password = form_data.get("password")
    
    # Validate inputs
    if not all([name, email, cnic, password]):
        raise HTTPException(status_code=400, detail="All fields are required")
    
    # Hash the password
    try:
        hashed_password = hash_password(password)
    except Exception as e:
        print(f"Error hashing password: {e}")
        raise HTTPException(status_code=500, detail="Error processing password")
    
    # Save to database
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor()
    
    try:
        # Check if email or CNIC already exists
        cursor.execute("SELECT * FROM users WHERE email = %s OR cnic = %s", (email, cnic))
        existing_user = cursor.fetchone()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email or CNIC already registered")
        
        # Insert new user
        cursor.execute(
            "INSERT INTO users (name, email, cnic, password) VALUES (%s, %s, %s, %s)",
            (name, email, cnic, hashed_password)
        )
        connection.commit()
        
        # Redirect to login page
        return RedirectResponse(url="/login", status_code=303)
    except Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        cursor.close()
        connection.close()

# Login page
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request):
    form_data = await request.form()
    email = form_data.get("email")
    password = form_data.get("password")
    
    if not email or not password:
        raise HTTPException(status_code=400, detail="Email and password are required")
    
    connection = get_db_connection()
    if connection is None:
        raise HTTPException(status_code=500, detail="Database connection failed")
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user by email
        cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not verify_password(password, user["password"]):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        # Create access token
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user["email"]}, expires_delta=access_token_expires
        )
        
        # Store token in session
        request.session["access_token"] = access_token
        
        # Redirect to review page
        return RedirectResponse(url="/review", status_code=303)
    except Error as e:
        print(f"Database error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")
    except HTTPException:
        raise
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred")
    finally:
        cursor.close()
        connection.close()

# Dependency to get current user
def get_current_user(request: Request):
    token = request.session.get("access_token")
    if not token:
        raise HTTPException(status_code=302, detail="Not authenticated", headers={"Location": "/login"})
    
    email = verify_token(token)
    if email is None:
        raise HTTPException(status_code=302, detail="Invalid token", headers={"Location": "/login"})
    
    return email

# Review page (protected)
@app.get("/review", response_class=HTMLResponse)
async def review_page(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse("review.html", {"request": request, "user": user})

# Logout
@app.get("/logout")
async def logout(request: Request):
    request.session.pop("access_token", None)
    return RedirectResponse(url="/")

# Prediction endpoint (protected)
@app.post("/predict")
async def predict(request: Request, user: str = Depends(get_current_user)):
    form_data = await request.form()
    text = form_data.get("text")
    
    if not text:
        return {"error": "No text provided"}
    
    results = predict_sentiment(text, model, tokenizer, label_encoder, device, max_len)
    return results