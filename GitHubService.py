import github
from github import Github, Auth


class GitHubService:
    def __init__(self, token, repo_name):
        auth = Auth.Token(token)
        self.github = Github(auth=auth)
        self.repo = self.github.get_repo(f'{repo_name}')
        self.last_fetched_SHA = ''

    def get_latest_commit(self,branch_name='main') -> github.Commit.Commit:
        branch = self.repo.get_branch(branch_name)
        latest_commit = self.repo.get_commit(sha=branch.commit.sha)

        print(f"Latest Commit SHA: {latest_commit.sha}")
        print(f"Commit Message:{latest_commit.commit.message}")
        print(f"Changes made:{latest_commit.files[0].patch}")

        return latest_commit
    
    # check if the commit just fetched is exactly the same as the previous one. If the same, then don't use it again
    def compare_commits(self, current: github.Commit.Commit) -> bool:
        if current.sha == self.last_fetched_SHA:
            return False
        else:
            self.last_fetched_SHA = current.sha
            return True
        
    def parse_job_info_from_latest_commit(self):
        latest_commit = self.get_latest_commit()
        changes = latest_commit.files[0].patch
        print(changes)

    
    
    


