import os
import csv
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

def setup_supabase_client():
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    if not url or not key:
        logging.error("Supabase URL or Key is missing")
        raise ValueError("Supabase URL or Key is missing")
    return create_client(url, key)

def fetch_data(client):
    try:
        live_data = client.table('Inputs').select("*").execute()
        logging.info(f"Fetched data: {live_data.data}")
        return live_data.data
    except Exception as e:
        logging.error(f"Failed to fetch data from Supabase: {e}")
        raise

def fetch_data_from_database_and_save(client):
    try:
        live_data = client.table('Inputs').select("*").execute()
        logging.info(f"Fetched live data from Supabase: {live_data.data}")

        csv_file_path = 'data/inputdata/input.csv' 
        os.makedirs(os.path.dirname(csv_file_path), exist_ok=True)

        if live_data.data:
            keys = live_data.data[0].keys()
            with open(csv_file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=keys)
                writer.writeheader()
                for data in live_data.data:
                    writer.writerow(data)
            logging.info(f"Data saved to {csv_file_path}")
        else:
            logging.warning("No data found in Supabase")

    except Exception as e:
        logging.error(f"Failed to fetch data from database and save to CSV: {e}")
        raise

def push_data_to_database(client, transcription_status, llm_answer_status):
    try:
        data = client.table('Q&A').insert({"Question": transcription_status, "Answer": llm_answer_status}).execute()
        logging.info(f"Data pushed to Supabase: {data}")
        return data
    except Exception as e:
        logging.error(f"Failed to push data to Supabase: {e}")
        return None
