import os
from dotenv import load_dotenv
from langchain.vectorstores.faiss import FAISS
from langchain.document_loaders import DirectoryLoader
from functions.MergeData import fetch_and_merge_data
from functions.CreateVector import create_vector_store, load_vector_store

# Load environment variables
load_dotenv()

# Directory to load documents from
directory_path = 'data/'

def update_vector_store():
    # Load local documents
    loader = DirectoryLoader(directory_path, glob_pattern="**/*.csv")
    local_docs = loader.load()

    # Merge with live data from Supabase
    all_docs = fetch_and_merge_data(local_docs)

    # Update vector store
    create_vector_store(all_docs)

if __name__ == "__main__":
    update_vector_store()

