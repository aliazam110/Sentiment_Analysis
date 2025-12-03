import torch
import pandas as pd
import numpy as np
from tensorflow.keras.preprocessing.sequence import pad_sequences
from .utils import clean_text

def predict_sentiment(text, model, tokenizer, label_encoder, device, max_len=100):
    cleaned = clean_text(text)
    
    # Tokenize and pad
    seq = tokenizer.texts_to_sequences([cleaned])
    padded = pad_sequences(seq, maxlen=max_len, padding='post', truncating='post')
    
    # Convert to tensor
    input_tensor = torch.tensor(padded, dtype=torch.long).to(device)
    
    # Predict
    model.eval()
    with torch.no_grad():
        outputs = model(input_tensor)
        probs = torch.softmax(outputs, dim=1)
        pred_idx = torch.argmax(probs, dim=1).item()
    
    # Get confidences and labels
    confidences = (probs[0].cpu().numpy() * 100).tolist()
    labels = label_encoder.classes_
    
    # Prepare results
    results = {
        'text': text,
        'predicted_sentiment': label_encoder.inverse_transform([pred_idx])[0],
        'confidences': {
            label: float(conf) for label, conf in zip(labels, confidences)
        },
        'chart_data': [
            {'sentiment': label, 'confidence': float(conf)} 
            for label, conf in zip(labels, confidences)
        ]
    }
    
    return results