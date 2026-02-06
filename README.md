<p align="center">
  <img src="https://img.icons8.com/fluency/96/000000/rabbit.png" alt="VertexRabbit Logo"/>
</p>

<h1 align="center">🐰 VertexRabbit</h1>

<p align="center">
  <strong>Free, Self-Hosted AI Code Reviewer</strong><br>
  <em>Your personal CodeRabbit alternative with multi-LLM support</em>
</p>

<p align="center">
  <a href="#features"><img src="https://img.shields.io/badge/AI%20Powered-🧠-purple?style=for-the-badge" alt="AI Powered"/></a>
  <a href="#providers"><img src="https://img.shields.io/badge/4%20Providers-🔄-blue?style=for-the-badge" alt="Multi Provider"/></a>
  <a href="#installation"><img src="https://img.shields.io/badge/Self%20Hosted-🏠-green?style=for-the-badge" alt="Self Hosted"/></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="MIT License"/></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.9+-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/GitHub%20App-181717?style=flat-square&logo=github&logoColor=white" alt="GitHub"/>
</p>

---

## ✨ What is VertexRabbit?

VertexRabbit is a **free, self-hosted AI code reviewer** that automatically analyzes your Pull Requests and provides intelligent feedback. Think of it as your personal [CodeRabbit](https://coderabbit.ai) that you control completely!

```
🔍 Opens PR → 🤖 AI Analyzes Code → 💬 Posts Review Comment
```

---

## 🚀 Features

<table>
<tr>
<td width="50%">

### 🛡️ Security Detection

- SQL Injection
- Hardcoded Secrets
- Path Traversal
- Command Injection
- Insecure Deserialization

</td>
<td width="50%">

### 🐛 Bug Detection

- Logic Errors
- Race Conditions
- Missing Error Handling
- Performance Issues
- Best Practice Violations

</td>
</tr>
</table>

### 📊 Beautiful Reports

```markdown
## 🐰 VertexRabbit Review

### 📊 Issues Summary

| #   | Severity | Location     | Issue                               |
| --- | -------- | ------------ | ----------------------------------- |
| 1   | Critical | auth.py:15   | SQL injection via string formatting |
| 2   | High     | config.py:23 | Hardcoded API key exposed           |

### 🔍 Detailed Analysis

**Issue #1: SQL Injection**

- Location: auth.py (Line 15)
- Problem: User input directly in query
- Fix: Use parameterized queries
```

---

## 🔌 Supported AI Providers

<table>
<tr>
<td align="center" width="25%">
<img src="https://img.icons8.com/color/48/000000/cloud.png" width="40"/><br>
<strong>FeatherLabs</strong><br>
<code>glm-4.7</code><br>
<sub>Free • High Limits</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/color/48/000000/router.png" width="40"/><br>
<strong>OpenRouter</strong><br>
<code>deepseek-v3</code><br>
<sub>300+ Models</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/color/48/000000/lightning-bolt.png" width="40"/><br>
<strong>Groq</strong><br>
<code>llama-3.3-70b</code><br>
<sub>Ultra Fast</sub>
</td>
<td align="center" width="25%">
<img src="https://img.icons8.com/color/48/000000/infinity.png" width="40"/><br>
<strong>A4F</strong><br>
<code>claude-opus-4.5</code><br>
<sub>Most Powerful</sub>
</td>
</tr>
</table>

---

## 📦 Installation

### 1️⃣ Clone & Install

```bash
git clone https://github.com/SKgiet2021/VertexRabbit.git
cd VertexRabbit
pip install -r requirements.txt
```

### 2️⃣ Configure Environment

Copy `.env.example` to `.env` and fill in your keys:

```bash
# Choose your AI provider
AI_PROVIDER=featherlabs  # or: openrouter, groq, a4f

# Provider API Keys (get your own at each provider)
FEATHERLABS_API_KEY=your_key_here
OPENROUTER_API_KEY=your_key_here
GROQ_API_KEY=your_key_here
A4F_API_KEY=your_key_here

# GitHub App (create at github.com/settings/apps)
GITHUB_APP_ID=your_app_id
GITHUB_PRIVATE_KEY_PATH=/path/to/private-key.pem
GITHUB_WEBHOOK_SECRET=your_webhook_secret
```

### 3️⃣ Create GitHub App

1. Go to **GitHub Settings** → **Developer Settings** → **GitHub Apps**
2. Create new app with these permissions:
   - **Pull Requests**: Read & Write
   - **Contents**: Read
3. Subscribe to webhook events:
   - `pull_request`
4. Generate and download private key
5. Install app on your repositories

### 4️⃣ Run the Server

```bash
# Start the server
python -m uvicorn app.main:app --reload --port 8001

# Expose via Cloudflare Tunnel (for GitHub webhooks)
cloudflared tunnel --url http://127.0.0.1:8001
```

### 5️⃣ Configure Webhook

Copy your Cloudflare tunnel URL and paste it as your GitHub App webhook URL:

```
https://your-tunnel-url.trycloudflare.com/api/v1/webhook
```

---

## 🎮 Usage

Once configured, VertexRabbit works automatically:

1. **Create a Pull Request** in any installed repository
2. **Wait ~30 seconds** for AI analysis
3. **See the review** appear as a PR comment!

### 🔄 Switching Providers

Edit `.env` and change `AI_PROVIDER`:

```bash
AI_PROVIDER=groq  # Ultra-fast with Llama
AI_PROVIDER=a4f   # Most powerful with Claude Opus
```

Then restart the server.

---

## 📁 Project Structure

```
VertexRabbit/
├── app/
│   ├── api/
│   │   └── webhook.py      # GitHub webhook handler
│   ├── ai/
│   │   └── reviewer.py     # Multi-provider AI reviewer
│   ├── github/
│   │   └── client.py       # GitHub API client
│   └── core/
│       └── config.py       # Multi-provider configuration
├── .env.example            # Environment template
├── requirements.txt        # Python dependencies
└── README.md
```

---

## 🆚 VertexRabbit vs CodeRabbit

| Feature            | CodeRabbit |  VertexRabbit  |
| ------------------ | :--------: | :------------: |
| PR Reviews         |     ✅     |       ✅       |
| Security Detection |     ✅     |       ✅       |
| Multi-LLM          |     ✅     | ✅ 4 providers |
| Self-Hosted        |     ❌     |       ✅       |
| **Price**          |  **$$$**   |    **FREE**    |

---

## 🛠️ Tech Stack

- **Backend**: FastAPI + Python 3.9+
- **AI**: OpenAI SDK (compatible with all providers)
- **GitHub**: PyGithub + GitHub App Authentication
- **Tunnel**: Cloudflare Tunnel

---

## 🤝 Contributing

PRs welcome! Feel free to:

- Add new AI providers
- Improve prompts
- Add features

SecureCloudPass = "asdade23243fc@343@"
---

## 📄 License

MIT License - Use it freely for personal or commercial projects!

---

<p align="center">
  Made with ❤️ by developers, for developers<br>
  <sub>🐰 VertexRabbit - Your AI Code Review Companion</sub>
</p>
