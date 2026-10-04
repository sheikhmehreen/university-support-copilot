import json
import os
import secrets

from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from openai import OpenAI
from pydantic import BaseModel

load_dotenv()

client = OpenAI(
    api_key=os.getenv("LLM_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)
MODEL = os.getenv("LLM_MODEL")
API_SECRET = os.getenv("API_SECRET")

app = FastAPI(title="University Student Support Copilot")

PRIORITIES = {"Low", "Medium", "High"}

SYSTEM_PROMPT = """You classify university student support tickets.
Return ONLY a JSON object with exactly these keys:
- "category": a short label, 2-3 words (e.g. "Account Access", "Fee Challan", "Result Issue")
- "priority": one of "Low", "Medium", "High"
- "summary": one sentence, max 20 words
Use High only for urgent issues such as exam or deadline problems or being locked out."""


class Ticket(BaseModel):
    student_name: str
    student_id: str
    email: str
    department: str
    subject: str | None = None
    description: str


def verify_key(x_api_key: str | None = Header(default=None)):
    if not API_SECRET or not x_api_key or not secrets.compare_digest(x_api_key, API_SECRET):
        raise HTTPException(status_code=401, detail="Invalid API key")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/classify", dependencies=[Depends(verify_key)])
def classify(ticket: Ticket):
    user_msg = (
        f"Department: {ticket.department}\n"
        f"Subject: {ticket.subject or 'N/A'}\n"
        f"Description: {ticket.description}"
    )
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_msg},
            ],
            response_format={"type": "json_object"},
            temperature=0,
        )
        data = json.loads(resp.choices[0].message.content)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM error: {e}")

    if data.get("priority") not in PRIORITIES:
        data["priority"] = "Medium"

    return {
        "category": data.get("category", "Uncategorized"),
        "priority": data["priority"],
        "summary": data.get("summary", ticket.description),
    }