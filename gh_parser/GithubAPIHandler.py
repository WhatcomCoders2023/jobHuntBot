import github
from github import Github, Auth
from typing import List
from datetime import datetime


class GithubAPIHandler:
    """
    connect to Github API using github python package
    basic Github operations
    """

    def __init__(self, logger, token: str, repo_name: str):
        self.logger = logger
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.repo_name = repo_name
        self.repo = self.github.get_repo(f"{repo_name}")
        self.last_fetched_SHA = None

    def get_latest_commit(self, branch_name="main") -> github.Commit.Commit:
        branch = self.repo.get_branch(branch_name)
        latest_commit = self.repo.get_commit(sha=branch.commit.sha)

        self.logger.info(f"Latest Commit SHA: {latest_commit.sha}")
        self.logger.info(f"Commit Message:{latest_commit.commit.message}")
        self.logger.info(f"Changes made:{latest_commit.files[0].patch}")

        return latest_commit

    def get_a_commit(self, sha: str) -> github.Commit.Commit:
        return self.repo.get_commit(sha)

    def get_latest_commits_since_timestamp(
        self, timestamp: datetime
    ) -> List[github.Commit.Commit]:
        return self.repo.get_commits(since=timestamp)

    # check if the commit just fetched is exactly the same as the previous one. If the same, then don't use it again
    def compare_commits(self, current: github.Commit.Commit) -> bool:
        if current.sha == self.last_fetched_SHA:
            return False
        else:
            self.last_fetched_SHA = current.sha
            return True

    # NOTE: commits list should be sorted from oldest to newest
    def get_latest_timestamp_from_commits(
        self, commits: List[github.Commit.Commit]
    ) -> datetime:
        """
        @param commits: list of GH commits; sorted from latest to oldest
        therefore, to get the latest timestamp, get it from the first commit in the list
        """
        latest_commit = commits[0]
        self.logger.info(
            f"Latest timestamp from commits {latest_commit.commit.author.date}"
        )
        return latest_commit.commit.author.date
