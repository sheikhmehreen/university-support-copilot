"""Security test 1: authentication and input validation.

Run (uvicorn must be running in another terminal):
    cd api
    python security_test.py

To test the deployed Vercel API instead:
    $env:BASE_URL = "https://your-app.vercel.app"
    python security_test.py
"""
import os

import httpx
from dotenv import load_dotenv

load_dotenv(override=True)

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:8000").rstrip("/")
KEY = os.getenv("API_SECRET")

GOOD = {"x-api-key": KEY}
BAD = {"x-api-key": "wrong-key"}

VALID_TICKET = {
    "student_name": "Test",
    "student_id": "BC000000",
    "email": "test@example.com",
    "department": "finance",
    "subject": "Fee",
    "description": "I paid my fee but it shows unpaid.",
}

# (name, method, path, headers, json body, expected status)
CASES = [
    ("health is public", "GET", "/health", {}, None, 200),
    ("classify: no key", "POST", "/classify", {}, VALID_TICKET, 401),
    ("classify: wrong key", "POST", "/classify", BAD, VALID_TICKET, 401),
    ("answer: no key", "POST", "/answer", {}, {"question": "When is the fee deadline?"}, 401),
    ("answer: wrong key", "POST", "/answer", BAD, {"question": "When is the fee deadline?"}, 401),
    ("search: no key", "POST", "/search", {}, {"query": "fee deadline"}, 401),
    ("search: wrong key", "POST", "/search", BAD, {"query": "fee deadline"}, 401),
    ("classify: missing field", "POST", "/classify", GOOD, {"student_name": "x"}, 422),
    ("answer: question too short", "POST", "/answer", GOOD, {"question": "hi"}, 422),
    ("answer: top_k too large", "POST", "/answer", GOOD, {"question": "fee deadline", "top_k": 99}, 422),
    ("search: bad department", "POST", "/search", GOOD, {"query": "fee deadline", "department": "hacking"}, 422),
]


def main():
    if not KEY:
        print("API_SECRET not found in .env")
        return
    passed = 0
    for name, method, path, headers, body, expected in CASES:
        try:
            r = httpx.request(method, BASE_URL + path, headers=headers, json=body, timeout=60)
            status = r.status_code
        except Exception as e:
            print(f"ERROR {name}: {e!r}")
            continue
        ok = status == expected
        passed += ok
        print(f"{'PASS' if ok else 'FAIL'}  {name}: expected {expected}, got {status}")
    print(f"\n{passed}/{len(CASES)} passed against {BASE_URL}")


if __name__ == "__main__":
    main()