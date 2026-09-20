// ── REVIEW CODE ───────────────────────────────
async function reviewCode() {
    const code     = document.getElementById("code-input").value.trim()
    const language = document.getElementById("language-select").value
    const btn      = document.getElementById("review-btn")

    if (!code) {
        alert("Please paste some code first.")
        return
    }

    btn.disabled    = true
    btn.textContent = "⏳ Reviewing..."

    resetAgentStatus()

    // Show all 4 agents running
    setAgentStatus("security", "running", "reviewing...")
    setTimeout(() => setAgentStatus("quality", "running", "reviewing..."), 500)
    setTimeout(() => setAgentStatus("docs",    "running", "reviewing..."), 1000)
    setTimeout(() => setAgentStatus("fix",     "running", "generating fix..."), 1500)

    showTab("report")
    setTabContent("report",   "<div class='placeholder'><span class='placeholder-icon'>⏳</span><p>Generating report...</p></div>")
    setTabContent("security", "<div class='placeholder'><span class='placeholder-icon'>⏳</span><p>Analysing security...</p></div>")
    setTabContent("quality",  "<div class='placeholder'><span class='placeholder-icon'>⏳</span><p>Checking quality...</p></div>")
    setTabContent("docs",     "<div class='placeholder'><span class='placeholder-icon'>⏳</span><p>Reviewing docs...</p></div>")
    setTabContent("fix",      "<div class='placeholder'><span class='placeholder-icon'>⏳</span><p>Generating fixed code...</p></div>")

    try {
        const response = await fetch("/review", {
            method : "POST",
            headers: { "Content-Type": "application/json" },
            body   : JSON.stringify({ code: code, language: language })
        })

        const data = await response.json()

        if (data.error) {
            setTabContent("report", `<div class='review-content'>❌ ${data.error}</div>`)
            resetAgentStatus()
        } else {
            // Mark all agents done
            setAgentStatus("security", "done", "done ✅")
            setAgentStatus("quality",  "done", "done ✅")
            setAgentStatus("docs",     "done", "done ✅")
            setAgentStatus("fix",      "done", "done ✅")

            // Fill all tabs
            setTabContent("report",   `<div class='review-content'>${formatText(data.final_report)}</div>`)
            setTabContent("security", `<div class='review-content'>${formatText(data.security_review)}</div>`)
            setTabContent("quality",  `<div class='review-content'>${formatText(data.quality_review)}</div>`)
            setTabContent("docs",     `<div class='review-content'>${formatText(data.docs_review)}</div>`)
            setTabContent("fix",      `<div class='review-content'>${formatText(data.fix_suggestion)}</div>`)
        }

    } catch (error) {
        setTabContent("report", `<div class='review-content'>❌ Something went wrong. Please try again.</div>`)
        resetAgentStatus()
    }

    btn.disabled    = false
    btn.textContent = "🔍 Review Code"
}


// ── TABS ──────────────────────────────────────
function showTab(name) {
    document.querySelectorAll(".tab-content").forEach(t => t.classList.remove("active"))
    document.querySelectorAll(".tab").forEach(t => t.classList.remove("active"))
    document.getElementById(`tab-${name}`).classList.add("active")
    document.querySelectorAll(".tab").forEach(t => {
        if (t.textContent.toLowerCase().includes(name)) t.classList.add("active")
    })
}

function setTabContent(name, html) {
    document.getElementById(`tab-${name}`).innerHTML = html
}


// ── AGENT STATUS ──────────────────────────────
function setAgentStatus(agent, status, text) {
    const el    = document.getElementById(`status-${agent}`)
    const state = document.getElementById(`state-${agent}`)
    el.className    = `agent-status ${status}`
    state.textContent = text
}

function resetAgentStatus() {
    ["security", "quality", "docs", "fix"].forEach(a => {
        setAgentStatus(a, "", "waiting")
    })
}


// ── FORMAT TEXT ───────────────────────────────
function formatText(text) {
    if (!text) return ""
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/## (.*)/g, "<h3 style='color:#7c83fd;margin:15px 0 8px'>$1</h3>")
        .replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>")
        .replace(/🔴/g, "<span style='color:#e74c3c'>🔴</span>")
        .replace(/🟡/g, "<span style='color:#f39c12'>🟡</span>")
        .replace(/🟢/g, "<span style='color:#5cb85c'>🟢</span>")
        .replace(/\n/g, "<br>")
}


// ── LOAD EXAMPLE ─────────────────────────────
function loadExample() {
    const example = `import sqlite3
import os

# Database connection
password = "admin123"
secret_key = "my_secret_key_12345"

def get_user(username):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    # Vulnerable to SQL injection
    query = "SELECT * FROM users WHERE username = '" + username + "'"
    cursor.execute(query)
    return cursor.fetchone()

def calculate(x, y, operation):
    # Unsafe eval usage
    result = eval(f"{x} {operation} {y}")
    return result

def process_data(data):
    for i in range(len(data)):
        print(data[i])

def login(u, p):
    user = get_user(u)
    if user and user[2] == p:
        return True
    return False`

    document.getElementById("code-input").value = example
    updateCodeInfo()
}


// ── CODE INFO ─────────────────────────────────
function updateCodeInfo() {
    const code  = document.getElementById("code-input").value
    const chars = code.length
    const lines = code.split("\n").length
    document.getElementById("char-count").textContent = `${chars} characters`
    document.getElementById("line-count").textContent = `${lines} lines`
}

document.getElementById("code-input")
    .addEventListener("input", updateCodeInfo)