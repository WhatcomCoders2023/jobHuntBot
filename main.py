import os
from datetime import datetime
from parser.GitHubService import GitHubService 
from parser.GithubTableMarkdownParser import GithubTableMarkdownParser
from parser.FileHandler import FileHandler
from FireStoreService import FireStoreService
from bot import JobHuntingBot
from dotenv import load_dotenv
from google.cloud import secretmanager
from constants import REPO_NAMES, DUMMY_FILENAME

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

    for repo_name in REPO_NAMES:
        # 2. fetch job postings from github repo and update datebase
        github_service = GitHubService(github_token, repo_name, db)
        latest_jobs_contents = github_service.get_job_posting()
        if latest_jobs_contents:
            updates = '\n'.join(latest_jobs_contents)
            # 3. save the job postings to file
            FileHandler.save_latest_update_into_file(filename=DUMMY_FILENAME, updates=updates)

            # 3. parse job postings from file to make JobPosting objects
            # reav_nail_parser = GithubTableMarkdownParser(DUMMY_FILENAME)
            # job_postings = reav_nail_parser.parse()

            # 4. give parsed info to bot to report
            channel_id = int(os.getenv("WHATCOM_CHANNEL_ID")) #TODO figure out why doesn't work in prod
            #channel_id = int(os.getenv("TEST_CHANNEL_ID")) #TODO figure out why doesn't work in prod
            job_hunting_bot = JobHuntingBot(DUMMY_FILENAME, channel_id)
            job_hunting_bot.run(bot_token)

    
# if __name__ == '__main__':
#     main("", "")