import os
from GitHubService import GitHubService 
from GithubTableMarkdownParser import GithubTableMarkdownParser

def main():
    token = os.getenv('GITHUB_ACCESS_TOKEN')
    repo_name ='ReaVNaiL/New-Grad-2024'
    github_service = GitHubService(token,repo_name)
    reav_nail_parser = GithubTableMarkdownParser('data/latest_commit_changes_multiple_roles.md')
    reav_nail_parser.parse()

    
if __name__ == '__main__':
    main()