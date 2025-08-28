from github import Github
from github.GithubException import UnknownObjectException

class GitHubManager:
    def __init__(self, pat):
        if not pat:
            raise ValueError("GitHub Personal Access Token is required.")
        self.github = Github(pat)

    def list_repos(self):
        """Lists the user's repositories."""
        try:
            repos = self.github.get_user().get_repos()
            return [repo.full_name for repo in repos]
        except Exception as e:
            return f"Error listing repositories: {e}"

    def create_issue(self, repo_full_name, title, body=""):
        """Creates an issue in a repository."""
        try:
            repo = self.github.get_repo(repo_full_name)
            issue = repo.create_issue(title=title, body=body)
            return f"Successfully created issue #{issue.number} in {repo_full_name}."
        except UnknownObjectException:
            return f"Error: Repository '{repo_full_name}' not found or you don't have access."
        except Exception as e:
            return f"Error creating issue: {e}"
