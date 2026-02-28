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