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

app = FastAPI()

# Configure CORS
origins = [
    "http://localhost",
    "http://localhost:8000",
    # Add additional origins as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods (GET, POST, etc.)
    allow_headers=["*"],  # Allow all headers
)

@app.get("/hello")
def read_root():
    return {"Hello": "World"}

# Load environment variables
load_dotenv()

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Setup Supabase client
supabase_client = SupaBase.setup_supabase_client()

# Initializes your Slack app with your bot token
slack_app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Initialize FastAPI app
handler = SlackRequestHandler(slack_app)

# Slack signature verifier
signature_verifier = SignatureVerifier(signing_secret=os.environ.get("SLACK_SIGNING_SECRET"))

# Scheduler for daily vector store update
scheduler = BackgroundScheduler()

@app.get("/api/update_vectorstore")
def fetch_data_rebuild_vectorstore():
    SupaBase.fetch_data_from_database_and_save(supabase_client)

    # Load documents from local folder
    local_docs = local_data_loader.load_local_documents("docs/opendata")

    # Fetch data from Supabase
    database_docs = local_data_loader.load_local_documents("docs/inputdata")

    # Combine documents from local and database
    combined_docs = [*local_docs, *database_docs]

    # Create and load vector store
    vector_store = CreateVector.create_vector_store(combined_docs)

    return 200, "Vectorstore created"


# Slack event handling
@slack_app.event("message")
def handle_message_events(body, say, logger):
    logger.info(f"Received message: {body}")
    try:
        event = body['event']
        user = event.get('user')
        text = event.get('text')
        channel_type = event.get('channel_type')
        thread_ts = event.get('ts')

        # Check if the message is in a direct message (im) or if the bot is mentioned
        if channel_type == 'im' or f'<@{os.environ.get("SLACK_BOT_USER_ID")}>' in text:
            response = run_chain(text)

            # Reply in a thread
            say(text=response, thread_ts=thread_ts)
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        say("Sorry, something went wrong while processing your message.")

@slack_app.event("app_mention")
def handle_app_mention_events(body, say, logger):
    logger.info(f"Received app_mention event: {body}")
    try:
        event = body['event']
        user = event.get('user')
        text = event.get('text')
        thread_ts = event.get('ts')

        response = ModifyingPrompt.create_chain(text)

        # Tokenize and chunk the input message
        chunks = Chunk.chunk_input_message(text)
        print("chunks are:", chunks)

        vector_store_path = 'data/static'
        vector_store = CreateVector.load_vector_store(vector_store_path)
        all_retrieved_docs = []

        for chunk in chunks:
            retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 2})
            retrieved_docs = retriever.invoke(chunk)
            all_retrieved_docs.extend(retrieved_docs)

        all_retrieved_docs = list({doc.page_content: doc for doc in all_retrieved_docs}.values())

        print(f"Number of retrieved documents: {len(all_retrieved_docs)}")    
        
        context_docs = "\n".join([doc.page_content for doc in all_retrieved_docs])
        print("Context to send:", context_docs)

        context_docs = truncate_context(context_docs, 6000)

        chain = ModifyingPrompt.create_chain(vector_store)

        response = chain.invoke({
        "input": text,
        "context": context_docs
        })

        llm_answer_status = response['answer']  
        print("Answer:", llm_answer_status)
        
        data = {
            "transcription_status": text,
            "llm_answer_status": llm_answer_status,
        }

        json_response = json.dumps(data)

        SupaBase.push_data_to_database(SupaBase.setup_supabase_client(), text, llm_answer_status)
        

        # Reply in a thread
        say(text=response, thread_ts=thread_ts)
    except Exception as e:
        logger.error(f"Error handling app_mention event: {e}")
        say("Sorry, something went wrong while processing your message.")


@app.post("/slack/events")
async def slack_events(request: Request, x_slack_signature: str = Header(None), x_slack_request_timestamp: str = Header(None)):
    if not signature_verifier.is_valid(
        body=await request.body(),
        timestamp=x_slack_request_timestamp,
        signature=x_slack_signature
    ):
        return JSONResponse(status_code=400, content={"error": "invalid request"})

    data = await request.json()
    if "challenge" in data:
        return JSONResponse(content={"challenge": data["challenge"]})

    return await handler.handle(request)


def truncate_context(context, max_tokens):
    tokens = context.split()
    if len(tokens) > max_tokens:
        tokens = tokens[:max_tokens]
    return ' '.join(tokens)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
