
import os
import shutil
import subprocess
import tempfile
import logging
import json
from contextlib import contextmanager

logger = logging.getLogger("tool_runner")

class ToolRunner:
    def __init__(self):
        pass

    @contextmanager
    def clone_repo(self, repo_url: str, branch: str = "main"):
        """
        Context manager to clone a repo to a temp dir and clean it up afterwards.
        repo_url: https://github.com/owner/repo.git
        """
        temp_dir = tempfile.mkdtemp(prefix="vertex_sast_")
        try:
            # We need to insert credentials if the repo is private
            # For this MVP, assuming public or that user has git creds helper configured
            # or we can pass the installation token in the URL: 
            # https://x-access-token:{token}@github.com/owner/repo.git
            
            logger.info(f"Cloning {repo_url} (branch: {branch}) to {temp_dir}")
            
            # Shallow clone to save bandwidth
            subprocess.run(
                ["git", "clone", "--depth", "1", "--branch", branch, repo_url, temp_dir],
                check=True,
                capture_output=True
            )
            
            yield temp_dir
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Git clone failed: {e.stderr.decode()}")
            yield None
        except Exception as e:
            logger.error(f"Error in clone_repo: {e}")
            yield None
        finally:
            # Cleanup
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
                logger.info(f"Cleaned up {temp_dir}")

    def run_bandit(self, target_dir: str):
        """
        Runs bandit on the target directory and returns list of issues.
        """
        if not target_dir:
            return []
            
        try:
            logger.info(f"Running Bandit on {target_dir}")
            
            # Run bandit outputting JSON using python -m
            # Use sys.executable to ensure we use the same python environment
            import sys
            result = subprocess.run(
                [sys.executable, "-m", "bandit", "-r", target_dir, "-f", "json"],
                capture_output=True,
                text=True
            )
            
            # Bandit returns exit code 1 if issues found, 0 if clean.
            # Only crash on system errors.
            
            output = result.stdout
            if not output:
                logger.warning("Bandit produced no output")
                return []
                
            data = json.loads(output)
            results = data.get("results", [])
            
            # Transform to our standard format
            # Bandit format: { 'filename': '...', 'line_number': 123, 'issue_text': '...', 'issue_severity': 'HIGH' }
            
            formatted_issues = []
            for item in results:
                # filename comes as absolute path from temp dir, need to relativize
                rel_path = os.path.relpath(item['filename'], target_dir)
                
                formatted_issues.append({
                    "path": rel_path.replace("\\", "/"), # Normalize for GitHub
                    "line": item['line_number'],
                    "body": f"🛡️ **Security Alert (Bandit)**: {item['issue_text']} ({item['issue_severity']} Severity)",
                    "severity": item['issue_severity'].lower()
                })
                
            logger.info(f"Bandit found {len(formatted_issues)} issues")
            return formatted_issues

        except json.JSONDecodeError:
            logger.error("Failed to parse Bandit JSON output")
            return []
        except Exception as e:
            logger.error(f"Bandit scan failed: {e}")
            return []
