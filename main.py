import warnings
warnings.filterwarnings("ignore")

import os
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# ─────────────────────────────────────────────
# FASTAPI SETUP
# ─────────────────────────────────────────────
app = FastAPI(title="AI Code Reviewer", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="static"), name="static")

# ─────────────────────────────────────────────
# LLM
# ─────────────────────────────────────────────
llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY"),
    model=os.getenv("GROQ_MODEL", "openai/gpt-oss-120b"),
    temperature=0.1
)

# ─────────────────────────────────────────────
# PYDANTIC MODEL
# ─────────────────────────────────────────────
class ReviewRequest(BaseModel):
    code    : str
    language: str = "python"


# ─────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────
class State(TypedDict):
    messages        : Annotated[list, add_messages]
    code            : str
    language        : str
    security_review : str
    quality_review  : str
    docs_review     : str
    final_report    : str
    fix_suggestion  : str


# ─────────────────────────────────────────────
# AGENT 1 — SECURITY REVIEWER
# finds security vulnerabilities
# ─────────────────────────────────────────────

def security_agent(state: State):
    """
    Reviews code for security issues:
    → SQL injection
    → hardcoded passwords/API keys
    → unsafe eval() usage
    → unvalidated inputs
    → exposed sensitive data
    """
    code     = state["code"]
    language = state["language"]

    response = llm.invoke([
        SystemMessage(content=f"""You are an expert security code reviewer.
        Review the {language} code for security vulnerabilities.

        Check for:
        1. Hardcoded passwords, API keys, or secrets
        2. SQL injection vulnerabilities
        3. Unsafe use of eval() or exec()
        4. Unvalidated or unsanitized user inputs
        5. Exposed sensitive data
        6. Insecure random number generation
        7. Missing authentication or authorization
        8. Unsafe file operations

        Format your response as:
        🔴 CRITICAL: (if any critical issues)
        🟡 WARNING: (if any warnings)
        🟢 GOOD: (what is done well security-wise)
        📋 RECOMMENDATIONS: (specific fixes)

        Be specific — mention line numbers or variable names when possible.
        If no issues found say "No security issues found ✅" """),
        HumanMessage(content=f"Review this code:\n\n```{language}\n{code}\n```")
    ])

    # Clean thinking tags
    review = response.content
    if "<think>" in review:
        review = review.split("</think>")[-1].strip()

    print("   ✅ Security review complete")
    return {"security_review": review}


# ─────────────────────────────────────────────
# AGENT 2 — QUALITY REVIEWER
# checks code quality and best practices
# ─────────────────────────────────────────────

def quality_agent(state: State):
    """
    Reviews code for quality issues:
    → code structure and readability
    → naming conventions
    → error handling
    → performance issues
    → code duplication
    """
    code     = state["code"]
    language = state["language"]

    response = llm.invoke([
        SystemMessage(content=f"""You are an expert code quality reviewer.
        Review the {language} code for quality and best practices.

        Check for:
        1. Naming conventions (variables, functions, classes)
        2. Code readability and clarity
        3. Error handling and exception management
        4. Code duplication (DRY principle)
        5. Function length and complexity
        6. Proper use of data structures
        7. Performance issues or inefficiencies
        8. Magic numbers or hardcoded values

        Format your response as:
        🔴 ISSUES: (critical quality problems)
        🟡 IMPROVEMENTS: (suggested improvements)
        🟢 STRENGTHS: (what is done well)
        📋 REFACTORING SUGGESTIONS: (specific code improvements)

        Be specific with examples of better code where possible.
        If code is good quality say "Code quality is good ✅" """),
        HumanMessage(content=f"Review this code:\n\n```{language}\n{code}\n```")
    ])

    review = response.content
    if "<think>" in review:
        review = review.split("</think>")[-1].strip()

    print("   ✅ Quality review complete")
    return {"quality_review": review}


# ─────────────────────────────────────────────
# AGENT 3 — DOCS REVIEWER
# checks documentation and comments
# ─────────────────────────────────────────────

def docs_agent(state: State):
    """
    Reviews code documentation:
    → function docstrings
    → inline comments
    → README worthiness
    → type hints
    """
    code     = state["code"]
    language = state["language"]

    response = llm.invoke([
        SystemMessage(content=f"""You are an expert documentation reviewer.
        Review the {language} code for documentation quality.

        Check for:
        1. Missing or incomplete docstrings
        2. Missing type hints (for Python)
        3. Unclear or missing inline comments
        4. Function/class purpose not documented
        5. Parameter descriptions missing
        6. Return value not documented
        7. Complex logic without explanation

        Format your response as:
        🔴 MISSING: (critical missing documentation)
        🟡 INCOMPLETE: (documentation that needs improvement)
        🟢 GOOD: (well documented parts)
        📋 SUGGESTIONS: (with example docstrings/comments)

        Provide example docstrings for undocumented functions.
        If documentation is good say "Documentation is good ✅" """),
        HumanMessage(content=f"Review this code:\n\n```{language}\n{code}\n```")
    ])

    review = response.content
    if "<think>" in review:
        review = review.split("</think>")[-1].strip()

    print("   ✅ Documentation review complete")
    return {"docs_review": review}


# ─────────────────────────────────────────────
# FINAL REPORT GENERATOR
# combines all 3 reviews into one report
# ─────────────────────────────────────────────

