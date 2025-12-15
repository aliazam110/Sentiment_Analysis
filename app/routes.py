from fastapi import APIRouter, Request, Form, Depends, HTTPException, status
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.exceptions import HTTPException
from model_loader import load_model_components
from predict import predict_sentiment
from database import get_db_connection
from auth import hash_password, verify_password, create_access_token, verify_token, ACCESS_TOKEN_EXPIRE_MINUTES
from models import UserCreate
import mysql.connector
from mysql.connector import Error
from datetime import timedelta
import json

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# Load model components once
model, tokenizer, label_encoder, device, max_len = load_model_components()

# Landing page
@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Signup page
@router.get("/signup", response_class=HTMLResponse)
async def signup_page(request: Request):
    return templates.TemplateResponse("signup.html", {"request": request})

@router.post("/signup")
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
@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    # Clear any existing session
    request.session.clear()
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
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
        
        # Store user info in session
        request.session["user"] = user["email"]
        request.session["access_token"] = access_token
        
        # Redirect to review page
        response = RedirectResponse(url="/review", status_code=303)
        
        # Add cache control headers
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        
        return response
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
    user = request.session.get("user")
    if not user:
        return None
    
    token = request.session.get("access_token")
    if not token:
        return None
    
    email = verify_token(token)
    if email is None:
        return None
    
    return email

# Review page (protected)
@router.get("/review", response_class=HTMLResponse)
async def review_page(request: Request):
    user = get_current_user(request)
    if user is None:
        return RedirectResponse(url="/login", status_code=302)
    
    response = templates.TemplateResponse("review.html", {"request": request, "user": user})
    
    # Add cache control headers
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# Logout
@router.get("/logout")
async def logout(request: Request):
    # Clear session
    request.session.clear()
    
    # Create response with redirect
    response = RedirectResponse(url="/login")
    response.delete_cookie("session")
    # Add cache control headers
    response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    
    return response

# Prediction endpoint (protected)
@router.post("/predict")
async def predict(request: Request):
    user = get_current_user(request)
    if user is None:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    
    form_data = await request.form()
    text = form_data.get("text")
    
    if not text:
        return {"error": "No text provided"}
    
    # Get sentiment analysis results
    results = predict_sentiment(text, model, tokenizer, label_encoder, device, max_len)
    
    # Get user ID
    connection = get_db_connection()
    if connection is None:
        return {"error": "Database connection failed"}
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE email = %s", (user,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return {"error": "User not found"}
        
        user_id = user_data["id"]
        
        # Store review and results in database using CRUD function
        from crud import create_review
        review = create_review(user_id, text, results)
        
        if not review:
            return {"error": "Failed to store review"}
        
        return results
    except Error as e:
        print(f"Database error: {e}")
        return {"error": "Failed to store review"}
    except Exception as e:
        print(f"Unexpected error: {e}")
        return {"error": "An unexpected error occurred"}
    finally:
        cursor.close()
        connection.close()

@router.get("/api/user-reviews")
async def get_user_reviews(request: Request):
    # Check if user is authenticated
    user = get_current_user(request)
    if user is None:
        return JSONResponse(status_code=401, content={"error": "Not authenticated"})
    
    # Get user ID
    connection = get_db_connection()
    if connection is None:
        return JSONResponse(status_code=500, content={"error": "Database connection failed"})
    
    cursor = connection.cursor(dictionary=True)
    
    try:
        # Get user ID
        cursor.execute("SELECT id FROM users WHERE email = %s", (user,))
        user_data = cursor.fetchone()
        
        if not user_data:
            return JSONResponse(status_code=404, content={"error": "User not found"})
        
        user_id = user_data["id"]
        
        # Get user reviews
        cursor.execute(
            "SELECT id, review_text, created_at FROM reviews WHERE user_id = %s ORDER BY created_at DESC LIMIT 5",
            (user_id,)
        )
        reviews = cursor.fetchall()
        
        return reviews
    except Error as e:
        print(f"Database error: {e}")
        return JSONResponse(status_code=500, content={"error": "Failed to fetch reviews"})
    except Exception as e:
        print(f"Unexpected error: {e}")
        return JSONResponse(status_code=500, content={"error": "An unexpected error occurred"})
    finally:
        cursor.close()
        connection.close()

@router.get("/api/check-auth")
async def check_auth(request: Request):
    user = get_current_user(request)
    if user is None:
        return JSONResponse(status_code=401, content={"authenticated": False})
    return {"authenticated": True, "user": user}