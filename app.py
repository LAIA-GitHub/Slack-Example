import os
import logging
from slack_sdk.signature import SignatureVerifier
from fastapi import FastAPI, Request, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('.env')

# Initialize logging
logging.basicConfig(level=logging.DEBUG)

# Initialize FastAPI app
app = FastAPI()

# Slack signature verifier
signature_verifier = SignatureVerifier(os.environ["SLACK_SIGNING_SECRET"])

@app.post("/slack/events")
async def slack_events(request: Request, x_slack_signature: str = Header(None), x_slack_request_timestamp: str = Header(None)):
    logging.info("Received Slack event")
    if not signature_verifier.is_valid_request(await request.body(), x_slack_signature, x_slack_request_timestamp):
        logging.error("Invalid request signature")
        return JSONResponse(status_code=400, content={"error": "invalid request"})

    data = await request.json()
    if "challenge" in data:
        logging.info("Responding to Slack challenge")
        return JSONResponse(content={"challenge": data["challenge"]})

    logging.info("Received event data: %s", data)
    return JSONResponse(status_code=200, content={"status": "ok"})

# Run the FastAPI app with Uvicorn
#if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=5000)
