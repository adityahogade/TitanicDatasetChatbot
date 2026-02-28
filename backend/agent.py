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

# ✅ CSV is read-only → safe
CSV_PATH = Path(__file__).parent / "components" / "titanic.csv"


# =========================
# SAFE TEMP DIRECTORY
# =========================
def get_plot_dir() -> Path:
    """
    Vercel allows writes ONLY inside /tmp
    """
    plot_dir = Path("/tmp/plots")
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


# =========================
# MAIN AGENT FUNCTION
# =========================
def csv_agent_func(question: str):
    plot_dir = get_plot_dir()
    plot_path = plot_dir / f"{uuid.uuid4().hex}.png"

    # ---- LLM selection ----
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

    # ---- CSV Agent ----
    agent = create_csv_agent(
        llm=llm,
        path=str(CSV_PATH),
        verbose=False,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
    )

    prompt = f"""
{question}

You are working inside a LangChain CSV agent to analyze the Titanic passenger dataset.

STRICT RULES (follow exactly):

1. You may use pandas and matplotlib internally.
2. If a visualization helps:
   - generate a chart using pandas/matplotlib
   - save it EXACTLY to this path:
     {plot_path}
   - do NOT display it
3. Do NOT include code blocks, markdown, or lists.
4. Do NOT mention file paths or image saving.
5. Output must be plain text.

Your response MUST start exactly with:

Final Answer:
"""

    result = agent.invoke(prompt)

    return {
        "answer": result["output"],
        # Optional: frontend can fetch this if needed
        "plot": str(plot_path) if plot_path.exists() else None,
    }