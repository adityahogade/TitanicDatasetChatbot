# backend/agent.py
import matplotlib
matplotlib.use("Agg")

import matplotlib.pyplot as plt
from io import BytesIO
import base64
from pathlib import Path
import os

from dotenv import load_dotenv
from langchain_experimental.agents import create_csv_agent
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

# =========================
# CSV PATH (SAFE)
# =========================
CSV_PATH = Path(__file__).parent / "components" / "titanic.csv"


# =========================
# HELPER: FIGURE → BASE64
# =========================
def fig_to_base64() -> str:
    buffer = BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    plt.close()
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")


# =========================
# MAIN AGENT FUNCTION
# =========================
def csv_agent_func(question: str):
    # ---- LLM (Vercel-safe) ----
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )

    # ---- CSV Agent ----
    agent = create_csv_agent(
        llm=llm,
        path=str(CSV_PATH),
        verbose=False,
        allow_dangerous_code=True,
        handle_parsing_errors=True,
    )

    # ---- Prompt ----
    prompt = f"""
{question}

You are working inside a LangChain CSV agent to analyze the Titanic passenger dataset.

STRICT RULES (follow exactly):

1. You may use pandas and matplotlib internally.
2. ALWAYS generate ONE appropriate visualization using matplotlib
   if the question involves counts, comparisons, distributions, or groups.
3. Do NOT display the plot.
4. Do NOT mention code, file paths, or saving images.
5. Output must be plain text only.

Your final response MUST start exactly with:

Final Answer:
"""

    # ---- Run Agent ----
    result = agent.invoke(prompt)

    # ---- Capture Plot (if created) ----
    plot_base64 = None
    if plt.get_fignums():
        plot_base64 = fig_to_base64()

    return {
        "answer": result["output"],
        "plot_base64": plot_base64,
    }