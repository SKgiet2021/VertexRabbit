<p align="center">
  <img src="https://img.icons8.com/fluency/96/000000/rabbit.png" alt="VertexRabbit Logo"/>
</p>

<h1 align="center">🐰 VertexRabbit</h1>

<p align="center">
  <strong>Free, Self-Hosted AI Code Reviewer</strong><br>
  <em>Pro-level features (Line-by-Line Reviews, SAST, Auto-Tickets) for free.</em>
</p>

<p align="center">
  <a href="#features"><img src="https://img.shields.io/badge/AI%20Powered-🧠-purple?style=for-the-badge" alt="AI Powered"/></a>
  <a href="#providers"><img src="https://img.shields.io/badge/Claude%203.7-🔥-orange?style=for-the-badge" alt="Claude"/></a>
  <a href="#security"><img src="https://img.shields.io/badge/SAST%20Integrated-🛡️-blue?style=for-the-badge" alt="SAST"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License"/></a>
</p>

---

## ✨ features

VertexRabbit is a **self-hosted GitHub App** that gives you **Pro-Level Code Reviews** without the subscription fee. It combines LLM intelligence with traditional security tools.

### 1. 📝 Line-by-Line Reviews

Instead of a generic summary, VertexRabbit posts **specific comments on the exact lines of code** that need attention.

- ✅ **Powered by Claude 3.7** (via A4F) for high accuracy.
- ✅ **Strict Context**: Only comments on _your changes_, not legacy code.

### 2. 🛡️ SAST Security Scanning

Every PR is automatically scanned by **Bandit** (Python Security Scanner) alongside the AI review.

- **SQL Injection**
- **Hardcoded Secrets**
- **Command Injection**
  _(These are hard-coded checks, not AI hallucinations)_

### 3. 🎫 Auto-Issue Creation

Found a **Critical Bugs**? VertexRabbit handles it:

- 🛑 If a bug matches **"HIGH" or "CRITICAL"** severity...
- 🎟️ It **automatically creates a GitHub Issue** assigned to the repo.

### 4. ⚡ Smart Rate Limiting

- Built-in **Token Bucket Limiter** (10 RPM).
- Usage of `tenacity` for smart retries.
- Never hits provider rate limits.

---

## 🛠️ Installation (Self-Hosted)

### 1️⃣ Clone & Install

```bash
git clone https://github.com/SKgiet2021/VertexRabbit.git
cd VertexRabbit
pip install -r requirements.txt
pip install bandit  # Required for SAST
```

### 2️⃣ Configure Environment

Copy `.env.example` to `.env`:

```bash
AI_PROVIDER=a4f
A4F_API_KEY=your_key
A4F_MODEL=provider-7/claude-3-7-sonnet-20250219

# GitHub App Credentials
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=vertexrabbit.private-key.pem
GITHUB_WEBHOOK_SECRET=your_secret
```

### 3️⃣ Run Server

```bash
# Windows
./start_server.ps1
```

### 4️⃣ Tunnel (for Webhooks)

```bash
cloudflared tunnel --url http://localhost:8001
```

_Copy the generated URL (e.g., `https://random.trycloudflare.com`) to your GitHub App Webhook settings._

---

## 📁 Project Structure

```
VertexRabbit/
├── app/
│   ├── ai/
│   │   └── reviewer.py     # Claude 3.7 Logic (Structured JSON)
│   ├── api/
│   │   └── webhook.py      # Handles PR events & Orchestration
│   ├── core/
│   │   └── limiter.py      # Rate Limiting (Token Bucket)
│   ├── github/
│   │   └── client.py       # GitHub API (Comments, Issues)
│   └── tools/
│       └── runner.py       # SAST Logic (Bandit)
├── start_server.ps1        # Launcher
└── requirements.txt
```

---

## 📄 License

MIT License. Free forever.

<p align="center">
  <sub>🐰 Built for Developers</sub>
</p>
