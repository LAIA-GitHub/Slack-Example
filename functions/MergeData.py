from dotenv import load_dotenv
from langchain_community.document_loaders.merge import MergedDataLoader, Document
from langchain_community.document_loaders import DirectoryLoader
from functions import SupaBaseSetup 
import json

# Load environment variables
load_dotenv()
# Setup Supabase client
supabase_client = SupaBaseSetup.setup_supabase_client()

def fetch_and_merge_data(supabase_client):
    # Fetch live data from Supabase
    live_data = SupaBaseSetup.fetch_data(supabase_client)

    # Convert live data to documents
    live_documents = []
    for entry in live_data:
        content = json.dumps(entry)
        live_documents.append(Document(page_content=content, metadata={"source": "Supabase"}))

    # Load local documents
    local_loader = DirectoryLoader('data/opendata', glob="**/*.csv")
    local_docs = local_loader.load()

    # Merge local documents and live documents
    merged_loader = MergedDataLoader(loaders=[local_docs, live_documents])

    # Load all documents
    all_docs = merged_loader.load()
    
    return all_docs