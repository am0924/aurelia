from promptql_api_sdk import PromptQLClient
from promptql_api_sdk.types.models import HasuraLLMProvider
import generate_jwt
from slack_bolt import App as SlackApp
from slack_bolt.adapter.fastapi import SlackRequestHandler
from fastapi import FastAPI, Request, responses
from pyngrok import ngrok
import atexit
import uvicorn
from dotenv import load_dotenv
import os

load_dotenv() 
SLACK_BOT_TOKEN = str(os.getenv("SLACK_BOT_TOKEN"))
print("SLACK_BOT_TOKEN: " + SLACK_BOT_TOKEN)
SLACK_SIGNING_SECRET = str(os.getenv("SLACK_SIGNING_SECRET"))
print("SLACK_SIGNING_SECRET: " + SLACK_SIGNING_SECRET)
PROMPTQL_API_KEY = os.getenv("PROMPTQL_API_KEY")
print("PROMPTQL_API_KEY: " + PROMPTQL_API_KEY)


public_url = ngrok.connect(3000)
print(f"🔗 Public URL for Slack: {public_url}")
atexit.register(ngrok.kill)

token = generate_jwt.generate("admin")
client = PromptQLClient(
    api_key=PROMPTQL_API_KEY,
    ddn_url="https://precise-tapir-9215.ddn.hasura.app/v1/sql",
    llm_provider=HasuraLLMProvider(),
    timezone="America/New_York",
    ddn_headers={"Authorization": f"Bearer {token}"}
)

slack_app = SlackApp(token=SLACK_BOT_TOKEN, signing_secret=SLACK_SIGNING_SECRET)
@slack_app.event("message")
def handle_message_events(body, say):
    say("I'm working on your request. Don't panic if I'm a little quiet. Once I've finished working, I'll send you a \"Finished working\" message.")
    message = body["event"].get("text")
    '''sentence = ""
    for chunk in client.query(message, stream=True):
        if hasattr(chunk, "message") and chunk.message:
            sentence+= chunk.message
            if "." in sentence:
                splitSentence = sentence.split(".")
                say(splitSentence[0])
                sentence = splitSentence[1].lstrip()'''

    response = client.query(message)
    for assistant_action in response.assistant_actions:
            say(assistant_action.message)
            if assistant_action.code_output is not None:
                say(assistant_action.code_output)
    say("Finished working.")    
handler = SlackRequestHandler(slack_app)

app = FastAPI()
@app.post("/slack/events")
async def slack_events(req: Request):
    body = await req.json()

    # Handle Slack's URL verification challenge
    if body.get("type") == "url_verification":
        return responses.PlainTextResponse(content=body["challenge"], status_code=200)
    return await handler.handle(req)

# Launch Uvicorn server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3000)