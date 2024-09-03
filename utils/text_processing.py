import re
from typing import List

def tokenize(text: str) -> List[str]:
    return re.findall(r'\b\w+\b', text.lower())

def remove_stopwords(tokens: List[str], stopwords: List[str]) -> List[str]:
    return [token for token in tokens if token not in stopwords]

def stem_words(tokens: List[str]) -> List[str]:
    # This is a very basic stemming. For better results, use a library like NLTK
    return [token[:-1] if token.endswith('s') else token for token in tokens]

def preprocess_text(text: str, stopwords: List[str]) -> List[str]:
    tokens = tokenize(text)
    tokens = remove_stopwords(tokens, stopwords)
    return stem_words(tokens)