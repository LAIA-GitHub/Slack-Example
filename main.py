import os
import logging
from slack_bolt import App
from slack_bolt.adapter.fastapi import SlackRequestHandler
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain
from langchain_openai import ChatOpenAI
from langchain.chains.conversation.memory import ConversationBufferWindowMemory
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

# Load environment variables from .env file
load_dotenv('.env')

# Initializes your app with your bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# Initialize FastAPI app
fastapi_app = FastAPI()
handler = SlackRequestHandler(app)

# LangChain implementation
system_message_prompt = SystemMessagePromptTemplate.from_template(
    "Assistant is a large language model trained by OpenAI. "
    "Assistant is designed to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations. "
    "Assistant is constantly learning and improving, capable of processing and understanding large amounts of text to provide accurate responses."
)

human_message_prompt = HumanMessagePromptTemplate.from_template("{human_input}")

chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])

chatgpt_chain = LLMChain(
    llm=ChatOpenAI(model="gpt-3.5-turbo", temperature=0.4),
    prompt=chat_prompt,
    memory=ConversationBufferWindowMemory(k=2)
)

@app.event("message")
def handle_message_events(body, say, logger):
    logger.info(f"Received message: {body}")
    try:
        event = body['event']
        user_input = event.get('text')
        if user_input:
            output = chatgpt_chain.predict(human_input=user_input)
            say(output)
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        say("Sorry, something went wrong while processing your message.")

@fastapi_app.post("/slack/events")
async def slack_events(request: Request):
    return await handler.handle(request)

# Run the FastAPI app with Uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(fastapi_app, host="0.0.0.0", port=3000)
