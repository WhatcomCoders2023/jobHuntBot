import github
from typing import List
from constants import REPO_NAME_TO_DOC_ID

class JobCommitExtractor:
    """
    check if there're jobs in the commits
    filter commits that have jobs
    extract job content from commits
    """

    def __init__(self, logger):
        self.logger = logger

   
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

    def extract_new_job_content_from_commits(
        self, latest_commits_with_job_postings: List[github.Commit.Commit]
    ) -> List[str]:
        """
        @param: list of commits that has job_postings
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
