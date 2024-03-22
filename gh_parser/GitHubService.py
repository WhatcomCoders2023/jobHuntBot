import github
from github import Github, Auth
from typing import List, Tuple
from datetime import datetime
from FireStoreService import FireStoreService
from constants import REPO_NAME_TO_DOC_ID

class GitHubService:
    def __init__(self, token: str, repo_name: str, db: FireStoreService):
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.repo_name = repo_name
        self.repo = self.github.get_repo(f'{repo_name}')
        self.db = db
        self.last_fetched_timestamp_in_db = None

    def get_latest_commit(self, branch_name='main') -> github.Commit.Commit:
        branch = self.repo.get_branch(branch_name)
        latest_commit = self.repo.get_commit(sha=branch.commit.sha)

        print(f"Latest Commit SHA: {latest_commit.sha}")
        print(f"Commit Message:{latest_commit.commit.message}")
        print(f"Changes made:{latest_commit.files[0].patch}")

        return latest_commit
    
    def get_a_commit(self,sha:str) -> github.Commit.Commit:
        return self.repo.get_commit(sha)
    
    def get_job_posting(self) -> List[str]:
        try:
            document_id = REPO_NAME_TO_DOC_ID.get(self.repo_name)
            last_fetched_timestamp_in_db = self.db.fetch_last_timestamp(document_id)
            self.last_fetched_timestamp_in_db = last_fetched_timestamp_in_db #todo - Bad but fix later
            new_commits = self.get_latest_commits_since_timestamp(last_fetched_timestamp_in_db)
            if not new_commits:
                print(f"There are no new commits since {last_fetched_timestamp_in_db}")
                return None
            
            latest_timestamp_from_new_commits = self.get_latest_timestamp_from_commits(new_commits)
            self.db.update_last_timestamp(document_id, latest_timestamp_from_new_commits) #TODO - Be aware that the discord bot could fail and the database could update

            commits_with_job_postings = self.filter_commits_with_new_jobs(new_commits)
            if not commits_with_job_postings:
                print(f"There're new commits, but not any for new jobs from {last_fetched_timestamp_in_db} to {latest_timestamp_from_new_commits}")
                return None
            
            latest_timestamp_from_commits_with_jobs = self.get_latest_timestamp_from_commits(commits_with_job_postings)

            if latest_timestamp_from_commits_with_jobs == last_fetched_timestamp_in_db:
                print(f"No new commits since {latest_timestamp_from_commits_with_jobs}")
                return None
        
            jobs_contents = self.extract_new_job_content_from_commits(commits_with_job_postings)
            
            return jobs_contents
        
        except Exception as e:
            print(f"error: {e}")
            return None
        
        # NOTE: timestamp must be in ISO8601 UTC format, no Zulu
    def get_latest_commits_since_timestamp(self, timestamp:datetime) -> List[github.Commit.Commit]:
        return self.repo.get_commits(since=timestamp)
    
    # check if the commit just fetched is exactly the same as the previous one. If the same, then don't use it again
    def compare_commits(self, current: github.Commit.Commit) -> bool:
        if current.sha == self.last_fetched_SHA:
            return False
        else:
            self.last_fetched_SHA = current.sha
            return True
    
    # TODO: this may be not correct for all cases
    def check_commit_with_new_job(self,commit:github.Commit.Commit, readme_index: int) -> bool:
        lines_added = commit.files[readme_index].additions
        lined_deleted = commit.files[readme_index].deletions
        return lines_added >= 1 and lined_deleted == 0
        
    # return only commits for new job posting
    def filter_commits_with_new_jobs(self, 
                                     new_commits: List[github.Commit.Commit],
                                     ) -> List[github.Commit.Commit]:
        filtered_commits = []
        for commit in new_commits:
            try: #todo - In the future, make it so only the commit that fails throws an exception and we skip it but the other ones keep getting processed
                readme_index = self.get_readme_index(commit)
                if readme_index >= 0 and self.check_commit_with_new_job(commit, readme_index):
                    filtered_commits.append(commit)
            except Exception as e:
                print(f"Failed to parse commit with new job: Error {e} for commit {commit} in repo {self.repo_name}")
        return filtered_commits
    
    def get_readme_index(self, commit: github.Commit.Commit) -> int:
        for i, f in enumerate(commit.files):
            if "readme.md" in f.filename.lower():
                return i
        return -1 #todo - maybe this should throw exception? I'm not sure
    
    def extract_new_job_content_from_commits(self, latest_commits_with_job_postings: List[github.Commit.Commit]) -> List[str]:
        filtered_commits_str = []
        for commit in latest_commits_with_job_postings:
            for f in commit.files: #todo - Lookup github api so that it retrieves the readme instead of looping through files
                if "readme.md" in f.filename.lower():
                    filtered_commits_str.append(f.patch)

        return filtered_commits_str
    
    # NOTE: commits list should be sorted from oldest to newest
    def get_latest_timestamp_from_commits(self,commits:List[github.Commit.Commit]) -> datetime:
        latest_commit = commits[0]
        print(f"latest timestamp from commits{latest_commit.commit.author.date}")
        return latest_commit.commit.author.date


    # 1. every period, fetch a new list of latest commits since last fetched timestamp
    # 2. filter out the bad ones: remove update, sort update, or duplicated job posting
    
    
   

                
                









    
    
    


