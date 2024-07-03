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
from functions import RAG
from functions import UpdateVectorStore
from functions import SupaBase
from openai import OpenAI


# Initialize FastAPI
app = FastAPI()

# Load environment variables
load_dotenv()

# Create a client instance
openai_client = OpenAI()

# Setup Supabase client
supabase_client = SupaBase.setup_supabase_client()

# Initialize Slack app
slack_app = App(signing_secret=os.environ["SLACK_SIGNING_SECRET"])
handler = SlackRequestHandler(slack_app)



@slack_app.event("message")
def handle_message_events(body, say):
    try:
        user_message = body['event']['text']
        channel_id = body['event']['channel']

        # Create the retrieval chain with the vector store
        chain = RAG.rag_processing(input_data, supabase_client)

        # Prepare the input for the chain
        input_data = {"input": user_message, "context": ""}  # You can add context if needed

        # Run the chain using __call__
        response = chain(input_data)

        # Send the response back to Slack
        say(text=response, channel=channel_id)

    except Exception as e:
        logging.error(f"Error handling message event: {e}")
        say(text="Sorry, I encountered an error while processing your request.", channel=channel_id)

@app.post("/slack/events")
async def slack_events(req: Request):
    return await handler.handle(req)

@app.get("/api/update_vectorstore")
def manual_update_vectorstore():
    try:
        UpdateVectorStore.update_vector_store()
        return {"status": "Vectorstore updated"}
    except Exception as e:
        logging.error(f"Failed to manually update vector store: {e}")
        return JSONResponse(status_code=500, content={"error": str(e)})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)