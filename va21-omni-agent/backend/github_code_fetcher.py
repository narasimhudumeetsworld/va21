from github import Github, GithubException

def fetch_repo_contents(repo_name: str, github_pat: str):
    """
    Fetches the contents of all files in a GitHub repository.

    :param repo_name: The name of the repository in "owner/repo" format.
    :param github_pat: A GitHub Personal Access Token for authentication.
    :return: A dictionary mapping file paths to their content, or None on error.
    """
    if not repo_name or not github_pat:
        print("[GitHubFetcher] Repository name or PAT is missing.")
        return None

    print(f"[GitHubFetcher] Authenticating with GitHub...")
    try:
        g = Github(github_pat)
        repo = g.get_repo(repo_name)
        print(f"[GitHubFetcher] Fetching contents for repository: {repo.full_name}")

        contents = repo.get_contents("")
        file_contents = {}

        while contents:
            file_content = contents.pop(0)
            if file_content.type == "dir":
                contents.extend(repo.get_contents(file_content.path))
            else:
                try:
                    # Only decode files that are not too large and are valid text
                    if file_content.size > 1000000: # 1MB limit
                        print(f"[GitHubFetcher] Skipping large file: {file_content.path}")
                        continue

                    decoded_content = file_content.decoded_content.decode('utf-8')
                    file_contents[file_content.path] = decoded_content
                    print(f"[GitHubFetcher] Fetched file: {file_content.path}")

                except (UnicodeDecodeError, GithubException):
                    print(f"[GitHubFetcher] Skipping non-text or problematic file: {file_content.path}")
                    continue

        return file_contents

    except GithubException as e:
        print(f"[GitHubFetcher] Error accessing repository {repo_name}: {e}")
        return None
    except Exception as e:
        print(f"[GitHubFetcher] An unexpected error occurred: {e}")
        return None

if __name__ == '__main__':
    # This is for manual testing by a developer.
    # It requires a .env file with GITHUB_PAT="your_token"
    # and changing the repo_name variable.
    try:
        from dotenv import load_dotenv
        import os
        load_dotenv()
        pat = os.getenv("GITHUB_PAT")
        repo_name = "jules-dot-ai/va21" # Example repo
        if pat and repo_name:
            all_files = fetch_repo_contents(repo_name, pat)
            if all_files:
                print(f"\nFetched {len(all_files)} files from the repository.")
                # print("First 500 chars of README.md:")
                # print(all_files.get("README.md", "README.md not found.")[:500])
        else:
            print("Please set GITHUB_PAT and repo_name for testing.")
    except ImportError:
        print("Please install python-dotenv for testing: pip install python-dotenv")
    pass
