import github
from github import Github, Auth
from typing import List
from datetime import datetime
from FireStoreService import FireStoreService
from constants import REPO_NAME_TO_DOC_ID


class GitHubService:
    def __init__(self, logger, token: str, repo_name: str, db: FireStoreService):
        self.logger = logger
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.repo_name = repo_name
        self.repo = self.github.get_repo(f"{repo_name}")
        self.db = db
        self.last_fetched_timestamp_in_db = None

    def get_latest_commit(self, branch_name="main") -> github.Commit.Commit:
        branch = self.repo.get_branch(branch_name)
        latest_commit = self.repo.get_commit(sha=branch.commit.sha)

        self.logger.info(f"Latest Commit SHA: {latest_commit.sha}")
        self.logger.info(f"Commit Message:{latest_commit.commit.message}")
        self.logger.info(f"Changes made:{latest_commit.files[0].patch}")

        return latest_commit

    def get_a_commit(self, sha: str) -> github.Commit.Commit:
        return self.repo.get_commit(sha)

    def get_job_posting(self) -> List[str]:
        """
        1. from db, get last (fetched) timestamp when the GH commit was fetched
        2. get latest commits from GH repos since last fetched-timestamp
            a. there may be no new commits since last fetched timestamp
        3. however, if they're new commits, once done getting latest commit, updates the last fetched timestamp
        4. from the latest commits, find the ones that are about new jobs. There're 2 scenarios:
            a. there are new commits, but none are about new jobs
            b. the latest commits were already fetched in the previous run, aka no new commits to GH repos since last time fetched
        """

        try:
            document_id = REPO_NAME_TO_DOC_ID.get(self.repo_name)
            last_fetched_timestamp_in_db = self.db.fetch_last_timestamp(document_id)
            self.last_fetched_timestamp_in_db = (
                last_fetched_timestamp_in_db  # todo - Bad but fix later
            )

            new_commits = self.get_latest_commits_since_timestamp(
                last_fetched_timestamp_in_db
            )
            if not new_commits:
                self.logger.info(
                    f"There are no new commits since {last_fetched_timestamp_in_db}"
                )
                return None

            latest_timestamp_from_new_commits = self.get_latest_timestamp_from_commits(
                new_commits
            )
            self.db.update_last_timestamp(
                document_id, latest_timestamp_from_new_commits
            )  # TODO - Be aware that the discord bot could fail and the database could update

            commits_with_job_postings = self.filter_commits_with_new_jobs(new_commits)
            if not commits_with_job_postings:
                self.logger.info(
                    f"There're new commits, but not any for new jobs from {last_fetched_timestamp_in_db} to {latest_timestamp_from_new_commits}"
                )
                return None

            latest_timestamp_from_commits_with_jobs = (
                self.get_latest_timestamp_from_commits(commits_with_job_postings)
            )

            if latest_timestamp_from_commits_with_jobs == last_fetched_timestamp_in_db:
                self.logger.info(
                    f"No new commits since {latest_timestamp_from_commits_with_jobs}"
                )
                return None

            jobs_contents = self.extract_new_job_content_from_commits(
                commits_with_job_postings
            )

            return jobs_contents

        except Exception as e:
            self.logger.error(f"error: {e}")
            return None

        # NOTE: timestamp must be in ISO8601 UTC format, no Zulu

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

    def check_commit_with_new_job(
        self, commit: github.Commit.Commit, readme_index: int
    ) -> bool:
        """
        @returns: check if the GH commit is about adding new jobs
        - lines added: the # of additions to the readme.md file (where the job postings located)
        - lines deleted: the # of deletions to the readme.md file (where the job postings located)
            The condition to check if the a GH commit contains new job posting is:
            - # of line added >= 0 and line deleter == 0

        NOTE: this assumption may be wrong
        TODO: this may be not correct for all cases
        """
        lines_added = commit.files[readme_index].additions
        lined_deleted = commit.files[readme_index].deletions
        return lines_added >= 1 and lined_deleted == 0

    def filter_commits_with_new_jobs(
        self,
        new_commits: List[github.Commit.Commit],
    ) -> List[github.Commit.Commit]:
        """
        Returns only commits for new job posting
        """
        filtered_commits = []
        for commit in new_commits:
            try:  # TODO - In the future, make it so only the commit that fails throws an exception and we skip it but the other ones keep getting processed
                readme_index = self.get_readme_index(commit)
                if readme_index >= 0 and self.check_commit_with_new_job(
                    commit, readme_index
                ):
                    filtered_commits.append(commit)
            except Exception as e:
                self.logger.error(
                    f"Failed to parse commit with new job: Error {e} for commit {commit} in repo {self.repo_name}"
                )
        return filtered_commits

    def get_readme_index(self, commit: github.Commit.Commit) -> int:
        """
        when fetching commit from GH API, the response will return 'files', an array of files modified in a GH commit.
        @returns: This function looks for the README.md, where the job posting contents are
        https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#:~:text=%7D%0A%20%20%5D%2C-,%22files%22%3A%20%5B,-%7B%0A%20%20%20%20%20%20%22sha%22
        """
        for i, f in enumerate(commit.files):
            if "readme.md" in f.filename.lower():
                return i
        return -1  # todo - maybe this should throw exception? I'm not sure

    def extract_new_job_content_from_commits(
        self, latest_commits_with_job_postings: List[github.Commit.Commit]
    ) -> List[str]:
        """
        API doc for github commit file and patch
        - patch: what changes made to the modified file (this case README.md: where you can extract new job posting)
        https://docs.github.com/en/rest/commits/commits?apiVersion=2022-11-28#:~:text=application/vnd.github.patch%3A-,Returns%20the%20patch%20of%20the%20commit,-.%20Diffs%20with%20binary%20data%20will%20have%20no%20patch%20property.%20Larger
        """
        filtered_commits_str = []
        for commit in latest_commits_with_job_postings:
            for (
                f
            ) in (
                commit.files
            ):  # todo - Lookup github api so that it retrieves the readme instead of looping through files
                if "readme.md" in f.filename.lower():
                    filtered_commits_str.append(f.patch)

        return filtered_commits_str

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

    # 1. every period, fetch a new list of latest commits since last fetched timestamp
    # 2. filter out the bad ones: remove update, sort update, or duplicated job posting
