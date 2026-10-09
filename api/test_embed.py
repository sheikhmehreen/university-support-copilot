import os
import httpx
from dotenv import load_dotenv

load_dotenv(override=True)
r = httpx.post(
    "https://api.jina.ai/v1/embeddings",
    headers={"Authorization": f"Bearer {os.getenv('EMBED_API_KEY')}"},
    json={
        "model": "jina-embeddings-v3",
        "task": "retrieval.query",
        "input": ["How do I reset my portal password?"],
    },
    timeout=30,
)
print(r.status_code)
print(len(r.json()["data"][0]["embedding"]))