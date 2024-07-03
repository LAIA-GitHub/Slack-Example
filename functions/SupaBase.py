from supabase import create_client as supabase_create_client, Client
import os
from dotenv import load_dotenv
import csv

load_dotenv()

def setup_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return supabase_create_client(url, key)

def fetch_data(client):
    LiveData = client.table('Inputs').select("*").execute()
    return LiveData.data  # Ensure to return just the data part if that's what you need
    

def fetch_data_from_database_and_save(client):
    live_data = client.table('Inputs').select("*").execute()

    # Define path to save CSV
    csv_file_path = 'data/inputdata/input.csv' 

    # Save the data to CSV
    if live_data.data:
        keys = live_data.data[0].keys()  # Grab the keys for CSV column headers
        with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for data in live_data.data:
                writer.writerow(data)

def push_data_to_database(client, transcription_status, llm_answer_status):
    #data = client.table('Q&A').insert({"id": 1, "Question": transcription_status, "Answer": llm_answer_status}).execute()
    
    try:
        data = client.table('Q&A').insert({"Question": transcription_status, "Answer": llm_answer_status}).execute()
        print(f"Data:", data)
        return data
    except Exception as e:
        print(f"Failed to save data: {e}")
        return None