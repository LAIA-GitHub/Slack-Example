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
from functions import SupaBaseSetup
from openai import OpenAI


# Initialize FastAPI
app = FastAPI()

# Load environment variables
load_dotenv()

# Create a client instance
openai_client = OpenAI()

# Setup Supabase client
supabase_client = SupaBaseSetup.setup_supabase_client()

# Initialize Slack app
slack_app = App(signing_secret=os.environ["SLACK_SIGNING_SECRET"])
handler = SlackRequestHandler(slack_app)



@slack_app.event("message")
def handle_message_events(body, say):
    response = "Sorry, I encountered an error while processing your request."  # Default response
    #input_data = None  # Define input_data to ensure it is in scope
    try:
        logging.info(f"Incoming body: {json.dumps(body, indent=2)}")

        user_message = body["event"]["text"]
        channel_id = body["event"]["channel"]

        text = text.replace("").strip()

        if not user_message:
            logging.error("No text found in the message event")
            say(text="No message text found.", channel=channel_id)
            return

        # Prepare the input for the chain
        input_data = {"input": text, "context": ""}  # You can add context if needed
        response_data = RAG.rag_processing(input_data, supabase_client)

        # Ensure the response is a string
        if isinstance(response_data, dict):
            response = response_data.get('answer', 'Sorry, I encountered an error while processing your request.')
        elif isinstance(response_data, str):
            response = response_data
        else:
            response = "Sorry, I encountered an unexpected response format."

        logging.info(f"Response to send: {response}")

    except Exception as e:
        logging.error(f"Error handling message event: {e}")
        
    say(text=response, channel=channel_id)

        

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