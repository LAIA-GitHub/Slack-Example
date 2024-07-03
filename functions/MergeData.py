from langchain.document_loaders import DirectoryLoader
from functions.SupaBase import fetch_data, setup_supabase_client
from langchain.document_loaders import Document

def fetch_and_merge_data(local_docs):
    # Setup Supabase client
    supabase_client = setup_supabase_client()

    # Fetch data from Supabase
    live_data = fetch_data(supabase_client)
    print("Live Data from Supabase:\n", live_data)

    # Convert live data to Document format if needed
    live_docs = [Document(content=str(item)) for item in live_data]

    # Merge local and live data
    all_docs = local_docs + live_docs
    return all_docs
