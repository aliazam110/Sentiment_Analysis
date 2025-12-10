from fastapi import FastAPI, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.exceptions import HTTPException

from model_loader import load_model_components
from predict import predict_sentiment
from database import get_db_connection, create_tables
from auth import hash_password
from models import UserCreate

import mysql.connector
from mysql.connector import Error
    
import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(title="PayFast Sentiment Analysis", description="Sentiment analysis API for PayFast")
    
app.mount("/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static")
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@app.on_event("startup")
def startup_event():
    create_tables()

model = tokenizer = label_encoder = device = max_len = None

if os.getenv("RUN_MAIN") == "true": 
    print("Loading model only once...")
    model, tokenizer, label_encoder, device, max_len = load_model_components()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

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
    
    if not all([name, email, cnic, password]):
        raise HTTPException(status_code=400, detail="All fields are required")
    
    hashed_password = hash_password(password)
    
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
        print(f"Error: {e}")
        raise HTTPException(status_code=500, detail="Failed to register user")
    finally:
        cursor.close()
        connection.close()

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})