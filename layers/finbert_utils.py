"""
Nova Engine — FinBERT Sentiment Analysis Utility

Uses ProsusAI/finbert to evaluate financial news headlines and extract a sentiment tensor.
Lazy-loads PyTorch and Transformers to prevent severe overhead on standard Engine imports.
"""
import logging

log = logging.getLogger("nova.finbert")

_tokenizer = None
_model = None
_device = None
_labels = ["positive", "negative", "neutral"]

def _load_model():
    global _tokenizer, _model, _device
    if _model is None:
        log.info("Lazy-loading ProsusAI/finbert PyTorch models into memory...")
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        _device = "cuda:0" if torch.cuda.is_available() else "cpu"
        _tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        _model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert").to(_device)
        log.info(f"FinBERT loaded successfully on {_device}.")

def estimate_sentiment(news_list: list[str]) -> tuple[float, str]:
    """
    Evaluates a list of headlines and returns the probability and label of the
    most dominant headline, or an aggregated score.
    """
    if not news_list:
        return 0.0, "neutral"
        
    _load_model()
    import torch
    
    # We'll batch process the headlines and take the average sentiment logits
    tokens = _tokenizer(news_list, return_tensors="pt", padding=True, truncation=True).to(_device)
    
    with torch.no_grad():
        outputs = _model(tokens["input_ids"], attention_mask=tokens["attention_mask"])
        
    # outputs.logits is shape (batch_size, 3)
    # Sum the logits across the batch to find the consensus
    summed_logits = torch.sum(outputs["logits"], dim=0)
    
    # Softmax to get probabilities
    probs = torch.nn.functional.softmax(summed_logits, dim=-1)
    
    winning_idx = torch.argmax(probs).item()
    winning_prob = probs[winning_idx].item()
    winning_label = _labels[winning_idx]
    
    return winning_prob, winning_label
