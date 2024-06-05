import github
from github import Github, Auth
from typing import List
from datetime import datetime
from FireStoreService import FireStoreService
from constants import REPO_NAME_TO_DOC_ID
from gh_parser.GithubAPIHandler import GithubAPIHandler
from gh_parser.JobCommitExtractor import JobCommitExtractor


class GitHubService:
    def __init__(
        self,
        logger,
        repo_name: str,
        db: FireStoreService,
        github_api_handler: GithubAPIHandler,
        job_extractor: JobCommitExtractor,
    ):
        self.logger = logger
        self.repo_name = repo_name
        self.github_api_handler = github_api_handler
        self.job_extractor = job_extractor
        self.db = db

    def process_job_commits(self) -> List[str]:
        """
        1. from db, get last (fetched) timestamp when the GH commit was fetched
        2. get latest commits from GH repos since last fetched-timestamp
            a. there may be no new commits since last fetched timestamp
        3. however, if they're new commits, get their latest timestamp from these new commits and update the timestamp
        4. from the new commits, extract the job postings
           a. there are new commits, but none are about new jobs
           b. the latest commits were already fetched in the previous run, aka no new commits to GH repos since last time fetched
        """
        try:
            # 1.
            document_id = REPO_NAME_TO_DOC_ID.get(self.repo_name)
            last_fetched_timestamp_in_db = self.db.fetch_last_timestamp(document_id)

            # 2.
            new_commits = self.github_api_handler.get_latest_commits_since_timestamp(
                last_fetched_timestamp_in_db
            )
            if not new_commits:
                self.logger.info(
                    f"There are no new commits since {last_fetched_timestamp_in_db}"
                )
                return None
            # 3.
            latest_timestamp_from_new_commits = (
                self.github_api_handler.get_latest_timestamp_from_commits(new_commits)
            )
            self.db.update_last_timestamp(
                document_id, latest_timestamp_from_new_commits
            )  # TODO - Be aware that the discord bot could fail and the database could update

            self.logger.debug(new_commits)
            # 4.
            commits_with_job_postings = self.job_extractor.filter_commits_with_new_jobs(
                new_commits
            )

            if not commits_with_job_postings:
                self.logger.info(
                    f"There're new commits, but not any for new jobs from {last_fetched_timestamp_in_db} to {latest_timestamp_from_new_commits}"
                )
                return None

            # TODO: this part is confusing, there are new commits for jobs, but have to check the timestamp again?
            # and why log out "no new commits " when we already checked if there new commit

            # latest_timestamp_from_commits_with_jobs = (
            #     self.github_api_handler.get_latest_timestamp_from_commits(commits_with_job_postings)
            # )

            # if latest_timestamp_from_commits_with_jobs == last_fetched_timestamp_in_db:
            #     self.logger.info(
            #         f"No new commits since {latest_timestamp_from_commits_with_jobs}"
            #     )
            #     return None

            jobs_contents = self.job_extractor.extract_new_job_content_from_commits(
                commits_with_job_postings
            )

            self.logger.info(f"New jobs found!!!")

            return jobs_contents

        except Exception as e:
            self.logger.error(f"error: {e}")
            return None

    # 1. every period, fetch a new list of latest commits since last fetched timestamp
    # 2. filter out the bad ones: remove update, sort update, or duplicated job posting
