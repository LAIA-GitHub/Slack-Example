import os
import logging
import json
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk.signature import SignatureVerifier
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler
from functions.ChainSelector import run_chain
from functions import SupaBase, local_data_loader, CreateVector, ModifyingPrompt, Chunk

# Initialize FastAPI
app = FastAPI()

# Initialize Slack app
slack_app = App(signing_secret=os.environ["SLACK_SIGNING_SECRET"])
handler = SlackRequestHandler(slack_app)

# Vector store instance (this should be created or loaded appropriately in your app)
vector_store_path = 'docs/static'
vector_store = CreateVector.load_vector_store(vector_store_path)


@slack_app.event("message")
def handle_message_events(body, say):
    try:
        user_message = body['event']['text']
        channel_id = body['event']['channel']

        # Create the retrieval chain with the vector store
        chain = ModifyingPrompt.create_chain(vector_store)

        # Prepare the input for the chain
        input_data = {"input": user_message, "context": ""}  # You can add context if needed

        # Run the chain
        response = chain.run(input_data)

        # Send the response back to Slack
        say(text=response, channel=channel_id)

    except Exception as e:
        logging.error(f"Error handling message event: {e}")
        say(text="Sorry, I encountered an error while processing your request.", channel=channel_id)

@app.post("/slack/events")
async def slack_events(req: Request):
    return await handler.handle(req)

# Function to update the vector store
def update_vector_store():
    try:
        logging.info("Starting vector store update...")
        client = SupaBase.setup_supabase_client()
        SupaBase.fetch_data_from_database_and_save(client)
        
        local_docs = local_data_loader.load_local_documents("data/opendata")
        database_docs = local_data_loader.load_local_documents("data/inputdata")
        combined_docs = [*local_docs, *database_docs]

        if not combined_docs:
            logging.warning("No documents found for vector store update.")
            return

        # Here ensure the vector store is created or updated correctly
        vector_store.create_or_update(combined_docs)  # Adjust this according to the vector store library

        logging.info("Vectorstore updated successfully")
    except Exception as e:
        logging.error(f"Failed to update vector store: {e}")

@app.get("/api/update_vectorstore")
def manual_update_vectorstore():
    try:
        update_vector_store()
        return {"status": "Vectorstore updated"}
    except Exception as e:
        logging.error(f"Failed to manually update vector store: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)