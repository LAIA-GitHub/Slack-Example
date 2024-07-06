
from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunk_input_message(input_text, chunk_size=300):
    # Initialize the text splitter
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=0,  # Adjust overlap as needed
    )
    
    # Split the input text into chunks
    chunks = splitter.split_text(input_text)
    
    return chunks
