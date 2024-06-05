import os
from dotenv import load_dotenv
from FireStoreService import FireStoreService
from google.cloud import secretmanager

from gh_parser.GitHubService import GitHubService
from gh_parser.GithubAPIHandler import GithubAPIHandler
from gh_parser.JobCommitExtractor import JobCommitExtractor
from gh_parser.GithubTableMarkdownParser import GithubTableMarkdownParser
from gh_parser.FileHandler import FileHandler

from bot import JobHuntingBot
from constants import REPO_NAMES, DUMMY_FILENAME, REPO_NAME_TO_PARSE_FLAG
from logger import init_logger

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
    logger = init_logger()
    logger.debug("Running application...")

    project_id = os.getenv("PROJECT_ID")
    github_token = access_secrets(
        project_id=project_id, secret_id="Min_GH_access_token"
    )
    bot_token = access_secrets(
        project_id=project_id, secret_id="Job_hunting_discord_bot_token"
    )
    channel_id = int(os.getenv("WHATCOM_CHANNEL_ID"))

    if os.getenv("DEV_MODE"):
        logger.debug("Running in test env..")
        bot_token = os.getenv("DISCORD_BOT_TOKEN")
        channel_id = int(os.getenv("TEST_CHANNEL_ID"))

    # 1. initialization
    db = FireStoreService(logger, project_id=os.getenv("PROJECT_NAME"))
    job_extractor = JobCommitExtractor(logger)

    job_postings_from_all_repo = []
    for repo_name in REPO_NAMES:
        logger.info(f"Extracting from repo: {repo_name}")
        parse_flag = REPO_NAME_TO_PARSE_FLAG.get(repo_name)

        # 2. fetch job postings from github repo and update datebase
        github_api_handler = GithubAPIHandler(logger, github_token, repo_name)
        github_service = GitHubService(
            logger, repo_name, db, github_api_handler, job_extractor
        )
        latest_jobs_contents = github_service.process_job_commits()

        if latest_jobs_contents:

            updates = "\n".join(latest_jobs_contents)
            FileHandler.save_latest_update_into_file(logger, DUMMY_FILENAME, updates)
            job_service = GithubTableMarkdownParser(
                logger, DUMMY_FILENAME, github_service.last_fetched_timestamp_in_db
            )

            job_postings = job_service.parse(parse_flag)
            if job_postings:
                job_postings_from_all_repo.extend(job_postings)

    if job_postings_from_all_repo:
        job_hunting_bot = JobHuntingBot(
            logger, DUMMY_FILENAME, channel_id, job_postings_from_all_repo
        )
        # TODO efficiently run for multiple repos without getting stuck
        job_hunting_bot.run(bot_token)


if os.getenv("DEV_MODE"):
    main("", "")
