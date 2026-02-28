# backend/agent.py
import matplotlib
matplotlib.use("Agg")

from langchain_experimental.agents import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama
from dotenv import load_dotenv
from pathlib import Path
import os
import uuid

load_dotenv()

# =========================
# CONSTANTS
# =========================

# CSV is read-only → SAFE
CSV_PATH = Path(__file__).parent / "components" / "titanic.csv"


# =========================
# TEMP PLOT DIRECTORY
# (ONLY writable place on Vercel)
# =========================
def get_plot_dir() -> Path:
    plot_dir = Path("/tmp/plots")
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


# =========================
# MAIN CSV AGENT FUNCTION
# =========================
def csv_agent_func(question: str):
    plot_dir = get_plot_dir()
    plot_name = f"{uuid.uuid4().hex}.png"
    plot_path = plot_dir / plot_name

    # ---------- LLM SELECTION ----------
    try:
        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0,
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    except Exception:
        llm = None

    if llm is None:
        llm = ChatOllama(model="llama3")

    # ---------- CSV AGENT ----------
    agent = create_csv_agent(
        llm=llm,
        path=str(CSV_PATH),
        verbose=False,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
    )

    # ---------- PROMPT ----------
    prompt = f"""
{question}

You are working inside a LangChain CSV agent analyzing the Titanic passenger dataset.

STRICT RULES (follow exactly):

1. You may use pandas and matplotlib internally if useful.
2. If a visualization helps understanding:
   - generate an appropriate chart
   - save it EXACTLY to this path:
     {plot_path}
   - do NOT display it
3. NEVER include code blocks or formatting.
4. NEVER mention file paths or image saving.
5. Output must be plain text only.

Your response MUST start exactly with:

Final Answer:
"""

    result = agent.invoke(prompt)

    return {
        "answer": result["output"],
        # Logical path exposed to frontend (served from /tmp)
        "plot": f"/plots/{plot_name}" if plot_path.exists() else None,
    }