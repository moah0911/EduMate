"""Utility functions for text processing."""
import os
import re
from docx import Document  # Ensure this works with python-docx
import PyPDF2
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Download NLTK resources if not already downloaded
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


def extract_text_from_file(file_path):
    """Extract text from a file based on its extension."""
    if not os.path.exists(file_path):
        return ""
    
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == '.txt':
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    
    elif ext == '.docx':
        try:
            doc = Document(file_path)
            return '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        except Exception as e:
            print(f"Error extracting text from DOCX: {e}")
            return ""
    
    elif ext == '.pdf':
        try:
            text = ""
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                for page_num in range(len(pdf_reader.pages)):
                    text += pdf_reader.pages[page_num].extract_text()
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {e}")
            return ""
    
    else:
        # For code files and other text-based files
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            print(f"Error extracting text from file: {e}")
            return ""


def preprocess_text(text):
    """Preprocess text for analysis."""
    if not text:
        return ""
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove special characters and numbers
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\d+', '', text)
    
    # Tokenize
    tokens = word_tokenize(text)
    
    # Remove stopwords
    stop_words = set(stopwords.words('english'))
    tokens = [word for word in tokens if word not in stop_words]
    
    # Join tokens back into a string
    return ' '.join(tokens)


def similarity_score(text1, text2):
    """Calculate similarity score between two texts using TF-IDF and cosine similarity."""
    if not text1 or not text2:
        return 0.0
    
    # Preprocess texts
    processed_text1 = preprocess_text(text1)
    processed_text2 = preprocess_text(text2)
    
    if not processed_text1 or not processed_text2:
        return 0.0
    
    # Create TF-IDF vectors
    vectorizer = TfidfVectorizer()
    try:
        tfidf_matrix = vectorizer.fit_transform([processed_text1, processed_text2])
        
        # Calculate cosine similarity
        similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0]
        return similarity
    except Exception as e:
        print(f"Error calculating similarity: {e}")
        return 0.0


def count_words(text):
    """Count the number of words in a text."""
    if not text:
        return 0
    
    # Tokenize the text
    tokens = word_tokenize(text)
    
    # Filter out punctuation and other non-word tokens
    words = [word for word in tokens if word.isalpha()]
    
    return len(words)


def summarize_text(text, max_sentences=3):
    """Create a simple summary of the text by extracting key sentences."""
    if not text or len(text.strip()) == 0:
        return ""
    
    # Split text into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', text)
    
    if len(sentences) <= max_sentences:
        return text
    
    # For a simple summary, just return the first few sentences
    return ' '.join(sentences[:max_sentences]) + "..."