import os
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from github import Github, GithubIntegration
load_dotenv()

app_id = os.getenv('TEST_APP_ID')
# Read the bot certificate
with open(
        os.path.normpath(os.path.expanduser(os.getenv('TEST_PRIVATE_KEY_PATH'))),
        'r'
) as cert_file:
    app_key = cert_file.read()

app = FastAPI()


# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)


@app.get("/")
@app.post("/")
async def read_root(request: Request):
    body = await request.body()
    json = await request.json()
    print(f"Received request: {json}")
    print(f"Received body: {body}")
    return body
