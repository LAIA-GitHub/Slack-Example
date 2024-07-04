import os
from dotenv import load_dotenv
from langchain.vectorstores.faiss import FAISS
from functions.MergeData import fetch_and_merge_data
from functions.CreateVector import create_vector_store
from functions.SupaBaseSetup import setup_supabase_client

# Load environment variables
load_dotenv()

# Directory to load local documents from
directory_path = 'data/opendata/'

def update_vector_store():
    try:
        # Setup Supabase client
        supabase_client = setup_supabase_client()

        # Fetch and merge data
        all_docs = fetch_and_merge_data(supabase_client, directory_path)

        # Update vector store with merged documents
        create_vector_store(all_docs)

        print("Vectorstore updated successfully")
    except Exception as e:
        print(f"Failed to update vector store: {e}")

if __name__ == "__main__":
    update_vector_store()

