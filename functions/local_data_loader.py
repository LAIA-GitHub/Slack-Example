import os
import logging
import pandas as pd

def load_local_documents(directory):
    documents = []
    for filename in os.listdir(directory):
        if filename.endswith(".csv"):
            file_path = os.path.join(directory, filename)
            try:
                logging.debug(f"Processing file: {file_path}")
                df = pd.read_csv(file_path)
                documents.append(df)
            except Exception as e:
                logging.error(f"Error loading file {file_path}: {e}")
    return documents
