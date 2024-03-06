import os

from GitHubService import GitHubService 

def main():
    token = os.getenv('GITHUB_ACCESS_TOKEN')
    repo_name ='ReaVNaiL/New-Grad-2024'
    github_service = GitHubService(token,repo_name)

    github_service.parse_job_info_from_latest_commit()
    
if __name__ == '__main__':
    # run the  bot
    main()