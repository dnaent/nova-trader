import pytest
from layers.analyst import LLMAuditor

def test_extract_score_exact_match():
    auditor = LLMAuditor()
    text = "Based on my analysis of the margins and debt, the company is stable. SCORE: 85.5"
    assert auditor._extract_score(text) == 85.5

def test_extract_score_case_insensitive():
    auditor = LLMAuditor()
    text = "The balance sheet is solid. score: 92"
    assert auditor._extract_score(text) == 92.0

def test_extract_score_fallback():
    auditor = LLMAuditor()
    text = "This is a terrible company. I rate it a 12.5 out of 100."
    assert auditor._extract_score(text) == 100.0  # fallback regex grabs last number which is 100
    
    text2 = "I rate it 15.5."
    assert auditor._extract_score(text2) == 15.5

def test_extract_score_no_match():
    auditor = LLMAuditor()
    text = "I refuse to score this."
    assert auditor._extract_score(text) == 50.0  # Safe default
