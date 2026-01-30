# PRD: VertexRabbit - AI Code Review Tool

> A CodeRabbit-like AI code review tool powered by Vertex AI with high RPM/RPD limits.

---

## 1. Executive Summary

**VertexRabbit** is an AI-powered code review tool that integrates with GitHub/GitLab to provide automated, context-aware pull request analysis. Built on **Google Vertex AI** (Gemini models), it leverages the high rate limits (RPM/RPD) to offer fast, reliable code reviews.

### Why FeatherLabs/Vertex AI?

| Feature            | FeatherLabs (GLM)   | OpenAI/Anthropic |
| ------------------ | ------------------- | ---------------- |
| RPM (Requests/min) | **High** (1500+)    | Low (60-500)     |
| RPD (Requests/day) | **Very High**       | Limited          |
| Cost               | Free tier available | Paid only        |
| API Compatibility  | OpenAI-compatible   | Native           |

### ⚠️ Server Limitations (Important!)

| Feature               | Status               | Notes                     |
| --------------------- | -------------------- | ------------------------- |
| Text Chat             | ✅ Works             | Input and output          |
| Streaming             | ✅ Works             | Real-time responses       |
| Vision/Images         | ❌ **Not Supported** | Server is text-only       |
| Tool/Function Calling | ❌ **Not Supported** | Must simulate via prompts |
| Code embeddings       | ❌ **Not Available** | Use local embeddings      |

**This means**: VertexRabbit will be a **text-based code review bot**. No screenshot analysis, no function calling. All logic via smart prompting.

---

## 2. What is CodeRabbit?

CodeRabbit is an AI code review tool that:

1. **Analyzes PRs in real-time** when opened
2. **Provides context-aware feedback** by understanding the entire repo
3. **Suggests one-click fixes** with inline code suggestions
4. **Learns from team preferences** via reinforcement learning
5. **Integrates with GitHub/GitLab** as a bot

### Key CodeRabbit Features

| Feature               | Description                         |
| --------------------- | ----------------------------------- |
| **PR Analysis**       | Automatic review when PR is opened  |
| **Context-Aware**     | Understands cross-file dependencies |
| **Chat Interface**    | Ask questions about the code        |
| **One-Click Fixes**   | Apply suggestions instantly         |
| **Security Scanning** | Detect vulnerabilities              |
| **Auto Summaries**    | Generate PR descriptions            |
| **Learning**          | Adapts to team coding standards     |

---

## 3. VertexRabbit Feature Set

### 3.1 Core Features (MVP) — All Text-Based

| Feature                     | Priority | Feasible?        |
| --------------------------- | -------- | ---------------- |
| PR Diff Analysis            | P0       | ✅ Text input    |
| Code Review Comments        | P0       | ✅ Text output   |
| Inline Suggestions          | P0       | ✅ Text patches  |
| PR Summary Generation       | P1       | ✅ Text output   |
| Chat with Codebase          | P1       | ✅ Text chat     |
| Security Scan (rules-based) | P2       | ✅ Text patterns |

### 3.2 NOT Possible (Server Limitations)

| Feature                | Reason                    |
| ---------------------- | ------------------------- |
| Screenshot/UI Analysis | No vision API             |
| Diagram Generation     | No image output           |
| Real Tool Calling      | Must parse JSON from text |
| Multi-modal Review     | Text only                 |

---

## 4. Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     GitHub/GitLab                        │
│                         │                               │
│                    Webhook (PR opened)                   │
└─────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────┐
│                   VertexRabbit API                       │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Webhook   │  │   PR Diff   │  │   Context   │     │
│  │   Handler   │→ │   Parser    │→ │   Builder   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
│                          │                              │
│                          ▼                              │
│  ┌─────────────────────────────────────────────────┐   │
│  │              Vertex AI (Gemini)                  │   │
│  │  - gemini-2.0-flash (fast)                      │   │
│  │  - gemini-1.5-pro (quality)                     │   │
│  └─────────────────────────────────────────────────┘   │
│                          │                              │
│                          ▼                              │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │   Review    │  │   Comment   │  │   GitHub    │     │
│  │   Engine    │→ │   Formatter │→ │   API       │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

