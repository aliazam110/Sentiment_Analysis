from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.model_loader import load_model_components
from app.predict import predict_sentiment

app = FastAPI(title="PayFast Sentiment Analysis", description="Sentiment analysis API for PayFast")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

model, tokenizer, label_encoder, device, max_len = load_model_components()

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/predict")
async def predict(request: Request):
    form_data = await request.form()
    text = form_data.get("text")
    
    if not text:
        return {"error": "No text provided"}
    
    results = predict_sentiment(text, model, tokenizer, label_encoder, device, max_len)
    return results