from dotenv import load_dotenv
load_dotenv()
import logging
from langchain_openai import OpenAIEmbeddings
from langchain.vectorstores import VectorStore
from langchain.vectorstores.faiss import FAISS

def create_vector_store(documents):
    try:
        # Assuming 'documents' is a list of DataFrames or similar structures
        if not documents:
            raise ValueError("No documents provided for vector store creation")
        
        logging.debug("Creating vector store with provided documents")
        # Logic to create and return the vector store
        vector_store = VectorStore(documents)
        logging.info("Vector store created successfully")
        return vector_store
    except Exception as e:
        logging.error(f"Failed to create vector store: {e}")
        raise

    
def load_vector_store(store_path: str) -> FAISS:
    vector_store = FAISS.load_local(store_path, OpenAIEmbeddings(), allow_dangerous_deserialization=True)
    return vector_store

