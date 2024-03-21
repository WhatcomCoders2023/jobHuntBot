import github
from github import Github, Auth
from google.cloud import datastore
from typing import List, Tuple
from datetime import datetime

class GitHubService:
    def __init__(self, token: str, repo_name: str, last_timestamp_in_db: datetime):
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.repo = self.github.get_repo(f'{repo_name}')
        self.gcp_client = datastore.Client()
        self.last_fetched_timestamp = last_timestamp_in_db

    def get_latest_commit(self, branch_name='main') -> github.Commit.Commit:
        branch = self.repo.get_branch(branch_name)
        latest_commit = self.repo.get_commit(sha=branch.commit.sha)

        print(f"Latest Commit SHA: {latest_commit.sha}")
        print(f"Commit Message:{latest_commit.commit.message}")
        print(f"Changes made:{latest_commit.files[0].patch}")

        return latest_commit
    
    def get_a_commit(self,sha:str) -> github.Commit.Commit:
        return self.repo.get_commit(sha)
    
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
        
    def check_commit_with_new_job(self,commit:github.Commit.Commit) -> bool:
        lines_added = commit.files[0].additions
        lined_deleted = commit.files[0].deletions
        return lines_added >= 1 and lined_deleted == 0
        
    # return changes from commits that add new jobs
    def filter_commits_with_new_jobs(self, latest_commits: List[github.Commit.Commit]) -> List[github.Commit.Commit]:
        filtered_commits = []
        # commits_count = len(latest_commits)

        # # sort from oldest to newest
        # for i in range(commits_count-1,-1,-1):
        #     commit = latest_commits[i]
        #     if self.check_commit_with_new_job(commit=commit):
        #         filtered_commits.append(commit)
        # return filtered_commits
    
        for commit in latest_commits:
             if self.check_commit_with_new_job(commit=commit):
                filtered_commits.append(commit)
        return filtered_commits
    
    def extract_new_job_content_from_commits(self, latest_commits_with_job_postings: List[github.Commit.Commit]) -> List[str]:
        filtered_commits_str = []
        for commit in latest_commits_with_job_postings:
            filtered_commits_str.append(commit.files[0].patch)

        return filtered_commits_str
    
    def run(self) -> Tuple[List[str], str]:
        latest_commits = self.get_latest_commits_since_timestamp(self.last_fetched_timestamp)
        latest_commits_with_job_postings = self.filter_commits_with_new_jobs(latest_commits)
        latest_timestamp_from_commits =self.get_latest_timestamp_from_commits(latest_commits_with_job_postings)
        if latest_timestamp_from_commits == self.last_fetched_timestamp:
            print(f"No new jobs since {latest_timestamp_from_commits}")
            return None, None #TODO: gracefully exit entire program 
        
        latest_jobs_contents = self.extract_new_job_content_from_commits(latest_commits_with_job_postings)
        
        return latest_jobs_contents, latest_timestamp_from_commits
    
    # NOTE: commits list should be sorted from oldest to newest
    def get_latest_timestamp_from_commits(self,commits:List[github.Commit.Commit]) -> datetime:
        latest_commit = commits[0]
        print(f"latest timestamp {latest_commit.commit.author.date}")
        print(f"latest timestamp from commit type is {type(latest_commit.commit.author.date)}")
        return latest_commit.commit.author.date


    # 1. every period, fetch a new list of latest commits since last fetched timestamp
    # 2. filter out the bad ones: remove update, sort update, or duplicated job posting
    
    
   

                
                









    
    
    


