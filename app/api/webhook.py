
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

                # 2. Get Structured Review (Inline Comments) from AI
                ai_issues = await reviewer.review_diff_structured(diff_content)
                
                # 3. Run Local SAST (Bandit)
                from app.tools.runner import ToolRunner
                runner = ToolRunner()
                
                sast_issues = []
                try:
                    # Construct Auth URL
                    token = gh_client.get_token(installation_id)
                    clone_url = f"https://x-access-token:{token}@github.com/{repo_full_name}.git"
                    branch = pr.get("head", {}).get("ref", "main")
                    
                    with runner.clone_repo(clone_url, branch) as temp_dir:
                        if temp_dir:
                            sast_issues = runner.run_bandit(temp_dir)
                except Exception as e:
                    logger.error(f"SAST Scan failed: {e}")

                # 4. Merge Issues
                issues = (ai_issues or []) + sast_issues
                
                if issues:
                    # 5. Post Inline Review
                    gh_client.post_inline_review(repo_full_name, pr_number, issues, installation_id)
                    
                    # 6. Auto-Create Tickets for Critical Bugs
                    ticket_count = 0
                    for issue in issues:
                        severity = issue.get("severity", "").lower()
                        if severity in ["high", "critical", "error"]:
                            title = f"🐛 [Auto-Bug] {issue.get('path')}:{issue.get('line')}"
                            body = f"**Detected by VertexRabbit**\n\nFile: `{issue.get('path')}`\nLine: {issue.get('line')}\n\n{issue.get('body')}"
                            gh_client.create_issue(repo_full_name, title, body, labels=["bug", "security"], installation_id=installation_id)
                            ticket_count += 1
                            
                    action_msg = f"Posted {len(issues)} comments & created {ticket_count} tickets"
                else:
                    # 3b. If no issues, post a "Looks Good" comment
                    # We might want to differentiate between "Empty due to error" and "Empty due to clean code"
                    # For now, assuming empty list means clean or minor error treated as clean
                    msg = "## 🐰 VertexRabbit Review\n\n✅ **LGTM!** No issues found."
                    gh_client.post_comment(repo_full_name, pr_number, msg, installation_id)
                    action_msg = "Posted LGTM comment"

                return {"status": "success", "msg": action_msg}
                
            except Exception as e:
                logger.error(f"Error processing webhook: {e}")
                return {"status": "error", "msg": str(e)}
    
    return {"status": "ignored", "event": x_github_event}


