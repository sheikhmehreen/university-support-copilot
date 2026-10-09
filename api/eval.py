import csv
import time

from fastapi.testclient import TestClient

from main import API_SECRET, app

client = TestClient(app)
HEADERS = {"x-api-key": API_SECRET or ""}

rows = list(csv.DictReader(open("eval_tickets.csv", encoding="utf-8")))
results = []
priority_ok = 0
review_ok = 0

print(f"{'#':<3} {'expected':<8} {'got':<8} {'prio':<5} {'review':<7} category (got / expected)")
print("-" * 80)

for i, row in enumerate(rows, start=1):
    ticket = {
        "student_name": "Eval",
        "student_id": "0",
        "email": "eval@example.com",
        "department": row["department"],
        "description": row["description"],
    }
    r = client.post("/classify", json=ticket, headers=HEADERS)

    if r.status_code != 200:
        print(f"{i:<3} request failed: {r.status_code} {r.text[:80]}")
        results.append({**row, "got_priority": "ERROR", "got_category": "", "got_review": ""})
        continue

    out = r.json()
    p_match = out["priority"] == row["expected_priority"]
    r_match = str(out["needs_review"]).lower() == row["expected_review"]
    priority_ok += p_match
    review_ok += r_match

    print(
        f"{i:<3} {row['expected_priority']:<8} {out['priority']:<8} "
        f"{'OK' if p_match else 'FAIL':<5} {'OK' if r_match else 'FAIL':<7} "
        f"{out['category']} / {row['expected_category']}"
    )
    results.append({
        **row,
        "got_priority": out["priority"],
        "got_category": out["category"],
        "got_review": out["needs_review"],
    })
    time.sleep(1)

total = len(rows)
print("-" * 80)
print(f"Priority accuracy:     {priority_ok}/{total} ({priority_ok / total:.0%})")
print(f"needs_review accuracy: {review_ok}/{total} ({review_ok / total:.0%})")
print("Category is free text, so compare the last column by eye.")

with open("eval_results.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(results[0].keys()))
    writer.writeheader()
    writer.writerows(results)
print("Saved eval_results.csv")