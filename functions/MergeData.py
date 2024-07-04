from langchain_community.document_loaders import DirectoryLoader
from langchain.schema import Document
from functions.SupaBaseSetup import fetch_data
import json

def fetch_and_merge_data(supabase_client, local_directory):
    # Fetch live data from Supabase
    live_data = fetch_data(supabase_client)

    # Convert live data to documents
    live_documents = []
    for entry in live_data:
        content = json.dumps(entry)
        live_documents.append(Document(page_content=content, metadata={"source": "Supabase"}))

    # Load local documents
    local_loader = DirectoryLoader(local_directory, glob="**/*.csv")
    local_docs = local_loader.load()

    # Combine local documents and live documents into a single list
    all_docs = local_docs + live_documents

    return all_docs
