from langchain_community.document_loaders.merge import MergedDataLoader
from langchain_community.document_loaders import DirectoryLoader
import SupaBase

# Setup Supabase client
supabase_client = SupaBase.setup_supabase_client()

    # Fetch data from Supabase
live_data = SupaBase.fetch_data(supabase_client)
print("Live Data from Supabase:\n", live_data)

loader_all = MergedDataLoader(loaders=[DirectoryLoader, live_data])

docs_all = loader_all.load()