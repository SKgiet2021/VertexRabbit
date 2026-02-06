
import logging
from github import Github, GithubIntegration

from app.core.config import settings

logger = logging.getLogger("github_client")

class GitHubClient:
    def __init__(self):
        # For now, using Personal Access Token or App ID
        # Ideally we use App Integration, but starting simple
        self.g = None
        if settings.GITHUB_PRIVATE_KEY and settings.GITHUB_APP_ID:
            # App Auth (Robust)
            self.integration = GithubIntegration(
                settings.GITHUB_APP_ID,
                settings.GITHUB_PRIVATE_KEY
            )
        else:
            # Fallback (for testing)
            self.g = Github() 

    def get_token(self, installation_id: int):
        """Get access token for a specific installation"""
        if hasattr(self, 'integration'):
            return self.integration.get_access_token(installation_id).token
        return None

    def get_pr_diff(self, repo_full_name: str, pr_number: int, installation_id: int = None) -> str:
        """Fetches the raw diff of a Pull Request"""
        try:
            # Authenticate
            gh = self.g
            if installation_id and hasattr(self, 'integration'):
                token = self.get_token(installation_id)
                gh = Github(login_or_token=token)
            
            if not gh:
                raise ValueError("GitHub Client not configured/authenticated")

            repo = gh.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            
            # Get Diff URL content
             # PyGithub doesn't fetch raw diff easily via get_pull, 
             # usually requires requests with Accept header.
             # Simplified approach: Use requests with the token
            import requests
            headers = {
                "Authorization": f"token {gh.get_oauth_application_token().token}" if not installation_id else f"token {token}",
                "Accept": "application/vnd.github.v3.diff"
            }
            # Note: PyGithub objects allow getting the diff_url
            response = requests.get(pr.diff_url, headers=headers)
            response.raise_for_status()
            return response.text

        except Exception as e:
            logger.error(f"Failed to fetch PR diff: {e}")
            raise
    
    def post_comment(self, repo_full_name: str, pr_number: int, body: str, installation_id: int = None):
        """Posts a general review comment on the PR"""
        try:
             # Authenticate
            gh = self.g
            if installation_id and hasattr(self, 'integration'):
                token = self.get_token(installation_id)
                gh = Github(login_or_token=token)

            repo = gh.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            pr.create_issue_comment(body)
            logger.info(f"Comment posted on {repo_full_name}#{pr_number}")

        except Exception as e:
            logger.error(f"Failed to post comment: {e}")
            raise

    def post_inline_review(self, repo_full_name: str, pr_number: int, comments: list, installation_id: int = None):
        """
        Posts inline review comments on specific lines.
        
        comments: list of dicts with keys:
            - path: file path (e.g., "src/main.py")
            - line: line number in the diff
            - body: comment text
        """
        try:
            gh = self.g
            if installation_id and hasattr(self, 'integration'):
                token = self.get_token(installation_id)
                gh = Github(login_or_token=token)

            repo = gh.get_repo(repo_full_name)
            pr = repo.get_pull(pr_number)
            
            # Get the latest commit SHA (required for review comments)
            commit = pr.get_commits().reversed[0]
            
            # Create review with inline comments
            pr.create_review(
                commit=commit,
                body="## 🐰 VertexRabbit Review",
                event="COMMENT",
                comments=[
                    {
                        "path": c.get("path"),
                        "line": c.get("line"),  # Line in the new file
                        "body": c.get("body")
                    }
                    for c in comments if c.get("path") and c.get("line")
                ]
            )
            logger.info(f"Inline review posted on {repo_full_name}#{pr_number} with {len(comments)} comments")

        except Exception as e:
            logger.error(f"Failed to post inline review: {e}")
            # Fallback to regular comment
            fallback_body = "## 🐰 VertexRabbit Review\n\n"
            for c in comments:
                fallback_body += f"**{c.get('path')}:{c.get('line')}** - {c.get('body')}\n\n"
            self.post_comment(repo_full_name, pr_number, fallback_body, installation_id)

            self.post_comment(repo_full_name, pr_number, fallback_body, installation_id)

    def create_issue(self, repo_full_name: str, title: str, body: str, labels: list = None, installation_id: int = None):
        """Creates a GitHub Issue in the repository"""
        try:
            gh = self.g
            if installation_id and hasattr(self, 'integration'):
                token = self.get_token(installation_id)
                gh = Github(login_or_token=token)

            repo = gh.get_repo(repo_full_name)
            issue = repo.create_issue(
                title=title,
                body=body,
                labels=labels or []
            )
            logger.info(f"Created Issue #{issue.number}: {title}")
            return issue.number

        except Exception as e:
            logger.error(f"Failed to create issue: {e}")
            return None
