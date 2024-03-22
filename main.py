import os
from datetime import datetime
from gh_parser.GitHubService import GitHubService 
from gh_parser.GithubTableMarkdownParser import GithubTableMarkdownParser
from gh_parser.FileHandler import FileHandler
from FireStoreService import FireStoreService
from bot import JobHuntingBot
from dotenv import load_dotenv
from google.cloud import secretmanager
from constants import REPO_NAMES, DUMMY_FILENAME, REPO_NAME_TO_PARSE_FLAG

load_dotenv()



def access_secrets(project_id, secret_id, version_id="latest"):
    """
    Access a secret version in Secret Manager.
    """
    # Create the Secret Manager client.
    client = secretmanager.SecretManagerServiceClient()

    # Build the resource name of the secret version.
    name = f"projects/{project_id}/secrets/{secret_id}/versions/{version_id}"

    # Access the secret version.
    response = client.access_secret_version(request={"name": name})

    # Return the payload as a string.
    return response.payload.data.decode("UTF-8")

def main(data, context):
    project_id = os.getenv('PROJECT_ID')
    github_token = access_secrets(project_id=project_id, secret_id="Min_GH_access_token")
    bot_token = access_secrets(project_id=project_id,secret_id="Job_hunting_discord_bot_token")

    # 1. fetch last timestamp from datastore
    db = FireStoreService(project_id=os.getenv('PROJECT_NAME'))

    job_postings_from_all_repo = []
    for repo_name in REPO_NAMES:
        parse_flag = REPO_NAME_TO_PARSE_FLAG.get(repo_name)
        # 2. fetch job postings from github repo and update datebase
        github_service = GitHubService(github_token, repo_name, db)
        latest_jobs_contents = github_service.get_job_posting()
        if latest_jobs_contents:
            updates = '\n'.join(latest_jobs_contents)
            FileHandler.save_latest_update_into_file(DUMMY_FILENAME, updates)
            job_service = GithubTableMarkdownParser(DUMMY_FILENAME, github_service.last_fetched_timestamp_in_db)
            job_postings = job_service.parse(parse_flag)
            if job_postings:
                job_postings_from_all_repo.extend(job_postings)

    if job_postings_from_all_repo:
        #channel_id = int(os.getenv("TEST_CHANNEL_ID")) #TODO figure out why doesn't work in prod
        channel_id = int(os.getenv("WHATCOM_CHANNEL_ID")) #TODO figure out why doesn't work in prod
        job_hunting_bot = JobHuntingBot(DUMMY_FILENAME, channel_id, job_postings_from_all_repo)
        job_hunting_bot.run(bot_token) #TODO efficiently run for multiple repos without getting stuck

    
# if __name__ == '__main__':
#     main("", "")