import os
import logging
from fastapi import FastAPI, Request, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from slack_sdk.signature import SignatureVerifier
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Initializes your Slack app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Initialize FastAPI app
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

handler = SlackRequestHandler(app)

# Slack signature verifier
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

# Handle Slack events
@app.event("message")
def handle_message_events(body, say, logger):
    logger.info(f"Received message: {body}")
    try:
        event = body['event']
        user_input = event.get('text')
        if user_input:
            say("This is a test response!")
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        say("Sorry, something went wrong while processing your message.")

@app.post("/slack/events")
async def slack_events(request: Request, x_slack_signature: str = Header(None), x_slack_request_timestamp: str = Header(None)):
    if not signature_verifier.is_valid_request(await request.body(), x_slack_signature, x_slack_request_timestamp):
        return JSONResponse(status_code=400, content={"error": "invalid request"})

    data = await request.json()
    if "challenge" in data:
        return JSONResponse(content={"challenge": data["challenge"]})

    return await handler.handle(request)

# Run the FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)
