
from fastapi import APIRouter, Header, Request, HTTPException
from app.github.client import GitHubClient
from app.ai.reviewer import VertexReviewer
from app.core.config import settings
import logging

router = APIRouter()
logger = logging.getLogger("webhook")

# Initialize Services
gh_client = GitHubClient()
reviewer = VertexReviewer()

@router.post("/webhook")
async def github_webhook(request: Request, x_github_event: str = Header(...)):
    """
    Handles GitHub Webhooks. Supported Events:
    - pull_request (opened, synchronize)
    """
    payload = await request.json()
    
    if x_github_event == "ping":
        return {"msg": "Pong!"}

    if x_github_event == "pull_request":
        action = payload.get("action")
        pr = payload.get("pull_request")
        repo = payload.get("repository")
        installation = payload.get("installation")
        
        if action in ["opened", "synchronize", "reopened"]:
            pr_number = pr.get("number")
            repo_full_name = repo.get("full_name")
            installation_id = installation.get("id") if installation else None
            
            logger.info(f"Processing PR #{pr_number} in {repo_full_name}")

            try:
                # 1. Get Diff
                diff_content = gh_client.get_pr_diff(repo_full_name, pr_number, installation_id)
                
                # 2. Use detailed text review for beautiful, comprehensive output
                review_text = reviewer.review_diff(diff_content)
                
                # 3. Post as PR comment with nice formatting
                final_body = f"## 🐰 VertexRabbit Review\n\n{review_text}"
                gh_client.post_comment(repo_full_name, pr_number, final_body, installation_id)
                
                return {"status": "success", "msg": "Review posted"}
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return {"status": "error", "msg": str(e)}
    
    return {"status": "ignored", "event": x_github_event}