def report_generator(state: State):
    """
    Takes all 3 reviews and generates
    a final comprehensive report with
    overall score and priority fixes
    """
    security = state["security_review"]
    quality  = state["quality_review"]
    docs     = state["docs_review"]
    language = state["language"]

    response = llm.invoke([
        SystemMessage(content=f"""You are a senior {language} developer.
        You have received 3 separate code reviews.
        Create a final comprehensive report.

        Your report must include:

        ## 📊 Overall Score
        Give a score out of 10 for:
        - Security: X/10
        - Code Quality: X/10
        - Documentation: X/10
        - Overall: X/10

        ## 🚨 Priority Fixes (do these first)
        List the top 3 most important things to fix

        ## 📋 Complete Review Summary
        Summarise each review section clearly

        ## ✅ What's Good
        Highlight positive aspects

        ## 🗺️ Action Plan
        Step by step what to improve

        Keep it professional and actionable."""),
        HumanMessage(content=f"""Security Review:
{security}

Quality Review:
{quality}

Documentation Review:
{docs}

Generate the final report.""")
    ])

    report = response.content
    if "<think>" in report:
        report = report.split("</think>")[-1].strip()

    print("   ✅ Final report generated")
    return {"final_report": report}



# ─────────────────────────────────────────────
# AGENT 4 — FIX SUGGESTER
# reads all reviews and rewrites fixed code
# ─────────────────────────────────────────────

def fix_agent(state: State):
    """
    Reads all 3 reviews and produces:
    1. Fixed version of the code
    2. Explanation of each change made
    """
    code     = state["code"]
    language = state["language"]
    security = state["security_review"]
    quality  = state["quality_review"]
    docs     = state["docs_review"]

    response = llm.invoke([
        SystemMessage(content=f"""You are an expert {language} developer.
        You have received code reviews from 3 specialists.
        Your job is to rewrite the code fixing ALL identified issues.

        Rules:
        1. Fix ALL security vulnerabilities
        2. Fix ALL quality issues
        3. Add missing documentation and type hints
        4. Keep the same logic and functionality
        5. Add comments explaining what you changed

        Your response must have exactly 2 sections:

        ## ✅ Fixed Code
```{language}
        (the complete fixed code here)
```

        ## 📝 Changes Made
        List every change you made and why:
        - Change 1: what → why
        - Change 2: what → why
        (and so on)"""),
        HumanMessage(content=f"""Original Code:
```{language}
{code}
```

Security Issues Found:
{security}

Quality Issues Found:
{quality}

Documentation Issues Found:
{docs}

Now rewrite the complete fixed code.""")
    ])

    fix = response.content
    if "<think>" in fix:
        fix = fix.split("</think>")[-1].strip()

    print("   ✅ Fix suggestions generated")
    return {"fix_suggestion": fix}



# ─────────────────────────────────────────────
# BUILD GRAPH
# ─────────────────────────────────────────────

graph_builder = StateGraph(State)

# Add all nodes
graph_builder.add_node("security_agent",  security_agent)
graph_builder.add_node("quality_agent",   quality_agent)
graph_builder.add_node("docs_agent",      docs_agent)
graph_builder.add_node("report_generator",report_generator)
graph_builder.add_node("fix_agent",        fix_agent)

# Entry point — start with security
graph_builder.set_entry_point("security_agent")

# Security → Quality → Docs → Report
# sequential execution
graph_builder.add_edge("security_agent",  "quality_agent")
graph_builder.add_edge("quality_agent",   "docs_agent")
graph_builder.add_edge("docs_agent",      "report_generator")
graph_builder.add_edge("report_generator", "fix_agent")
graph_builder.add_edge("fix_agent", END)

# Compile
graph = graph_builder.compile()


# ─────────────────────────────────────────────
# RUN REVIEW
# ─────────────────────────────────────────────

def run_review(code: str, language: str) -> dict:
    """Run all 3 agents and return complete review"""

    print(f"\n🔍 Starting code review...")
    print(f"   Language: {language}")
    print(f"   Code length: {len(code)} characters")

    result = graph.invoke({
        "messages"       : [HumanMessage(content=code)],
        "code"           : code,
        "language"       : language,
        "security_review": "",
        "quality_review" : "",
        "docs_review"    : "",
        "final_report"   : "",
        "fix_suggestion" : ""
    })

    return {
        "security_review": result["security_review"],
        "quality_review" : result["quality_review"],
        "docs_review"    : result["docs_review"],
        "final_report"   : result["final_report"],
        "fix_suggestion" : result["fix_suggestion"]
    }


# ─────────────────────────────────────────────
# FASTAPI ROUTES
# ─────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def home():
    with open("templates/index.html", "r") as f:
        return f.read()


@app.post("/review")
async def review(request: ReviewRequest):
    """
    Receives code from browser
    Runs 3 LangGraph agents
    Returns complete review
    """
    if not request.code.strip():
        return {"error": "Please paste some code to review."}

    if len(request.code) > 10000:
        return {"error": "Code too long. Please keep under 10000 characters."}

    try:
        result = run_review(request.code, request.language)
        return result
    except Exception as e:
        return {"error": f"Review failed: {str(e)}"}


@app.get("/status")
async def status():
    return {"status": "running", "agents": ["security", "quality", "docs"]}


# ─────────────────────────────────────────────
# RUN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8001))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)