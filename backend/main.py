from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent import csv_agent_func

app = FastAPI()

# Serve plots
app.mount("/plots", StaticFiles(directory="/tmp/plots"), name="plots")

# ✅ Request schema
class ChatRequest(BaseModel):
    question: str

@app.post("/chat")
def chat(request: ChatRequest):
    return csv_agent_func(request.question)