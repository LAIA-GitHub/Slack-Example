import nltk
from nltk.tokenize import word_tokenize
# Download the NLTK sentence tokenizer model
nltk.download('punkt')

def chunk_input_message(input_text, chunk_size=3):
    # Tokenize and chunk input text into smaller meaningful chunks (every 3 words as a separate chunk).
    words = word_tokenize(input_text)
    chunks = [" ".join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
    return chunks
