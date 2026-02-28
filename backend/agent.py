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
from pathlib import Path
import tempfile

load_dotenv()

CSV_PATH = Path(__file__).parent / "components" / "titanic.csv"


PLOT_DIR = Path(tempfile.gettempdir()) / "plots"
PLOT_DIR.mkdir(parents=True, exist_ok=True)
# agent.py (LLM section only)

from langchain_google_genai import ChatGoogleGenerativeAI
import os

def get_llm():
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise RuntimeError("GOOGLE_API_KEY not set in Vercel environment")

    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0,
        google_api_key=api_key,
    )
def csv_agent_func(question: str):
    plot_path = PLOT_DIR / f"{uuid.uuid4().hex}.png"

    try:
        llm = get_llm()
    except Exception:
        llm = None

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

Your goal is to provide clear analytical insight about passengers and, when useful, visual insight.

STRICT RULES (follow exactly):

1. You may use pandas and matplotlib internally if needed to analyze passenger data.
2. If a visualization helps to understand passenger patterns or distributions:
   - generate an appropriate chart using pandas and matplotlib
   - save the figure exactly to this path:
     {plot_path}
   - do NOT display the figure
3. NEVER include code blocks, markdown, or explanations of code in your output.
4. NEVER include bullet points, lists, or special formatting.
5. NEVER mention file paths, filenames, or saving images.
6. Your final response MUST be plain text only.

Your final response MUST start exactly with:

Final Answer:

After "Final Answer:", clearly explain the passenger insight in natural language.
Include important numbers such as counts, percentages, or averages.
If a chart was generated, describe the visual insight it provides about passengers.
"""

    result = agent.invoke(prompt)

    return {
        "answer": result["output"],
        "plot": f"plots/{plot_path.name}" if plot_path.exists() else None
        }