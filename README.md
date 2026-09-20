# 🔍 AI Code Reviewer

An intelligent multi-agent code reviewer built with **LangGraph** that analyses your code for security vulnerabilities, quality issues, documentation gaps — and automatically generates a fixed version of your code.

## 🔗 Live Demo
**[👉 Click here to try the app](<PASTE YOUR LIVE LINK HERE>)**

---

## ✨ Features

### 4 Specialist AI Agents
- 🔒 **Security Agent** — finds SQL injection, hardcoded secrets, unsafe eval, unvalidated inputs
- ⚡ **Quality Agent** — checks naming conventions, error handling, code duplication, performance
- 📚 **Docs Agent** — finds missing docstrings, type hints, inline comments
- 🔧 **Fix Agent** — rewrites your entire code fixing ALL identified issues with explanations

### Other Features
- 📊 **Overall Score** — Security, Quality, Docs scored out of 10
- 🎯 **Priority Fixes** — top 3 most important things to fix first
- 🗺️ **Action Plan** — step by step improvement guide
- 🌐 **Multi-language** — Python, JavaScript, Java, C++, TypeScript
- ⚡ **Fast** — all agents run sequentially and return in under 30 seconds

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| AI Framework | LangGraph + LangChain |
| AI Model | Groq API |
| Frontend | HTML + CSS + JavaScript |
| Deployment | Railway |

---

## 🔧 How It Works

```
User pastes code
        ↓
🔒 Security Agent reviews for vulnerabilities
        ↓
⚡ Quality Agent reviews for best practices
        ↓
📚 Docs Agent reviews for documentation
        ↓
📊 Report Generator creates final report with scores
        ↓
🔧 Fix Agent rewrites entire code with all issues fixed
        ↓
5 tabs of results returned to user
```

---

## 🚀 Run Locally

### 1. Clone the repo
```bash
git clone https://github.com/Akansh60/code-reviewer.git
cd code-reviewer
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Create a `.env` file
```
GROQ_API_KEY=your_groq_api_key_here
GROQ_MODEL=openai/gpt-oss-120b
```

Get your free Groq API key at [console.groq.com](https://console.groq.com)

### 4. Run the app
```bash
python main.py
```

### 5. Open in browser
```
http://127.0.0.1:8001
```

### 6. View API docs
```
http://127.0.0.1:8001/docs
```

---

## 📁 Project Structure

```
code-reviewer/
├── main.py              ← FastAPI + LangGraph agents
├── requirements.txt     ← Python dependencies
├── Dockerfile           ← Docker configuration
├── .gitignore           ← Git ignore rules
├── README.md            ← This file
├── templates/
│   └── index.html       ← Frontend HTML
└── static/
    ├── style.css        ← Dark theme styling
    └── script.js        ← Frontend logic
```

---

## 💡 Example — What Gets Caught

Paste this code and click Review:

```python
import sqlite3

password = "admin123"
secret_key = "my_secret_key_12345"

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def calculate(x, y, operation):
    result = eval(f"{x} {operation} {y}")
    return result

def login(u, p):
    user = get_user(u)
    if user and user[2] == p:
        return True
    return False
```

### What Each Agent Finds

```
🔒 Security Agent:
→ 🔴 Hardcoded password "admin123"
→ 🔴 Hardcoded secret key
→ 🔴 SQL injection vulnerability
→ 🔴 Unsafe eval() usage

⚡ Quality Agent:
→ 🟡 Bad variable names (u, p)
→ 🟡 No error handling
→ 🟡 No input validation

📚 Docs Agent:
→ 🔴 Missing docstrings on all functions
→ 🔴 Missing type hints
→ 🟡 No inline comments

🔧 Fix Agent:
→ Rewrites entire code
→ Fixes all issues
→ Explains every change
```

---

## 📊 Output Tabs

| Tab | Contents |
|-----|----------|
| 📊 Final Report | Overall scores + priority fixes + action plan |
| 🔒 Security | Detailed security vulnerability analysis |
| ⚡ Quality | Code quality and best practice review |
| 📚 Docs | Documentation completeness review |
| 🔧 Fixed Code | Complete rewritten code + changes explained |

---

## 🌐 Supported Languages

```
→ Python
→ JavaScript
→ Java
→ C++
→ TypeScript
```

---

## 📦 Dependencies

```
fastapi
uvicorn
groq
python-dotenv
langgraph
langchain
langchain-groq
langchain-core
```

---

## 🔑 Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `GROQ_API_KEY` | ✅ Yes | Your Groq API key |
| `GROQ_MODEL` | ✅ Yes | Groq model to use |

---

## 🌐 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Main web interface |
| POST | `/review` | Submit code for review |
| GET | `/status` | Check app status |
| GET | `/docs` | Auto API documentation |

---

## 👨‍💻 Built By

**Akansh Rastogi**
[GitHub](https://github.com/Akansh60)