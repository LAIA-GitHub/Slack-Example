from supabase import create_client 
import os
from dotenv import load_dotenv
import csv

load_dotenv()



url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_KEY")

supabase = create_client(url, key)

transcription_status = "This is a first Test text"
llm_answer_status = "this is a second answer"

data = supabase.table('Q&A').insert({"Question": transcription_status, "Answer": llm_answer_status}).execute()
    



