# backend/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from backend.agent import csv_agent_func
import traceback

app = FastAPI(title="Titanic Dataset Chatbot")

class Query(BaseModel):
    question: str

@app.post("/chat")
def chat(query: Query):
    try:
        result = csv_agent_func(query.question)
        return {
            "ok": True,
            "answer": result.get("answer") if isinstance(result, dict) else result,
            "plot": result.get("plot") if isinstance(result, dict) else None
        }
    except Exception as e:
        traceback.print_exc()
        return {
            "ok": False,
            "answer": "⚠️ Backend error occurred.",
            "error": str(e)
        }