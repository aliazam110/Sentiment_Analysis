import torch
import pickle
from utils import LSTMClassifier

def load_model_components():
    # Load tokenizer and label encoder
    with open("models/tokenizer.pkl", "rb") as f:
        tokenizer = pickle.load(f)
    
    with open("models/label_encoder.pkl", "rb") as f:
        label_encoder = pickle.load(f)
    
    # Model parameters
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    embedding_dim = 128
    hidden_dim = 128
    output_dim = 3
    vocab_size = 10000
    max_len = 100
    
    # Initialize model
    model = LSTMClassifier(
        vocab_size=vocab_size,
        embedding_dim=embedding_dim,
        hidden_dim=hidden_dim,
        output_dim=output_dim,
        max_len=max_len
    )
    
    # Load saved weights
    model.load_state_dict(torch.load("models/lstm_sentiment_model.pth", map_location=device))
    model = model.to(device)
    model.eval()
    
    return model, tokenizer, label_encoder, device, max_len