---

## 5. Technical Implementation

### 5.1 Components

| Component          | Technology                | Purpose                   |
| ------------------ | ------------------------- | ------------------------- |
| API Server         | FastAPI (Python)          | Handle webhooks, serve UI |
| Vertex AI Client   | `google-cloud-aiplatform` | LLM inference             |
| GitHub Integration | PyGithub / REST API       | Read PRs, post comments   |
| Context Store      | SQLite / Redis            | Cache repo context        |
| Queue              | Celery / async            | Handle concurrent reviews |

### 5.2 Vertex AI Configuration

```python
# models to use
MODELS = {
    "fast": "gemini-2.0-flash",      # Quick reviews
    "quality": "gemini-1.5-pro",     # Deep analysis
}

# Vertex AI has high limits
# RPM: 1500+ requests/minute
# TPM: 4M+ tokens/minute
```

### 5.3 Review Pipeline

1. **Webhook receives PR event**
2. **Fetch PR diff** from GitHub API
3. **Build context** (related files, history)
4. **Chunk diff** into reviewable sections
5. **Send to Vertex AI** with review prompt
6. **Parse response** into structured comments
7. **Post comments** to GitHub PR

---

## 6. Prompting Strategy

### System Prompt (Code Reviewer)

```
You are an expert code reviewer. Analyze the following code changes and provide:
1. Issues: bugs, security vulnerabilities, performance problems
2. Suggestions: cleaner patterns, better naming, refactoring opportunities
3. Questions: unclear intent, missing tests, edge cases

Format each finding as:
- FILE: <filename>
- LINE: <line number>
- SEVERITY: critical/warning/info
- ISSUE: <description>
- SUGGESTION: <code fix if applicable>

Be concise. Focus on actionable feedback.
```

### Context Building

```
CONTEXT:
- Repository: {repo_name}
- Branch: {branch}
- Files changed: {file_list}
- Previous PR comments: {history}
- Team coding standards: {standards}

DIFF:
{unified_diff}
```

---

## 7. Deployment Options

| Option             | Pros               | Cons           |
| ------------------ | ------------------ | -------------- |
| **Cloud Run**      | Serverless, scales | Cold starts    |
| **GKE**            | Full control       | More complex   |
| **Compute Engine** | Simple             | Manual scaling |

**Recommended**: Cloud Run with min instances = 1 (no cold starts)

---

## 8. Success Metrics

| Metric                 | Target            |
| ---------------------- | ----------------- |
| Review time per PR     | < 30 seconds      |
| False positive rate    | < 10%             |
| Issues caught          | > 70% (vs manual) |
| Developer satisfaction | > 4/5 rating      |

---

## 9. MVP Scope

### Phase 1: Basic PR Review (Week 1-2)

- [ ] GitHub webhook integration
- [ ] Diff parsing and chunking
- [ ] Vertex AI integration
- [ ] Basic review comments

### Phase 2: Enhanced Features (Week 3-4)

- [ ] PR summary generation
- [ ] Chat interface for Q&A
- [ ] Context caching (faster reviews)
- [ ] Custom rules via config file

### Phase 3: Polish (Week 5+)

- [ ] GitLab support
- [ ] Analytics dashboard
- [ ] Team settings UI
- [ ] Learning from accepted/rejected suggestions

---

## 10. Open Questions

1. **Self-hosted or SaaS?** - Deploy on user's GCP or offer hosted service?
2. **Pricing model?** - Per repo, per seat, or usage-based?
3. **GitLab support?** - Same priority as GitHub?
4. **Custom models?** - Allow users to fine-tune prompts?

---

## 11. Next Steps

1. ✅ Research CodeRabbit (done)
2. ⏳ Set up VertexAI directory structure
3. ⏳ Create GitHub App for webhook
4. ⏳ Build basic PR analysis pipeline
5. ⏳ Test with sample repositories

---

_Document created: 2026-01-29_
_Author: Antigravity AI_
