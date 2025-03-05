import os
import zipfile
import logging
import requests
from fastapi import FastAPI, Request, Response, status
from dotenv import load_dotenv
from github import Github, GithubIntegration
from src.llama_agent import Agent  # Fix the import statement
logger = logging.getLogger(__name__)
load_dotenv()

app_id = os.getenv('APP_ID')
# Read the bot certificate
with open(
        os.path.normpath(os.path.expanduser(os.getenv('PRIVATE_KEY_PATH'))),
        'r', encoding='utf-8'
) as cert_file:
    app_key = cert_file.read()

app = FastAPI()


# Create an GitHub integration instance
git_integration = GithubIntegration(
    app_id,
    app_key,
)

# Create an agent instance
agent = Agent()


@app.post("/", status_code=status.HTTP_200_OK)
async def read_root(request: Request, response: Response):
    """
    Handle GitHub webhook events.

    Args:
        request (Request): The incoming request object.
        response (Response): The response object to set status codes.

    Returns:
        str: A message indicating the result of the event handling.
    """
    if not request.headers.get('X-GitHub-Event'):
        logger.warning("No GitHub event received. Headers: %s",
                       request.headers)
        response.status_code = status.HTTP_400_BAD_REQUEST
        return "No GitHub event received"
    event = request.headers['X-GitHub-Event']
    payload = await request.json()
    logger.info("Received event: %s", event)
    if event == 'installation':
        if payload['action'] == 'created':
            client_id = payload['client_id']
            logger.info("Installation created with client_id: %s", client_id)
            return "Install success! You can now use the app"
        if payload['action'] == 'deleted':
            client_id = payload['client_id']
            logger.info("Installation removed with client_id: %s", client_id)
            return "Uninstall success!"
    if event == 'workflow_run':
        conclusion = payload['workflow_run']['conclusion']
        workflow_event = payload['workflow_run']['event']
        workflow_run_id = int(payload['workflow_run']['id'])
        action = payload['action']
        logger.info("Workflow run id: %s, event: %s, status: %s, conclusion: %s",
                    workflow_run_id, workflow_event, action, conclusion)
        if workflow_event == 'pull_request':
            pull_request_id = payload['workflow_run']['pull_requests'][0]['number']
            logger.debug("Pull request: %s", pull_request_id)
            if action != 'completed':
                logger.debug("Workflow to be run")
                return "Workflow to be run"
            if conclusion == 'cancelled':
                logger.debug("Workflow is cancelled")
                return "Workflow is cancelled"
            if conclusion == 'failure':
                owner = payload['repository']['owner']['login']
                repo_name = payload['repository']['name']
                installation = git_integration.get_repo_installation(
                    owner, repo_name)
                if installation is None:
                    logger.error(
                        "Installation not found for %s/%s", owner, repo_name)
                    response.status_code = status.HTTP_401_UNAUTHORIZED
                    return {"error": f"Installation not found for {owner}/{repo_name}"}
                token = git_integration.get_access_token(
                    git_integration.get_repo_installation(owner, repo_name).id
                ).token
                git_connection = Github(
                    login_or_token=token
                )
                repo = git_connection.get_repo(f"{owner}/{repo_name}")
                pr = repo.get_pull(pull_request_id)
                workflow_run = repo.get_workflow_run(workflow_run_id)
                headers = {
                    'Authorization': f'Bearer {token}',
                    'Accept': 'application/vnd.github.v3+json',
                }
                response = requests.get(
                    workflow_run.logs_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    zip_file_path = os.path.join(os.getcwd(), 'tmp', f'{owner}/{repo_name}',
                                                 str(workflow_run_id), 'log.zip')
                    rst = download_log_file(response.content, zip_file_path)
                    folder_path = rst['logs_path']
                    logger.debug("Logs saved and extracted successfully at %s",
                                 folder_path)
                    response = agent.check_logs(folder_path)
                    response_status = response.status
                    error_info = response.error_info
                    pr.create_issue_comment(
                        f"## DevOps AI Agent\n\n"
                        f"Logs are checked and here is the status: {response_status}\n\n"
                        f"Error info: {error_info}"
                    )
                    logger.debug("Analysis status: %s, error info: %s",
                                 response_status, error_info)
                else:
                    response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
                    logger.error("Failed to fetch logs, status code: %s",
                                 response.status_code)
                    return {"error": f"Failed to fetch logs, status code: {response.status_code}"}
    return "ok"


def download_log_file(content, zip_file_path):
    """
    Download the log file and extract it.
    """
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
