import os
import requests
import zipfile
from fastapi import FastAPI, Request
from dotenv import load_dotenv
from github import Github, GithubIntegration
load_dotenv()

app_id = os.getenv('APP_ID')
# Read the bot certificate
with open(
        os.path.normpath(os.path.expanduser(os.getenv('PRIVATE_KEY_PATH'))),
        'r'
) as cert_file:
    app_key = cert_file.read()

app = FastAPI()


# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)


@app.post("/")
async def read_root(request: Request):
    json = await request.json()
    event = json['event']
    if event == 'installation':
        payload = json['payload']
        return "installation"
    if event == 'workflow_run':
        payload = json['payload']
        if payload['action'] != 'completed':
            return "Workflow to be run"
        owner = payload['repository']['owner']['login']
        repo_name = payload['repository']['name']
        workflow_run_id = int(payload['workflow_run']['id'])
        token = git_integration.get_access_token(
                git_integration.get_installation(owner, repo_name).id
                ).token
        git_connection = Github(
            login_or_token=token
            )
        repo = git_connection.get_repo(f"{owner}/{repo_name}")
        workflow_run = repo.get_workflow_run(workflow_run_id)   
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github.v3+json',
        }
        response = requests.get(workflow_run.logs_url, headers=headers)
        if response.status_code == 200:
            zip_file_path = os.path.join(os.getcwd(), 'tmp', f'{owner}/{repo_name}', 
                                         str(workflow_run_id), 'log.zip')
            return download_log_file(response.content, zip_file_path)
        else:
            return {"error": f"Failed to fetch logs, status code: {response.status_code}"}
    return "ok"

def download_log_file(content, zip_file_path):
    os.makedirs(os.path.dirname(zip_file_path), exist_ok=True)
    log_folder_path = os.path.dirname(zip_file_path)
    with open(zip_file_path, 'wb') as zip_file:
        zip_file.write(content)
    
    # Unzip the file
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        zip_ref.extractall(log_folder_path)
    
    os.remove(zip_file_path)
    
    return {
        "message": "Logs saved and extracted successfully",
        "logs_path": log_folder_path
    }
